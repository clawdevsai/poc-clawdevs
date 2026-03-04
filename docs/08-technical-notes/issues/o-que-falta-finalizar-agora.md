# O que falta para finalizar (agora)

Resumo do que ainda pode ser feito para considerar o projeto **finalizado** no estado atual (Fases 0–7 concluídas no repositório).

---

## 1. No repositório — nada obrigatório pendente

As **Fases 0 a 7** estão implementadas e documentadas no plano:

- **Fase 0–3:** Fundação, Agentes, Segurança, Operações ✅  
- **Fase 4:** Config/FinOps (040, 041) ✅  
- **Fase 5:** Self-improvement e memória (050–053) ✅  
- **Fase 6:** Habilidades transversais (060, 061) ✅  
- **Fase 7:** Ferramentas (070–075) ✅  

Não há itens obrigatórios em aberto no escopo atual do repo.

**Itens Fase 2/3 priorizados (021, 024, 028, 126, 127, 128):** Documentação de implementação e critérios marcados: [021-implementacao.md](021-implementacao.md), [024-implementacao.md](024-implementacao.md), [028-implementacao.md](028-implementacao.md), [126-implementacao.md](126-implementacao.md), [127-implementacao.md](127-implementacao.md), [128-implementacao.md](128-implementacao.md).

---

## 2. Para “fechar com chave de ouro” (opcional)

Se quiser validar que tudo funciona antes de dar por encerrado:

1. **Checklist Fase 4** — [fase4-o-que-falta-finalizar.md](fase4-o-que-falta-finalizar.md) §4:
   - **Script único:** `./scripts/run_validacao_fase4.sh` (roda test_config_finops + validate_reverse_po)
   - `kubectl apply -f k8s/security/` (finops-config, agent-profiles)
   - Gateway sobe com envFrom finops-config
   - `POST /publish-to-cloud` retorna 200

2. **Token Git no .env** — Para scripts/agentes acessarem git/gh: definir `GH_TOKEN` ou `GITHUB_TOKEN` no `.env` (já documentado em [.env.example](../../.env.example) e [20-ferramenta-github-gh.md](../20-ferramenta-github-gh.md)).

3. **Ollama rodando** — Para testar `scripts/ollama.py list` (e uso local do Ollama).

---

## 3. Fora do repositório (OpenClaw / contrato)

Dependem do código e da operação do OpenClaw, não do repo:

- Usar **`/publish-to-cloud`** para eventos à nuvem (em vez de publicar direto).
- Aplicar **MAX_TOKENS** e **constraints de perfil** (CEO/PO) no provedor.
- Ver [fase4-o-que-falta-finalizar.md](fase4-o-que-falta-finalizar.md) §2.

---

## 4. Próximos passos (quando quiser avançar)

- **Fase 8** (090–099): Skills e ambiente (descoberta/instalação, criação de skills, auto-atualização, FreeRide).
- **Fases 9–11:** Integrações, Frontend/UX, Avançado (War Room, Chaos, balanceamento).

Ref: [.cursor/plans/plano_clawdevs_fases_5ff4260b.plan.md](../../.cursor/plans/plano_clawdevs_fases_5ff4260b.plan.md), [README.md](README.md) (tabela de fases).
