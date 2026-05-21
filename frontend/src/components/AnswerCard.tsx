"use client";

import { BookOpen } from "lucide-react";
import ReactMarkdown from "react-markdown";
import type { AskResponse } from "@/lib/types";
import { SourceCard } from "./SourceCard";

interface Props {
  query: string;
  data: AskResponse;
}

export function AnswerCard({ query, data }: Props) {
  return (
    <article className="animate-slide-up space-y-6">
      <h2 className="text-xl font-semibold leading-snug tracking-tight">{query}</h2>

      <div className="rounded-2xl border border-[color:var(--color-border)] bg-[color:var(--color-surface)] p-5 shadow-sm">
        <div className="prose-answer text-[color:var(--color-text)]">
          <ReactMarkdown
            components={{
              code: ({ children }) => (
                <code className="font-mono text-[0.85em]">{children}</code>
              ),
            }}
          >
            {data.answer}
          </ReactMarkdown>
        </div>
      </div>

      {data.sources.length > 0 && (
        <section>
          <div className="mb-3 flex items-center gap-1.5 text-xs font-medium uppercase tracking-wide text-[color:var(--color-text-muted)]">
            <BookOpen size={12} />
            Fontes citadas ({data.sources.length})
          </div>
          <div className="space-y-2">
            {data.sources.map((hit, i) => (
              <SourceCard key={hit.chunk_id} hit={hit} index={i} />
            ))}
          </div>
        </section>
      )}
    </article>
  );
}
