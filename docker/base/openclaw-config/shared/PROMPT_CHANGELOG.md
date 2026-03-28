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

# PROMPT CHANGELOG

History of relevant changes to operational prompts and SDD templates.

## 2026-03-25

### Added
- Operational gates and minimum output for auditing at `SDD_OPERATIONAL_PROMPTS.md`.
- Blocos few-shot (`entrada -> output`) for role in `SDD_OPERATIONAL_PROMPTS.md`.
- Operational reverse prompting section in `SDD_OPERATIONAL_PROMPTS.md`.
- Gate and traceability fields in `VALIDATE_TEMPLATE.md`.

### Changed
- Agent rules (`ceo`, `po`, `arquiteto`, `dev_backend`) for hard gate SDD and mandatory evidence before `DONE`.

## Registration convention
- Always record: date, type (`Added|Changed|Removed`), file and expected impact.
- In changes that alter behavior, include a short before/after example in the PR.