const fs = require('fs');
const path = require('path');
const https = require('https');

(async () => {
  // Caminho da lista de vídeos curados
  const listPath = path.resolve(__dirname, '../../assets/videos_chuva.json');
  
  // Caminho de saída (passado por argumento ou fallback para pasta temporária de teste)
  const targetDir = process.argv[2] ? path.resolve(process.argv[2]) : path.resolve(__dirname, '../../output/v1');
  const targetPath = path.join(targetDir, 'chuva_fundo.mp4');

  if (!fs.existsSync(targetDir)) {
    fs.mkdirSync(targetDir, { recursive: true });
  }

  console.log(`Lendo lista de vídeos de: ${listPath}`);
  let videos;
  try {
    videos = JSON.parse(fs.readFileSync(listPath, 'utf8'));
  } catch (err) {
    console.error('Erro ao ler a lista de vídeos curados:', err.message);
    process.exit(1);
  }

  if (!Array.isArray(videos) || videos.length === 0) {
    console.error('A lista de vídeos está vazia ou é inválida.');
    process.exit(1);
  }

  // Tentar baixar os vídeos em ordem aleatória até encontrar um funcional
  const shuffledVideos = [...videos].sort(() => Math.random() - 0.5);
  let success = false;

  for (const video of shuffledVideos) {
    console.log(`Tentando baixar o vídeo: "${video.titulo}" (ID: ${video.id})`);
    console.log(`URL de download: ${video.url}`);

    try {
      await new Promise((resolve, reject) => {
        const fileStream = fs.createWriteStream(targetPath);
        
        const requestOptions = {
          headers: {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
            'Referer': 'https://mixkit.co/'
          },
          timeout: 30000 // 30 segundos de timeout
        };
        
        const request = https.get(video.url, requestOptions, (res) => {
          // Lidar com redirecionamentos HTTP
          if (res.statusCode === 301 || res.statusCode === 302) {
            console.log(`Redirecionando download para: ${res.headers.location}`);
            const redirectOptions = {
              headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
                'Referer': 'https://mixkit.co/'
              },
              timeout: 30000
            };
            https.get(res.headers.location, redirectOptions, (redirectRes) => {
              if (redirectRes.statusCode !== 200) {
                reject(new Error(`Falha no redirecionamento. Status: ${redirectRes.statusCode}`));
                return;
              }
              redirectRes.pipe(fileStream);
              fileStream.on('finish', () => {
                fileStream.close();
                resolve();
              });
            }).on('error', reject);
            return;
          }

          if (res.statusCode !== 200) {
            reject(new Error(`Falha ao baixar. Status: ${res.statusCode}`));
            return;
          }

          res.pipe(fileStream);
          fileStream.on('finish', () => {
            fileStream.close();
            resolve();
          });
        });

        request.on('error', reject);
        request.on('timeout', () => {
          request.destroy();
          reject(new Error('Timeout de requisição excedido'));
        });
      });

      console.log(`Download concluído com sucesso: ${targetPath}`);
      success = true;
      break;
    } catch (downloadErr) {
      console.warn(`Aviso: Falha ao baixar o vídeo (ID: ${video.id}). Erro: ${downloadErr.message}`);
      // Remove o arquivo parcialmente baixado, se houver
      if (fs.existsSync(targetPath)) {
        try {
          fs.unlinkSync(targetPath);
        } catch (e) {}
      }
    }
  }

  if (!success) {
    console.error('Erro crítico: Nenhum dos vídeos da lista pôde ser baixado.');
    process.exit(1);
  }

  console.log('Operação de download concluída com sucesso!');
})();
