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

"""Human-readable labels for OpenClaw session keys (main vs delegated/sub)."""


def session_kind(session_key: str | None, agent_slug: str | None) -> str:
    """Return 'main' for agent:<slug>:main, else 'sub'."""
    if not session_key or not agent_slug:
        return "sub"
    normalized = session_key.strip().lower()
    expected = f"agent:{agent_slug.strip().lower()}:main"
    return "main" if normalized == expected else "sub"


def session_display_label(session_key: str | None, agent_slug: str | None) -> str:
    """Short UI label: Principal vs Subagente · <suffix>."""
    if not session_key:
        return "—"
    if session_kind(session_key, agent_slug) == "main":
        return "Principal"
    parts = session_key.split(":", 2)
    suffix = parts[2] if len(parts) > 2 else session_key
    if len(suffix) > 48:
        suffix = suffix[:45] + "…"
    return f"Subagente · {suffix}"
