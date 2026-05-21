"use client";

import { ChevronDown, FileText } from "lucide-react";
import { useState } from "react";
import type { SearchHit } from "@/lib/types";

interface Props {
  hit: SearchHit;
  index: number;
}

function citationLabel(meta: SearchHit["metadata"]): string {
  const parts: string[] = [];
  if (meta.section) parts.push(`Seção ${meta.section}`);
  if (meta.subsection) parts.push(meta.subsection);
  if (meta.item) parts.push(`item ${meta.item}`);
  return parts.join(" · ") || "Sem cabeçalho";
}

function sourceLabel(source?: string): string {
  if (!source) return "documento desconhecido";
  return source.replace(/\.pdf$/i, "");
}

export function SourceCard({ hit, index }: Props) {
  const [open, setOpen] = useState(false);

  return (
    <div className="overflow-hidden rounded-lg border border-[color:var(--color-border)] bg-[color:var(--color-surface)] transition hover:border-[color:var(--color-accent)]">
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className="flex w-full items-start gap-3 px-4 py-3 text-left"
      >
        <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-md bg-[color:var(--color-accent-soft)] text-[11px] font-semibold text-[color:var(--color-accent)]">
          {index + 1}
        </span>
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-1.5 text-[11px] font-medium uppercase tracking-wide text-[color:var(--color-text-muted)]">
            <FileText size={11} />
            <span className="truncate">{sourceLabel(hit.metadata.source)}</span>
          </div>
          <p className="mt-1 truncate text-sm font-medium">
            {citationLabel(hit.metadata)}
          </p>
        </div>
        <div className="ml-auto flex items-center gap-2">
          <span className="font-mono text-[10px] text-[color:var(--color-text-muted)]">
            {hit.score.toFixed(3)}
          </span>
          <ChevronDown
            size={16}
            className={`text-[color:var(--color-text-muted)] transition-transform ${open ? "rotate-180" : ""}`}
          />
        </div>
      </button>
      {open && (
        <div className="border-t border-[color:var(--color-border)] bg-[color:var(--color-surface-muted)] px-4 py-3">
          <p className="whitespace-pre-wrap text-[13.5px] leading-relaxed text-[color:var(--color-text-muted)]">
            {hit.text}
          </p>
        </div>
      )}
    </div>
  );
}
