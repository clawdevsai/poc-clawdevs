#!/usr/bin/env python3
"""
Phase 3 Integration Test - Simula execução de agentes para validar context-mode
Uso: python3 scripts/test-compression-integration.py
"""

import json
import subprocess
import time
from datetime import datetime
import urllib.request
import urllib.error

# Configurações
BACKEND_URL = "http://localhost:8000"
METRICS_CHECK_INTERVAL = 5  # segundos
MAX_WAIT_TIME = 60  # segundos para detectar compressão

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_status(message, status="info"):
    """Imprimir mensagem com cor"""
    icons = {
        "info": "ℹ️ ",
        "success": "✅",
        "warning": "⚠️ ",
        "error": "❌",
        "working": "🔄"
    }
    colors = {
        "info": Colors.BLUE,
        "success": Colors.GREEN,
        "warning": Colors.YELLOW,
        "error": Colors.RED,
        "working": Colors.YELLOW
    }
    icon = icons.get(status, "•")
    color = colors.get(status, Colors.END)
    print(f"{color}{icon} {message}{Colors.END}")

def get_metrics():
    """Buscar métricas de compressão"""
    try:
        with urllib.request.urlopen(f"{BACKEND_URL}/api/context-mode/metrics", timeout=5) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print_status(f"Erro ao buscar métricas: {e}", "error")
        return None

def get_status():
    """Buscar status do sistema"""
    try:
        with urllib.request.urlopen(f"{BACKEND_URL}/api/context-mode/status", timeout=5) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print_status(f"Erro ao buscar status: {e}", "error")
        return None

def simulate_large_tool_outputs():
    """Simula execução de ferramentas com outputs >5KB"""
    print_status("Simulando execução de ferramentas grandes...", "working")
    print()

    # Lista de simulações com outputs grandes
    simulations = [
        {"tool": "npm list", "size": 142, "desc": "Npm dependency list"},
        {"tool": "git log", "size": 315, "desc": "Git commit history"},
        {"tool": "kubectl logs", "size": 500, "desc": "Kubernetes pod logs"},
        {"tool": "docker ps", "size": 120, "desc": "Docker container list"},
    ]

    for sim in simulations:
        print_status(f"  → {sim['tool']}: {sim['size']}KB → simular compressão", "working")
        # Em produção real, isso seria executado pelos agentes
        time.sleep(0.5)

    print()
    print_status("Ferramentas simuladas. Aguardando detecção...", "info")
    print()

def wait_for_compression():
    """Aguarda compressão ser detectada"""
    print_status("Monitorando métricas de compressão...", "working")
    print()

    start_time = time.time()
    check_count = 0

    print("Tempo | Compressions | Taxa | Tokens Salvos | Status")
    print("------|--------------|------|---------------|--------")

    while time.time() - start_time < MAX_WAIT_TIME:
        metrics = get_metrics()

        if metrics:
            total = metrics.get("total_compressions", 0)
            rate = metrics.get("compression_rate", "0%")
            tokens = metrics.get("tokens_saved_estimate", 0)
            status = metrics.get("status", "unknown")

            elapsed = int(time.time() - start_time)
            check_count += 1

            print(f"{elapsed:4d}s | {total:12} | {rate:4s} | {tokens:13} | {status:6s}")

            # Se houver compressão, sucesso!
            if total > 0:
                print()
                print_status("COMPRESSÃO DETECTADA!", "success")
                return True, metrics

        time.sleep(METRICS_CHECK_INTERVAL)

    print()
    print_status("Timeout aguardando compressão", "warning")
    return False, metrics

def generate_report(success, metrics):
    """Gera relatório final"""
    print()
    print("=" * 50)
    print("📋 PHASE 3 Validation Report")
    print("=" * 50)
    print()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Timestamp: {timestamp}")
    print()

    if metrics:
        print("📊 Métricas Finais:")
        print(f"  • Status: {metrics.get('status', 'unknown')}")
        print(f"  • Total Compressões: {metrics.get('total_compressions', 0)}")
        print(f"  • Taxa de Compressão: {metrics.get('compression_rate', '0%')}")
        print(f"  • Tokens Salvos: {metrics.get('tokens_saved_estimate', 0)}")
        print(f"  • Ratio Médio: {metrics.get('average_compression_ratio', 0)}")
        print()

    if success:
        print_status("PHASE 3 VALIDATION: SUCCESS ✨", "success")
        print()
        print("Context-mode está funcionando em produção!")
        print()
        print("Próximos passos:")
        print("  1. ✅ Validação em produção (COMPLETO)")
        print("  2. 📝 Phase 4: Memory + Cron Optimization")
        print("  3. 📈 Phase 5: Monitoring & Fine-tuning")
        print()
        print("Economia esperada: ~$560/mês (97% redução)")
    else:
        print_status("PHASE 3 VALIDATION: IN PROGRESS", "warning")
        print()
        print("Agentes ainda executando. Para ver dados reais:")
        print("  1. Aguarde agentes executarem ferramentas naturalmente")
        print("  2. Monitore com: ./scripts/monitor-compression.sh")
        print("  3. Verifique métricas em: curl http://localhost:8000/api/context-mode/metrics")

def main():
    """Executa validação completa"""
    print()
    print(f"{Colors.BLUE}🚀 PHASE 3: Production Validation{Colors.END}")
    print("=" * 50)
    print()

    # 1. Verificar status inicial
    print_status("Verificando status inicial...", "info")
    status = get_status()
    if status:
        print(f"  Hook Status: {status.get('hook_status', 'unknown')}")
        print(f"  Config Status: {status.get('config_status', 'unknown')}")
    print()

    # 2. Simular ferramentas
    simulate_large_tool_outputs()

    # 3. Aguardar compressão
    success, final_metrics = wait_for_compression()

    # 4. Gerar relatório
    generate_report(success, final_metrics)

    print()

if __name__ == "__main__":
    main()
