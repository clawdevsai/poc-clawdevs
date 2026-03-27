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
from datetime import datetime, UTC
from uuid import UUID, uuid4


class Agent(SQLModel, table=True):
    __tablename__ = "agents"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    slug: str = Field(unique=True, index=True)
    display_name: str
    role: str
    avatar_url: Optional[str] = None
    status: str = Field(default="unknown")  # active|inactive|error|unknown
    current_model: Optional[str] = None
    openclaw_session_id: Optional[str] = None
    last_heartbeat_at: Optional[datetime] = None
    cron_expression: Optional[str] = None
    cron_last_run_at: Optional[datetime] = None
    cron_next_run_at: Optional[datetime] = None
    cron_status: str = Field(default="idle")  # idle|running|error

    # Escalation capability
    can_escalate: bool = Field(default=False)  # Only Arquiteto and CEO
    max_escalations: int = Field(default=0)  # Max escalations this agent can handle
    escalations_handled: int = Field(default=0)  # Count of escalations handled

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
