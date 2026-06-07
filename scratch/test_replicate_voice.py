import os
import requests
import replicate

# IMPORTANTE: Para que este script funcione, você precisa configurar seu token do Replicate.
# No terminal do Windows (CMD): set REPLICATE_API_TOKEN=sua_chave_aqui
# No PowerShell: $env:REPLICATE_API_TOKEN="sua_chave_aqui"

# Usamos o modelo XTTS-v2 que é o padrão de ouro open-source para clonagem de voz e suporta Português (pt)
model_name = "lucataco/xtts-v2:684bc3855b37866c0c65add2ff39c78f3dea3f4ff103a436465326e0f438d55e"

# Texto de teste no estilo podcast
prompt_text = "Fala galera do podcast! Este é um teste oficial de clonagem de voz rodando diretamente pela API do Replicate. O que vocês acharam do sotaque brasileiro?"

# Áudio de referência padrão para o teste de clonagem (substitua por um link de áudio seu de 5-10s se quiser)
# Nota: O Replicate exige que o áudio de referência seja enviado como uma URL pública (ex: hospedada no Dropbox, GitHub ou S3)
default_ref_wav = "https://raw.githubusercontent.com/coqui-ai/TTS/main/tests/data/ljspeech/wavs/LJ001-0001.wav"

def run_test():
    api_token = os.environ.get("REPLICATE_API_TOKEN")
    if not api_token:
        print("\n[ERRO] Variável de ambiente REPLICATE_API_TOKEN não encontrada!")
        print("Antes de rodar, execute no seu terminal:")
        print('No CMD: set REPLICATE_API_TOKEN="sua_chave_aqui"')
        print('No PowerShell: $env:REPLICATE_API_TOKEN="sua_chave_aqui"')
        return

    try:
        print("Enviando requisição de áudio para os servidores do Replicate...")
        
        # Executa o modelo de clonagem XTTS-v2
        output_url = replicate.run(
            model_name,
            input={
                "text": prompt_text,
                "language": "pt",
                "speaker": default_ref_wav
            }
        )
        
        print(f"Áudio gerado com sucesso! URL do arquivo: {output_url}")
        
        # Baixa o áudio gerado localmente
        print("Fazendo o download do áudio gerado para a pasta local...")
        response = requests.get(output_url)
        if response.status_code == 200:
            output_path = "teste_voz_podcast.wav"
            with open(output_path, "wb") as f:
                f.write(response.content)
            print(f"\n[SUCESSO] O arquivo de áudio foi baixado e salvo em: {os.path.abspath(output_path)}")
        else:
            print(f"[ERRO] Falha ao baixar o áudio da URL gerada. Status: {response.status_code}")

    except Exception as e:
        print(f"\n[ERRO] Ocorreu uma falha ao executar a API: {e}")

if __name__ == "__main__":
    run_test()
