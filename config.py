import os
import glob

# --- LLM -------------------------------------------------------------------
# Any OpenAI-compatible provider. Defaults to Groq's free tier.
# Switch providers by setting LLM_BASE_URL and LLM_MODEL — no code change.
LLM_API_KEY  = os.environ.get("LLM_API_KEY", "")
LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "https://api.groq.com/openai/v1")
LLM_MODEL    = os.environ.get("LLM_MODEL", "openai/gpt-oss-20b")

# --- Retrieval -------------------------------------------------------------
EMBED_MODEL = "all-MiniLM-L6-v2"   # local, no API key, no cost

CHROMA_PATH     = "./chroma_db"
COLLECTION_NAME = "juniper_switches"

# Datasheets are dense spec tables, so smaller chunks retrieve more precisely
# than large ones — a 600-word chunk sweeps in three unrelated sections.
# Changing these only takes effect after re-running ingest.py.
CHUNK_SIZE    = 250
CHUNK_OVERLAP = 50

# Top-k of 10 sent ~8k tokens of context per question. The answer is almost
# always in the first few chunks; anything past that is padding you pay for.
TOP_K = 4

# Chroma returns exactly TOP_K results whether or not they're relevant.
# Cosine distance — lower is closer. Chunks past this are dropped, so a
# narrow question costs a fraction of a broad one.
MAX_DISTANCE = 1.2

DATASHEET_PATHS = glob.glob("./datasheets/**/*.pdf")
