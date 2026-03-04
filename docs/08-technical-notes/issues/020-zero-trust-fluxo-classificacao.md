# [team-devs-ai] Postura Zero Trust: fluxo e classificação de ações

**Fase:** 2 — Segurança  
**Labels:** security, zero-trust

## Descrição

Implementar a postura Zero Trust (nunca confiar, sempre verificar). Fluxo PARAR → PENSAR → VERIFICAR → PERGUNTAR → AGIR → REGISTRAR antes de ações externas. Classificação de ações: PERGUNTAR PRIMEIRO vs FAZER LIVREMENTE.

## Critérios de aceite

- [ ] Fluxo em 6 passos integrado aos agentes (ou documentado em SOUL/TOOLS para seguirem).
- [ ] Tabela de classificação aplicada: PERGUNTAR PRIMEIRO (URLs desconhecidas, envio de mensagens, transações, criar contas, APIs desconhecidas, etc.); FAZER LIVREMENTE (operações locais, buscas em motores confiáveis, leitura de doc, desenvolvimento local).
- [ ] Regras de credenciais: armazenar em ~/.config/ com permissões 600; nunca ecoar/logar/commitar; nunca em respostas de chat.
- [ ] Red flags documentadas e checadas: sudo, código ofuscado, "confie em mim", urgência artificial, desativar segurança, credenciais via chat.
- [ ] Regras de instalação: nunca instalar pacotes sem verificar origem, ler código/descrição e aprovação do Diretor.
- [ ] **Score de confiança e quarentena:** para requisições de rede/skills com **manifesto validado na borda** (ex.: x255) e **sem binários ocultos**, executar em **sandbox/quarentena isolada** em vez de pausar para OK manual do Diretor; casos de baixa confiança mantêm "perguntar primeiro". Ver [05-seguranca-e-etica.md](../05-seguranca-e-etica.md) (matriz de escalonamento probabilística).
- [ ] **Proxy de dependências:** sandbox Developer air-gapped obtém pacotes via **proxy reverso** com manifesto estático (ex.: package.json/lock) e **hashes aprovados** (whitelist determinística); fora da lista → timeout.
- [ ] **Sandbox para URLs/APIs desconhecidas:** para acessar URL ou API não classificada como confiável, executar a requisição em **container efêmero isolado** (sem rede principal), registrar payload de entrada/saída e syscalls; se resultado seguro, prosseguir; Diretor revisa **resultado da interação** no digest diário (não cada pedido). Ver [05-seguranca-e-etica.md](../05-seguranca-e-etica.md) e [14-seguranca-runtime-agentes.md](../14-seguranca-runtime-agentes.md).
- [ ] **Acelerador preditivo de orçamento:** quando o sistema prever estouro (ex.: por tamanho do diff do PR), rotear tarefa para **modelo local em CPU** em vez de disparar freio de emergência e Telegram; manter esteira sem travar sprint. Ver [05-seguranca-e-etica.md](../05-seguranca-e-etica.md) e [07-configuracao-e-prompts.md](../07-configuracao-e-prompts.md).
- [ ] **Pipeline de quarentena automatizada:** orquestrador **provisiona sandbox isolado instantaneamente** quando o Developer pedir um pacote novo (**em vez de mandar mensagem no Telegram**); **não interrompe a sprint**. Dentro do sandbox, agente guardião (ex.: CyberSec) roda **varredura** (ex.: Snyk, Trivy) e **testes de injeção**. Antes de transferir para o repositório: verificação de **assinaturas criptográficas** (matriz de confiança), **SAST leve (semgrep)** com regras estritas e **checagem de entropia contextual** (whitelist de extensões; rejeitar ou escalar para CyberSec conforme issue 128) — ver [128-sast-entropia-quarentena.md](128-sast-entropia-quarentena.md), [05-seguranca-e-etica.md](../05-seguranca-e-etica.md) e [14-seguranca-runtime-agentes.md](../14-seguranca-runtime-agentes.md)). Se a biblioteca tiver **score impecável** e as validações passarem, **aprovação temporária** para uso imediato; o humano é **notificado de forma assíncrona só no resumo diário** — audita depois, **sem travar o código agora**. Zero Trust na velocidade da máquina.
- [ ] **Zonas de confiança de autores:** permitir que o agente DevOps instale dependências **sem aprovação direta** se o pacote for **assinado criptograficamente por publicadores da matriz** (ex.: Google, Vercel, Microsoft — coisas oficiais). **Reservar a atenção do Diretor humano só para bibliotecas comunitárias desconhecidas**, onde o risco real de ataque existe. Diretor volta a ser **estrategista em vez de apertador de botão de aprovação de pacote**. Ver [05-seguranca-e-etica.md](../05-seguranca-e-etica.md).
- [ ] **Egress/domínios:** alinhar à **whitelist global estática** no Gateway e **verificação de reputação de domínio** (não depender da autodeclaração da skill no manifesto). Ver [024-skills-terceiros-checklist-egress.md](024-skills-terceiros-checklist-egress.md) e [05-seguranca-e-etica.md](../05-seguranca-e-etica.md).

## Implementação (início Fase 2)

- **Fluxo 6 passos e classificação:** Documentado em [20-zero-trust-fluxo.md](../20-zero-trust-fluxo.md) (referência para SOUL/TOOLS).
- **Egress whitelist:** ConfigMap de referência [k8s/security/egress-whitelist-configmap.yaml](../../k8s/security/egress-whitelist-configmap.yaml); Gateway deve usar lista estática e validação de reputação de domínio.
- Demais itens (score de confiança, proxy de dependências, sandbox URL, pipeline de quarentena, zonas de confiança) seguem em [05-seguranca-e-etica.md](../05-seguranca-e-etica.md) e [14-seguranca-runtime-agentes.md](../14-seguranca-runtime-agentes.md); implementação operacional conforme evolução do orquestrador.

## Referências

- [05-seguranca-e-etica.md](../05-seguranca-e-etica.md)
- [07-configuracao-e-prompts.md](../07-configuracao-e-prompts.md) (Acelerador preditivo)
- [14-seguranca-runtime-agentes.md](../14-seguranca-runtime-agentes.md) (Sandbox URL/API)
