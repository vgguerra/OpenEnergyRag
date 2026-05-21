import { Zap, Github } from "lucide-react";

export function Header() {
  return (
    <header className="w-full border-b border-[color:var(--color-border)] bg-[color:var(--color-surface)]">
      <div className="mx-auto flex max-w-3xl items-center justify-between px-6 py-4">
        <div className="flex items-center gap-2.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[color:var(--color-accent)]">
            <Zap size={18} strokeWidth={2.5} className="text-white" />
          </div>
          <div className="leading-tight">
            <p className="text-sm font-semibold tracking-tight">Open Energy RAG</p>
            <p className="text-[11px] text-[color:var(--color-text-muted)]">
              PRODIST / ANEEL / ONS · citation-first
            </p>
          </div>
        </div>
        <a
          href="https://github.com/vgguerra/OpenEnergyRag"
          target="_blank"
          rel="noreferrer noopener"
          className="flex items-center gap-1.5 rounded-md border border-[color:var(--color-border)] px-2.5 py-1.5 text-xs font-medium text-[color:var(--color-text-muted)] transition hover:border-[color:var(--color-accent)] hover:text-[color:var(--color-text)]"
        >
          <Github size={14} />
          GitHub
        </a>
      </div>
    </header>
  );
}
