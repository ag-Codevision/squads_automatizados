# Squad Memory: youtube-black-screen

## Estilo de Escrita
- Títulos e descrições otimizados para SEO e focados em benefícios para a saúde (sono, ansiedade, zumbido).

## Design Visual
- Priorizar paisagens calmas da natureza, janelas chuvosas, cabanas e cidades cyberpunk chuvosas, garantindo ausência de pessoas ou tráfego urbano que distraia.
- Aplicar fade-out gradual do vídeo até o preto total após 30 segundos de vídeo.

## Estrutura de Conteúdo
- Seguir a biblioteca de mídias e fórmulas contidas em [biblioteca-midias.md](file:///f:/openSquad/squads/youtube-black-screen/pipeline/data/biblioteca-midias.md).
- Vídeos longos de relaxamento devem ter duração padrão de 8 a 10 horas.

## Proibições Explícitas
- Nunca marcar o vídeo como "Sim, é criado para crianças" (público infantil) no YouTube Studio.
- Nunca marcar "Sim" na pergunta sobre Utilização de IA (conteúdo sintético/realista gerado por IA) no YouTube Studio.
- Nunca utilizar clipes que possuam pessoas, rostos ou tráfego de pedestres ativo.

## Técnico (específico do squad)
- No upload automatizado do YouTube Studio, a configuração de público-alvo (COPPA) deve ser definida estritamente como **"Não, não é criado para crianças"** (seletor `tp-yt-paper-radio-button[name="VIDEO_MADE_FOR_KIDS_FALSE"]`).
- No upload do YouTube Studio, a pergunta sobre "Utilização de IA" (conteúdo alterado/sintético) deve ser respondida estritamente como **"Não"** (seletor `tp-yt-paper-radio-button[name="ALTERED_CONTENT_FALSE"]`).
- Utilizar renderização unificada com geração processual de áudio (brown/pink noise) no FFMPEG para evitar arquivos temporários gigantes.

