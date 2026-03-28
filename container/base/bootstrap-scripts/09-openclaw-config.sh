# Copyright (c) 2026 Diego Silva Morais <lukewaresoftwarehouse@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Verificar se o config ja existe e tem o token correto - evitar sobrescrita
# desnecessaria que causa "missing-meta-before-write" e faz o gateway encerrar.
_existing_token="$(jq -r '.gateway.auth.token // empty' "${OPENCLAW_STATE_DIR}/openclaw.json" 2>/dev/null || true)"
_existing_bind="$(jq -r '.gateway.bind // empty' "${OPENCLAW_STATE_DIR}/openclaw.json" 2>/dev/null || true)"
_allowed_origins_json="${OPENCLAW_CONTROL_UI_ALLOWED_ORIGINS_JSON:-}"
if [ -z "${_allowed_origins_json}" ]; then
  _allowed_origins_json="$(jq -cn \
    --arg o1 "http://127.0.0.1:18789" \
    --arg o2 "http://localhost:18789" \
    --arg o3 "http://openclaw:18789" \
    '[$o1,$o2,$o3] | unique')"
fi

is_valid_telegram_bot_token() {
  case "${1:-}" in
    ''|*' '*|*'	'*)
      return 1
      ;;
    *)
      ;;
  esac
  printf '%s' "${1}" | grep -Eq '^[0-9]{6,}:[A-Za-z0-9_-]{20,}$'
}

is_valid_telegram_chat_id() {
  printf '%s' "${1:-}" | grep -Eq '^-?[0-9]{5,}$'
}

_telegram_bot_token="${TELEGRAM_BOT_TOKEN_CEO:-}"
_telegram_chat_id="${TELEGRAM_CHAT_ID:-}"
_telegram_enabled="true"
if ! is_valid_telegram_bot_token "${_telegram_bot_token}" || ! is_valid_telegram_chat_id "${_telegram_chat_id}"; then
  _telegram_enabled="false"
  echo "[bootstrap] Telegram desabilitado: TELEGRAM_BOT_TOKEN_CEO/TELEGRAM_CHAT_ID invalidos ou placeholders"
fi
if [ "${_telegram_enabled}" = "true" ]; then
  _telegram_probe_http_code="$(curl -sS --max-time 8 -o /tmp/telegram-getme-probe.json -w "%{http_code}" "https://api.telegram.org/bot${_telegram_bot_token}/getMe" 2>/dev/null || true)"
  if [ "${_telegram_probe_http_code}" = "401" ]; then
    _telegram_enabled="false"
    echo "[bootstrap] Telegram desabilitado: bot token rejeitado pela API do Telegram"
  elif [ "${_telegram_probe_http_code}" != "200" ]; then
    echo "[bootstrap] Telegram probe inconclusivo (HTTP ${_telegram_probe_http_code:-n/a}); mantendo configuracao atual"
  fi
fi

_sandbox_mode="${OPENCLAW_SANDBOX_MODE:-off}"
case "${_sandbox_mode}" in
  off|non-main|all) ;;
  *)
    echo "[bootstrap] OPENCLAW_SANDBOX_MODE='${_sandbox_mode}' invalido; usando 'off'"
    _sandbox_mode="off"
    ;;
esac
_sandbox_session_tools_visibility="${OPENCLAW_SANDBOX_SESSION_TOOLS_VISIBILITY:-all}"
case "${_sandbox_session_tools_visibility}" in
  all|spawned) ;;
  *)
    _sandbox_session_tools_visibility="all"
    ;;
esac

if [ -f "${OPENCLAW_STATE_DIR}/openclaw.json" ] && [ -n "${_existing_token}" ] && [ "${_existing_token}" = "${OPENCLAW_GATEWAY_TOKEN}" ] && [ "${_existing_bind}" = "lan" ]; then
  echo "[bootstrap] openclaw.json ja configurado com token correto e bind valido (${_existing_bind}), pulando escrita"
  mkdir -p ~/.openclaw
  cp "${OPENCLAW_STATE_DIR}/openclaw.json" ~/.openclaw/openclaw.json
