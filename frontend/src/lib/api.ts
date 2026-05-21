import type { AskRequest, AskResponse } from "./types";

export class AskError extends Error {
  constructor(message: string, public status?: number) {
    super(message);
    this.name = "AskError";
  }
}

export async function ask(req: AskRequest): Promise<AskResponse> {
  const res = await fetch("/api/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });

  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new AskError(text || `Request failed with status ${res.status}`, res.status);
  }

  return (await res.json()) as AskResponse;
}
