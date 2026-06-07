import os
import replicate
from dotenv import load_dotenv

# Carrega o .env
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "squads", "conexao_artificial", ".env")
load_dotenv(dotenv_path)

api_token = os.environ.get("REPLICATE_API_TOKEN")
if not api_token:
    print("REPLICATE_API_TOKEN nao encontrada no .env!")
else:
    print(f"Token do Replicate encontrado: {api_token[:8]}...")
    try:
        print("Testando geração de texto com meta/meta-llama-3-70b-instruct no Replicate...")
        output = replicate.run(
            "meta/meta-llama-3-70b-instruct",
            input={
                "prompt": "Escreva apenas 'OK' se receber esta mensagem.",
                "max_tokens": 10
            }
        )
        # O retorno costuma ser um gerador de strings
        resultado = "".join(output)
        print(f"Resultado: {resultado}")
    except Exception as e:
        print(f"Erro ao testar Replicate Text: {e}")
