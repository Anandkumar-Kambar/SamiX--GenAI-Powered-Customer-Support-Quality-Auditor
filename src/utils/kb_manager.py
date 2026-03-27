"""
SamiX Knowledge Intelligence & RAG Engine

Optimized for Render.com:
1. Uses HuggingFace Inference API for Embeddings (0MB RAM).
2. Conditional Reranker loading (Disabled on Render to save 300MB RAM).
3. Robust logging to replace Streamlit-only warnings.
"""
from __future__ import annotations

import io
import asyncio
import json
import os
import re
import logging
import textwrap
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

# Setup logging for backend visibility
logger = logging.getLogger("samix.kb")

# RAG Configuration 
CHUNK_SIZE     = 800      
CHUNK_OVERLAP  = 100
TOP_K          = 10      
RERANK_K       = 4       
EMBED_MODEL    = "sentence-transformers/all-MiniLM-L6-v2"
RERANK_MODEL   = "cross-encoder/ms-marco-MiniLM-L-6-v2"
MILVUS_DB      = "milvus_lite.db"
META_PATH      = "data/kb/kb_meta.json"
KB_DIR         = "data/kb"

COLLECTIONS    = ["policies", "product_kb", "compliance"]

# Seed Knowledge (Built-in)
GENERALISED_KB: list[dict] = [
    {
        "name":       "Customer Support Best Practices (ITIL v4)",
        "collection": "policies",
        "chunks":     120,
        "content": textwrap.dedent("""\
            Incident management: acknowledge within 60 seconds.
            Always confirm customer identity before accessing account data.
            Closing protocol: confirm resolution before ending every call.
            Escalation path: agent -> senior agent -> supervisor -> manager.
            SLA for billing disputes: resolve within 2 business days.
            Empathy language: mirror customer emotion, then redirect to solution.
        """),
    },
    {
        "name":       "BPO Compliance Framework (ISO 9001-2015)",
        "collection": "compliance",
        "chunks":     98,
        "content": textwrap.dedent("""\
            All agents must follow approved scripts for regulated topics.
            Financial information must not be disclosed without identity verification.
            Call recordings are mandatory for quality assurance.
            Non-compliance must be reported within 24 hours.
            Corrective actions must be documented and reviewed quarterly.
        """),
    },
    {
        "name":       "De-escalation Techniques",
        "collection": "policies",
        "chunks":     65,
        "content": textwrap.dedent("""\
            Step 1: Let the customer finish speaking without interruption.
            Step 2: Acknowledge the frustration explicitly: 'I completely understand'.
            Step 3: Apologise for the inconvenience before moving to resolution.
            Step 4: Offer a concrete next step with a specific timeline.
            Step 5: Confirm the customer is satisfied before closing.
            Avoid: 'calm down', 'that is our policy', 'there is nothing I can do'.
        """),
    },
    {
        "name":       "GDPR Customer Data Handling",
        "collection": "compliance",
        "chunks":     88,
        "content": textwrap.dedent("""\
            Never read back full card numbers or passwords on a call.
            Only collect data necessary for the stated purpose.
            Customer has the right to data deletion within 30 days of request.
            Any data breach must be reported to the DPO within 72 hours.
            Call recordings may not be retained beyond 12 months without consent.
        """),
    },
    {
        "name":       "Empathy Language Patterns (50 phrases)",
        "collection": "policies",
        "chunks":     50,
        "content": textwrap.dedent("""\
            'I completely understand how frustrating that must be.'
            'I sincerely apologise that this has happened.'
            'Thank you for bringing this to our attention.'
            'I appreciate your patience while I look into this.'
            'I can absolutely see why you feel that way.'
            'Let me personally make sure this is resolved for you.'
            'I am going to take ownership of this issue right now.'
        """),
    },
    {
        "name":       "GenAI QA Auditor Standard Rubric",
        "collection": "product_kb",
        "chunks":     72,
        "content": textwrap.dedent("""\
            Empathy (20%): acknowledgment, emotional mirroring, apology quality.
            Professionalism (15%): language, tone, script adherence.
            Compliance (25%): policy accuracy, regulatory adherence, script compliance.
            Resolution (20%): issue resolved, root cause addressed, no false close.
            Communication (5%): clarity, pacing, active listening signals.
            Integrity (15%): factual accuracy, no hallucinations, correct policy citation.
            Phase bonus (+/-5): improving arc = +5, declining arc = -5.
            Auto-fail triggers: rude language, data breach, impossible promise.
        """),
    },
]

@dataclass
class KBFile:
    filename:   str
    collection: str
    chunks:     int  = 0
    size_bytes: int  = 0
    indexed:    bool = False

    @property
    def size_label(self) -> str:
        kb = self.size_bytes / 1024
        return f"{kb:.1f} KB" if kb < 1024 else f"{kb / 1024:.1f} MB"

