#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fill_answers.py
===============
Runs each test question through YOUR Lumie pipeline (process_query) and writes the
answer into testset_questions.jsonl, so lumie_eval.py can score it.

Your pipeline (pipeline.py) exposes:
    async def process_query(question, language=None, session_id=None)
        -> {"answer": str, "sources": list}

This script imports that function, calls it (handling the async + the global FAISS
vectorstore), and stores result["answer"].

RUN IT FROM THE REPO ROOT so that `src/`, your `.env`, and the FAISS index resolve:

    # from C:\\Users\\julia\\Downloads\\chatbot_python-main
    python eval\\fill_answers.py --dataset eval\\testset_questions.jsonl

If your pipeline.py lives somewhere other than the repo root, set its import path:
    set PIPELINE_MODULE=src.rag_pipeline.pipeline      (Windows)
    python eval\\fill_answers.py --dataset eval\\testset_questions.jsonl
"""

import argparse, asyncio, importlib, json, os, re, sys

# --- make the repo importable no matter where we're launched from ---
_HERE = os.path.dirname(os.path.abspath(__file__))
for p in (os.getcwd(), os.path.dirname(_HERE), _HERE):
    if p and p not in sys.path:
        sys.path.insert(0, p)

# --- locate process_query ---
def _load_process_query():
    candidates = []
    env = os.environ.get("PIPELINE_MODULE")
    if env:
        candidates.append(env)
    candidates += ["pipeline", "src.rag_pipeline.pipeline", "src.pipeline",
                   "app.pipeline", "src.app.pipeline"]
    for mod in candidates:
        try:
            m = importlib.import_module(mod)
            if hasattr(m, "process_query"):
                sys.stderr.write(f"[ok] using process_query from '{mod}'\n")
                return m.process_query
        except Exception:
            continue
    sys.exit("Could not import process_query. Run from the repo root, or set "
             "PIPELINE_MODULE to the dotted path of the module that defines it.")

process_query = _load_process_query()

# --- one persistent event loop for all the async calls ---
_LOOP = asyncio.new_event_loop()
asyncio.set_event_loop(_LOOP)

def _warm_vectorstore():
    """Load the global FAISS vectorstore exactly like the app server does."""
    try:
        from src.rag_pipeline.retrieval.vectorstore import init_vectorstore
        from src.app.core.config import settings
        init_vectorstore(settings.faiss_index_path)
        sys.stderr.write(f"[ok] vectorstore loaded from {settings.faiss_index_path}\n")
    except Exception as exc:
        sys.stderr.write(f"[warn] could not warm vectorstore: {exc}\n")

_NOT_READY = "sistema de busca ainda não está pronto"

def get_lumie_answer(question: str) -> str:
    result = _LOOP.run_until_complete(
        process_query(question, language="auto", session_id=None)  # no history => independent Qs
    )
    return (result or {}).get("answer", "") or ""

# --- citation / source-reference stripping ---
# The bot embeds inline references like "O item 1.2.2 está na página 2" and
# "Mais informações em Regulamento_11OBG_2026 — pag 3". These are navigation
# aids, not factual claims, but the decomposer treats them as atoms and FactScore
# marks them unsupported (the corpus doesn't contain page-number metadata).
# Stripping them before scoring isolates the real factual quality.

_REF_PATTERNS = [
    # "O item X.X do regulamento está na página N"
    r"[Oo]\s*item\s+[\d\.]+\s+(?:do\s+regulamento\s+)?(?:está|esta)\s+na\s+p[aá]gina\s+\d+\.?",
    # "Mais informações podem ser encontradas em ..."  (whole sentence)
    r"[Mm]ais\s+informa[çc][õo]es\s+(?:podem\s+ser\s+)?(?:encontrad[ao]s?\s+)?(?:em|no|na|nos|nas)\s+[^.]*\.?",
    # "Informações adicionais podem ser encontradas em ..."
    r"[Ii]nforma[çc][õo]es\s+adicionais\s+(?:podem\s+ser\s+)?(?:encontrad[ao]s?\s+)?(?:em|no|na|nos|nas)\s+[^.]*\.?",
    # "Você pode encontrar mais informações no/em ..."
    r"[Vv]oc[êe]\s+pode\s+encontrar\s+mais\s+informa[çc][õo]es\s+[^.]*\.?",
    # "Sugiro que entre em contato ... para obter essa informação."
    r"[Ss]ugiro\s+que\s+entre\s+em\s+contato\s+[^.]*\.?",
    # Generic "pode ser encontrado/a em/no ..." (catches any subject)
    r"[^.]*pode\s+ser\s+encontrad[oa]\s+(?:em|no|na|nos|nas)\s+[^.]*\.?",
    # "O regulamento/documento mencionado é <filename>"
    r"[^.]*(?:regulamento|documento|edital|complemento)\s+mencionad[oa]\s+[eé]\s+[^.]*\.?",
    # "— item X.X — pag N" or "- pag N" trailing references
    r"[\-—–]\s*(?:item\s+[\d\.]+\s*)?[\-—–]?\s*p[aá]g(?:ina)?\s*\d+\.?",
    # Any sentence containing a known document filename (bare reference)
    r"[^.]*(?:Regulamento_\w+|Complemento_Base\w*|Edital_Selec\w*|Procedimentos_Alteracao\w*|"
    r"D[uú]vidas_e_Suporte\w*|Modelo_QUEST\w*|Anexo_\d\w*)[^.]*\.?",
    # "Fonte:" / "Fontes:" / "Sources:" / "Referências:" trailing blocks
    r"\n\s*(?:Fontes?|Sources?|Refer[eê]ncias?|Citations?)\s*:.*",
    # "O documento fornecido não especifica ..."
    r"[Oo]\s+documento\s+fornecido\s+n[aã]o\s+especifica\s+[^.]*\.?",
]

import re as _re
_REF_RE = _re.compile("|".join(_REF_PATTERNS), _re.IGNORECASE | _re.DOTALL)

def strip_citations(text):
    if not text:
        return text
    cleaned = _REF_RE.sub("", text)
    # collapse multiple spaces / blank lines left behind
    cleaned = _re.sub(r" {2,}", " ", cleaned)
    cleaned = _re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="testset_questions.jsonl")
    ap.add_argument("--keep-citations", action="store_true")
    ap.add_argument("--overwrite", action="store_true",
                    help="Re-answer rows that already have an answer.")
    args = ap.parse_args()

    with open(args.dataset, encoding="utf-8") as fh:
        rows = [json.loads(l) for l in fh if l.strip()]

    _warm_vectorstore()

    done, checked_ready = 0, False
    for i, r in enumerate(rows, 1):
        if r.get("generated_answer") and not args.overwrite:
            continue
        try:
            ans = get_lumie_answer(r["question"])
        except Exception as exc:                                   # noqa: BLE001
            sys.stderr.write(f"[warn] row {r.get('id')} failed: {exc}\n")
            r["generated_answer"] = None
            continue

        # Stop early instead of filling 200 junk answers if the index never loaded.
        if not checked_ready:
            checked_ready = True
            if _NOT_READY in (ans or "").lower():
                sys.exit("Retrieval returned 'sistema de busca ainda não está pronto' — the "
                         "FAISS vectorstore is not loaded.\nEasiest fix: keep your chatbot "
                         "SERVER running and answer via HTTP instead (tell me the local "
                         "endpoint and I'll switch the hook), or tell me the function that "
                         "initializes the vectorstore so I can call it here.")

        r["generated_answer"] = ans if args.keep_citations else strip_citations(ans)
        done += 1
        if i % 20 == 0:
            sys.stderr.write(f"  {i}/{len(rows)} answered\n")

    with open(args.dataset, "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    sys.stderr.write(f"Done. Filled {done} answers in {args.dataset}\n")

if __name__ == "__main__":
    main()