import re
from pathlib import Path


def check_links():
    root = Path("/home/luke/Workspace/clawdevs-1")
    md_files = list(root.glob("**/*.md"))
    broken_links = []

    for md_file in md_files:
        content = md_file.read_text()
        # Find [text](link)
        links = re.findall(r"\[.*?\]\((?!http)(.*?)\)", content)
        for link in links:
            # Remove anchors
            link_path = link.split("#")[0]
            if not link_path:
                continue

            # Resolve relative path
            target = (md_file.parent / link_path).resolve()

            if not target.exists():
                broken_links.append(f"{md_file}: {link} -> {target}")

    return broken_links


if __name__ == "__main__":
    broken = check_links()
    for b in broken:
        print(b)