@dataclass
class RAGResult:
    text:       str
    source:     str
    collection: str
    score:      float     
    page:       int = 0

    def to_citation(self) -> str:
        return f"{self.source} (conf {self.score:.2f})"


class KBManager:
    def __init__(self) -> None:
        os.makedirs(KB_DIR, exist_ok=True)
        self._files: list[KBFile]      = []
        self._embeddings               = None
        self._reranker                 = None
        self._stores: dict[str, object] = {}   
        self._load_meta()
        self._init_embeddings()
        self._init_reranker()
        self._reload_existing_stores()
        self._load_generalised_kb()
        self._autoload_dropped_files()

    def _init_embeddings(self) -> None:
        """ Uses HF Inference API to save ~400MB of RAM. """
        try:
            token = os.getenv("HF_TOKEN")
            if not token:
                logger.error("HF_TOKEN missing. Vector search will be disabled.")
                return

            from langchain_huggingface import HuggingFaceInferenceAPIEmbeddings
            self._embeddings = HuggingFaceInferenceAPIEmbeddings(
                api_key=token,
                model_name=EMBED_MODEL
            )
            logger.info("KBManager: Embeddings initialized via Cloud API.")
        except Exception as exc:
            logger.error(f"KBManager: Embedding init failed: {exc}")
            self._embeddings = None

    def _init_reranker(self) -> None:
        """ Skips loading Cross-Encoder on Render to prevent OOM crashes. """
        if os.getenv("RENDER"):
            logger.info("KBManager: Render environment detected. Skipping Reranker to save RAM.")
            return

        try:
            from sentence_transformers import CrossEncoder
            self._reranker = CrossEncoder(RERANK_MODEL, device="cpu")
        except Exception as exc:
            logger.warning(f"KBManager: Reranker unavailable: {exc}")
            self._reranker = None

    def _load_meta(self) -> None:
        if os.path.exists(META_PATH):
            try:
                with open(META_PATH) as fh:
                    raw = json.load(fh)
                self._files = [KBFile(**r) for r in raw]
            except Exception:
                self._files = []

    def _save_meta(self) -> None:
        os.makedirs(os.path.dirname(META_PATH), exist_ok=True)
        with open(META_PATH, "w") as fh:
            json.dump([asdict(f) for f in self._files], fh, indent=2)

    def _reload_existing_stores(self) -> None:
        if not self._embeddings: return
        for col in COLLECTIONS:
            store = self._try_connect_store(col)
            if store: self._stores[col] = store

    def _try_connect_store(self, collection: str) -> Optional[object]:
        try:
            from langchain_milvus import Milvus
            uri = MILVUS_DB.replace("\\", "/")
            return Milvus(
                embedding_function=self._embeddings,
                connection_args={"uri": uri},
                collection_name=collection,
                drop_old=False,
            )
        except Exception:
            return None

    def _load_generalised_kb(self) -> None:
        for item in GENERALISED_KB:
            if os.path.exists(self._fallback_path(item["name"])): continue
            self._index_text(item["content"], item["name"], item["collection"])

    def _autoload_dropped_files(self) -> None:
        known = {f.filename for f in self._files}
        for fname in os.listdir(KB_DIR):
            if fname.endswith(".chunks.txt") or fname == "kb_meta.json" or fname.startswith("."): continue
            if fname.endswith((".txt", ".pdf")) and fname not in known:
                try:
                    path = os.path.join(KB_DIR, fname)
                    with open(path, "rb") as fh: data = fh.read()
                    text = self._extract_text(data, fname)
                    chunks = self._chunk_text(text)
                    self._index_text_chunks(chunks, fname, "policies")
                    self._files.append(KBFile(fname, "policies", len(chunks), len(data), self._embeddings is not None))
                    self._save_meta()
                except Exception as e: logger.error(f"Auto-load failed for {fname}: {e}")

    @staticmethod
    def _safe_source_name(source: str) -> str:
        return source.replace(":", "-").replace("/", "_").replace("\\", "_")

    def _fallback_path(self, source: str) -> str:
        return os.path.join(KB_DIR, f"{self._safe_source_name(source)}.chunks.txt")

    @property
    def is_vector_enabled(self) -> bool: return self._embeddings is not None

    @property
    def files(self) -> list[KBFile]: return self._files

    @property
    def generalised_kb(self) -> list[dict]: return GENERALISED_KB

    def add_file(self, file_bytes: bytes, filename: str, collection: str = "policies") -> KBFile:
        dest = os.path.join(KB_DIR, filename)
        with open(dest, "wb") as fh: fh.write(file_bytes)
        text = self._extract_text(file_bytes, filename)
        chunks = self._chunk_text(text)
        self._index_text_chunks(chunks, filename, collection)
        kbf = KBFile(filename, collection, len(chunks), len(file_bytes), True)
        self._files = [f for f in self._files if f.filename != filename] + [kbf]
        self._save_meta()
        return kbf

    async def query(self, question: str, top_k: int = TOP_K, collection: Optional[str] = None) -> list[RAGResult]:
        return await asyncio.to_thread(self._sync_query, question, top_k, collection)

    def _sync_query(self, question: str, top_k: int, collection: Optional[str]) -> list[RAGResult]:
        cols = [collection] if collection else COLLECTIONS
        v_res, k_res = [], []
        for col in cols:
            store = self._stores.get(col)
            if store: v_res.extend(self._milvus_query(store, question, col, top_k * 2))
            k_res.extend(self._bm25_query(question, col, top_k * 2))
        
        candidates = self._fuse_results(v_res, k_res, top_k * 2)
        return self._rerank_results(question, candidates, top_k)

    def _rerank_results(self, query: str, results: list[RAGResult], top_k: int) -> list[RAGResult]:
        if not self._reranker or not results: return results[:top_k]
        try:
            import numpy as np
            pairs = [[query, r.text] for r in results]
            scores = self._reranker.predict(pairs)
            for res, sc in zip(results, scores):
                res.score = float(1.0 / (1.0 + np.exp(-float(sc))))
            return sorted(results, key=lambda x: x.score, reverse=True)[:top_k]
        except Exception: return results[:top_k]

    def _fuse_results(self, vector_res: list[RAGResult], keyword_res: list[RAGResult], top_k: int, k: int = 60) -> list[RAGResult]:
        scores: dict[str, float] = {}
        meta: dict[str, RAGResult] = {}
        for rank, res in enumerate(vector_res, 1):
            scores[res.text] = scores.get(res.text, 0) + 1.0 / (k + rank)
            meta[res.text] = res
        for rank, res in enumerate(keyword_res, 1):
            scores[res.text] = scores.get(res.text, 0) + 1.0 / (k + rank)
            if res.text not in meta: meta[res.text] = res
        fused = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [RAGResult(meta[t].text, meta[t].source, meta[t].collection, min(0.99, round(s * k, 3))) for t, s in fused[:top_k]]

    def _index_text(self, text: str, source: str, collection: str) -> None:
        chunks = self._chunk_text(text)
        self._index_text_chunks(chunks, source, collection)

    def _index_text_chunks(self, chunks: list[str], source: str, collection: str) -> None:
        if not chunks: return
        with open(self._fallback_path(source), "w", encoding="utf-8") as fh:
            for c in chunks: fh.write(c + "\n---CHUNK---\n")
        if not self._embeddings: return
        try:
            from langchain_milvus import Milvus
            from langchain_core.documents import Document
            docs = [Document(page_content=c, metadata={"source": source, "collection": collection}) for c in chunks]
            uri = MILVUS_DB.replace("\\", "/")
            if collection in self._stores: self._stores[collection].add_documents(docs)
            else: self._stores[collection] = Milvus.from_documents(docs, self._embeddings, connection_args={"uri": uri}, collection_name=collection, drop_old=False)
        except Exception as e: logger.error(f"Milvus error: {e}")

    def _milvus_query(self, store: object, question: str, col: str, top_k: int) -> list[RAGResult]:
        try:
            docs = store.max_marginal_relevance_search(question, k=top_k, fetch_k=top_k * 3, lambda_mult=0.6)
            return [RAGResult(d.page_content, d.metadata.get("source", "KB"), col, 0.85) for d in docs]
        except Exception: return []

    def _bm25_query(self, question: str, collection: str, top_k: int) -> list[RAGResult]:
        try:
            from rank_bm25 import BM25Okapi
            chunks = []
            for fn in os.listdir(KB_DIR):
                if fn.endswith(".chunks.txt"):
                    with open(os.path.join(KB_DIR, fn), encoding="utf-8") as f:
                        for c in f.read().split("---CHUNK---\n"):
                            if c.strip(): chunks.append((c.strip(), fn.replace(".chunks.txt", "")))
            if not chunks: return []
            bm25 = BM25Okapi([re.findall(r"[a-z0-9]+", c[0].lower()) for c in chunks])
            scores = bm25.get_scores(re.findall(r"[a-z0-9]+", question.lower()))
            idx = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
            return [RAGResult(chunks[i][0], chunks[i][1], collection, round(scores[i]/max(scores), 3)) for i in idx[:top_k] if scores[i] > 0]
        except Exception: return []

    @staticmethod
    def _extract_text(data: bytes, filename: str) -> str:
        if filename.lower().endswith(".pdf"):
            from pypdf import PdfReader
            return "\n".join(p.extract_text() or "" for p in PdfReader(io.BytesIO(data)).pages)
        return data.decode("utf-8", errors="replace")

    @staticmethod
    def _chunk_text(text: str) -> list[str]:
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP, separators=["\n\n", "\n", ". ", " "])
        return [c for c in splitter.split_text(text) if c.strip()]
