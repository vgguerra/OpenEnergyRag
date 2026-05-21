import { AlertTriangle } from "lucide-react";

interface Props {
  message: string;
}

export function ErrorState({ message }: Props) {
  return (
    <div className="animate-slide-up flex items-start gap-3 rounded-2xl border border-red-200 bg-red-50 p-5 text-sm text-red-800 dark:border-red-900/50 dark:bg-red-950/40 dark:text-red-200">
      <AlertTriangle size={18} className="mt-0.5 shrink-0" />
      <div>
        <p className="font-medium">Falha ao consultar o backend</p>
        <p className="mt-1 break-words text-red-800/80 dark:text-red-200/80">{message}</p>
      </div>
    </div>
  );
}
