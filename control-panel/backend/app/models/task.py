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

from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4


class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str
    description: Optional[str] = None
    status: str = Field(default="inbox", index=True)  # inbox|in_progress|review|done
    priority: str = Field(default="medium")  # low|medium|high
    assigned_agent_id: Optional[UUID] = Field(
        default=None, foreign_key="agents.id", index=True
    )
    github_issue_number: Optional[int] = None
    github_issue_url: Optional[str] = None
    github_repo: Optional[str] = None
    label: Optional[str] = Field(
        default=None, index=True
    )  # back_end|front_end|mobile|tests|devops|dba|security|ux
    due_at: Optional[datetime] = None

    # Failure tracking fields
    failure_count: int = Field(default=0, index=True)
    consecutive_failures: int = Field(default=0)
    last_error: Optional[str] = None
    error_reason: Optional[str] = None
    last_failed_at: Optional[datetime] = None

    # Escalation fields
    escalated_to_agent_id: Optional[UUID] = Field(
        default=None, foreign_key="agents.id", index=True
    )
    escalation_reason: Optional[str] = None
    escalated_at: Optional[datetime] = None

    # Cost tracking fields
    estimated_cost: Optional[float] = None
    actual_cost: float = Field(default=0.0)
    cost_tier: Optional[str] = Field(default=None)  # local|medium|premium

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
