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

from typing import Dict

VALID_TASK_LABELS = [
    "back_end",
    "front_end",
    "mobile",
    "tests",
    "devops",
    "dba",
    "security",
    "ux",
]

LABEL_ALIASES: Dict[str, str] = {
    "back-end": "back_end",
    "backend": "back_end",
    "back-end": "back_end",
    "front-end": "front_end",
    "frontend": "front_end",
}

LABEL_TO_AGENT_SLUG: Dict[str, str] = {
    "back_end": "dev_backend",
    "front_end": "dev_frontend",
    "mobile": "dev_mobile",
    "tests": "qa_engineer",
    "devops": "devops_sre",
    "dba": "dba_data_engineer",
    "security": "security_engineer",
    "ux": "ux_designer",
}


def normalize_label(label: str) -> str:
    """Normalize a task label to the canonical form."""
    normalized = label.strip().lower()
    return LABEL_ALIASES.get(normalized, normalized)


def is_valid_label(label: str) -> bool:
    """Check if a label is valid."""
    normalized = normalize_label(label)
    return normalized in VALID_TASK_LABELS


def get_escalation_agent(label: str) -> str:
    """Get the escalation agent for a given task label."""
    normalized = normalize_label(label)
    if normalized in LABEL_TO_AGENT_SLUG:
        return LABEL_TO_AGENT_SLUG[normalized]
    return "arquiteto"
