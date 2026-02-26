# Verificação da máquina (máquina de referência)

Resumo **somente leitura** de CPU, GPU, RAM e disco. Use para confirmar se sua máquina é equivalente à [máquina de referência](../00-objetivo-e-maquina-referencia.md). Não altera nenhuma configuração.

## Uso

A partir da pasta `docs/agents-devs/scripts/`:

```bash
./verify-machine.sh
```

Ou de qualquer lugar (ajuste o caminho ao repo):

```bash
/path/to/docs/agents-devs/scripts/verify-machine.sh
```

## O que é exibido

| Seção | Comando / fonte | Informação |
|-------|-----------------|------------|
| **CPU** | `lscpu` | Nome do modelo, CPU(s), threads por núcleo, núcleos por soquete (ou primeiras 20 linhas) |
| **GPU** | `nvidia-smi` | Nome, memória total, versão do driver (CSV). Se não houver NVIDIA: mensagem e `lspci` (VGA/3D) |
| **RAM** | `free -h` | Duas primeiras linhas (total, usado, livre, compartilhado, buff/cache, disponível) |
| **SSD / discos** | `lsblk -d -o NAME,SIZE,ROTA,MODEL` e `df -h /` | Dispositivos de bloco (tamanho, modelo) e partição raiz (tamanho, usado, disponível) |

## Comandos manuais (equivalente ao script)

Para verificar sem executar o script:

```bash
echo "=== CPU ==="
lscpu 2>/dev/null | grep -E "Nome do modelo|CPU\(s\)|Thread\(s\) per núcleo|Núcleo\(s\) por soquete" || lscpu 2>/dev/null | head -20

echo "=== GPU ==="
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader 2>/dev/null || nvidia-smi 2>/dev/null | head -15
# Se não tiver nvidia-smi: lspci | grep -iE "vga|3d"

echo "=== RAM ==="
free -h | head -2

echo "=== SSD / Discos ==="
lsblk -d -o NAME,SIZE,ROTA,MODEL 2>/dev/null
df -h /
```

## Referência

- Máquina de referência e specs esperadas: [00-objetivo-e-maquina-referencia.md](../00-objetivo-e-maquina-referencia.md)
- Limites de recursos (65%) e Minikube: [04-infraestrutura.md](../04-infraestrutura.md)
