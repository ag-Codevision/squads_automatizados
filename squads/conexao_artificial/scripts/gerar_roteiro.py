import os
import requests
import sys
from dotenv import load_dotenv

load_dotenv()

def gerar_texto_ia(prompt, system_instruction=None):
    """Usa a API do Gemini (Google) com a chave fornecida. Se falhar, faz fallback em cascata."""
    if system_instruction is None:
        system_instruction = "Você é o roteirista principal do podcast 'Conexão Artificial'. Escreva estritamente em português do Brasil (pt-BR). O tom é de bate-papo de rádio profissional de tecnologia. Responda APENAS com o texto solicitado em português do Brasil, sem introduções ou observações."
        
    api_key_gemini = os.environ.get("GEMINI_API_KEY")
    if api_key_gemini:
        print("[IA] Consultando Cérebro da Inteligência Artificial via API Direta do Gemini...")
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
            print("[SUCESSO] Resposta via API do Gemini obtida com sucesso!")
            return texto
        except Exception as e:
            print(f"[ERRO] Falha ao conectar na API Direta do Gemini: {e}")

    # Fallback 1: OmniRoute
    model_name = os.environ.get("OMNI_MODEL")
    if not model_name or model_name.strip() == "":
        model_name = "g"
        
    if model_name != "pollinations":
        print("[IA] [FALLBACK] Consultando Cérebro da Inteligência Artificial via OmniRoute...")
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
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data['choices'][0]['message']['content']
        except Exception as e:
            print(f"[ERRO] Erro ao conectar na IA OmniRoute ({model_name}): {e}")

    # Fallback 2: Pollinations
    print("[IA] [FALLBACK] Tentando obter resposta via Pollinations (Gratuito)...")
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
        print("[SUCESSO] Resposta via Pollinations obtida com sucesso!")
        return response_fallback.text
    except Exception as e_fallback:
        print(f"[ERRO] Falha ao consultar Pollinations: {e_fallback}")

    # Todos os provedores falharam
    print("[ERRO CRÍTICO] Nenhuma das APIs de IA respondeu (Gemini, OmniRoute, Pollinations). Abortando.")
    sys.exit(1)

