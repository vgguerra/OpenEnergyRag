interface Props {
  query: string;
}

export function LoadingState({ query }: Props) {
  return (
    <div className="animate-slide-up space-y-6">
      <h2 className="text-xl font-semibold leading-snug tracking-tight">{query}</h2>
      <div className="space-y-3 rounded-2xl border border-[color:var(--color-border)] bg-[color:var(--color-surface)] p-5 shadow-sm">
        <div className="h-3 w-[85%] animate-pulse-soft rounded bg-[color:var(--color-surface-muted)]" />
        <div className="h-3 w-[72%] animate-pulse-soft rounded bg-[color:var(--color-surface-muted)]" />
        <div className="h-3 w-[90%] animate-pulse-soft rounded bg-[color:var(--color-surface-muted)]" />
        <div className="h-3 w-[55%] animate-pulse-soft rounded bg-[color:var(--color-surface-muted)]" />
      </div>
    </div>
  );
}
