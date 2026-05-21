export type RetrievalMode = "hybrid" | "dense";

export interface ChunkMetadata {
  source?: string;
  section?: string;
  subsection?: string;
  item?: string;
  page_start?: number;
  [key: string]: unknown;
}

export interface SearchHit {
  chunk_id: string;
  score: number;
  text: string;
  metadata: ChunkMetadata;
}

export interface AskResponse {
  answer: string;
  sources: SearchHit[];
}

export interface AskRequest {
  query: string;
  top_k?: number;
  mode?: RetrievalMode;
}