def main():
    # O orquestrador vai passar o tema pela linha de comando
    tema = sys.argv[1] if len(sys.argv) > 1 else "Inovações surpreendentes da Inteligência Artificial"
    
    print(f"=== INICIANDO GERAÇÃO DE ROTEIRO ===")
    print(f"Tema recebido da fila: {tema}")
    
    # Se for um tema aleatório ou genérico, a IA escolhe uma notícia quente/relevante da semana sobre IA/Tecnologia
    tema_limpo = tema.strip().lower()
    if tema_limpo in ["aleatório (notícias do dia)", "aleatorio (noticias do dia)", "aleatório", "aleatorio", "notícias do dia", "noticias do dia", ""]:
        print("[ROTEIRO] Tema aleatório detectado. Consultando Gemini para escolher um assunto único quente de IA/Tecnologia da semana...")
        prompt_escolha = (
            "Escolha um único assunto ou notícia quente, recente e impactante da semana no mundo da tecnologia e da Inteligência Artificial "
            "(preferencialmente IA, como lançamentos de novos modelos, avanços de hardware, robótica ou o impacto de IA na sociedade). "
            "Responda estritamente apenas com o nome curto e claro desse tema (exemplo: 'China Cria Sol Artificial: Transformando o Mundo!' ou 'Lançamento do Modelo Gemini 1.5 Pro' ou 'Avanços nos chips de IA da NVIDIA'), sem nenhuma introdução, aspas, ponto final ou qualquer formatação extra."
        )
        tema_ia = gerar_texto_ia(prompt_escolha)
        if tema_ia and tema_ia.strip():
            tema = tema_ia.strip()
            print(f"[ROTEIRO] Novo tema focado escolhido pela IA: {tema}")

    # Cria a pasta de output se não existir
    os.makedirs('output', exist_ok=True)
    
    # 1. Gerar Informações do Tema (Pauta Única)
    prompt_noticias = (
        f"Crie 3 seções de informações/notícias tecnológicas muito detalhadas e aprofundadas (com pelo menos 3 parágrafos explicativos para cada uma) "
        f"especificamente e exclusivamente sobre o tema central '{tema}'. "
        f"Divida a explicação do tema em 3 aspectos importantes (ex: Funcionamento Técnico/Notícia, Aplicações Práticas, e Impactos/Desafios Futuros). "
        f"Escreva em formato Markdown com números (1., 2., 3.), de forma profunda, em português do Brasil (pt-BR), soando como um portal de notícias de tecnologia do futuro."
    )
    noticias = gerar_texto_ia(prompt_noticias)
    
    with open(os.path.join('output', 'noticias_do_dia.md'), 'w', encoding='utf-8') as f:
        f.write("# Notícias do Dia\n\n" + noticias)
    print("Notícias geradas.")

    # Carrega as diretrizes do redator do arquivo _memory/prompt_redator.md
    prompt_redator_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "_memory", "prompt_redator.md")
    if os.path.exists(prompt_redator_path):
        with open(prompt_redator_path, "r", encoding="utf-8") as pf:
            diretrizes_redator = pf.read()
    else:
        diretrizes_redator = "Escreva um roteiro de podcast longo para Tom e Bia."

    prompt_roteiro = f"""
    Escreva o roteiro completo do episódio de hoje do podcast baseado nas notícias detalhadas abaixo e seguindo rigorosamente as diretrizes de formato, persona e duração estabelecidas.
    
    Tema de hoje: {tema}
    
    Notícias detalhadas para basear o episódio:
    {noticias}
    
    DIRETRIZES DE PERSONA, FORMATO E DIÁLOGO (REGRAS OBRIGATÓRIAS):
    - O roteiro DEVE ser escrito no formato de DIÁLOGO dinâmico e natural alternando estritamente entre os apresentadores Tom (homem) e Bia (mulher).
    - O Tom é mais sério, calmo, ponderado e analítico, trazendo os fatos de forma jornalística, clara e profissional.
    - A Bia é curiosa, empática, inspiradora e um pouco mais viva e animada, ajudando a simplificar os conceitos técnicos com leveza.
    - Cada fala individual DEVE começar exatamente com 'Tom: ' ou 'Bia: ' (sem aspas, sem asteriscos, sem colchetes no nome do apresentador).
    - NÃO use "Locutor:", "Narrador:", "Apresentador:", "Entrevistado:" ou qualquer outro nome. Use APENAS "Tom: " e "Bia: " no início das falas.
    - NÃO inclua no roteiro nenhuma descrição de efeitos sonoros, músicas de fundo ou transições de cena (ex: remova completamente termos como '[Intro música]', '[Música de transição]', '[Efeitos]', etc.). O roteiro deve conter apenas o diálogo dos personagens.
    - Comece com Tom e Bia se apresentando de forma natural e falando o nome do podcast ("Conexão artificial").
    - NÃO mencione a fonte de onde as notícias foram retiradas. Apenas as comente e debata no diálogo de forma orgânica.
    - Este NÃO é o primeiro episódio do podcast. Aja como se o programa já existisse há muito tempo.
    - O roteiro deve ser LONGO e aprofundado (de 1200 a 2000 palavras no total), contendo no mínimo 18 a 25 falas (interações) de cada apresentador para garantir que o áudio atinja a duração desejada (mínimo de 6 minutos e máximo de 15 minutos).
    - Use marcações de sentimento oficiais do Gemini TTS no início das falas (ex: [excitedly], [laughter], [gasp], [whispering], [sighs], [sadly]).
    - Ao finalizar o episódio, após debater todas as notícias, faça uma breve recapitulação resumida das notícias discutidas e, em seguida, traga uma reflexão com abordagem filosófica profunda sobre os impactos futuros dessas tecnologias na nossa sociedade e existência para fazer o público pensar. Logo após essa reflexão, faça o encerramento padrão pedindo para compartilhar nas redes sociais, agradeça a audiência e despeça-se com "Até a próxima!".
    """
    
    system_instruction_roteiro = f"""
    Você é o roteirista do podcast "Conexão artificial".
    Você DEVE escrever o roteiro no formato de DIÁLOGO dinâmico e natural alternando estritamente entre os apresentadores Tom e Bia.
    
    REGRAS DE FORMATO CRÍTICAS:
    - O roteiro DEVE ser estruturado estritamente com falas iniciando por "Tom: " ou "Bia: " (sem aspas, sem asteriscos, sem colchetes no nome do apresentador).
    - Exemplo de formato de linha: Tom: [excitedly] Fala do Tom aqui.
    - Exemplo de formato de linha: Bia: [laughter] Fala da Bia aqui.
    - NÃO use "Locutor:", "Apresentador:", "Narrador:" ou qualquer outro nome que não seja "Tom" ou "Bia".
    - NÃO inclua descrições de efeitos sonoros, músicas de fundo ou transições como '[Intro música]' ou '[Música de transição]'. O texto deve conter apenas os diálogos dos personagens com suas tags de sentimento.
    
    Diretrizes de Persona e Formato (Siga à risca):
    {diretrizes_redator}
    """
    roteiro = gerar_texto_ia(prompt_roteiro, system_instruction=system_instruction_roteiro)
    
    with open(os.path.join('output', 'roteiro_episodio.txt'), 'w', encoding='utf-8') as f:
        f.write(roteiro)
    print("Roteiro gerado.")
    
    # 3. Gerar Metadados (YouTube/Spotify)
    prompt_meta = f"Crie um Título clickbait (mas sem exagero, máximo 60 caracteres) para o YouTube e uma Descrição de 3 linhas para o episódio de podcast sobre '{tema}'. Escreva em português do Brasil (pt-BR). Formato OBRIGATÓRIO:\nTítulo: [Seu Titulo Aqui]\nDescrição:\n[Sua Descricao Aqui]"
    meta = gerar_texto_ia(prompt_meta)
    
    with open(os.path.join('output', 'youtube_metadata.txt'), 'w', encoding='utf-8') as f:
        f.write(meta)
    print("Metadados gerados.")
    
    print("Cérebro da Inteligência Artificial finalizou sua etapa!")

if __name__ == "__main__":
    main()
