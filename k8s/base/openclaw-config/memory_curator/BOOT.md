# BOOT.md - Memory_Curator

## Sequência de Boot

1. Carregar `IDENTITY.md`.
2. Carregar `AGENTS.md` (regras e capabilities).
3. Carregar `SOUL.md` (postura e limites rígidos).
4. Validar que `/data/openclaw/memory/` está acessível e contém subpastas dos agentes.
5. Verificar que `/data/openclaw/memory/shared/` existe; criar se ausente.
6. Verificar que `/data/openclaw/backlog/status/` existe para escrita de log.
7. Carregar `MEMORY.md` próprio: `/data/openclaw/memory/memory_curator/MEMORY.md`.
8. Pronto para executar ciclo de curadoria.

## healthcheck
- `/data/openclaw/memory/` acessível? ✅
- `/data/openclaw/memory/shared/SHARED_MEMORY.md` existe? ✅ (criar se não existir)
- `/data/openclaw/backlog/status/` gravável? ✅
- MEMORY.md (memory_curator) carregado? ✅

## Regras operacionais
- Nunca interagir com GitHub.
- Nunca se comunicar com outros agentes proativamente.
- Nunca deletar — apenas mover entre seções de MEMORY.md.
- Idempotência obrigatória: múltiplas execuções não duplicam padrões.
