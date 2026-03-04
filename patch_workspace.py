import os
import glob
import re

rule = """
## Workspace e Repositórios

**Obrigatório:** Todos os projetos GitHub que forem baixados via comando DEVEM ser clonados e salvos no diretório `/workspace`. Nunca clone ou baixe repositórios na raiz do sistema ou outras pastas.
"""

def process_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    if "## Workspace e Repositórios" in content:
        print(f"Already applied to {filepath}")
        return
        
    # Inject before "## Onde posso falhar" or "---" at the end if possible, or just before "## Onde"
    if "## Onde posso falhar" in content:
        content = content.replace("## Onde posso falhar", rule + "\n## Onde posso falhar")
    else:
        content += "\n" + rule
        
    with open(filepath, 'w') as f:
        f.write(content)
    print(f"Updated {filepath}")

for f in glob.glob("docs/soul/*.md"):
    process_file(f)

# Also update configmaps
def process_configmap(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
        
    if "## Workspace e Repositórios" in content:
        print(f"Already applied to {filepath}")
        return
        
    content = content.replace("## Onde posso falhar", rule.replace('\n', '\n    ') + "\n    ## Onde posso falhar")
    content = content.replace("**Nunca:**", "**Workspace:** Todos os projetos GitHub baixados devem ir para `/workspace`.\n    **Nunca:**")
    
    with open(filepath, 'w') as f:
        f.write(content)
    print(f"Updated {filepath}")

process_configmap("k8s/management-team/soul/configmap.yaml")
process_configmap("k8s/development-team/soul/configmap.yaml")

