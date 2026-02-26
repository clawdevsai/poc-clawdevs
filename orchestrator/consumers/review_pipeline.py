"""
ClawDevs — Pipeline Explícito de Revisão (Slot Único)
Job "Revisão pós-Dev" que adquire o GPU Lock UMA vez e executa
Architect → QA → CyberSec → DBA em sequência.

Evita que múltiplos agentes acordem ao mesmo tempo para o evento code:ready
e disputem o GPU Lock simultaneamente (causando OOM na VRAM).

Pipeline pré-GPU: validação em CPU (síntaxe, lint, SOLID) antes de disputar GP lock.
Batching de PRs: acumula micro-alterações para revisão em lote.

Referências:
  docs/issues/125-pipeline-explicito-slot-unico-revisao.md
  docs/estrategia-uso-hardware-gpu-cpu.md
  docs/03-arquitetura.md (Estágio pré-GPU, Batching de PRs)
"""

import os
import time
import logging
import json

logger = logging.getLogger("clawdevs.review_pipeline")


class PreGPUValidator:
    """Validação determinística em CPU antes de disputar o GPU Lock.
    Usa SLM leve (Phi-3 Mini via Ollama em CPU) para sintaxe, lint e SOLID básico.
    Falhas aqui evitam que diff inválido entre na fila da GPU.
    """

    def __init__(self, ollama_base_url: str = "http://ollama:11434"):
        self.ollama_url = ollama_base_url
        self.cpu_model = os.getenv("PRE_GPU_MODEL", "phi3:mini")

    def validate(self, diff_content: str, language: str = "python") -> dict:
        """Aplica validação leve em CPU. Retorna dict com resultado."""
        import requests

        prompt = (
            f"Você é um analisador estático leve. Analise o diff abaixo APENAS para:\n"
            f"1. Erros de sintaxe óbvios em {language}\n"
            f"2. Violações graves de SOLID (ex.: God Object, acoplamento direto entre camadas)\n"
            f"3. Imports de bibliotecas suspeitas ou não padrão\n\n"
            f'Responda APENAS com JSON: {{"valid": true/false, "issues": ["issue1", ...]}}\n\n'
            f"DIFF:\n{diff_content[:3000]}"  # Limitar para CPU
        )
        try:
            resp = requests.post(
                f"{self.ollama_url}/api/generate",
                json={"model": self.cpu_model, "prompt": prompt, "stream": False},
                timeout=30,
            )
            resp.raise_for_status()
            response_text = resp.json().get("response", "{}")
            # Extrair JSON da resposta
            import re

            json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            logger.warning(
                "Validação pré-GPU falhou (%s). Deixando passar para GPU.", e
            )
        return {"valid": True, "issues": []}  # Fail open para não travar esteira


class BatchingBuffer:
    """Acumula micro-PRs do Developer para revisão em lote pelo Architect.
    Reduz contenção no GPU Lock.
    """

    BATCH_KEY_PREFIX = "batching:pr_queue"
    BATCH_LOCK_KEY = "batching:flush_lock"

    def __init__(self, r, max_batch_size: int = 5, max_wait_seconds: int = 120):
        self.r = r
        self.batch_key = (
            f"{self.BATCH_KEY_PREFIX}:{os.getenv('AGENT_NAMESPACE', 'default')}"
        )
        self.max_size = int(os.getenv("BATCH_MAX_SIZE", str(max_batch_size)))
        self.max_wait = int(os.getenv("BATCH_MAX_WAIT_SECONDS", str(max_wait_seconds)))

    def add(self, pr_id: str, diff_content: str) -> int:
        """Adiciona PR ao batch. Retorna tamanho atual do batch."""
        import time

        entry = json.dumps(
            {
                "pr_id": pr_id,
                "diff": diff_content,
                "added_at": int(time.time()),
            }
        )
        self.r.rpush(self.batch_key, entry)
        self.r.expire(self.batch_key, self.max_wait * 2)
        return self.r.llen(self.batch_key)

    def should_flush(self) -> bool:
        """Verifica se deve fazer flush do batch (tamanho ou tempo máximo atingido)."""
        size = self.r.llen(self.batch_key)
        if size >= self.max_size:
            return True
        # Verificar tempo do primeiro item
        first = self.r.lindex(self.batch_key, 0)
        if first:
            try:
                data = json.loads(first)
                age = int(time.time()) - data.get("added_at", 0)
                if age >= self.max_wait:
                    return True
            except Exception:
                pass
        return False

    def flush(self) -> list[dict]:
        """Retorna todos os PRs do batch e limpa a fila."""
        entries = []
        while True:
            item = self.r.lpop(self.batch_key)
            if not item:
                break
            try:
                entries.append(json.loads(item))
            except Exception:
                pass
        return entries


