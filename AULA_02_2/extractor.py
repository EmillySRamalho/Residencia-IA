import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
modelo = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

if not api_key:
    raise ValueError(
        "A variável OPENAI_API_KEY não foi encontrada! "
        "Verifique se o arquivo .env existe e possui a chave configurada."
    )

client = OpenAI(api_key=api_key)

os.makedirs("output", exist_ok=True)


def extrair_metadados(caminho_md):
    """Lê um arquivo Markdown e extrai título, autores, ano, métodos, métricas e limitações em formato JSON."""
    
    with open(caminho_md, "r", encoding="utf-8") as arquivo:
        conteudo = arquivo.read()

    resposta = client.chat.completions.create(
        model=modelo,
        messages=[
            {
                "role": "system",
                "content": (
                    "Extraia o título, autores, ano, métodos/técnicas utilizadas, métricas/resultados principais e limitações do artigo. "
                    "Caso o texto não mencione explicitamente algum item, insira uma lista vazia ou descrição breve da ausência. "
                    "Responda estritamente em JSON."
                )
            },
            {
                "role": "user",
                "content": conteudo
            }
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "paper_metadata",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "titulo": {
                            "type": "string"
                        },
                        "autores": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            }
                        },
                        "ano": {
                            "type": "integer"
                        },
                        "metodos": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "Metodologias, modelos, arquiteturas ou algoritmos utilizados na pesquisa."
                        },
                        "metricas": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "Métricas, resultados numéricos ou dados de desempenho citados no artigo."
                        },
                        "limitacoes": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "Limitações, trabalhos futuros ou restrições apontadas pelos autores."
                        }
                    },
                    "required": [
                        "titulo",
                        "autores",
                        "ano",
                        "metodos",
                        "metricas",
                        "limitacoes"
                    ],
                    "additionalProperties": False
                }
            }
        }
    )

    metadados = json.loads(resposta.choices[0].message.content)

    nome_base = os.path.splitext(os.path.basename(caminho_md))[0]
    caminho_saida = os.path.join("output", f"output_{nome_base}.json")

    with open(caminho_saida, "w", encoding="utf-8") as arquivo:
        json.dump(
            metadados,
            arquivo,
            ensure_ascii=False,
            indent=4
        )

    print(f"✅ Arquivo salvo em: {caminho_saida}")


if __name__ == "__main__":
    pasta_markdowns = "Markdowns"

    if os.path.exists(pasta_markdowns):
        for arquivo in os.listdir(pasta_markdowns):
            if arquivo.endswith(".md"):
                caminho = os.path.join(pasta_markdowns, arquivo)
                extrair_metadados(caminho)
    else:
        print(f"⚠️ A pasta '{pasta_markdowns}' não foi encontrada no diretório atual.")
