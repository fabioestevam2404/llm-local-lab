# llm-local-lab

Estudo prático de LLMs locais: rodando modelos open-source com Ollama, chamando pela API em Python e medindo desempenho na minha própria máquina.

## Objetivo

Aprender como um modelo de linguagem roda fora de uma API na nuvem. Quero entender na prática:

- o que limita o tamanho do modelo que cabe numa máquina comum (memória, não só processador)
- o que é quantização e o quanto ela afeta tamanho, velocidade e qualidade
- como chamar um modelo local por código, do mesmo jeito que se chama uma API
- quantos tokens por segundo um notebook sem GPU dedicada consegue entregar

Por enquanto o escopo é só rodar modelos prontos. Fine-tuning e RAG ficam para depois, se este laboratório render material.

## Ambiente

| Item | Valor |
|---|---|
| Máquina | Dell Inspiron 15 3520 |
| Processador | Intel Core i5-1235U (12ª geração), 1,30 GHz |
| RAM | 8 GB (7,69 GB utilizáveis) |
| Vídeo | Intel UHD Graphics (integrado, sem GPU dedicada) |
| Armazenamento | SSD de 477 GB, cerca de 179 GB livres |
| Sistema | Windows 11, 64 bits |
| Ollama | _preencher a versão (`ollama --version`)_ |

**O que isso significa:** sem GPU dedicada, a inferência roda na CPU e usa a RAM do sistema. Com 8 GB, o Windows e os programas abertos já ocupam boa parte, então sobram uns 3 a 4 GB para o modelo. Por isso o foco é em modelos de 1B a 3B parâmetros quantizados. Modelos de 7B a 8B, que ocupam cerca de 5 GB em 4 bits, devem passar do limite e ficar muito lentos. Vou testar um deles só para registrar onde a máquina quebra.

## Como rodar

### 1. Instalar o Ollama

Baixe o instalador para Windows em [ollama.com](https://ollama.com) e execute. Depois, no PowerShell:

```powershell
ollama --version
```

### 2. Baixar e conversar com um modelo

```powershell
ollama pull llama3.2:1b
ollama run llama3.2:1b
```

Os nomes e tamanhos disponíveis mudam com frequência. Confira a lista atual em [ollama.com/library](https://ollama.com/library) e escolha pelo tamanho em disco.

Para sair do chat, digite `/bye`.

### 3. Chamar pela API em Python

O Ollama sobe um servidor local na porta 11434. Crie o ambiente e instale a dependência:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install requests
```

Salve como `ask.py`:

```python
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
```

Execute:

```powershell
python ask.py llama3.2:1b "Qual a diferença entre ETL e ELT?"
```

### 4. Conferir se está rodando na CPU ou na GPU

Com o modelo carregado, em outro terminal:

```powershell
ollama ps
```

A coluna `PROCESSOR` mostra onde o modelo está. Nesta máquina o esperado é `100% CPU`.

Para acompanhar o consumo de memória, abra o Gerenciador de Tarefas (Ctrl+Shift+Esc) e olhe a aba Desempenho enquanto o modelo responde.

## Experimentos

Mesmo prompt em todos os testes, três execuções por modelo, anotando a média. A primeira execução costuma ser mais lenta porque o modelo ainda está carregando, então ela fica de fora da média.

| Modelo | Parâmetros | Tamanho em disco | Tokens/s | RAM em uso | Observações |
|---|---|---|---|---|---|
| llama3.2:1b | 1B | _medir_ | _medir_ | _medir_ | |
| llama3.2:3b | 3B | _medir_ | _medir_ | _medir_ | |
| _modelo de ~1,5B de outra família_ | | _medir_ | _medir_ | _medir_ | |
| _modelo de 7B/8B (teste de limite)_ | | _medir_ | _medir_ | _medir_ | |

Prompt padrão usado: `Explique o que é um Lakehouse em 3 frases.`

## Aprendizados

_Preencher conforme os testes avançam. Algumas perguntas para guiar:_

- A partir de que tamanho a máquina começa a usar o disco como memória (swap) e a velocidade despenca?
- Dá para usar o modelo de 1B para algo útil, como classificar texto ou resumir?
- A qualidade das respostas em português muda de um modelo para outro?
- Fechar o navegador e outros programas muda o resultado de forma visível?

## Próximos passos

- [ ] Medir os modelos da tabela acima
- [ ] Testar o mesmo modelo em duas quantizações diferentes e comparar
- [ ] Rodar um modelo por `llama.cpp` direto, sem Ollama, e comparar a velocidade
- [ ] Montar um RAG simples com PostgreSQL e pgvector

## Referências

- [Ollama](https://ollama.com) e a [API do Ollama](https://github.com/ollama/ollama/blob/main/docs/api.md)
- [llama.cpp](https://github.com/ggml-org/llama.cpp)
- [nanoGPT](https://github.com/karpathy/nanoGPT), para entender como o treino funciona por dentro
