#!/usr/bin/env python3
"""
Script para debugar o problema dos agents não aparecendo no banco de dados.
Simula a inicialização da aplicação e testa a sincronização.
"""

import asyncio
import sys
from pathlib import Path

# Adicionar o diretório da aplicação ao path
sys.path.insert(0, str(Path(__file__).parent / "control-panel" / "backend"))

async def debug_agents():
    """Debug script para testar sincronização de agents."""

    # Setup
    print("=" * 80)
    print("DEBUG: Iniciando teste de sincronização de agents")
    print("=" * 80)

    try:
        # Import após adicionar ao path
        from app.core.config import get_settings
        from app.core.database import AsyncSessionLocal, run_migrations
        from app.services.agent_sync import sync_agents, AGENT_SLUGS
        from sqlmodel import select
        from app.models import Agent

        settings = get_settings()
        print(f"\n1. Configuração carregada:")
        print(f"   - Database URL: {settings.database_url}")
        print(f"   - OpenClaw data path: {settings.openclaw_data_path}")
        print(f"   - Run migrations on startup: {settings.run_db_migrations_on_startup}")

        # Tentar conectar ao banco
        print(f"\n2. Testando conexão com banco de dados...")
        try:
            async with AsyncSessionLocal() as session:
                result = await session.exec(select(Agent))
                existing_agents = result.all()
                print(f"   ✓ Conexão OK")
                print(f"   - Agents existentes no DB: {len(existing_agents)}")
                for agent in existing_agents:
                    print(f"     • {agent.slug}: {agent.display_name}")
        except Exception as e:
            print(f"   ✗ Erro ao conectar: {e}")
            return

        # Testar sincronização
        print(f"\n3. Testando sincronização de agents...")
        print(f"   - Total de agents definidos: {len(AGENT_SLUGS)}")
        print(f"   - Agents: {', '.join(AGENT_SLUGS)}")

        try:
            async with AsyncSessionLocal() as session:
                print(f"\n   Iniciando sincronização...")
                await sync_agents(session)
                print(f"   ✓ Sincronização concluída")
        except Exception as e:
            print(f"   ✗ Erro durante sincronização: {e}")
            import traceback
            traceback.print_exc()
            return

        # Verificar resultado
        print(f"\n4. Verificando resultado da sincronização...")
        try:
            async with AsyncSessionLocal() as session:
                result = await session.exec(select(Agent).order_by(Agent.slug))
                agents = result.all()
                print(f"   - Agents no DB agora: {len(agents)}")
                for agent in agents:
                    print(f"     • {agent.slug}: {agent.display_name} ({agent.role})")

                if len(agents) == len(AGENT_SLUGS):
                    print(f"\n✓ SUCESSO: Todos os {len(AGENT_SLUGS)} agents foram sincronizados!")
                else:
                    print(f"\n✗ FALHA: Esperava {len(AGENT_SLUGS)} agents, encontrou {len(agents)}")
        except Exception as e:
            print(f"   ✗ Erro ao verificar: {e}")
            return

    except ImportError as e:
        print(f"✗ Erro ao importar módulos: {e}")
        print(f"   Certifique-se de que está rodando no diretório correto")
        return
    except Exception as e:
        print(f"✗ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        return

if __name__ == "__main__":
    asyncio.run(debug_agents())