else
echo "[bootstrap] escrevendo openclaw.json (primeira execucao ou token mudou)"
cat > "${OPENCLAW_STATE_DIR}/openclaw.json" <<'EOF'
{
  "gateway": {
      "mode": "local",
      "bind": "lan",
      "port": 18789,
      "http": {
        "endpoints": {
          "chatCompletions": {
            "enabled": true
          }
        }
      },
    "controlUi": {
      "dangerouslyAllowHostHeaderOriginFallback": false,
      "dangerouslyDisableDeviceAuth": false,
      "allowedOrigins": __CONTROL_UI_ALLOWED_ORIGINS__
    },
    "auth": {
      "token": "__TOKEN__",
      "rateLimit": {
        "maxAttempts": 10,
        "windowMs": 60000,
        "lockoutMs": 300000
      }
    }
  },
  "models": {
    "providers": {
      "ollama": {
        "baseUrl": "http://ollama:11434",
        "models": [
          {
            "id": "qwen3-next:80b-cloud",
            "name": "qwen3-next:80b-cloud"
          },
          {
            "id": "gpt-oss:120b-cloud",
            "name": "gpt-oss:120b-cloud"
          },
          {
            "id": "nemotron-3-super:cloud",
            "name": "nemotron-3-super:cloud"
          },
          {
            "id": "qwen3-coder:480b-cloud",
            "name": "qwen3-coder:480b-cloud"
          },
          {
            "id": "gemma3:27b-cloud",
            "name": "gemma3:27b-cloud"
          },
          {
            "id": "qwen3-vl:235b-cloud",
            "name": "qwen3-vl:235b-cloud"
          },
          {
            "id": "qwen3.5:397b-cloud",
            "name": "qwen3.5:397b-cloud"
          },
          {
            "id": "minimax-m2.7:cloud",
            "name": "minimax-m2.7:cloud"
          },
          {
            "id": "qwen3-coder-next:cloud",
            "name": "qwen3-coder-next:cloud"
          }
        ]
      }
    }
  },
  "tools": {
    "profile": "coding",
    "sessions": {
      "visibility": "all"
    },
    "agentToAgent": {
      "enabled": true,
      "allow": ["ceo", "po", "arquiteto", "dev_backend", "dev_frontend", "dev_mobile", "qa_engineer", "devops_sre", "security_engineer", "ux_designer", "dba_data_engineer", "memory_curator"]
    }
  },
  "session": {
    "dmScope": "per-channel-peer",
    "maintenance": {
      "mode": "enforce",
      "pruneAfter": "365d",
      "maxEntries": 2000,
      "rotateBytes": "50mb",
      "maxDiskBytes": "3gb",
      "highWaterBytes": "2.4gb"
    },
    "sendPolicy": {
      "rules": [
        {
          "match": { "channel": "unknown", "chatType": "group" },
          "action": "deny"
        }
      ],
      "default": "allow"
    }
  },
  "skills": {
    "load": {
      "watch": true,
      "watchDebounceMs": 250
    }
  },
  "agents": {
    "defaults": {
      "memorySearch": {
        "enabled": true,
        "provider": "ollama",
        "model": "nomic-embed-text"
      },
      "model": "ollama/nemotron-3-super:cloud",
      "bootstrapMaxChars": 25000,
      "thinkingDefault": "low",
      "typingMode": "instant",
      "typingIntervalSeconds": 4,
      "sandbox": {
        "mode": "all",
        "sessionToolsVisibility": "all"
      },
      "subagents": {
        "runTimeoutSeconds": 1800,
        "maxConcurrent": 6,
        "maxSpawnDepth": 3,
        "maxChildrenPerAgent": 8,
        "archiveAfterMinutes": 120
      },
      "heartbeat": {
        "includeReasoning": true
      }
    },
    "list": [
      {
        "id": "ceo",
        "default": true,
        "name": "CEO",
        "model": "ollama/qwen3-vl:235b-cloud",
        "workspace": "/data/openclaw/workspace-ceo",
        "agentDir": "/data/openclaw/agents/ceo/agent",
        "skills": ["ceo_orchestration", "markdown_converter", "market_research"],
        "tools": {
          "allow": [
            "read",
            "write",
            "exec",
            "process",
            "browser",
            "message",
            "agents_list",
            "sessions_list",
            "sessions_history",
            "sessions_send",
            "sessions_spawn",
            "session_status",
            "group:plugins"
          ],
          "exec": {
            "host": "gateway",
            "security": "allowlist",
            "ask": "on-miss",
            "strictInlineEval": true
          }
        },
        "subagents": {
          "allowAgents": ["po", "arquiteto", "dev_backend", "dev_frontend", "dev_mobile", "qa_engineer", "devops_sre", "security_engineer", "ux_designer", "dba_data_engineer"]
        }
      },
      {
        "id": "po",
        "name": "PO",
        "model": "ollama/minimax-m2.7:cloud",
        "workspace": "/data/openclaw/workspace-po",
        "agentDir": "/data/openclaw/agents/po/agent",
        "skills": ["po_product_delivery", "prompt_engineering_expert", "clawddocs"],
        "tools": {
          "allow": [
            "read",
            "write",
            "exec",
            "process",
            "browser",
            "message",
            "agents_list",
            "sessions_list",
            "sessions_history",
            "sessions_send",
            "sessions_spawn",
            "session_status",
            "group:plugins"
          ],
          "exec": {
            "host": "gateway",
            "security": "allowlist",
            "ask": "on-miss",
            "strictInlineEval": true
          }
        },
        "subagents": {
          "allowAgents": ["arquiteto", "ux_designer", "dev_backend", "dev_frontend", "dev_mobile", "qa_engineer", "devops_sre", "security_engineer", "dba_data_engineer"]
        }
      },
      {
        "id": "arquiteto",
        "name": "Arquiteto",
        "model": "ollama/minimax-m2.7:cloud",
        "workspace": "/data/openclaw/workspace-arquiteto",
        "agentDir": "/data/openclaw/agents/arquiteto/agent",
        "skills": ["arquiteto_engineering"],
        "tools": {
          "allow": [
            "read",
            "write",
            "exec",
            "process",
            "browser",
            "message",
            "agents_list",
            "sessions_list",
            "sessions_history",
            "sessions_send",
            "sessions_spawn",
            "session_status",
            "group:plugins"
          ],
          "exec": {
            "host": "gateway",
            "security": "allowlist",
            "ask": "on-miss",
            "strictInlineEval": true
          }
        },
        "subagents": {
          "allowAgents": ["dev_backend", "dev_frontend", "dev_mobile", "qa_engineer", "devops_sre", "security_engineer", "dba_data_engineer"]
        }
      },
      {
        "id": "dev_backend",
        "name": "Dev_Backend",
        "model": "ollama/minimax-m2.7:cloud",
        "workspace": "/data/openclaw/workspace-dev_backend",
        "agentDir": "/data/openclaw/agents/dev_backend/agent",
        "skills": ["dev_backend_implementation"],
        "tools": {
          "allow": [
            "read",
            "write",
            "exec",
            "process",
            "browser",
            "message",
            "sessions_list",
            "sessions_history",
            "sessions_send",
            "sessions_spawn",
            "session_status",
            "group:plugins"
          ],
          "exec": {
            "host": "gateway",
            "security": "allowlist",
            "ask": "on-miss",
            "strictInlineEval": true
          }
        },
        "subagents": {
          "allowAgents": ["qa_engineer", "security_engineer"]
        }
      },
      {
        "id": "dev_frontend",
        "name": "Dev_Frontend",
        "model": "ollama/minimax-m2.7:cloud",
        "workspace": "/data/openclaw/workspace-dev_frontend",
        "agentDir": "/data/openclaw/agents/dev_frontend/agent",
        "skills": ["dev_frontend_implementation"],
        "tools": {
          "allow": [
            "read",
            "write",
            "exec",
            "process",
            "browser",
            "message",
            "sessions_list",
            "sessions_history",
            "sessions_send",
            "sessions_spawn",
            "session_status",
            "group:plugins"
          ],
          "exec": {
            "host": "gateway",
            "security": "allowlist",
            "ask": "on-miss",
            "strictInlineEval": true
          }
        },
        "subagents": {
          "allowAgents": ["qa_engineer", "security_engineer"]
        }
      },
      {
        "id": "dev_mobile",
        "name": "Dev_Mobile",
        "model": "ollama/minimax-m2.7:cloud",
        "workspace": "/data/openclaw/workspace-dev_mobile",
        "agentDir": "/data/openclaw/agents/dev_mobile/agent",
        "skills": ["dev_mobile_implementation"],
        "tools": {
          "allow": [
            "read",
            "write",
            "exec",
            "process",
            "browser",
            "message",
            "sessions_list",
            "sessions_history",
            "sessions_send",
            "sessions_spawn",
            "session_status",
            "group:plugins"
          ],
          "exec": {
            "host": "gateway",
            "security": "allowlist",
            "ask": "on-miss",
            "strictInlineEval": true
          }
        },
        "subagents": {
          "allowAgents": ["qa_engineer", "security_engineer"]
        }
      },
      {
        "id": "qa_engineer",
        "name": "QA_Engineer",
        "model": "ollama/minimax-m2.7:cloud",
        "workspace": "/data/openclaw/workspace-qa_engineer",
        "agentDir": "/data/openclaw/agents/qa_engineer/agent",
        "skills": ["qa_engineer_validation", "test-specialist", "qa-bug-investigation", "self-improving"],
        "tools": {
          "allow": [
            "read",
            "write",
            "exec",
            "process",
            "browser",
            "message",
            "sessions_list",
            "sessions_history",
            "sessions_send",
            "sessions_spawn",
            "session_status",
            "group:plugins"
          ],
          "exec": {
            "host": "gateway",
            "security": "allowlist",
            "ask": "on-miss",
            "strictInlineEval": true
          }
        },
        "subagents": {
          "allowAgents": []
        }
      },
      {
        "id": "devops_sre",
        "name": "DevOps_SRE",
        "model": "ollama/minimax-m2.7:cloud",
        "workspace": "/data/openclaw/workspace-devops_sre",
        "agentDir": "/data/openclaw/agents/devops_sre/agent",
        "skills": ["devops_sre_operations", "docker_essentials"],
        "tools": {
          "allow": [
            "read",
            "write",
            "exec",
            "process",
            "browser",
            "message",
            "sessions_list",
            "sessions_history",
            "sessions_send",
            "sessions_spawn",
            "session_status",
            "group:plugins"
          ],
          "exec": {
            "host": "gateway",
            "security": "allowlist",
            "ask": "on-miss",
            "strictInlineEval": true
          }
        },
        "subagents": {
          "allowAgents": []
        }
      },
      {
        "id": "security_engineer",
        "name": "Security_Engineer",
        "model": "ollama/minimax-m2.7:cloud",
        "workspace": "/data/openclaw/workspace-security_engineer",
        "agentDir": "/data/openclaw/agents/security_engineer/agent",
        "skills": ["security_engineer_scan"],
        "tools": {
          "allow": [
            "read",
            "write",
            "exec",
            "process",
            "browser",
            "message",
            "sessions_list",
            "sessions_history",
            "sessions_send",
            "sessions_spawn",
            "session_status",
            "group:plugins"
          ],
          "exec": {
            "host": "gateway",
            "security": "allowlist",
            "ask": "on-miss",
            "strictInlineEval": true
          }
        },
        "subagents": {
          "allowAgents": ["dev_backend", "dev_frontend", "dev_mobile"]
        }
      },
      {
        "id": "ux_designer",
        "name": "UX_Designer",
        "model": "ollama/nminimax-m2.7:cloud",
        "workspace": "/data/openclaw/workspace-ux_designer",
        "agentDir": "/data/openclaw/agents/ux_designer/agent",
        "skills": ["ux_designer_artifacts", "ux_ui_pro_rules"],
        "tools": {
          "allow": [
            "read",
            "write",
            "exec",
            "process",
            "browser",
            "message",
            "sessions_list",
            "sessions_history",
            "sessions_send",
            "sessions_spawn",
            "session_status",
            "group:plugins"
          ],
          "exec": {
            "host": "gateway",
            "security": "allowlist",
            "ask": "on-miss",
            "strictInlineEval": true
          }
        },
        "subagents": {
          "allowAgents": []
        }
      },
      {
        "id": "dba_data_engineer",
        "name": "DBA_DataEngineer",
        "model": "ollama/minimax-m2.7:cloud",
        "workspace": "/data/openclaw/workspace-dba_data_engineer",
        "agentDir": "/data/openclaw/agents/dba_data_engineer/agent",
        "skills": ["dba_data_engineer_schema"],
        "tools": {
          "allow": [
            "read",
            "write",
            "exec",
            "process",
            "browser",
            "message",
            "sessions_list",
            "sessions_history",
            "sessions_send",
            "sessions_spawn",
            "session_status",
            "group:plugins"
          ],
          "exec": {
            "host": "gateway",
            "security": "allowlist",
            "ask": "on-miss",
            "strictInlineEval": true
          }
        },
        "subagents": {
          "allowAgents": ["dev_backend", "devops_sre"]
        }
      },
      {
        "id": "memory_curator",
        "name": "Memory_Curator",
        "model": "ollama/minimax-m2.7:cloud",
        "workspace": "/data/openclaw/workspace-memory_curator",
        "agentDir": "/data/openclaw/agents/memory_curator/agent",
        "skills": ["memory_curator_promotion"],
        "tools": {
          "allow": [
            "read",
            "write",
            "exec",
            "message",
            "agents_list",
            "sessions_list",
            "sessions_history",
            "sessions_send",
            "sessions_spawn",
            "session_status",
            "group:plugins"
          ],
          "exec": {
            "host": "gateway",
            "security": "allowlist",
            "ask": "on-miss",
            "strictInlineEval": true
          }
        },
        "subagents": {
          "allowAgents": []
        }
      }
    ]
  },
  "bindings": [
    {
      "agentId": "ceo",
      "match": {
        "channel": "telegram",
        "accountId": "default"
      }
    }
  ],
  "plugins": {
    "slots": {
      "memory": "memory-core"
    }
  },
  "commands": {
    "native": "auto",
    "nativeSkills": "auto",
    "restart": true,
    "ownerDisplay": "hash"
  },
  "channels": {
    "telegram": {
      "dmPolicy": "allowlist",
      "allowFrom": ["__TELEGRAM_CHAT_ID__"],
      "groupPolicy": "allowlist",
      "groupAllowFrom": ["__TELEGRAM_CHAT_ID__"],
      "streaming": "partial",
      "accounts": {
        "default": {
          "botToken": "__TELEGRAM_BOT_TOKEN_CEO__",
          "dmPolicy": "allowlist",
          "allowFrom": ["__TELEGRAM_CHAT_ID__"],
          "groupPolicy": "allowlist",
          "groupAllowFrom": ["__TELEGRAM_CHAT_ID__"],
          "streaming": "partial"
        }
      }
    }
  }
}
EOF
sed -i "s/__TOKEN__/${OPENCLAW_GATEWAY_TOKEN}/g" "${OPENCLAW_STATE_DIR}/openclaw.json"
sed -i "s/__TELEGRAM_BOT_TOKEN_CEO__/${TELEGRAM_BOT_TOKEN_CEO}/g" "${OPENCLAW_STATE_DIR}/openclaw.json"
sed -i "s/__TELEGRAM_CHAT_ID__/${TELEGRAM_CHAT_ID}/g" "${OPENCLAW_STATE_DIR}/openclaw.json"
sed -i "s#__CONTROL_UI_ALLOWED_ORIGINS__#${_allowed_origins_json}#g" "${OPENCLAW_STATE_DIR}/openclaw.json"
mkdir -p ~/.openclaw
cp "${OPENCLAW_STATE_DIR}/openclaw.json" ~/.openclaw/openclaw.json
fi
# Remover campos depreciados do openclaw.json (roda sempre, inclusive em configs reaproveitados).
if [ -f "${OPENCLAW_STATE_DIR}/openclaw.json" ]; then
  _tmp_openclaw_json="$(mktemp)"
  if jq 'del(.agents.defaults.memorySearch.baseUrl)' \
      "${OPENCLAW_STATE_DIR}/openclaw.json" > "${_tmp_openclaw_json}"; then
    mv "${_tmp_openclaw_json}" "${OPENCLAW_STATE_DIR}/openclaw.json"
    mkdir -p ~/.openclaw
    cp "${OPENCLAW_STATE_DIR}/openclaw.json" ~/.openclaw/openclaw.json
  else
    rm -f "${_tmp_openclaw_json}"
    echo "[bootstrap] falha ao remover campos depreciados do openclaw.json"
  fi
