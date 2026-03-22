# BOOT.md - Memory_Curator

## Inicialização

Ao ser ativado (por cron ou chamada explícita):

1. Verificar que `/data/openclaw/memory/` existe e é acessível
2. Verificar que `/data/openclaw/memory/shared/SHARED_MEMORY.md` existe (criar se não existir)
3. Verificar que cada agente tem seu diretório em `/data/openclaw/memory/<id>/`
4. Confirmar permissões de escrita no PVC
5. Executar ciclo de promoção conforme HEARTBEAT.md

## Saída padrão ao iniciar

```
[Memory_Curator] Iniciando ciclo de curadoria — <timestamp>
[Memory_Curator] Agentes verificados: <N>
[Memory_Curator] Padrões coletados: <N>
```
