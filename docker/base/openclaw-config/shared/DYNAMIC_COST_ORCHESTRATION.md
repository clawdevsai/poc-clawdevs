<!-- 
  Copyright (c) 2026 Diego Silva Morais <lukewaresoftwarehouse@gmail.com>

  Permission is hereby granted, free of charge, to any person obtaining a copy
  of this software and associated documentation files (the "Software"), to deal
  in the Software without restriction, including without limitation the rights
  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
  copies of the Software, and to permit persons to whom the Software is
  furnished to do so, subject to the following conditions:

  The above copyright notice and this permission notice shall be included in all
  copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
  SOFTWARE.
 -->

# Dynamic Cost Orchestration

> Guidelines for selecting the optimal LLM model based on task complexity to maximize performance while minimizing cost.

## Model Tiers

### Tier 1: Local Models (Ollama) - Low Cost
**Use for:** Simple, repetitive tasks
- Code generation from templates
- Documentation writing
- Simple refactoring (rename, formatting)
- File operations (read, write, search)
- Regex pattern generation

**Available Models:**
- llama3.2:1b - Fastest, basic tasks
- llama3.2:3b - Balanced speed/quality

### Tier 2: Remote Models (OpenRouter) - Medium Cost
**Use for:** Complex tasks requiring better reasoning
- Architecture decisions
- Complex debugging
- Security reviews
- API design
- Multi-file refactoring
- Performance optimization

**Available Models:**
- anthropic/claude-3.5-sonnet - Balanced reasoning
- openai/gpt-4o - Strong general purpose
- google/gemini-pro - Fast reasoning

### Tier 3: Premium Models (OpenRouter) - High Cost
**Use for:** Critical decisions requiring maximum reasoning
- Security vulnerability assessment
- Complex architectural trade-offs
- Novel problem solving
- Critical bug analysis

**Available Models:**
- anthropic/claude-3-opus - Maximum reasoning

## Decision Matrix

| Task Type | Recommended Tier | Fallback |
|-----------|-----------------|----------|
| Write unit test | Tier 1 | Tier 2 |
| Refactor function | Tier 1 | Tier 2 |
| API endpoint | Tier 2 | Tier 1 |
| Database schema | Tier 2 | Tier 3 |
| Security audit | Tier 2 | Tier 3 |
| Architecture design | Tier 3 | Tier 2 |
| Debug production issue | Tier 3 | Tier 2 |

## Implementation Rules

1. **Start with Tier 1** - Always attempt simple tasks with local models first
2. **Escalate on failure** - If Tier 1 fails or produces poor results, retry with Tier 2
3. **Log selection rationale** - Always log which tier was selected and why in task artifacts
4. **Cache decisions** - If similar tasks succeed with a specific tier, use that for future similar tasks
5. **Never use Tier 3 for:**
   - Documentation
   - Simple code generation
   - File operations

## Cost Tracking

Agents MUST log model selection in task artifacts:

```markdown
## Model Selection
- Tier: 2
- Model: anthropic/claude-3.5-sonnet
- Rationale: Complex debugging requiring reasoning about multi-file interactions
- Estimated cost: ~$0.01
```

## Environment Variables

- `OLLAMA_BASE_URL` - Local Ollama endpoint (default: http://ollama:11434)
- `OPENROUTER_API_KEY` - Remote API key
- `OPENROUTER_MODEL` - Default remote model
- `PROVEDOR_LLM` - Default provider (ollama/openrouter)

## Agent Behavior

1. **Analyze task complexity** before starting
2. **Select appropriate tier** based on decision matrix
3. **Execute with selected model**
4. **Evaluate output quality**
5. **Escalate if needed** - If output is poor, retry with higher tier
6. **Log selection** - Record tier, model, and rationale
