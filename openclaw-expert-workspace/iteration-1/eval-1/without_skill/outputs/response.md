# OpenClaw: Agent Loop Explicado

## Visão Geral

O OpenClaw é um framework de agentes de IA para aplicações em canais de mensageria (WhatsApp, Telegram, etc.). O agent loop é o coração do sistema - o ciclo contínuo que processa mensagens de usuários e gera respostas inteligentes.

## O Fluxo Completo: Da Mensagem à Resposta

### 1. **Entrada da Mensagem**
- Um usuário envia uma mensagem através de um canal (WhatsApp, Telegram, Discord, etc.)
- O OpenClaw intercepta essa mensagem através de um webhook ou polling do servidor de mensageria
- A mensagem é extraída com metadados: remetente, timestamp, canal, contexto

### 2. **Processamento Inicial**
- A mensagem é validada e normalizada
- Contexto da conversa é recuperado (histórico de mensagens anteriores)
- Informações do usuário são carregadas se disponível
- Sistema de permissões/autenticação é verificado

### 3. **Roteamento e Intenção**
- O sistema analisa a mensagem para entender a intenção do usuário
- Decide qual agente ou skill deve processar a mensagem
- Pode haver múltiplos agentes especializados em diferentes tarefas
- Exemplo: um agente para FAQ, outro para processamento de pedidos, outro para suporte

### 4. **Execução do Agent Loop (Iterativo)**

Este é o núcleo do sistema. O loop funciona em iterações:

**Iteração 1:**
- Agent recebe a mensagem e contexto
- Analisa o que precisa ser feito
- Decide se pode responder diretamente OU se precisa usar ferramentas
- Se precisa de ferramentas → chama APIs, bancos de dados, serviços externos
- Se pode responder → gera a resposta

**Iteração 2+ (se necessário):**
- Aguarda resultado da ferramenta anterior
- Analisa o resultado
- Decide próximo passo: usar outra ferramenta, formular resposta, ou pedir esclarecimento
- Continua até ter informações suficientes para responder

### 5. **Construção da Resposta**
- Agent formata a resposta de forma apropriada para o canal
- Respeita limitações do canal (tamanho, formatação)
- Inclui elementos interativos se disponível (botões, menus)

### 6. **Envio da Resposta**
- Resposta é enviada ao usuário através do canal original
- Sistema registra a interação para análise e melhorias
- Estado da conversa é atualizado

## Exemplo Prático

```
Usuário: "Quero fazer um pedido de 2 pizzas"

1. ENTRADA: Mensagem recebida
2. PROCESSAMENTO: Extrair dados (quantidade, produto)
3. ROTEAMENTO: Chamar agente de pedidos
4. LOOP ITERAÇÃO 1:
   - Agente vê que precisa de mais informações
   - Pergunta: Qual sabor?
5. Usuário responde: "Margherita e Calabresa"
6. LOOP ITERAÇÃO 2:
   - Agente tem informações suficientes
   - Chama ferramenta: verificar disponibilidade no banco
   - Resultado: "Ambas disponíveis"
7. LOOP ITERAÇÃO 3:
   - Agente chama ferramenta: registrar pedido
   - Cria pedido no sistema
8. RESPOSTA: "Seu pedido foi registrado! Será entregue em 45 minutos"
```

## Componentes Chave do Loop

### Tool Calling (Chamada de Ferramentas)
- Agent pode chamar ferramentas externas (APIs, funções)
- Aguarda resultado antes de continuar
- Usa resultado para tomar próximas decisões

### Context Management (Gerenciamento de Contexto)
- Sistema mantém histórico da conversa
- Context é passado a cada iteração
- Permite que agent entenda conversa anterior

### State Machine (Máquina de Estados)
- Conversa segue estados (esperando info, processando, respondendo)
- Transições entre estados baseadas em ações
- Permite controlar fluxo de conversa complexa

### Rate Limiting & Throttling
- Sistema controla velocidade de envio de mensagens
- Evita flood e respeita limites do canal
- Gerencia carga do servidor

## Diferenças por Tipo de Agente

### Agente Simples
- Processa 1-2 iterações
- Responde com base em contexto da mensagem
- Exemplo: FAQ automático

### Agente Complexo
- Múltiplas iterações
- Chama várias ferramentas
- Mantém estado complexo
- Exemplo: Sistema de vendas com confirmação de pagamento

## Tratamento de Erros

Se algo der errado em qualquer etapa:
- Agent detecta o erro
- Tenta recuperação (retry, chamada alternativa)
- Se não conseguir, responde ao usuário com mensagem apropriada
- Registra erro para análise

## Resumo do Fluxo

```
Mensagem de Entrada
         ↓
    Validação
         ↓
   Roteamento
         ↓
┌─ AGENT LOOP ─────────────┐
│  Análise da Mensagem      │
│         ↓                 │
│  Precisa de Ferramenta?   │
│    ↙              ↘       │
│  Sim            Não       │
│   ↓              ↓        │
│ Chamar    Gerar Resposta  │
│ Ferramenta    ↓           │
│   ↓        Pronto         │
│ Aguardar      ↑           │
│  Resultado    │           │
│   ↓           └─← (volta)─┘
│  Analisar
│  Voltar ao Loop
└───────────────────────────┘
         ↓
  Formatação da Resposta
         ↓
  Envio ao Canal
         ↓
  Registro de Interação
```

## Conceitos Importantes

- **Streaming**: Alguns agentes enviam respostas parciais enquanto processam
- **Callbacks**: Sistema pode usar callbacks para eventos assíncronos
- **Timeout**: Se agent leva muito tempo, sistema cancela e responde erro
- **Fallback**: Se agente principal falha, tenta agente alternativo
- **Logging**: Cada passo é registrado para debug e analytics

O agent loop do OpenClaw é flexível e permite desde respostas simples e rápidas até processamentos complexos com múltiplas chamadas de ferramenta.
