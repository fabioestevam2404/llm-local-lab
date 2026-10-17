import sys
import requests

MODELO = sys.argv[1] if len(sys.argv) > 1 else "llama3.2:1b"
PROMPT = sys.argv[2] if len(sys.argv) > 2 else "Explique o que é um Lakehouse em 3 frases."

resp = requests.post(
    "http://localhost:11434/api/generate",
    json={"model": MODELO, "prompt": PROMPT, "stream": False},
    timeout=300,
)
resp.raise_for_status()
dados = resp.json()

print(dados["response"])

# eval_duration vem em nanosegundos
tokens = dados["eval_count"]
segundos = dados["eval_duration"] / 1e9
print(f"\n{tokens} tokens em {segundos:.1f}s -> {tokens / segundos:.1f} tokens/s")
