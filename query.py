import requests
import chromadb
from sentence_transformers import SentenceTransformer
from config import (
    LLM_API_KEY, LLM_BASE_URL, LLM_MODEL,
    CHROMA_PATH, COLLECTION_NAME, EMBED_MODEL, TOP_K, MAX_DISTANCE,
)

embedder      = SentenceTransformer(EMBED_MODEL)
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection    = chroma_client.get_or_create_collection(COLLECTION_NAME)

SYSTEM = """You answer questions about Juniper Networks switches using only the datasheet excerpts provided.

Rules:
- Use only the context given. If the answer isn't there, say so plainly.
- Never estimate or infer a spec that isn't stated.
- Quote exact figures (port counts, PoE budgets, throughput) as written.
- Be concise. A spec question deserves a spec answer, not a paragraph."""


def query(question):
    """Returns (answer, sources). Sources are datasheet paths, in rank order."""
    question_embedding = embedder.encode(question).tolist()

    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=TOP_K,
        include=["documents", "metadatas", "distances"],
    )

    docs      = results["documents"][0]
    metas     = results["metadatas"][0]
    distances = results["distances"][0]

    # Drop anything past the relevance cutoff, but always keep the best hit
    # so a valid question never arrives at the model with empty context.
    kept = [
        (d, m) for d, m, dist in zip(docs, metas, distances) if dist <= MAX_DISTANCE
    ] or list(zip(docs[:1], metas[:1]))

    context = "\n\n---\n\n".join(d for d, _ in kept)
    sources = [m["source"] for _, m in kept]

    answer = ask_llm(f"Context:\n{context}\n\nQuestion: {question}")
    return answer, sources


def ask_llm(user_content):
    if not LLM_API_KEY:
        return "LLM_API_KEY is not set. Export it and restart the app."

    res = requests.post(
        f"{LLM_BASE_URL}/chat/completions",
        headers={
            "content-type": "application/json",
            "authorization": f"Bearer {LLM_API_KEY}",
        },
        json={
            "model": LLM_MODEL,
            "temperature": 0.1,
            "max_tokens": 800,
            "messages": [
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": user_content},
            ],
        },
        timeout=45,
    )

    if res.status_code != 200:
        return f"The model returned {res.status_code}: {res.text[:200]}"

    return res.json()["choices"][0]["message"]["content"].strip()


if __name__ == "__main__":
    q = input("Ask a question about Juniper switches: ")
    answer, sources = query(q)
    print(f"\n{answer}\n")
    print("Sources:", ", ".join(sources))
