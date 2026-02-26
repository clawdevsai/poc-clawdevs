---
description: Gestão de custos de API (FinOps) e eficiência energética/hardware (Ollama/GPU).
---
# ⚡ Hardware e FinOps (Baixo Custo e Performance)

- **Soberania do Host (Teto 65%):** O ecossistema de agentes (Pods K8s e Ollama) deve ser configurado para nunca ultrapassar 65% da CPU e RAM do hospedeiro.
- **GPU Lock Transacional:**
    - Toda inferência local exige a aquisição do `gpu_lock`.
    - O lock deve ser liberado imediatamente após a inferência para permitir a rotatividade entre agentes.
    - O lock possui TTL automático; nunca tente estender o lock manualmente além do tempo de uma requisição.
- **Pre-flight CPU:** Antes de solicitar a GPU para raciocínio complexo, use modelos SLM leves em CPU (ex: Phi-3 Mini) para validar sintaxe, lint e aderência superficial.
- **VFM (Value-for-Money):**
    - Toda proposta de evolução ou refatoração requer a geração do artefato `vfm_score.json`.
    - A decisão de seguir com a implementação é baseada na pontuação (Horas Salvas vs Custo de Tokens). Se negativo, simplifique a abordagem ou use modelos locais.
- **Token Bucket Estratégico:** Respeite o limite determinístico do Gateway para eventos de estratégia (ex: CEO limitado a 5 diretrizes/hora).
- **Acelerador Preditivo:** Se houver previsão de estouro de orçamento diário ($5/dia), o sistema deve forçar automaticamente o roteamento para modelos locais, degradando a velocidade em favor da continuidade financeira.
