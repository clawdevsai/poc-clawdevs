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

from datetime import datetime, UTC
from typing import Any, Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel


class RuntimeSetting(SQLModel, table=True):
    __tablename__ = "runtime_setting"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    key: str = Field(index=True)
    value_json: Optional[Any] = Field(default=None, sa_column=Column(JSON))
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC).replace(tzinfo=None)
    )
    updated_by_user_id: Optional[UUID] = Field(default=None, foreign_key="users.id")


class RuntimeSettingAudit(SQLModel, table=True):
    __tablename__ = "runtime_setting_audit"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    setting_key: str = Field(index=True)
    previous_value_json: Optional[Any] = Field(
        default=None, sa_column=Column(JSON)
    )
    new_value_json: Optional[Any] = Field(default=None, sa_column=Column(JSON))
    action: str = Field(default="update")
    confirm_text: Optional[str] = None
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC).replace(tzinfo=None)
    )
    created_by_user_id: Optional[UUID] = Field(default=None, foreign_key="users.id")