fi

# Hardening minimo: manter autenticacao de dispositivo habilitada no Control UI.
if [ -f "${OPENCLAW_STATE_DIR}/openclaw.json" ]; then
  _tmp_openclaw_json="$(mktemp)"
  if jq --argjson allowedOrigins "${_allowed_origins_json}" '
      .gateway.controlUi.dangerouslyDisableDeviceAuth = false
      | .gateway.controlUi.dangerouslyAllowHostHeaderOriginFallback = false
      | .gateway.controlUi.allowedOrigins = $allowedOrigins
      | .gateway.auth.rateLimit = {
          "maxAttempts": (.gateway.auth.rateLimit.maxAttempts // 10),
          "windowMs": (.gateway.auth.rateLimit.windowMs // 60000),
          "lockoutMs": (.gateway.auth.rateLimit.lockoutMs // 300000)
        }
    ' "${OPENCLAW_STATE_DIR}/openclaw.json" > "${_tmp_openclaw_json}"; then
    mv "${_tmp_openclaw_json}" "${OPENCLAW_STATE_DIR}/openclaw.json"
    mkdir -p ~/.openclaw
    cp "${OPENCLAW_STATE_DIR}/openclaw.json" ~/.openclaw/openclaw.json
  else
    rm -f "${_tmp_openclaw_json}"
    echo "[bootstrap] falha ao aplicar hardening de device auth no openclaw.json"
  fi
fi

# Telegram opcional: remove canal/bindings se token/chat id estiverem invalidos.
if [ -f "${OPENCLAW_STATE_DIR}/openclaw.json" ]; then
  _tmp_openclaw_json="$(mktemp)"
  if [ "${_telegram_enabled}" = "true" ]; then
    if jq '
        .channels.telegram.enabled = true
      ' "${OPENCLAW_STATE_DIR}/openclaw.json" > "${_tmp_openclaw_json}"; then
      mv "${_tmp_openclaw_json}" "${OPENCLAW_STATE_DIR}/openclaw.json"
      mkdir -p ~/.openclaw
      cp "${OPENCLAW_STATE_DIR}/openclaw.json" ~/.openclaw/openclaw.json
    else
      rm -f "${_tmp_openclaw_json}"
      echo "[bootstrap] falha ao habilitar canal Telegram no openclaw.json"
    fi
  else
    if jq '
        del(.channels.telegram)
        | .bindings = ((.bindings // []) | map(select((.match.channel // "") != "telegram")))
      ' "${OPENCLAW_STATE_DIR}/openclaw.json" > "${_tmp_openclaw_json}"; then
      mv "${_tmp_openclaw_json}" "${OPENCLAW_STATE_DIR}/openclaw.json"
      mkdir -p ~/.openclaw
      cp "${OPENCLAW_STATE_DIR}/openclaw.json" ~/.openclaw/openclaw.json
    else
      rm -f "${_tmp_openclaw_json}"
      echo "[bootstrap] falha ao desabilitar canal Telegram no openclaw.json"
    fi
  fi
fi

# Zero Trust baseline: sandbox global, exec allowlist + prompt on miss + deny fallback.
if [ -f "${OPENCLAW_STATE_DIR}/openclaw.json" ]; then
  _tmp_openclaw_json="$(mktemp)"
  if jq --arg sandboxMode "${_sandbox_mode}" --arg sandboxVisibility "${_sandbox_session_tools_visibility}" '
      .agents.defaults.sandbox.mode = $sandboxMode
      | .agents.defaults.sandbox.sessionToolsVisibility = $sandboxVisibility
      | .tools.exec.strictInlineEval = true
      | .agents.list |= map(
          .tools.exec = (
            (.tools.exec // {})
            + {
              "host": "gateway",
              "security": "allowlist",
              "ask": "on-miss",
              "strictInlineEval": true
            }
          )
        )
    ' "${OPENCLAW_STATE_DIR}/openclaw.json" > "${_tmp_openclaw_json}"; then
    mv "${_tmp_openclaw_json}" "${OPENCLAW_STATE_DIR}/openclaw.json"
    mkdir -p ~/.openclaw
    cp "${OPENCLAW_STATE_DIR}/openclaw.json" ~/.openclaw/openclaw.json
  else
    rm -f "${_tmp_openclaw_json}"
    echo "[bootstrap] falha ao aplicar baseline zero-trust de sandbox/exec no openclaw.json"
  fi
fi

# Zero Trust break-glass: bloquear canal alternativo de elevated fora do painel.
if [ -f "${OPENCLAW_STATE_DIR}/openclaw.json" ]; then
  _tmp_openclaw_json="$(mktemp)"
  if jq '
      .tools.elevated = { "enabled": false }
      | (.agents.list[]?.tools.elevated) = { "enabled": false }
    ' "${OPENCLAW_STATE_DIR}/openclaw.json" > "${_tmp_openclaw_json}"; then
    mv "${_tmp_openclaw_json}" "${OPENCLAW_STATE_DIR}/openclaw.json"
    mkdir -p ~/.openclaw
    cp "${OPENCLAW_STATE_DIR}/openclaw.json" ~/.openclaw/openclaw.json
  else
    rm -f "${_tmp_openclaw_json}"
    echo "[bootstrap] falha ao desabilitar elevated fora do painel"
  fi
fi

# Otimizacao: Configuracoes de sessao para agentes de desenvolvimento (ambiente dev intenso).
# Reduz acumulacao de sessoes de cron jobs que rodam a cada 30 minutos.
if [ -f "${OPENCLAW_STATE_DIR}/openclaw.json" ]; then
  _tmp_openclaw_json="$(mktemp)"
  if jq '
      .session.maintenance = {
        "mode": "enforce",
        "pruneAfter": "7d",
        "maxEntries": 200,
        "rotateBytes": "10mb",
        "maxDiskBytes": "1gb",
        "highWaterBytes": "800mb",
        "resetArchiveRetention": "3d"
      }
      | .cron.sessionRetention = "2h"
      | .session.dmScope = "main"
    ' "${OPENCLAW_STATE_DIR}/openclaw.json" > "${_tmp_openclaw_json}"; then
    mv "${_tmp_openclaw_json}" "${OPENCLAW_STATE_DIR}/openclaw.json"
    mkdir -p ~/.openclaw
    cp "${OPENCLAW_STATE_DIR}/openclaw.json" ~/.openclaw/openclaw.json
    echo "[bootstrap] openclaw.json otimizado para agentes de desenvolvimento"
  else
    rm -f "${_tmp_openclaw_json}"
    echo "[bootstrap] falha ao otimizar openclaw.json para dev"
  fi
fi

# Garantir skill self-improving para todos os agentes sem remover skills existentes.
# Requisito: adicao idempotente (nao duplica entradas).
if [ -f "${OPENCLAW_STATE_DIR}/openclaw.json" ]; then
  _tmp_openclaw_json="$(mktemp)"
  if jq '
      .agents.list |= map(
        .skills = (
          (.skills // [])
          | if index("self-improving") then . else . + ["self-improving"] end
        )
      )
    ' "${OPENCLAW_STATE_DIR}/openclaw.json" > "${_tmp_openclaw_json}"; then
    mv "${_tmp_openclaw_json}" "${OPENCLAW_STATE_DIR}/openclaw.json"
    mkdir -p ~/.openclaw
    cp "${OPENCLAW_STATE_DIR}/openclaw.json" ~/.openclaw/openclaw.json
    echo "[bootstrap] self-improving garantido em agents.list[].skills"
  else
    rm -f "${_tmp_openclaw_json}"
    echo "[bootstrap] falha ao aplicar patch da skill self-improving em openclaw.json"
  fi
fi

# Garantir skills compartilhadas para todos os agentes sem remover skills existentes.
# Requisito: adicao idempotente (nao duplica entradas).
if [ -f "${OPENCLAW_STATE_DIR}/openclaw.json" ]; then
  _tmp_openclaw_json="$(mktemp)"
  if jq '
      .agents.list |= map(
        .skills = (
          (.skills // [])
          | if index("moltguard") then . else . + ["moltguard"] end
          | if index("memory_setup") then . else . + ["memory_setup"] end
        )
      )
    ' "${OPENCLAW_STATE_DIR}/openclaw.json" > "${_tmp_openclaw_json}"; then
    mv "${_tmp_openclaw_json}" "${OPENCLAW_STATE_DIR}/openclaw.json"
    mkdir -p ~/.openclaw
    cp "${OPENCLAW_STATE_DIR}/openclaw.json" ~/.openclaw/openclaw.json
    echo "[bootstrap] skills compartilhadas (moltguard, memory_setup) garantidas em agents.list[].skills"
  else
    rm -f "${_tmp_openclaw_json}"
    echo "[bootstrap] falha ao aplicar patch das skills compartilhadas em openclaw.json"
  fi
fi

# Cada agente usa seu proprio workspace com identidade isolada (workspace definido por agente no JSON).

# Exec approvals zero trust:
# - allowlist explicita
# - ask=on-miss
# - sem askFallback (schema atual do OpenClaw nao aceita essa chave)
# - autoAllowSkills=false para evitar trust implicito
EXEC_APPROVALS_FILE=~/.openclaw/exec-approvals.json
cat > "${EXEC_APPROVALS_FILE}" << 'EOFAPPROVALS'
{
  "version": 1,
  "defaults": {
    "security": "allowlist",
    "ask": "on-miss",
    "autoAllowSkills": false,
    "allowlist": []
  },
  "agents": {
    "ceo": {
      "security": "allowlist",
      "ask": "on-miss",
      "autoAllowSkills": false,
      "allowlist": [
        { "pattern": "/usr/bin/cat" },
        { "pattern": "/usr/bin/ls" },
        { "pattern": "/usr/bin/grep" },
        { "pattern": "/usr/bin/find" },
        { "pattern": "/usr/bin/sed" },
        { "pattern": "/usr/bin/awk" },
        { "pattern": "/usr/bin/jq" },
        { "pattern": "/usr/bin/head" },
        { "pattern": "/usr/bin/tail" },
        { "pattern": "/usr/bin/wc" },
        { "pattern": "/usr/bin/sort" },
        { "pattern": "/usr/bin/uniq" },
        { "pattern": "/usr/bin/cut" },
        { "pattern": "/usr/bin/xargs" },
        { "pattern": "/usr/bin/stat" },
        { "pattern": "/usr/bin/date" },
        { "pattern": "/usr/bin/env" },
        { "pattern": "/usr/bin/printenv" },
        { "pattern": "/usr/bin/tee" },
        { "pattern": "/usr/bin/tr" }
      ]
    },
    "po": {
      "security": "allowlist",
      "ask": "on-miss",
      "autoAllowSkills": false,
      "allowlist": [
        { "pattern": "/usr/bin/cat" },
        { "pattern": "/usr/bin/ls" },
        { "pattern": "/usr/bin/grep" },
        { "pattern": "/usr/bin/find" },
        { "pattern": "/usr/bin/sed" },
        { "pattern": "/usr/bin/awk" },
        { "pattern": "/usr/bin/jq" },
        { "pattern": "/usr/bin/head" },
        { "pattern": "/usr/bin/tail" },
        { "pattern": "/usr/bin/wc" },
        { "pattern": "/usr/bin/sort" },
        { "pattern": "/usr/bin/uniq" },
        { "pattern": "/usr/bin/cut" },
        { "pattern": "/usr/bin/xargs" },
        { "pattern": "/usr/bin/stat" },
        { "pattern": "/usr/bin/date" },
        { "pattern": "/usr/bin/env" },
        { "pattern": "/usr/bin/printenv" },
        { "pattern": "/usr/bin/tee" },
        { "pattern": "/usr/bin/tr" }
      ]
    },
    "arquiteto": {
      "security": "allowlist",
      "ask": "on-miss",
      "autoAllowSkills": false,
      "allowlist": [
        { "pattern": "/usr/bin/cat" },
        { "pattern": "/usr/bin/ls" },
        { "pattern": "/usr/bin/grep" },
        { "pattern": "/usr/bin/find" },
        { "pattern": "/usr/bin/sed" },
        { "pattern": "/usr/bin/awk" },
        { "pattern": "/usr/bin/jq" },
        { "pattern": "/usr/bin/head" },
        { "pattern": "/usr/bin/tail" },
        { "pattern": "/usr/bin/wc" },
        { "pattern": "/usr/bin/sort" },
        { "pattern": "/usr/bin/uniq" },
        { "pattern": "/usr/bin/cut" },
        { "pattern": "/usr/bin/xargs" },
        { "pattern": "/usr/bin/stat" },
        { "pattern": "/usr/bin/date" },
        { "pattern": "/usr/bin/env" },
        { "pattern": "/usr/bin/printenv" },
        { "pattern": "/usr/bin/tee" },
        { "pattern": "/usr/bin/tr" },
        { "pattern": "/usr/bin/git" },
        { "pattern": "/usr/bin/curl" }
      ]
    },
    "dev_backend": {
      "security": "allowlist",
      "ask": "on-miss",
      "autoAllowSkills": false,
      "allowlist": [
        { "pattern": "/usr/bin/cat" },
        { "pattern": "/usr/bin/ls" },
        { "pattern": "/usr/bin/grep" },
        { "pattern": "/usr/bin/find" },
        { "pattern": "/usr/bin/sed" },
        { "pattern": "/usr/bin/awk" },
        { "pattern": "/usr/bin/jq" },
        { "pattern": "/usr/bin/head" },
        { "pattern": "/usr/bin/tail" },
        { "pattern": "/usr/bin/wc" },
        { "pattern": "/usr/bin/sort" },
        { "pattern": "/usr/bin/uniq" },
        { "pattern": "/usr/bin/cut" },
        { "pattern": "/usr/bin/xargs" },
        { "pattern": "/usr/bin/stat" },
        { "pattern": "/usr/bin/date" },
        { "pattern": "/usr/bin/env" },
        { "pattern": "/usr/bin/printenv" },
        { "pattern": "/usr/bin/tee" },
        { "pattern": "/usr/bin/tr" },
        { "pattern": "/usr/bin/git" },
        { "pattern": "/usr/bin/curl" }
      ]
    },
    "dev_frontend": {
      "security": "allowlist",
      "ask": "on-miss",
      "autoAllowSkills": false,
      "allowlist": [
        { "pattern": "/usr/bin/cat" },
        { "pattern": "/usr/bin/ls" },
        { "pattern": "/usr/bin/grep" },
        { "pattern": "/usr/bin/find" },
        { "pattern": "/usr/bin/sed" },
        { "pattern": "/usr/bin/awk" },
        { "pattern": "/usr/bin/jq" },
        { "pattern": "/usr/bin/head" },
        { "pattern": "/usr/bin/tail" },
        { "pattern": "/usr/bin/wc" },
        { "pattern": "/usr/bin/sort" },
        { "pattern": "/usr/bin/uniq" },
        { "pattern": "/usr/bin/cut" },
        { "pattern": "/usr/bin/xargs" },
        { "pattern": "/usr/bin/stat" },
        { "pattern": "/usr/bin/date" },
        { "pattern": "/usr/bin/env" },
        { "pattern": "/usr/bin/printenv" },
        { "pattern": "/usr/bin/tee" },
        { "pattern": "/usr/bin/tr" },
        { "pattern": "/usr/bin/git" },
        { "pattern": "/usr/bin/curl" }
      ]
    },
    "dev_mobile": {
      "security": "allowlist",
      "ask": "on-miss",
      "autoAllowSkills": false,
      "allowlist": [
        { "pattern": "/usr/bin/cat" },
        { "pattern": "/usr/bin/ls" },
        { "pattern": "/usr/bin/grep" },
        { "pattern": "/usr/bin/find" },
        { "pattern": "/usr/bin/sed" },
        { "pattern": "/usr/bin/awk" },
        { "pattern": "/usr/bin/jq" },
        { "pattern": "/usr/bin/head" },
        { "pattern": "/usr/bin/tail" },
        { "pattern": "/usr/bin/wc" },
        { "pattern": "/usr/bin/sort" },
        { "pattern": "/usr/bin/uniq" },
        { "pattern": "/usr/bin/cut" },
        { "pattern": "/usr/bin/xargs" },
        { "pattern": "/usr/bin/stat" },
        { "pattern": "/usr/bin/date" },
        { "pattern": "/usr/bin/env" },
        { "pattern": "/usr/bin/printenv" },
        { "pattern": "/usr/bin/tee" },
        { "pattern": "/usr/bin/tr" },
        { "pattern": "/usr/bin/git" },
        { "pattern": "/usr/bin/curl" }
      ]
    },
    "qa_engineer": {
      "security": "allowlist",
      "ask": "on-miss",
      "autoAllowSkills": false,
      "allowlist": [
        { "pattern": "/usr/bin/cat" },
        { "pattern": "/usr/bin/ls" },
        { "pattern": "/usr/bin/grep" },
        { "pattern": "/usr/bin/find" },
        { "pattern": "/usr/bin/sed" },
        { "pattern": "/usr/bin/awk" },
        { "pattern": "/usr/bin/jq" },
        { "pattern": "/usr/bin/head" },
        { "pattern": "/usr/bin/tail" },
        { "pattern": "/usr/bin/wc" },
        { "pattern": "/usr/bin/sort" },
        { "pattern": "/usr/bin/uniq" },
        { "pattern": "/usr/bin/cut" },
        { "pattern": "/usr/bin/xargs" },
        { "pattern": "/usr/bin/stat" },
        { "pattern": "/usr/bin/date" },
        { "pattern": "/usr/bin/env" },
        { "pattern": "/usr/bin/printenv" },
        { "pattern": "/usr/bin/tee" },
        { "pattern": "/usr/bin/tr" },
        { "pattern": "/usr/bin/git" },
        { "pattern": "/usr/bin/curl" }
      ]
    },
    "security_engineer": {
      "security": "allowlist",
      "ask": "on-miss",
      "autoAllowSkills": false,
      "allowlist": [
        { "pattern": "/usr/bin/cat" },
        { "pattern": "/usr/bin/ls" },
        { "pattern": "/usr/bin/grep" },
        { "pattern": "/usr/bin/find" },
        { "pattern": "/usr/bin/sed" },
        { "pattern": "/usr/bin/awk" },
        { "pattern": "/usr/bin/jq" },
        { "pattern": "/usr/bin/head" },
        { "pattern": "/usr/bin/tail" },
        { "pattern": "/usr/bin/wc" },
        { "pattern": "/usr/bin/sort" },
        { "pattern": "/usr/bin/uniq" },
        { "pattern": "/usr/bin/cut" },
        { "pattern": "/usr/bin/xargs" },
        { "pattern": "/usr/bin/stat" },
        { "pattern": "/usr/bin/date" },
        { "pattern": "/usr/bin/env" },
        { "pattern": "/usr/bin/printenv" },
        { "pattern": "/usr/bin/tee" },
        { "pattern": "/usr/bin/tr" },
        { "pattern": "/usr/bin/git" },
        { "pattern": "/usr/bin/curl" },
        { "pattern": "/usr/bin/openssl" },
        { "pattern": "/usr/bin/sha256sum" }
      ]
    },
    "ux_designer": {
      "security": "allowlist",
      "ask": "on-miss",
      "autoAllowSkills": false,
      "allowlist": [
        { "pattern": "/usr/bin/cat" },
        { "pattern": "/usr/bin/ls" },
        { "pattern": "/usr/bin/grep" },
        { "pattern": "/usr/bin/find" },
        { "pattern": "/usr/bin/sed" },
        { "pattern": "/usr/bin/awk" },
        { "pattern": "/usr/bin/jq" },
        { "pattern": "/usr/bin/head" },
        { "pattern": "/usr/bin/tail" },
        { "pattern": "/usr/bin/wc" },
        { "pattern": "/usr/bin/sort" },
        { "pattern": "/usr/bin/uniq" },
        { "pattern": "/usr/bin/cut" },
        { "pattern": "/usr/bin/xargs" },
        { "pattern": "/usr/bin/stat" },
        { "pattern": "/usr/bin/date" },
        { "pattern": "/usr/bin/env" },
        { "pattern": "/usr/bin/printenv" },
        { "pattern": "/usr/bin/tee" },
        { "pattern": "/usr/bin/tr" },
        { "pattern": "/usr/bin/git" }
      ]
    },
    "devops_sre": {
      "security": "allowlist",
      "ask": "on-miss",
      "autoAllowSkills": false,
      "allowlist": [
        { "pattern": "/usr/bin/cat" },
        { "pattern": "/usr/bin/ls" },
        { "pattern": "/usr/bin/grep" },
        { "pattern": "/usr/bin/find" },
        { "pattern": "/usr/bin/sed" },
        { "pattern": "/usr/bin/awk" },
        { "pattern": "/usr/bin/jq" },
        { "pattern": "/usr/bin/head" },
        { "pattern": "/usr/bin/tail" },
        { "pattern": "/usr/bin/wc" },
        { "pattern": "/usr/bin/sort" },
        { "pattern": "/usr/bin/uniq" },
        { "pattern": "/usr/bin/cut" },
        { "pattern": "/usr/bin/xargs" },
        { "pattern": "/usr/bin/stat" },
        { "pattern": "/usr/bin/date" },
        { "pattern": "/usr/bin/env" },
        { "pattern": "/usr/bin/printenv" },
        { "pattern": "/usr/bin/tee" },
        { "pattern": "/usr/bin/tr" },
        { "pattern": "/usr/bin/git" },
        { "pattern": "/usr/bin/curl" },
        { "pattern": "/usr/bin/docker" }
      ]
    },
    "dba_data_engineer": {
      "security": "allowlist",
      "ask": "on-miss",
      "autoAllowSkills": false,
      "allowlist": [
        { "pattern": "/usr/bin/cat" },
        { "pattern": "/usr/bin/ls" },
        { "pattern": "/usr/bin/grep" },
        { "pattern": "/usr/bin/find" },
        { "pattern": "/usr/bin/sed" },
        { "pattern": "/usr/bin/awk" },
        { "pattern": "/usr/bin/jq" },
        { "pattern": "/usr/bin/head" },
        { "pattern": "/usr/bin/tail" },
        { "pattern": "/usr/bin/wc" },
        { "pattern": "/usr/bin/sort" },
        { "pattern": "/usr/bin/uniq" },
        { "pattern": "/usr/bin/cut" },
        { "pattern": "/usr/bin/xargs" },
        { "pattern": "/usr/bin/stat" },
        { "pattern": "/usr/bin/date" },
        { "pattern": "/usr/bin/env" },
        { "pattern": "/usr/bin/printenv" },
        { "pattern": "/usr/bin/tee" },
        { "pattern": "/usr/bin/tr" },
        { "pattern": "/usr/bin/git" }
      ]
    },
    "memory_curator": {
      "security": "allowlist",
      "ask": "on-miss",
      "autoAllowSkills": false,
      "allowlist": [
        { "pattern": "/usr/bin/cat" },
        { "pattern": "/usr/bin/ls" },
        { "pattern": "/usr/bin/grep" },
        { "pattern": "/usr/bin/find" },
        { "pattern": "/usr/bin/sed" },
        { "pattern": "/usr/bin/awk" },
        { "pattern": "/usr/bin/jq" },
        { "pattern": "/usr/bin/head" },
        { "pattern": "/usr/bin/tail" },
        { "pattern": "/usr/bin/wc" },
        { "pattern": "/usr/bin/sort" },
        { "pattern": "/usr/bin/uniq" },
        { "pattern": "/usr/bin/cut" },
        { "pattern": "/usr/bin/xargs" },
        { "pattern": "/usr/bin/stat" },
        { "pattern": "/usr/bin/date" },
        { "pattern": "/usr/bin/env" },
        { "pattern": "/usr/bin/printenv" },
        { "pattern": "/usr/bin/tee" },
        { "pattern": "/usr/bin/tr" }
      ]
    }
  }
}
EOFAPPROVALS
echo "[bootstrap] zero-trust exec approvals aplicadas (allowlist + ask=on-miss + autoAllowSkills=false)"
# Repair agent main sessions when the persisted transcript is missing, invalid,
# or contains no assistant text messages that the chat UI can render.
repair_main_session() {
  agent_id="$1"
  workspace_dir="$2"
  seed_text="$3"
  sess_dir="${OPENCLAW_STATE_DIR}/agents/${agent_id}/sessions"
  sess_key="agent:${agent_id}:main"
  mkdir -p "${sess_dir}"
  if [ ! -f "${sess_dir}/sessions.json" ]; then
    ts="$(date -u +%Y%m%dT%H%M%SZ)"
    new_id="$(cat /proc/sys/kernel/random/uuid)"
    now_ms="$(($(date -u +%s)*1000))"
    cat > "${sess_dir}/${new_id}.jsonl" <<SEEDEOF
{"type":"session","version":3,"id":"${new_id}","timestamp":"$(date -u +%Y-%m-%dT%H:%M:%S.000Z)","cwd":"${workspace_dir}"}
{"type":"message","id":"seed-${agent_id}-main","parentId":null,"timestamp":"$(date -u +%Y-%m-%dT%H:%M:%S.000Z)","message":{"role":"assistant","content":[{"type":"text","text":"${seed_text}"}],"stopReason":"stop","provider":"system","model":"seed"}}
SEEDEOF
    printf '{"agent:%s:main":{"sessionId":"%s","updatedAt":%s,"chatType":"direct","deliveryContext":{"channel":"webchat"},"lastChannel":"webchat","origin":{"provider":"webchat","surface":"webchat","chatType":"direct"},"sessionFile":"%s","abortedLastRun":false,"compactionCount":0}}\n' \
      "${agent_id}" "${new_id}" "${now_ms}" "${sess_dir}/${new_id}.jsonl" \
      > "${sess_dir}/sessions.json"
    return 0
  fi
  main_file="$(jq -r --arg key "${sess_key}" '.[$key].sessionFile // empty' "${sess_dir}/sessions.json" 2>/dev/null || true)"
  main_ok=0
  if [ -n "${main_file}" ] && [ -f "${main_file}" ]; then
    if jq -c . "${main_file}" >/dev/null 2>&1; then
      if jq -e 'select(.type=="message" and .message.role=="assistant") | .message.content[]? | select(.type=="text" and ((.text // "") | length > 0))' "${main_file}" >/dev/null 2>&1; then
        main_ok=1
      fi
    fi
  fi
  if [ "${main_ok}" -eq 1 ]; then
    return 0
  fi
  ts="$(date -u +%Y%m%dT%H%M%SZ)"
  new_id="$(cat /proc/sys/kernel/random/uuid)"
  now_ms="$(($(date -u +%s)*1000))"
  cp "${sess_dir}/sessions.json" "${sess_dir}/sessions.json.bak.${ts}"
  if [ -n "${main_file}" ] && [ -f "${main_file}" ]; then
    cp "${main_file}" "${main_file}.bak.${ts}"
  fi
  cat > "${sess_dir}/${new_id}.jsonl" <<EOF
{"type":"session","version":3,"id":"${new_id}","timestamp":"$(date -u +%Y-%m-%dT%H:%M:%S.000Z)","cwd":"${workspace_dir}"}
{"type":"message","id":"seed-${agent_id}-main","parentId":null,"timestamp":"$(date -u +%Y-%m-%dT%H:%M:%S.000Z)","message":{"role":"assistant","content":[{"type":"text","text":"${seed_text}"}],"stopReason":"stop","provider":"system","model":"seed"}}
EOF
  jq --arg key "${sess_key}" \
     --arg newId "${new_id}" \
     --arg newFile "${sess_dir}/${new_id}.jsonl" \
     --argjson now "${now_ms}" \
     '.[$key].sessionId = $newId |
      .[$key].updatedAt = $now |
      .[$key].chatType = "direct" |
      .[$key].deliveryContext = {"channel":"webchat"} |
      .[$key].lastChannel = "webchat" |
      .[$key].origin = {"provider":"webchat","surface":"webchat","chatType":"direct"} |
      .[$key].sessionFile = $newFile |
      .[$key].abortedLastRun = false |
      .[$key].compactionCount = 0' \
     "${sess_dir}/sessions.json" > "${sess_dir}/sessions.json.tmp"
  mv "${sess_dir}/sessions.json.tmp" "${sess_dir}/sessions.json"
}
# Configurar provider LLM dinamico via PROVEDOR_LLM.
# Regras:
# - PROVEDOR_LLM=openrouter|open-router|or -> usa OpenRouter
# - PROVEDOR_LLM=ollama -> usa Ollama
# - PROVEDOR_LLM vazio/auto/invalido -> auto-detecta (OPENROUTER_API_KEY => openrouter, senao ollama)
_provedor_raw="${PROVEDOR_LLM:-}"
_provedor="$(printf '%s' "${_provedor_raw}" | tr '[:upper:]' '[:lower:]' | tr -d '[:space:]')"
if [ -z "${_provedor}" ] || [ "${_provedor}" = "auto" ]; then
  if [ -n "${OPENROUTER_API_KEY:-}" ]; then
    _provedor="openrouter"
  else
    _provedor="ollama"
  fi
fi
case "${_provedor}" in
  openrouter|open-router|or)
    _provedor="openrouter"
    ;;
  ollama)
    _provedor="ollama"
    ;;
  *)
    echo "[bootstrap] AVISO: PROVEDOR_LLM invalido (${_provedor_raw}), aplicando fallback automatico"
    if [ -n "${OPENROUTER_API_KEY:-}" ]; then
      _provedor="openrouter"
    else
      _provedor="ollama"
    fi
    ;;
esac
echo "[bootstrap] LLM provider selecionado=${_provedor}"

if [ "${_provedor}" = "openrouter" ]; then
  if [ -z "${OPENROUTER_API_KEY:-}" ]; then
    echo "[bootstrap] AVISO: provider=openrouter mas OPENROUTER_API_KEY nao definida; mantendo modelos atuais"
  else
    _tmp_or="$(mktemp)"
    _or_model="${OPENROUTER_MODEL:-stepfun/step-3.5-flash:free}"
    _or_base_url="${OPENROUTER_BASE_URL:-https://openrouter.ai/api/v1}"
    case "${_or_model}" in
      openrouter/*) _or_model_full="${_or_model}" ;;
      *) _or_model_full="openrouter/${_or_model}" ;;
    esac
    _or_model_id="${_or_model_full#openrouter/}"
    if jq \
      --arg apiKey "${OPENROUTER_API_KEY}" \
      --arg baseUrl "${_or_base_url}" \
      --arg model "${_or_model_full}" \
      --arg modelId "${_or_model_id}" \
      '
        .models.providers.openrouter = {
          "apiKey": $apiKey,
          "baseUrl": $baseUrl,
          "models": [
            { "id": $modelId, "name": $modelId }
          ]
        }
        | .agents.defaults.model = $model
        | (.agents.list[].model) = $model
      ' "${OPENCLAW_STATE_DIR}/openclaw.json" > "${_tmp_or}"; then
      mv "${_tmp_or}" "${OPENCLAW_STATE_DIR}/openclaw.json"
      mkdir -p ~/.openclaw
      cp "${OPENCLAW_STATE_DIR}/openclaw.json" ~/.openclaw/openclaw.json
      echo "[bootstrap] provider=openrouter aplicado para todos os agentes (model=${_or_model_full})"
    else
      rm -f "${_tmp_or}"
      echo "[bootstrap] ERRO ao aplicar patch openrouter no openclaw.json"
    fi
  fi
fi

# Compat: schema atual exige models.providers.openrouter.baseUrl.
# Se existir provider openrouter legado sem baseUrl, completa com default.
if [ -f "${OPENCLAW_STATE_DIR}/openclaw.json" ]; then
  _tmp_or_base="$(mktemp)"
  _or_base_url="${OPENROUTER_BASE_URL:-https://openrouter.ai/api/v1}"
  if jq \
    --arg baseUrl "${_or_base_url}" \
    '
      if .models.providers.openrouter? then
        .models.providers.openrouter.baseUrl = (.models.providers.openrouter.baseUrl // $baseUrl)
      else
        .
      end
    ' "${OPENCLAW_STATE_DIR}/openclaw.json" > "${_tmp_or_base}"; then
    mv "${_tmp_or_base}" "${OPENCLAW_STATE_DIR}/openclaw.json"
    mkdir -p ~/.openclaw
    cp "${OPENCLAW_STATE_DIR}/openclaw.json" ~/.openclaw/openclaw.json
  else
    rm -f "${_tmp_or_base}"
    echo "[bootstrap] falha ao aplicar compat de openrouter.baseUrl"
  fi
fi

repair_main_session "ceo"              "${OPENCLAW_STATE_DIR}/workspace-ceo"              "CEO pronto. Delegacao imediata na mesma sessao — sem fila com prazos em horas entre agentes. Pode acionar por aqui."
repair_main_session "po"               "${OPENCLAW_STATE_DIR}/workspace-po"               "PO pronto. Pode me acionar para planejamento, backlog, prioridades e coordenacao com Arquiteto."
repair_main_session "arquiteto"        "${OPENCLAW_STATE_DIR}/workspace-arquiteto"        "Arquiteto pronto. Pode me acionar para desenho tecnico, tasks e trade-offs de arquitetura."
repair_main_session "dev_backend"      "${OPENCLAW_STATE_DIR}/workspace-dev_backend"      "Dev_Backend pronto. Pode me acionar para implementacao de tasks, testes e atualizacao de status."
repair_main_session "dev_frontend"     "${OPENCLAW_STATE_DIR}/workspace-dev_frontend"     "Dev_Frontend pronto. Pode me acionar para implementacao de tasks frontend, testes e atualizacao de status."
repair_main_session "dev_mobile"       "${OPENCLAW_STATE_DIR}/workspace-dev_mobile"       "Dev_Mobile pronto. Pode me acionar para implementacao de tasks mobile, testes e atualizacao de status."
repair_main_session "qa_engineer"      "${OPENCLAW_STATE_DIR}/workspace-qa_engineer"      "QA_Engineer pronto. Pode me acionar para validacao, testes BDD e relatorios de qualidade."
repair_main_session "devops_sre"       "${OPENCLAW_STATE_DIR}/workspace-devops_sre"       "DevOps_SRE pronto. Pode me acionar para pipelines, infra, SLOs e escalacao de incidentes."
repair_main_session "security_engineer" "${OPENCLAW_STATE_DIR}/workspace-security_engineer" "Security_Engineer pronto. Pode me acionar para scans de seguranca, CVEs e escalacao de vulnerabilidades."
repair_main_session "ux_designer"      "${OPENCLAW_STATE_DIR}/workspace-ux_designer"      "UX_Designer pronto. Pode me acionar para wireframes, fluxos de usuario e design tokens."
repair_main_session "dba_data_engineer" "${OPENCLAW_STATE_DIR}/workspace-dba_data_engineer" "DBA_DataEngineer pronto. Pode me acionar para schemas, migrations, queries e compliance LGPD."
repair_main_session "memory_curator"   "${OPENCLAW_STATE_DIR}/workspace-memory_curator"   "Memory_Curator pronto. Executo curadoria diaria de padroes cross-agent e promocao para SHARED_MEMORY."


