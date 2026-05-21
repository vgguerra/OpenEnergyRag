import { Info } from "lucide-react";

export function Disclaimer() {
  return (
    <div className="flex items-start gap-2 rounded-lg border border-[color:var(--color-border)] bg-[color:var(--color-surface-muted)] px-3 py-2 text-[12.5px] text-[color:var(--color-text-muted)]">
      <Info size={13} className="mt-0.5 shrink-0" />
      <span>
        Demo educativa. Não é assessoria regulatória. Sempre confira o documento original citado.
      </span>
    </div>
  );
}
