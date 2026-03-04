# GitHub — criar chave SSH e registrar no GitHub

Abordagem recomendada para autenticação no **host**: usar chave SSH em vez de token no `.env` para git (clone, push, pull). O `gh` CLI também pode usar SSH (`gh auth login -p ssh`).

## 1. Gerar chave SSH (ed25519)

```bash
ssh-keygen -t ed25519 -C "seu-email@exemplo.com" -f ~/.ssh/id_ed25519_github -N ""
```

- `-f ~/.ssh/id_ed25519_github`: arquivo da chave (ajuste no `.env` como `GIT_SSH_KEY_PATH` se usar outro nome).
- `-N ""`: sem passphrase (para automação/scripts). Para uso interativo, pode usar passphrase e `ssh-agent`.

## 2. Adicionar a chave ao ssh-agent (opcional, recomendado se usar passphrase)

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519_github
```

## 3. Usar a chave em comandos git

Para um único comando:

```bash
GIT_SSH_COMMAND="ssh -i $HOME/.ssh/id_ed25519_github -o IdentitiesOnly=yes" git clone git@github.com:clawdevsai/clawdevs.git
```

Ou no `.env` defina `GIT_SSH_KEY_PATH=~/.ssh/id_ed25519_github` e use:

```bash
GIT_SSH_COMMAND="ssh -i ${GIT_SSH_KEY_PATH/#\~/$HOME} -o IdentitiesOnly=yes" git clone git@github.com:owner/repo.git
```

Configuração persistente no `~/.ssh/config` (recomendado):

```
Host github.com
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519_github
  IdentitiesOnly yes
```

Depois disso, `git clone git@github.com:owner/repo.git` usa a chave automaticamente.

## 4. Registrar a chave pública no GitHub

1. Copie o conteúdo da chave **pública** (nunca a privada):

   ```bash
   cat ~/.ssh/id_ed25519_github.pub
   ```

2. No GitHub: **Settings** → **SSH and GPG keys** → **New SSH key**.
3. Cole o conteúdo em **Key**; em **Title** use um nome (ex.: `clawdevs-host`).
4. Salve.

## 5. Testar

```bash
ssh -T git@github.com
```

Deve aparecer algo como: `Hi <user>! You've successfully authenticated...`

## 6. Repositórios: usar URL SSH

- Clone: `git clone git@github.com:clawdevsai/clawdevs.git`
- Se o remote estiver em HTTPS, troque: `git remote set-url origin git@github.com:clawdevsai/clawdevs.git`

## 7. Agentes no cluster (workspace compartilhado)

Os agentes (CEO, PO, etc.) usam a chave em **`/workspace/.ssh/`** no pod (= **`~/clawdevs-shared/.ssh/`** no host). O arquivo **não vem gerado** — é preciso colocar a chave lá:

1. Gere a chave no host (passos 1 e 4 acima) ou use uma chave existente.
2. Crie a pasta no workspace compartilhado e copie a chave (mesmo nome que o pod espera):

   ```bash
   mkdir -p ~/clawdevs-shared/.ssh
   cp ~/.ssh/id_ed25519_github ~/clawdevs-shared/.ssh/
   cp ~/.ssh/id_ed25519_github.pub ~/clawdevs-shared/.ssh/
   chmod 700 ~/clawdevs-shared/.ssh
   chmod 600 ~/clawdevs-shared/.ssh/id_ed25519_github
   ```

3. O deployment do OpenClaw já define `GIT_SSH_COMMAND` apontando para `/workspace/.ssh/id_ed25519_github`. Os agentes devem usar URL SSH nos clones, ex.: `git clone git@github.com:clawdevsai/clawdevs /workspace/workspace/clawdevs`.

## 8. Resolver "Permission denied (publickey)" no pod

Se no pod aparecer `git@github.com: Permission denied (publickey)` ao clonar:

**Opção A — Corrigir SSH:** A chave pública usada no pod deve estar no GitHub na **conta que tem acesso** ao repositório. No host, veja a chave: `cat ~/clawdevs-shared/.ssh/id_ed25519_github.pub`. No GitHub: **Settings** → **SSH and GPG keys** → **New SSH key** → cole o conteúdo e salve.

**Opção B — Usar HTTPS com token (fallback):** O pod recebe `GITHUB_TOKEN` do Secret `clawdevs-github-secret`. Clone assim: `git clone https://x-access-token:$GITHUB_TOKEN@github.com/clawdevsai/clawdevs.git /workspace/workspace/clawdevs`. Funciona sem configurar SSH no GitHub.

## Referências

- [20-ferramenta-github-gh.md](20-ferramenta-github-gh.md) — uso do `gh` e token para pods.
- [GitHub: Connecting with SSH](https://docs.github.com/en/authentication/connecting-to-github-with-ssh).
