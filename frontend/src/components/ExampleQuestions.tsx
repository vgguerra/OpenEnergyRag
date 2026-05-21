"use client";

import { Sparkles } from "lucide-react";

const EXAMPLES = [
  "Como classificar a tensão de atendimento?",
  "Quais são os indicadores de continuidade individual?",
  "O que é energia injetada na geração distribuída?",
  "Quem fiscaliza o cumprimento dos procedimentos de distribuição?",
];

interface Props {
  onPick: (q: string) => void;
  disabled?: boolean;
}

export function ExampleQuestions({ onPick, disabled }: Props) {
  return (
    <div className="mt-6">
      <div className="mb-3 flex items-center gap-1.5 text-xs font-medium uppercase tracking-wide text-[color:var(--color-text-muted)]">
        <Sparkles size={12} />
        Tente perguntar
      </div>
      <div className="flex flex-wrap gap-2">
        {EXAMPLES.map((q) => (
          <button
            key={q}
            type="button"
            disabled={disabled}
            onClick={() => onPick(q)}
            className="rounded-full border border-[color:var(--color-border)] bg-[color:var(--color-surface)] px-3.5 py-1.5 text-sm text-[color:var(--color-text-muted)] transition hover:border-[color:var(--color-accent)] hover:text-[color:var(--color-text)] disabled:cursor-not-allowed disabled:opacity-50"
          >
            {q}
          </button>
        ))}
      </div>
    </div>
  );
}
