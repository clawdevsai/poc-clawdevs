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
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import Column
from sqlalchemy import JSON


class Approval(SQLModel, table=True):
    __tablename__ = "approvals"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    agent_id: Optional[UUID] = Field(default=None, foreign_key="agents.id", index=True)
    openclaw_approval_id: Optional[str] = Field(default=None, index=True)
    action_type: str
    payload: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    confidence: Optional[float] = None
    rubric_scores: Optional[Dict[str, Any]] = Field(
        default=None, sa_column=Column(JSON)
    )
    status: str = Field(default="pending", index=True)  # pending|approved|rejected
    decided_by_id: Optional[UUID] = Field(
        default=None, foreign_key="users.id", index=True
    )
    justification: Optional[str] = None
    decided_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
