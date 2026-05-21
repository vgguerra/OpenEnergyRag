"use client";

import { useState } from "react";
import { AnswerCard } from "@/components/AnswerCard";
import { Disclaimer } from "@/components/Disclaimer";
import { ErrorState } from "@/components/ErrorState";
import { ExampleQuestions } from "@/components/ExampleQuestions";
import { Header } from "@/components/Header";
import { LoadingState } from "@/components/LoadingState";
import { QuestionInput } from "@/components/QuestionInput";
import { ask, AskError } from "@/lib/api";
import type { AskResponse } from "@/lib/types";

type Status =
  | { kind: "idle" }
  | { kind: "loading"; query: string }
  | { kind: "answer"; query: string; data: AskResponse }
  | { kind: "error"; query: string; message: string };

function parseErrorMessage(err: unknown): string {
  if (err instanceof AskError) {
    try {
      const parsed = JSON.parse(err.message);
      if (typeof parsed?.detail === "string") return parsed.detail;
    } catch {
      /* fallthrough */
    }
    return err.message;
  }
  return err instanceof Error ? err.message : "Erro desconhecido";
}

export default function Home() {
  const [status, setStatus] = useState<Status>({ kind: "idle" });

  const loading = status.kind === "loading";

  async function handleAsk(query: string) {
    setStatus({ kind: "loading", query });
    try {
      const data = await ask({ query, top_k: 5, mode: "hybrid" });
      setStatus({ kind: "answer", query, data });
    } catch (err) {
      setStatus({ kind: "error", query, message: parseErrorMessage(err) });
    }
  }

  const showHero = status.kind === "idle";

  return (
    <div className="flex min-h-dvh flex-col">
      <Header />

      <main className="mx-auto flex w-full max-w-3xl flex-1 flex-col px-6 py-10">
        {showHero && (
          <div className="mb-8">
            <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">
              Pergunte sobre os normativos do setor elétrico.
            </h1>
            <p className="mt-3 max-w-xl text-[15px] text-[color:var(--color-text-muted)]">
              RAG sobre PRODIST, ONS e correlatos. Cada resposta vem com a citação
              exata (documento, seção, item) dos PDFs públicos.
            </p>
          </div>
        )}

        <div className="space-y-3">
          <QuestionInput onSubmit={handleAsk} loading={loading} autoFocus />
          <Disclaimer />
        </div>

        {showHero && <ExampleQuestions onPick={handleAsk} disabled={loading} />}

        <div className="mt-10 space-y-8">
          {status.kind === "loading" && <LoadingState query={status.query} />}
          {status.kind === "answer" && (
            <AnswerCard query={status.query} data={status.data} />
          )}
          {status.kind === "error" && (
            <div className="space-y-4">
              <h2 className="text-xl font-semibold leading-snug tracking-tight">
                {status.query}
              </h2>
              <ErrorState message={status.message} />
            </div>
          )}
        </div>
      </main>

      <footer className="border-t border-[color:var(--color-border)] bg-[color:var(--color-surface)] py-4 text-center text-[12px] text-[color:var(--color-text-muted)]">
        Dataset 100% público (ANEEL, ONS). Reproduza o benchmark em{" "}
        <a
          href="https://github.com/vgguerra/OpenEnergyRag"
          target="_blank"
          rel="noreferrer noopener"
          className="underline-offset-2 hover:text-[color:var(--color-text)] hover:underline"
        >
          vgguerra/OpenEnergyRag
        </a>
        .
      </footer>
    </div>
  );
}
