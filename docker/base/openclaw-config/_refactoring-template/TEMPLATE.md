# OpenClaw Agent Refactoring Template

## Objetivo

Este template fornece a estrutura de referência para refatorar os 16 OpenClaw agents para uma estrutura production-grade full-stack. Cada agent deve seguir este padrão de organização para garantir:

- Consistência entre agents
- Manutenibilidade e escalabilidade
- Separação clara de responsabilidades
- Facilidade de testes e documentação

## Estrutura de Diretórios

```
agent-name/
├── IDENTITY.md              # Definição da identidade e propósito do agent
├── SKILL.md                 # Documentação da skill (interface pública)
├── manifest.json            # Metadados e configuração do agent
├── src/                     # Código-fonte principal
│   ├── index.ts            # Entry point principal
│   ├── core/               # Lógica central do agent
│   │   ├── agent.ts
│   │   ├── handlers.ts
│   │   └── utils.ts
│   ├── schemas/            # Validação com Zod/TypeScript
│   │   ├── config.ts
│   │   ├── request.ts
│   │   └── response.ts
│   └── integrations/       # Integrações externas
│       └── [service].ts
├── tests/                   # Suite de testes
│   ├── unit/
│   │   ├── core.test.ts
│   │   ├── handlers.test.ts
│   │   └── utils.test.ts
│   ├── integration/
│   │   └── agent.integration.test.ts
│   └── fixtures/           # Dados de teste
│       └── samples.ts
├── docs/                    # Documentação expandida
│   ├── README.md           # Visão geral
│   ├── ARCHITECTURE.md     # Arquitetura técnica
│   ├── CONFIGURATION.md    # Guia de configuração
│   └── TROUBLESHOOTING.md  # Resolução de problemas
├── examples/               # Exemplos de uso
│   ├── basic.ts
│   ├── advanced.ts
│   └── config-example.json
├── .env.example            # Variáveis de ambiente esperadas
├── .test.env               # Variáveis de teste
└── package.json            # Dependências e scripts

```

## Descrição de Arquivos Principais

### IDENTITY.md
Define a identidade do agent:
- Nome, propósito e responsabilidades
- Casos de uso principais
- Limites e restrições
- Integração com o ecossistema OpenClaw

### SKILL.md
Documentação da interface pública:
- Função/comando principal
- Parâmetros de entrada
- Saída esperada
- Exemplos de uso
- Tratamento de erros

### manifest.json
Configuração e metadados:
```json
{
  "name": "agent-name",
  "version": "1.0.0",
  "description": "Descrição breve",
  "main": "src/index.ts",
  "config": {
    "required": ["API_KEY"],
    "optional": ["OPTION_1"]
  },
  "hooks": ["on_startup", "on_shutdown"],
  "dependencies": []
}
```

### src/ - Código-fonte

#### core/
- `agent.ts`: Classe/função principal do agent
- `handlers.ts`: Manipuladores de eventos e requisições
- `utils.ts`: Funções utilitárias e helpers

#### schemas/
Validação de entrada/saída com Zod:
- `config.ts`: Schema para configuração
- `request.ts`: Schema para requisições
- `response.ts`: Schema para respostas

#### integrations/
Integrações com serviços externos (APIs, SDKs, etc)

### tests/
Suite de testes completa:
- Unit tests para funções isoladas
- Integration tests para fluxos completos
- Fixtures com dados de exemplo

### docs/
Documentação expandida:
- `README.md`: Overview e quick start
- `ARCHITECTURE.md`: Design técnico
- `CONFIGURATION.md`: Como configurar
- `TROUBLESHOOTING.md`: Problemas comuns e soluções

### examples/
Exemplos práticos de uso:
- `basic.ts`: Exemplo simples
- `advanced.ts`: Uso avançado
- `config-example.json`: Arquivo de configuração de exemplo

## Checklist de Refatoração

Veja `checklist.md` para lista completa de verificação com 14+ items para validar cada agent refatorado.

## Princípios de Design

1. **Separação de Responsabilidades**: Código organizado por função
2. **Type Safety**: TypeScript strict mode em todos os arquivos
3. **Testabilidade**: Cada função testável isoladamente
4. **Documentação**: Código autodocumentado com comments claros
5. **Configuração**: Externalizar via env vars e config files
6. **Validação**: Schemas Zod em pontos de entrada
7. **Error Handling**: Tratamento consistente de erros
8. **Logging**: Logs estruturados e rastreáveis

## Próximos Passos

1. Copiar esta estrutura para cada agent
2. Adaptar nomes e configurações específicas
3. Implementar ou refatorar o código existente
4. Executar checklist.md para validação
5. Atualizar documentação conforme necessário
6. Executar testes completamente
7. Fazer commit e PR

---

**Última atualização**: 2026-03-31
**Versão do template**: 1.0.0
