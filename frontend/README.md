# open-energy-rag frontend

Next.js 15 + TypeScript + Tailwind v4 UI for the open-energy-rag backend. Single-page Q&A interface: ask a question about Brazilian electric-sector regulations, get a citation-first answer.

## Architecture

- App Router, single page (`src/app/page.tsx`).
- Server route handler at `src/app/api/ask/route.ts` proxies to the FastAPI backend via the server-side `BACKEND_URL` env var (browser never sees the backend URL).
- Components in `src/components/`, types in `src/lib/types.ts`, fetch wrapper in `src/lib/api.ts`.
- Tailwind v4 with CSS-based theming (light/dark via `prefers-color-scheme`).

## Run locally

Prereqs: Node.js 20+, pnpm or npm, and the backend running on `http://localhost:8000`.

```bash
cd frontend
pnpm install            # or: npm install
cp .env.example .env.local
pnpm dev                # or: npm run dev
```

Open `http://localhost:3000`.

## Environment

| Variable      | Default                  | Purpose                                        |
|---------------|--------------------------|------------------------------------------------|
| `BACKEND_URL` | `http://localhost:8000`  | FastAPI base URL, used by the `/api/ask` proxy |

`BACKEND_URL` is server-side only. It is not exposed to the browser bundle.
