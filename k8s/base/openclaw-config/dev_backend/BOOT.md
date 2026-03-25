# BOOT.md - Dev_Backend

## Sequência de Boot

1. Carregar `IDENTITY.md`.
2. Carregar `AGENTS.md`.
3. Ler `README.md` do repositório para entender a aplicação, stack e fluxo antes de implementar.
4. Carregar `SOUL.md`.
5. Carregar `INPUT_SCHEMA.json`.
6. Ler `/data/openclaw/memory/shared/SHARED_MEMORY.md` — aplicar padrões globais do time como contexto base.
7. Ler `/data/openclaw/memory/dev_backend/MEMORY.md` — resgatar aprendizados próprios de implementação relevantes.
8. Validar `/data/openclaw/` e workspace de implementação.
9. Detectar linguagem pelo `technology_stack` da task ou arquivos do projeto.
10. Carregar comandos padrão por linguagem (fallback se task não trouxer `## Comandos`):
    - Node.js: `npm ci`, `npm test`, `npm run lint`, `npm run build`
    - Python: `pip install -r requirements.txt`, `pytest`, `flake8`
    - Java (Maven): `mvn test`, `mvn -q -DskipTests package`
    - Go: `go test ./...`, `go vet ./...`, `go build ./...`
    - Rust: `cargo test`, `cargo clippy`, `cargo build --release`
11. Validar ferramentas: `read`, `write`, `exec`, `git`, `sessions_send`.
12. Verificar comandos via `exec`: `gh`, `web-search`, `web-read`.
13. Carregar metas padrão: latência alvo, consumo de recursos, custo por requisição.
14. Ao concluir a sessão: registrar até 3 aprendizados em `/data/openclaw/memory/dev_backend/MEMORY.md`.
15. Pronto para receber task do Arquiteto.

## healthcheck
- `/data/openclaw/` acessível? ✅
- INPUT_SCHEMA.json carregado? ✅
- Stack detectada? ✅
- Ferramentas `read`, `write`, `exec`, `git` disponíveis? ✅
- SHARED_MEMORY.md e MEMORY.md (dev_backend) lidos? ✅
- `ACTIVE_GITHUB_REPOSITORY` definido? ✅
