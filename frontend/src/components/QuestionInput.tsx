"use client";

import { ArrowRight, Loader2 } from "lucide-react";
import { useState, type FormEvent, type KeyboardEvent } from "react";

interface Props {
  onSubmit: (query: string) => void;
  loading: boolean;
  autoFocus?: boolean;
}

export function QuestionInput({ onSubmit, loading, autoFocus }: Props) {
  const [value, setValue] = useState("");

  function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const trimmed = value.trim();
    if (!trimmed || loading) return;
    onSubmit(trimmed);
  }

  function handleKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      const trimmed = value.trim();
      if (!trimmed || loading) return;
      onSubmit(trimmed);
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="group relative flex items-end gap-2 rounded-2xl border border-[color:var(--color-border)] bg-[color:var(--color-surface)] p-3 shadow-sm transition focus-within:border-[color:var(--color-accent)] focus-within:shadow-md"
    >
      <textarea
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Pergunte sobre PRODIST, ONS, classificação de tensão, indicadores DEC/FEC..."
        rows={1}
        autoFocus={autoFocus}
        disabled={loading}
        className="max-h-40 min-h-[2.5rem] flex-1 resize-none bg-transparent px-1 py-2 text-[15px] outline-none placeholder:text-[color:var(--color-text-muted)] disabled:opacity-60"
      />
      <button
        type="submit"
        disabled={loading || !value.trim()}
        aria-label="Enviar pergunta"
        className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-[color:var(--color-accent)] text-white transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-40"
      >
        {loading ? (
          <Loader2 size={18} className="animate-spin" />
        ) : (
          <ArrowRight size={18} strokeWidth={2.5} />
        )}
      </button>
    </form>
  );
}
