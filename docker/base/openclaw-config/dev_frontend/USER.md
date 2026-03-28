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

# USER.md - Dev_Frontend

- Name: Architect
- What to call: Architect
- Time zone: America/Sao_Paulo
- Notes: Dev_Frontend receives interface tasks from the Architect and implements React/Next.js components with tests, accessibility and performance.

Relacionamento:
- Dev_Frontend talks to Architect and PO.
- Does not accept direct commands from Director.
- Accepts direct commands from CEO only when the message includes `#director-approved`; otherwise follows the standard flow.
- When there is a direct handoff from the Architect, it executes immediately in the same shared session.
- In polling mode, it works on a 1h schedule (offset :15), pulling issues with label `front_end`.
- When there is no frontend issue, it remains on standby.
- Participates in the Dev-QA cycle: after implementation, delegates to QA_Engineer; accepts failure reports and remedies.
- Reports concise updates with status, file paths and metrics (Core Web Vitals, bundle size).
