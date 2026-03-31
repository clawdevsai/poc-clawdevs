---
name: openclaw-expert-bundle
version: 1.0.0
description: "Complete OpenClaw expertise bundle. Provides 4 integrated skills covering agent loop, plugin development, multi-agent patterns, and automation/troubleshooting. Use whenever working with OpenClaw - automatically routes to the right specialized skill based on user context."
keywords: ["openclaw", "agents", "plugins", "automation", "multi-agent", "architecture"]
license: MIT
---

# OpenClaw Expert Bundle

Complete expertise system for OpenClaw development with 4 integrated skills.

## 📚 Included Skills

1. **openclaw-expert** — Core concepts, agent loop, context engine, memory management
2. **openclaw-plugin-builder** — Building plugins step by step with examples
3. **openclaw-agent-patterns** — Advanced patterns (supervisor, pipeline, router, critic loop)
4. **openclaw-automation-troubleshooting** — Hooks, webhooks, cron, debugging

## 🚀 Quick Start

```bash
# Install the bundle
openclaw plugin install ./openclaw-expert-bundle

# Use in your agent
{
  "plugins": ["openclaw-expert-bundle"],
  "config": {
    "openclaw-expert-bundle": {
      "autoRoute": true,
      "enableWebSearch": true
    }
  }
}
```

## 💡 How It Works

The bundle intelligently routes queries to the appropriate skill:

- **Agent loop, context, memory?** → `openclaw-expert`
- **Creating a plugin?** → `openclaw-plugin-builder`
- **Multi-agent, supervisor pattern?** → `openclaw-agent-patterns`
- **Hooks, webhooks, debugging?** → `openclaw-automation-troubleshooting`

## 📖 What You Can Do

- Learn OpenClaw concepts with deep explanations
- Get step-by-step guides for building plugins
- Understand multi-agent architectures
- Set up automations (hooks, webhooks, cron)
- Troubleshoot issues with structured checklists
- Get pseudocode examples in Python, TypeScript, Go
- Receive project structure recommendations
- Access web search for latest OpenClaw docs

## 🔧 Configuration

```json
{
  "openclaw-expert-bundle": {
    "autoRoute": true,
    "enableWebSearch": true,
    "pseudocodeLanguages": ["python", "typescript", "go"],
    "detailLevel": "professional"
  }
}
```

## 📚 Examples

**Learn the agent loop:**
```
User: "Explain how the agent loop works"
→ Routes to openclaw-expert
→ Gets 13-step explanation with pseudocode
```

**Build a plugin:**
```
User: "Create a plugin that integrates with my API"
→ Routes to openclaw-plugin-builder
→ Gets folder structure, manifest, hooks, testing strategy
```

**Design multi-agent system:**
```
User: "I need a supervisor agent with specialists"
→ Routes to openclaw-agent-patterns
→ Gets delegate architecture pattern with error handling
```

**Debug webhook:**
```
User: "My webhook isn't firing"
→ Routes to openclaw-automation-troubleshooting
→ Gets structured troubleshooting checklist
```

## 📝 Skills are in Portuguese (PT-BR)

All skills default to Portuguese (Brazilian). Configuration to switch languages coming in v1.1.

## 🤝 Support

For OpenClaw documentation: https://docs.openclaw.ai
For issues: Report in your project

---

Enjoy building with OpenClaw! 🚀
