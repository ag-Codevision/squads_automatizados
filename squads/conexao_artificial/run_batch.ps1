$ErrorActionPreference = "Stop"

for ($i = 1; $i -le 4; $i++) {
    Write-Host "=============================================="
    Write-Host " INICIANDO GERACAO DO EPISODIO $i"
    Write-Host "=============================================="

    Copy-Item "output\ep$($i)_news.md" -Destination "output\noticias_do_dia.md" -Force
    Copy-Item "output\ep$($i)_roteiro.txt" -Destination "output\roteiro_episodio.txt" -Force
    Copy-Item "output\ep$($i)_meta.txt" -Destination "output\youtube_metadata.txt" -Force

    Write-Host "-> Gerando Audio..."
    py scripts\gerar_audio.py

    Write-Host "-> Gerando Video..."
    py scripts\gerar_video.py

    Write-Host "-> Fazendo Upload para o YouTube..."
    py -3.12 scripts\upload_youtube.py

    Write-Host "-> Organizando Pastas..."
    py scripts\organizar_episodio.py

    Write-Host "-> Atualizando RSS do Spotify..."
    py scripts\gerar_rss_spotify.py

    Write-Host "-> Fazendo Upload para o GitHub Pages..."
    py scripts\upload_github.py

    Write-Host "=============================================="
    Write-Host " EPISODIO $i CONCLUIDO COM SUCESSO!"
    Write-Host " Aguardando 1 minuto para evitar limites de API..."
    Write-Host "=============================================="
    Start-Sleep -Seconds 60
}

Write-Host "TODOS OS 4 EPISODIOS FORAM GERADOS E PUBLICADOS!"
