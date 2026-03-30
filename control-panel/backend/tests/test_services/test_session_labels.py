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

"""Tests for session_labels helpers."""

from app.services.session_labels import session_display_label, session_kind


class TestSessionKind:
    def test_main_key(self):
        assert session_kind("agent:po:main", "po") == "main"
        assert session_kind("AGENT:PO:MAIN", "po") == "main"

    def test_sub_key(self):
        assert session_kind("agent:po:delegation-abc", "po") == "sub"
        assert session_kind(None, "po") == "sub"
        assert session_kind("agent:po:main", None) == "sub"


class TestSessionDisplayLabel:
    def test_principal(self):
        assert session_display_label("agent:po:main", "po") == "Principal"

    def test_subagent_suffix(self):
        assert (
            session_display_label("agent:po:delegation-xyz", "po")
            == "Subagente · delegation-xyz"
        )

    def test_empty_key(self):
        assert session_display_label(None, "po") == "—"
