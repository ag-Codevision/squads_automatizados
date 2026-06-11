import os
import requests
import sys
import json
from dotenv import load_dotenv

load_dotenv()

def gerar_texto_ia(prompt, system_instruction=None):
    """Usa a API do Gemini com a chave fornecida. Se falhar, faz fallback em cascata (OmniRoute, Pollinations)."""
    if system_instruction is None:
        system_instruction = (
            "Você é um especialista em SEO do YouTube e criador de conteúdo do canal 'Black Sleep Screen'. "
            "Escreva estritamente em português do Brasil (pt-BR). Responda APENAS com o texto solicitado, "
            "sem introduções, observações ou explicações extras."
        )
        
    api_key_gemini = os.environ.get("GEMINI_API_KEY")
    if api_key_gemini:
        print("[IA] Consultando Cérebro via API Direta do Gemini...")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key_gemini}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ],
            "systemInstruction": {
                "parts": [
                    {"text": system_instruction}
                ]
            },
            "generationConfig": {
                "temperature": 0.7
            }
        }
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=45)
            response.raise_for_status()
            data = response.json()
            texto = data['candidates'][0]['content']['parts'][0]['text']
            print("[SUCESSO] Resposta via API do Gemini obtida!")
            return texto
        except Exception as e:
            print(f"[ERRO] Falha na API do Gemini: {e}")

    # Fallback 1: OmniRoute
    model_name = os.environ.get("OMNI_MODEL") or "g"
    if model_name != "pollinations":
        print("[IA] [FALLBACK] Consultando via OmniRoute...")
        url = os.environ.get("OMNI_URL") or "http://srv1268090.hstgr.cloud:20128/v1/chat/completions"
        api_key = os.environ.get("OMNI_API_KEY") or "sk-c50ed36fd3f69f11-057eaa-08ce3407"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            texto = data['choices'][0]['message']['content']
            if texto:
                return texto
        except Exception as e:
            print(f"[ERRO] Erro na IA OmniRoute: {e}")

    # Fallback 2: Pollinations
    print("[IA] [FALLBACK] Tentando via Pollinations...")
    url_fallback = "https://text.pollinations.ai/"
    payload_fallback = {
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt}
        ],
        "model": "openai"
    }
    headers_fallback = {"Content-Type": "application/json"}
    try:
        response_fallback = requests.post(url_fallback, headers=headers_fallback, json=payload_fallback, timeout=20)
        response_fallback.raise_for_status()
        return response_fallback.text
    except Exception as e_fallback:
        print(f"[ERRO] Falha ao consultar Pollinations: {e_fallback}")

    print("[ERRO CRÍTICO] Nenhuma API de IA respondeu. Abortando.")
    sys.exit(1)

def main():
    tema = sys.argv[1] if len(sys.argv) > 1 else "Som de chuva para relaxar"
    run_dir = sys.argv[2] if len(sys.argv) > 2 else "output"
    
    print(f"=== INICIANDO GERAÇÃO DE METADADOS ===")
    print(f"Tema recebido da fila: {tema}")
    
    tema_limpo = tema.strip().lower()
    if tema_limpo in ["aleatório (notícias do dia)", "aleatorio (noticias do dia)", "aleatório", "aleatorio", "som de chuva para relaxar", ""]:
        print("[ROTEIRO] Escolhendo tema de sono aleatório...")
        prompt_escolha = (
            "Escolha um cenário ou tipo de som de chuva/tempestade muito aconchegante para um vídeo de sono do YouTube "
            "(exemplo: 'Chuva forte na cabana na floresta', 'Chuva na janela do sótão', 'Tempestade com trovões distantes no lago'). "
            "Responda estritamente apenas com o nome curto e claro desse cenário, sem introduções ou observações."
        )
        tema_ia = gerar_texto_ia(prompt_escolha)
        if tema_ia and tema_ia.strip():
            tema = tema_ia.strip()
            print(f"[ROTEIRO] Tema escolhido pela IA: {tema}")

    os.makedirs(run_dir, exist_ok=True)
    
    prompt_metadata = f"""
    Crie o roteiro e os metadados de SEO para um vídeo longo (10 horas) de tela preta com som de chuva relaxante baseado no cenário '{tema}'.
    
    Você deve responder exatamente no formato Markdown abaixo, mantendo as tags 'titulo', 'thumbnail_concept', 'estrutura_video', 'descricao' e 'tags' formatadas em blocos de código YAML válidos.
    
    DIRETRIZES DA DESCRIÇÃO (OBRIGATÓRIO):
    - A descrição deve conter pelo menos 250 palavras.
    - Deve descrever de forma profissional a originalidade do áudio (ex: gravado em floresta nativa com gravador Zoom H6, editado em estúdio eliminando picos sonoros bruscos de trovão para não acordar o espectador).
    - Deve explicar o benefício da tela preta (fade visual aos 3 minutos para escuridão total, removendo emissão de luz azul e economizando bateria, enquanto o áudio continua tocando em volume estável até o fim de 10 horas).
    - Mencione explicitamente que os anúncios mid-rolls foram desativados para não interromper o sono.
    
    DIRETRIZES DO TÍTULO:
    - Máximo de 85 caracteres. Exemplo: 'Chuva Forte na Janela com Trovões Distantes para Dormir | 10 Horas Tela Preta'
    
    FORMATO DE RETORNO OBRIGATÓRIO (Mantenha o markdown exatamente assim):
    
    # Roteiro e Metadados — Vídeo de Sono
    
    ## Metadados do Vídeo Longo
    
    ```yaml
    titulo: "[Título do vídeo aqui]"
    thumbnail_concept: "[Conceito visual para a miniatura]"
    estrutura_video:
      abertura: "0:00 - 3:00 | Vídeo dinâmico em 4K mostrando o cenário do tema."
      transicao: "3:00 - 5:00 | Fade out gradual e linear da imagem para o preto absoluto."
      tela_preta: "5:00 - 9:59:00 | Tela preta pura com som de chuva/trovoadas."
      encoding: "9:59:00 - 10:00:00 | Fade-out de áudio de 1 minuto até o silêncio."
    descricao: |
      [Sua descrição longa e detalhada aqui. Mantenha os recuos corretos para o bloco YAML literal]
    tags: "[Palavras-chave separadas por vírgula]"
    ```
    """
    
    metadata = gerar_texto_ia(prompt_metadata)
    
    file_path = os.path.join(run_dir, 'roteiro-e-metadados.md')
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(metadata)
        
    print(f"[SUCESSO] Roteiro e metadados salvos em: {file_path}")

if __name__ == "__main__":
    main()
