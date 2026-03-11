"use client";

import { useState, useTransition } from "react";

type DirectiveFormProps = {
  onCompleted?: () => void;
};

export function DirectiveForm({ onCompleted }: DirectiveFormProps) {
  const [directive, setDirective] = useState("");
  const [requiresApproval, setRequiresApproval] = useState(true);
  const [message, setMessage] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();

  return (
    <form
      className="panel panel-strong rounded-3xl p-6"
      onSubmit={(event) => {
        event.preventDefault();
        setMessage(null);
        startTransition(async () => {
          const endpoint = requiresApproval ? "/api/approvals" : "/api/directives";
          const payload = requiresApproval
            ? { action: "create", directive }
            : { directive };
          const response = await fetch(endpoint, {
            method: "POST",
            headers: {
              "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
          });
          const result = (await response.json()) as { issueId?: string; error?: string };
          if (!response.ok) {
            setMessage(`Erro: ${result.error ?? "directive_error"}`);
            return;
          }
          setMessage(
            requiresApproval
              ? `Diretiva aguardando aprovação. Ref ${result.issueId}`
              : `Diretiva enviada com sucesso. Ref ${result.issueId}`
          );
          setDirective("");
          onCompleted?.();
        });
      }}
    >
      <div className="mb-4 flex items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-semibold text-white">Console do diretor</h2>
          <p className="mt-1 text-sm text-[var(--muted)]">
            Envie uma demanda unica para o stream `cmd:strategy`.
          </p>
        </div>
      </div>
      <textarea
        value={directive}
        onChange={(event) => setDirective(event.target.value)}
        placeholder="Exemplo: criar backlog inicial para um CRUD de usuarios em Go, com auth JWT e persistencia Postgres."
        className="min-h-40 w-full rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-sm text-white outline-none transition focus:border-cyan-300"
      />
      <label className="mt-4 flex items-center gap-3 text-sm text-[var(--muted)]">
        <input
          type="checkbox"
          checked={requiresApproval}
          onChange={(event) => setRequiresApproval(event.target.checked)}
          className="h-4 w-4 rounded border-white/20 bg-black/40 text-cyan-300"
        />
        Requer aprovacao humana antes de iniciar o pipeline.
      </label>
      <div className="mt-4 flex items-center justify-between gap-4">
        <p className="text-sm text-[var(--muted)]">{message ?? "O envio gera um item para o PO consumir."}</p>
        <button
          type="submit"
          disabled={isPending || !directive.trim()}
          className="rounded-full bg-cyan-300 px-5 py-2 text-sm font-semibold text-slate-950 transition hover:bg-cyan-200 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {isPending ? "Enviando..." : "Enviar diretiva"}
        </button>
      </div>
    </form>
  );
}
