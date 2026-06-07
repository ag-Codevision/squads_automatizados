import os
import requests
import replicate

# Script de teste para o modelo google/gemini-3.1-flash-tts no Replicate

model_name = "google/gemini-3.1-flash-tts"

# Texto de teste usando tags de expressão nativas do Gemini TTS
prompt_text = "[excitedly] Olá ouvintes! Sejam muito bem-vindos ao nosso podcast. [whispering] Este é um teste com a voz gerada pelo novíssimo modelo Gemini 3.1 Flash da Google."

# Prompt de estilo para orientar a entonação da IA
style_prompt = "A professional Brazilian Portuguese podcast host, speaking naturally, clearly and with good energy."

def run_test():
    api_token = os.environ.get("REPLICATE_API_TOKEN")
    if not api_token:
        print("\n[ERRO] Variável de ambiente REPLICATE_API_TOKEN não encontrada!")
        print("Antes de rodar, execute no seu terminal:")
        print('No CMD: set REPLICATE_API_TOKEN="sua_chave_aqui"')
        print('No PowerShell: $env:REPLICATE_API_TOKEN="sua_chave_aqui"')
        return

    try:
        print("Enviando requisição de áudio para o Google Gemini 3.1 Flash TTS no Replicate...")
        
        # Chama o modelo Gemini TTS
        # Nota: Usamos language_code como 'pt-BR'
        output = replicate.run(
            model_name,
            input={
                "text": prompt_text,
                "prompt": style_prompt,
                "language_code": "pt-BR",
                "voice": "Kore" # Usando uma voz de teste padrão (ex: Kore)
            }
        )
        
        # No Replicate o retorno do gemini-3.1-flash-tts pode ser uma URL ou uma string/objeto contendo a URL
        output_url = getattr(output, "url", None) or str(output)
        print(f"Áudio gerado com sucesso! URL do arquivo: {output_url}")
        
        # Baixa o áudio gerado localmente
        print("Fazendo o download do áudio gerado para a pasta local...")
        response = requests.get(output_url)
        if response.status_code == 200:
            output_path = "teste_gemini_tts.wav"
            with open(output_path, "wb") as f:
                f.write(response.content)
            print(f"\n[SUCESSO] O arquivo de áudio foi baixado e salvo em: {os.path.abspath(output_path)}")
        else:
            print(f"[ERRO] Falha ao baixar o áudio da URL gerada. Status: {response.status_code}")

    except Exception as e:
        print(f"\n[ERRO] Ocorreu uma falha ao executar a API: {e}")

if __name__ == "__main__":
    run_test()