class ReviewPipeline:
    """Slot único de revisão: adquire GPU Lock UMA vez e executa todos os revisores em sequência.
    Revisores: Architect → QA → CyberSec → DBA
    Uso do mesmo modelo (carregado uma vez na VRAM).
    """

    REVIEW_STREAM = "code:ready"
    REVIEW_GROUP = "cg-review"
    RESULT_STREAM = "review:result"

    def __init__(self):
        from orchestrator.consumers.base_consumer import _get_redis
        from scripts.gpu_lock import GPULock

        self.r = _get_redis()
        self.GPULock = GPULock
        self.pre_gpu = PreGPUValidator()
        self.ollama_url = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
        self.review_model = os.getenv("REVIEW_MODEL", "llama3:8b")

    def _call_ollama(self, prompt: str, timeout: int = 60) -> str:
        import requests

        try:
            resp = requests.post(
                f"{self.ollama_url}/api/generate",
                json={"model": self.review_model, "prompt": prompt, "stream": False},
                timeout=timeout,
            )
            resp.raise_for_status()
            return resp.json().get("response", "")
        except Exception as e:
            logger.error("Erro chamando Ollama: %s", e)
            raise

    def run_review(self, pr_id: str, diff_content: str, issue_id: str) -> dict:
        """Executa pipeline completo de revisão para um PR.
        1. Validação pré-GPU (CPU, sem lock)
        2. Acquire GPU Lock
        3. Architect → QA → CyberSec → DBA (sequencialmente, mesmo lock)
        4. Release GPU Lock
        """
        results = {"pr_id": pr_id, "issue_id": issue_id, "reviews": {}}

        # PASSO 1: Validação pré-GPU em CPU (sem lock)
        logger.info("[ReviewPipeline] PR %s — validação pré-GPU em CPU...", pr_id)
        pre_result = self.pre_gpu.validate(diff_content)
        if not pre_result.get("valid", True):
            results["pre_gpu_failed"] = True
            results["pre_gpu_issues"] = pre_result.get("issues", [])
            logger.warning(
                "[ReviewPipeline] PR %s rejeitado na pré-GPU: %s",
                pr_id,
                pre_result["issues"],
            )
            self._publish_result(results, approved=False)
            return results

        # PASSO 2-4: Adquirir GPU Lock e executar revisores em sequência
        event_key = f"issue:{issue_id}"
        logger.info(
            "[ReviewPipeline] PR %s — adquirindo GPU Lock (event_key=%s)...",
            pr_id,
            event_key,
        )

        with self.GPULock(event_key=event_key):
            logger.info(
                "[ReviewPipeline] PR %s — GPU Lock adquirido. Iniciando revisores.",
                pr_id,
            )

            # Architect
            results["reviews"]["architect"] = self._run_architect(
                pr_id, diff_content, issue_id
            )

            # QA (apenas se Architect aprovado)
            if results["reviews"]["architect"].get("approved"):
                results["reviews"]["qa"] = self._run_qa(pr_id, diff_content)

            # CyberSec (independente do QA)
            results["reviews"]["cybersec"] = self._run_cybersec(pr_id, diff_content)

            # DBA (apenas se mudanças de banco detectadas)
            if "migration" in diff_content.lower() or "schema" in diff_content.lower():
                results["reviews"]["dba"] = self._run_dba(pr_id, diff_content)

        # Calcular aprovação final
        arch_approved = results["reviews"].get("architect", {}).get("approved", False)
        sec_approved = results["reviews"].get("cybersec", {}).get("approved", True)
        qa_approved = results["reviews"].get("qa", {}).get("approved", True)
        dba_approved = results["reviews"].get("dba", {}).get("approved", True)

        all_approved = arch_approved and sec_approved and qa_approved and dba_approved
        results["approved"] = all_approved
        self._publish_result(results, approved=all_approved)
        return results

    def _run_architect(self, pr_id: str, diff: str, issue_id: str) -> dict:
        logger.info("[ReviewPipeline] Architect revisando PR %s...", pr_id)
        prompt = (
            f"Você é o Agente Architect do ClawDevs. Revise APENAS o diff abaixo.\n"
            f"Critérios: arquitetura limpa, padrões SOLID, sem over-engineering.\n"
            f'Responda em JSON: {{"approved": true/false, "comments": ["..."]}}\n\n'
            f"DIFF DO PR {pr_id}:\n{diff[:5000]}"
        )
        response = self._call_ollama(prompt, timeout=90)
        return self._parse_review_response(response)

    def _run_qa(self, pr_id: str, diff: str) -> dict:
        logger.info("[ReviewPipeline] QA revisando PR %s...", pr_id)
        prompt = (
            f"Você é o Agente QA do ClawDevs. Verifique se o diff tem:\n"
            f"1. Testes unitários adequados\n"
            f"2. Edge cases cobertos\n"
            f"3. Sem regressões óbvias\n"
            f'Responda em JSON: {{"approved": true/false, "comments": ["..."]}}\n\n'
            f"DIFF:\n{diff[:5000]}"
        )
        response = self._call_ollama(prompt, timeout=60)
        return self._parse_review_response(response)

    def _run_cybersec(self, pr_id: str, diff: str) -> dict:
        logger.info("[ReviewPipeline] CyberSec revisando PR %s...", pr_id)
        prompt = (
            f"Você é o Agente CyberSec do ClawDevs (OWASP, Zero Trust).\n"
            f"Verifique: injeções, chaves expostas, dependências suspeitas, SSRF, path traversal.\n"
            f"IMPORTANTE: Se encontrar vulnerabilidade crítica, marcar approved=false com tag 'cybersec'.\n"
            f'Responda em JSON: {{"approved": true/false, "critical": false, "tag": "cybersec", "comments": ["..."]}}\n\n'
            f"DIFF:\n{diff[:5000]}"
        )
        response = self._call_ollama(prompt, timeout=60)
        return self._parse_review_response(response)

    def _run_dba(self, pr_id: str, diff: str) -> dict:
        logger.info(
            "[ReviewPipeline] DBA revisando PR %s (mudanças de banco detectadas)...",
            pr_id,
        )
        prompt = (
            f"Você é o Agente DBA do ClawDevs. Revise apenas as mudanças de banco de dados:\n"
            f"migrations, schema, queries, índices. Foco em performance e normalização.\n"
            f'Responda em JSON: {{"approved": true/false, "comments": ["..."]}}\n\n'
            f"DIFF:\n{diff[:3000]}"
        )
        response = self._call_ollama(prompt, timeout=60)
        return self._parse_review_response(response)

    def _parse_review_response(self, response: str) -> dict:
        import re

        try:
            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception:
            pass
        return {"approved": False, "comments": ["Erro ao parsear resposta do agente."]}

    def _publish_result(self, results: dict, approved: bool):
        self.r.xadd(
            self.RESULT_STREAM,
            {
                "pr_id": results.get("pr_id", ""),
                "issue_id": results.get("issue_id", ""),
                "approved": "true" if approved else "false",
                "results_json": json.dumps(results),
                "timestamp": str(int(time.time())),
            },
        )
