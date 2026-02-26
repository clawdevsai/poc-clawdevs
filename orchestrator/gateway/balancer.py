"""
ClawDevs — Dynamic GPU/CPU Balancer
Implementa lógica de balanceamento de carga entre Nuvem, GPU local e CPU.
Atua em conjunto com o Gateway para otimizar custo e performance.
"""

import os
import logging
from dataclasses import dataclass

logger = logging.getLogger("clawdevs.balancer")

@dataclass
class ResourceState:
    gpu_locked: bool
    queue_depth: int
    daily_budget_ratio: float  # ratio of spent/limit (0.0 to 1.0)
    efficiency_ratio: float     # ratio of success/total (0.0 to 1.0)

class DynamicBalancer:
    """Decide qual recurso usar (Nuvem, GPU, CPU) com base no estado atual do sistema."""
    
    def __init__(self, r):
        self.r = r
        self.threshold_budget = float(os.getenv("BALANCER_BUDGET_THRESHOLD", "0.8")) # 80% do budget
        self.threshold_efficiency = float(os.getenv("BALANCER_EFFICIENCY_THRESHOLD", "0.4"))

    def get_resource_state(self) -> ResourceState:
        """Coleta estado atual do sistema do Redis."""
        gpu_locked = bool(self.r.get("gpu_active_lock"))
        queue_depth = int(self.r.xlen("orchestrator:events") or 0)
        
        # Simulação de budget e eficiência (valores reais viriam de counters do Redis)
        spent = float(self.r.get("finops:daily_spent") or 0.0)
        limit = float(os.getenv("FINOPS_DAILY_LIMIT", "5.0"))
        budget_ratio = spent / limit if limit > 0 else 1.0
        
        ceo_total = int(self.r.get("efficiency:ceo_ideas_total") or 1)
        po_approved = int(self.r.get("efficiency:po_approved_total") or 0)
        eff_ratio = po_approved / ceo_total
        
        return ResourceState(gpu_locked, queue_depth, budget_ratio, eff_ratio)

    def decide_placement(self, agent_role: str, task_priority: int = 1) -> str:
        """
        Retorna o tier de execução: 'cloud', 'gpu', 'cpu'.
        
        Regras:
        1. Se budget > 80% → Move tudo para GPU ou CPU (exceto CEO alta prioridade).
        2. Se eficiência < 40% → CEO e PO movem para CPU (phi-3) para reduzir desperdício de $.
        3. Se GPU lock ativa + fila > 5 → Se budget permite, escala para nuvem; senão CPU.
        4. Agentes leves (DevOps, UX) → Preferir CPU sempre.
        """
        state = self.get_resource_state()
        
        # Regra de Ouro: Emergência (Budget estourado)
        if state.daily_budget_ratio >= 1.0:
            logger.warning("BUDGET EXCEDIDO (%d%%). Forçando local unicamente.", state.daily_budget_ratio * 100)
            return "gpu" if not state.gpu_locked else "cpu"

        # Regra 1: Economia agressiva (Budget quase no fim)
        if state.daily_budget_ratio > self.threshold_budget:
            if agent_role not in ["CEO", "Architect"] or task_priority < 2:
                return "gpu" if not state.gpu_locked else "cpu"

        # Regra 2: Eficiência baixa (Punição de hardware)
        if state.efficiency_ratio < self.threshold_efficiency:
            if agent_role in ["CEO", "PO"]:
                logger.info("BAIXA EFICIÊNCIA (%.1f%%). Movendo CEO/PO para CPU.", state.efficiency_ratio * 100)
                return "cpu"

        # Regra 3: Gestão de fila
        if state.gpu_locked and state.queue_depth > 5:
            if state.daily_budget_ratio < 0.5: # Temos gordura financeira
                return "cloud"
            else:
                return "cpu"

        # Designação por Papel (Padrão)
        role_map = {
            "CEO": "cloud",
            "PO": "cloud",
            "Architect": "gpu",
            "Developer": "gpu",
            "QA": "gpu",
            "CyberSec": "gpu",
            "DBA": "gpu",
            "DevOps": "cpu",
            "UX": "cpu"
        }
        
        tier = role_map.get(agent_role, "cpu")
        
        # Ajuste se o tier desejado for GPU mas estiver lockada
        if tier == "gpu" and state.gpu_locked:
            return "cpu"
            
        return tier

    def get_model_for_tier(self, tier: str, agent_role: str) -> str:
        """Mapeia tier + papel para um modelo real (OpenRouter, Ollama GPU, Ollama CPU)."""
        if tier == "cloud":
            if agent_role == "CEO": return "openrouter/google/gemini-2.0-pro-02-05:free"
            return "openrouter/google/gemini-2.0-flash-001:free"
            
        if tier == "gpu":
            if agent_role in ["Developer", "DBA"]: return "ollama/deepseek-coder:6.7b"
            return "ollama/llama3:8b"
            
        # tier == "cpu"
        return "ollama/phi3:mini"
