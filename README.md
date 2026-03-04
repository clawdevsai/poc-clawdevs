# ClawDevsAI - Guia de Início Rápido para Desenvolvedores 🚀

Bem-vindo ao **ClawDevsAI**! Este repositório contém todo o ecossistema K8s de agentes geridos pelo OpenClaw e suportado por LLMs locais (Ollama).

Este guia possui **exatamente o que você precisa saber** e a **ordem correta dos comandos** para rodar o projeto na sua máquina local a partir do zero.

---

## 📋 Como Funciona a Arquitetura Básica?

Antes de rodar os comandos, é importante saber que **tudo roda dentro do Kubernetes** (`minikube`). Não rodamos nada solto na máquina!
- **Orquestração:** OpenClaw Gateway.
- **LLM (Cérebro):** Ollama rodando nativamente no cluster (com suporte a GPU).
- **Memória / Estado:** Redis gerencia filas (streams) e sessões.
- **Agentes:** CEO, PO, Developer, DevOps, Revisão, etc., como PODs que conversam entre si.

---

## 💻 Passo a Passo: Subindo o Ambiente (Na Ordem Certa)

Siga os passos exatamente nesta ordem para garantir que a instalação seja bem sucedida.

### Passo 1: Configurar Variáveis de Ambiente
O sistema depende de chaves para acessar o GitHub e o Telegram/Slack.
1. Crie um arquivo chamado `.env` na raiz deste projeto.
2. Adicione os tokens de acessos necessários (peça o `.env` base para sua equipe).
   - O sistema precisa desses segredos para rodar scripts como o de puxar/enviar código, orquestração e alertas.

### Passo 2: Preparar a sua Máquina (`make prepare`)
Este comando checa o que você já tem na máquina e instala os requisitos invisíveis (Docker, Minikube, Kubectl), além de criar e ligar o cluster onde a mágica acontece.
```bash
make prepare
```
> **Aviso:** Ele pode pedir sua senha (`sudo`) para instalar ferramentas. Caso ele instale o Docker, você pode ter que sair e entrar (logoff/login) na sua conta de usuário no PC para o Linux reconhecer a permissão do Docker.

### Passo 3: Criar a Pasta Compartilhada (`make shared`)
As IAs (agentes) vão editar arquivos e clonar códigos automaticamente. É necessário montar uma pasta na sua máquina para você ler os resultados localmente.
```bash
make shared
```
> Isso criará a pasta `~/clawdevs-shared` e a deixará sincronizada com o interior do Minikube.

### Passo 4: Subir Todo o Sistema (`make up`)
Chegamos ao passo principal. Isso vai empacotar o cérebro das IAs, aplicar as redes do Redis, alocar o Ollama (aproveitando sua GPU) e ligar todas as "pessoas" do time (agentes/PODs).
```bash
make up
```
> **Nota:** Esse processo pode demorar um pouco na primeira vez, pois ele fará o download de imagens de containers e preparará todo o ecossistema. No final do processo, ele imprimirá uma URL com a cara do painel de controle! (Algo como `http://<IP_DO_MINIKUBE>:30000`).
>
> **Alternativa:** Se precisar já aplicar todas as regras de segurança adicionais e ferramentas avançadas junto, você pode usar `make up-all`.

---

## 🛠️ Controle do Dia a Dia (Comandos Frequentes)

Você não fará o `make prepare` todos os dias. No seu fluxo normal, os comandos mais úteis que você vai utilizar são:

| O que você quer fazer? | Comando | Descrição |
| :--- | :--- | :--- |
| **Como estão os Agentes?** | `make status` | Mostra se os processos e serviços subiram corretamente dentro do Kubernetes. |
| **O que eles estão falando?** | `make status-pods` | Mostra os *logs* (diários de bordo) em tempo real do Ollama, Redis, OpenClaw, etc. |
| **Zerar a memória das IAs** | `make reset-memory` | Esquece todas as conversas anteriores para os agentes iniciarem projetos limpos. |
| **Meu PC aguenta a IA?** | `make verify` | Testa sua Placa de Vídeo (GPU) e CPU para garantir a estabilidade. |
| **Erro no Github?** | `make test-github-access` | Valida as credenciais do seu `.env` contra o Github para ver se a IA pode baixar o código. |
| **Dashboad Visual do K8s** | `make dashboard` | Abre o painel oficial do Kubernetes diretamente no seu navegador. |
| **Parar e apagar tudo** | `make down` | Desliga todos os processos e zera o cluster. Útil quando algo corrompeu e você quer um início limpo. |

---

## ⚠️ Boas Práticas (Regras de Ouro do ClawDevs)

1. **Nunca crie código se o OpenClaw já fizer:** Nosso sistema é baseado 100% no OpenClaw. Não reinvente a roda!
2. **K8s Ecosystem:** Nenhuma persistência de dados de runtime fica no "host" (seu PC). Tudo vive no Minikube e usa PVCs e Redis.
3. **Gratuito e Open Source:** Este projeto foca no uso estrito de Ollama e ferramentas abertas (sem OpenAI paga na infra principal).
