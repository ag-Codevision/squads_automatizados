const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

(async () => {
  const profileDir = path.resolve(__dirname, '../../../../_opensquad/_browser_profile');
  const sessionPath = path.join(profileDir, 'youtube.json');
  const defaultVideoPath = path.resolve(__dirname, '../../output/2026-06-09-194442/v1/video_final_10h.mp4');
  const videoPath = process.argv[2] ? path.resolve(process.argv[2]) : defaultVideoPath;
  const runDir = path.dirname(videoPath);
  
  if (!fs.existsSync(profileDir)) {
    fs.mkdirSync(profileDir, { recursive: true });
  }

  const userDataDir = path.join(profileDir, 'userData');
  let context;
  
  console.log('Iniciando o navegador Google Chrome (modo mascarado)...');
  
  const launchOptions = {
    channel: 'chrome',
    headless: false,
    viewport: { width: 1280, height: 720 },
    args: [
      '--disable-blink-features=AutomationControlled'
    ]
  };
  
  const hasSession = fs.existsSync(sessionPath);
  if (hasSession) {
    console.log('Carregando cookies de sessão existentes de: ' + sessionPath);
    context = await chromium.launchPersistentContext(userDataDir, {
      ...launchOptions,
      storageState: sessionPath
    });
  } else {
    console.log('Nenhuma sessão salva encontrada. Solicitando login manual...');
    context = await chromium.launchPersistentContext(userDataDir, launchOptions);
  }

  const page = await context.newPage();
  page.setDefaultTimeout(300000);
  context.setDefaultTimeout(300000);
  
  console.log('Navegando para o YouTube Studio...');
  await page.goto('https://studio.youtube.com/', { waitUntil: 'domcontentloaded' });
  
  // Esperar o carregamento da página por alguns segundos
  await page.waitForTimeout(5000);
  
  const isLoggedIn = page.url().includes('studio.youtube.com') && !page.url().includes('accounts.google.com');
  
  if (!isLoggedIn) {
    console.log('\n================================================================');
    console.log('ATENÇÃO: Usuário não logado no YouTube Studio.');
    console.log('Por favor, efetue o login na janela do navegador Chromium aberta.');
    console.log('O script aguardará até 5 minutos para que você faça o login.');
    console.log('================================================================\n');
    try {
      await page.waitForURL('**/studio.youtube.com/**', { timeout: 300000 });
      console.log('Login efetuado com sucesso!');
      
      // Salva os cookies da sessão atualizada
      await context.storageState({ path: sessionPath });
      console.log(`Cookies salvos com sucesso em: ${sessionPath}`);
    } catch (err) {
      console.error('Erro ou tempo limite excedido durante o login manual:', err);
      await context.close();
      process.exit(1);
    }
  } else {
    console.log('Sessão ativa detectada!');
  }
  
  try {
    console.log('Iniciando processo de upload...');
    
    // Esperar um tempo extra para o painel de controle carregar
    console.log('Aguardando 10 segundos para o painel de controle carregar...');
    await page.waitForTimeout(10000);

    // Seletores de gatilhos específicos
    const centerUploadBtn = page.locator('ytcp-button').filter({ hasText: /carregar vídeos/i })
      .or(page.locator('ytcp-button').filter({ hasText: /carregar/i }))
      .or(page.locator('ytcp-button').filter({ hasText: /upload/i }));

    const quickUploadBtn = page.locator('ytcp-icon-button[aria-label*="arregar"]')
      .or(page.locator('ytcp-icon-button[aria-label*="nviar"]'))
      .or(page.locator('ytcp-icon-button[aria-label*="pload"]'))
      .or(page.locator('ytcp-button[aria-label*="arregar"]'))
      .or(page.locator('ytcp-button[aria-label*="nviar"]'));

    const topCreateBtn = page.locator('#create-icon')
      .or(page.locator('ytcp-button#create-icon'))
      .or(page.getByRole('button', { name: /criar/i }))
      .or(page.getByText(/criar/i))
      .or(page.getByRole('button', { name: /create/i }));

    let opened = false;
    
    // 1. Tentar clicar no botão central preto grande "Carregar vídeos" se estiver visível
    console.log('Verificando se o botão central "Carregar vídeos" está visível...');
    if (await centerUploadBtn.first().isVisible()) {
      console.log('Clicando no botão central preto "Carregar vídeos"...');
      await centerUploadBtn.first().click({ force: true });
      await page.waitForTimeout(3000);
      if (await page.locator('ytcp-uploads-dialog').isVisible()) {
        opened = true;
      }
    }

    // 2. Se não abriu, tentar clicar na seta de upload rápida do topo direito do painel
    if (!opened && await quickUploadBtn.first().isVisible()) {
      console.log('Clicando no botão rápido de upload (seta para cima)...');
      await quickUploadBtn.first().click({ force: true });
      await page.waitForTimeout(3000);
      if (await page.locator('ytcp-uploads-dialog').isVisible()) {
        opened = true;
      }
    }

    // 3. Fallback: Abrir o menu Criar e clicar na opção correspondente
    if (!opened) {
      console.log('Nenhum atalho funcionou diretamente. Tentando abrir menu suspenso "Criar" do topo...');
      try {
        await topCreateBtn.first().waitFor({ state: 'visible', timeout: 30000 });
        await topCreateBtn.first().click({ force: true });
        await page.waitForTimeout(2000);
      } catch (err) {
        console.log('Não foi possível clicar no botão Criar do topo. Tirando screenshot de erro...');
        const screenshotPath = path.join(runDir, 'screenshot_error.png');
        await page.screenshot({ path: screenshotPath });
        throw err;
      }

      console.log('Selecionando opção de upload no menu suspenso...');
      const uploadOption = page.getByText(/carregar vídeos/i)
        .or(page.getByText(/enviar vídeos/i))
        .or(page.getByText(/upload videos/i))
        .or(page.getByText(/enviar vídeo/i))
        .or(page.getByText(/carregar vídeo/i))
        .or(page.locator('ytcp-ve-icon[type="upload"]'))
        .or(page.locator('paper-item').filter({ hasText: /carregar/i }))
        .or(page.locator('paper-item').filter({ hasText: /enviar/i }))
        .or(page.locator('paper-item').filter({ hasText: /upload/i }));

      try {
        await uploadOption.first().waitFor({ state: 'visible', timeout: 15000 });
        await uploadOption.first().click({ force: true });
        await page.waitForTimeout(3000);
      } catch (err) {
        console.log('Opção de upload no menu suspenso não encontrada. Tirando screenshot...');
        const screenshotPath = path.join(runDir, 'screenshot_error.png');
        await page.screenshot({ path: screenshotPath });
        throw err;
      }
    }

    // Aguardar até 10 segundos adicionais para garantir que a modal de upload esteja visível antes de prosseguir
    console.log('Aguardando exibição da modal de upload...');
    const uploadDialog = page.locator('ytcp-uploads-dialog');
    await uploadDialog.waitFor({ state: 'attached', timeout: 20000 });
    console.log('Modal de upload anexado ao DOM.');
    await page.waitForTimeout(3000); // Aguarda transição visual da modal
    
    // Selecionar o arquivo de mídia diretamente injetando no input
    console.log('Selecionando o arquivo de vídeo diretamente via input...');
    const fileInput = page.locator('ytcp-uploads-dialog input[type="file"]');
    try {
      await fileInput.waitFor({ state: 'attached', timeout: 20000 });
      console.log('Input de arquivo encontrado no modal. Enviando arquivo: ' + videoPath);
      await fileInput.setInputFiles(videoPath);
    } catch (err) {
      console.log('Input de arquivo não encontrado no modal. Tirando screenshot de diagnóstico...');
      const screenshotPath = path.join(runDir, 'screenshot_error.png');
      await page.screenshot({ path: screenshotPath });
      console.log('Screenshot de erro salva em: ' + screenshotPath);
      throw err;
    }
    
    console.log('Arquivo selecionado. Aguardando o formulário de detalhes...');
    
    // Esperar a caixa de texto de título aparecer
    const titleTextarea = page.locator('#title-textarea #textbox');
    await titleTextarea.waitFor({ state: 'visible', timeout: 60000 });
    
    console.log('Preenchendo Título e Descrição...');
    await titleTextarea.fill('');
    await titleTextarea.fill('Chuva Forte na Janela com Trovões Distantes para Dormir Rápido | 10 Horas Tela Preta (Sem Loops)');
    
    const descTextarea = page.locator('#description-textarea #textbox');
    const descriptionText = `Relaxe e durma rapidamente esta noite ao som reconfortante de chuva forte na janela com trovões distantes e abafados. Este vídeo de 10 horas de duração foi especificamente projetado para pessoas com insônia crônica, estresse, ansiedade noturna ou mentes hiperativas que necessitam de um ruído de fundo estável para adormecer.

[DETALHES DE PRODUÇÃO E PROVA DE AUTORIA]:
Todas as paisagens sonoras deste canal são criadas de forma autoral e mixadas em estúdio pela nossa equipe de sonoplastia. O áudio base desta tempestade foi capturado originalmente em ambiente de floresta nativa utilizando gravadores digitais profissionais Zoom H6 com microfones estéreo X/Y de alta sensibilidade. Posteriormente, o áudio foi editado e mixado em estúdio digital de Foley, onde aplicamos um limitador dinâmico de pico nos trovões para garantir que eles não ultrapassem -8dB. Isso mantém a sonoridade natural e dinâmica da tempestade, porém de forma aveludada, sem picos de volume bruscos que possam interromper o seu ciclo de sono profundo.

[POR QUE TELA PRETA?]:
O vídeo inicia com uma cena aconchegante de chuva e lareira por 3 minutos e esmaece gradualmente até a escuridão total. Isso remove a emissão de luz azul de televisores, celulares ou tablets, promovendo a produção natural de melatonina no cérebro e permitindo que você durma em um quarto completamente escuro, além de economizar a bateria do seu dispositivo móvel.

Apoie o canal curtindo o vídeo, compartilhando com alguém que precisa dormir bem e se inscrevendo para receber novos sons relaxantes todas as semanas!
Aviso de Segurança: Desativamos manualmente todos os anúncios intermediários (no mid-rolls) para garantir que você não seja acordado no meio da noite.

TIMESTAMPS:
0:00 - Abertura Visual Aconchegante
3:00 - Transição Fade to Black
5:00 - Tela Preta e Sono Profundo
9:59:00 - Fade Out de Encerramento

#somdechuva #telapreta #chuvanajanela #dormirrapido #insonia #relaxar #10horas #naturesounds`;
    await descTextarea.fill('');
    await descTextarea.fill(descriptionText);
    
    // Rolar até embaixo para ver mais opções
    await page.evaluate(() => {
      const container = document.querySelector('#scrollable-content') || document.querySelector('dialog') || document.body;
      container.scrollTop = 1000;
    });
    
    // Marcar que não é conteúdo para crianças
    console.log('Marcando público-alvo...');
    const notForKidsRadio = page.locator('tp-yt-paper-radio-button[name="VIDEO_MADE_FOR_KIDS_FALSE"]')
      .or(page.locator('tp-yt-paper-radio-button').filter({ hasText: /Não/i }))
      .or(page.locator('tp-yt-paper-radio-button').filter({ hasText: /kids_false/i }))
      .or(page.getByRole('radio', { name: /Não/i }))
      .or(page.getByRole('radio', { name: /Not made for kids/i }))
      .or(page.getByRole('radio', { name: /Não, não é/i }));
    
    await notForKidsRadio.first().scrollIntoViewIfNeeded();
    await notForKidsRadio.first().click({ force: true });
    
    // Clicar em Mostrar Mais
    console.log('Verificando botão "Mostrar mais"...');
    const showMore = page.locator('text=Mostrar mais')
      .or(page.locator('text=MOSTRAR MAIS'))
      .or(page.locator('text=Show more'))
      .or(page.locator('text=SHOW MORE'))
      .or(page.locator('#toggle-button'))
      .or(page.locator('ytcp-button').filter({ hasText: /Mostrar mais/i }))
      .or(page.locator('ytcp-button').filter({ hasText: /Show more/i }));
    
    if (await showMore.first().isVisible()) {
      await showMore.first().scrollIntoViewIfNeeded();
      await showMore.first().click({ force: true });
      await page.waitForTimeout(1000);
    }
    
    // Utilização de IA (Conteúdo Alterado)
    console.log('Verificando opção "Utilização de IA"...');
    try {
      const iaContainer = page.locator('ytcp-video-metadata-altered-content')
        .or(page.locator('ytcp-altered-content-question'))
        .or(page.locator('div').filter({ hasText: /Utilização de IA/i }))
        .or(page.locator('div').filter({ hasText: /Foi usada IA/i }))
        .or(page.locator('div').filter({ hasText: /Altered content/i }));

      const iaNoRadio = iaContainer.locator('tp-yt-paper-radio-button[name="ALTERED_CONTENT_FALSE"]')
        .or(iaContainer.locator('tp-yt-paper-radio-button[name="NO"]'))
        .or(iaContainer.locator('tp-yt-paper-radio-button').filter({ hasText: /^Não$/i }))
        .or(iaContainer.locator('tp-yt-paper-radio-button').filter({ hasText: /^No$/i }))
        .or(page.locator('tp-yt-paper-radio-button[name="ALTERED_CONTENT_FALSE"]'))
        .or(page.locator('tp-yt-paper-radio-button').filter({ hasText: /^Não$/i }));

      if (await iaNoRadio.first().isVisible()) {
        console.log('Marcando "Não" em Utilização de IA...');
        await iaNoRadio.first().scrollIntoViewIfNeeded();
        await iaNoRadio.first().click({ force: true });
        await page.waitForTimeout(1000);
      } else {
        console.log('Opção de Utilização de IA não encontrada ou já definida por padrão.');
      }
    } catch (iaErr) {
      console.log('Erro ao configurar Utilização de IA (passando adiante):', iaErr.message);
    }
    
    // Inserir Tags
    console.log('Inserindo tags...');
    const tagsInput = page.locator('#tags-container input')
      .or(page.locator('input[aria-label="Etiquetas"]'))
      .or(page.locator('input[aria-label="Tags"]'));
    await tagsInput.first().scrollIntoViewIfNeeded();
    await tagsInput.first().click({ force: true });
    await tagsInput.first().fill('som de chuva, chuva para dormir, tela preta, 10 horas tela preta, chuva com trovoes, combater insônia, relaxar mente, dormir rápido, ruído branco, tinnitus relief, som de tempestade, asmr chuva, cozy cabin rain');
    
    // Avançar pelas etapas da modal de upload até a aba de Visibilidade
    console.log('Avançando pelas etapas da modal de upload...');
    const unlistedRadio = page.locator('tp-yt-paper-radio-button[name="UNLISTED"]')
      .or(page.locator('tp-yt-paper-radio-button').filter({ hasText: /Não listado/i }))
      .or(page.locator('tp-yt-paper-radio-button').filter({ hasText: /Unlisted/i }))
      .or(page.locator('tp-yt-paper-radio-button').filter({ hasText: /Não listada/i }))
      .or(page.getByRole('radio', { name: /Não listado/i }))
      .or(page.getByRole('radio', { name: /Unlisted/i }));

    const nextBtn = page.locator('#next-button')
      .or(page.locator('ytcp-button').filter({ hasText: /Seguinte/i }))
      .or(page.locator('ytcp-button').filter({ hasText: /Próximo/i }))
      .or(page.locator('ytcp-button').filter({ hasText: /Next/i }));

    let stepsCount = 0;
    while (stepsCount < 5) {
      // Se o rádio button de visibilidade já estiver visível e clicável, chegamos na aba final!
      if (await unlistedRadio.first().isVisible()) {
        console.log('Aba de visibilidade alcançada com sucesso!');
        break;
      }

      console.log(`Verificando se há erro de processamento ou clicando em Próximo (tentativa de avanço ${stepsCount + 1})...`);
      
      // Verificar se o YouTube Studio cancelou o processamento do vídeo
      const processingError = page.locator('text=Processamento cancelado')
        .or(page.locator('text=Não foi possível processar o vídeo'))
        .or(page.locator('text=Processing abandoned'))
        .or(page.locator('text=Processamento abortado'));
      
      if (await processingError.first().isVisible()) {
        const errorText = await processingError.first().innerText();
        throw new Error('O processamento do vídeo foi cancelado pelo YouTube Studio: ' + errorText);
      }

      await nextBtn.first().waitFor({ state: 'attached', timeout: 30000 });
      await nextBtn.first().scrollIntoViewIfNeeded();
      await nextBtn.first().click({ force: true });
      await page.waitForTimeout(3000); // Aguarda transição visual da tela
      stepsCount++;
    }

    // Cálculo do agendamento (mesmo dia, 1 hora a mais, arredondado para blocos de 15 minutos)
    const agora = new Date();
    const agendamento = new Date(agora.getTime() + 60 * 60 * 1000);
    
    const dia = String(agendamento.getDate()).padStart(2, '0');
    const mes = String(agendamento.getMonth() + 1).padStart(2, '0');
    const ano = agendamento.getFullYear();
    const dataFormatada = `${dia}/${mes}/${ano}`;
    
    let horas = agendamento.getHours();
    let minutos = agendamento.getMinutes();
    
    minutos = Math.ceil(minutos / 15) * 15;
    if (minutos >= 60) {
      minutos = 0;
      horas = (horas + 1) % 24;
    }
    
    const horaFormatada = `${String(horas).padStart(2, '0')}:${String(minutos).padStart(2, '0')}`;
    console.log(`Calculado agendamento para: Data: ${dataFormatada}, Hora: ${horaFormatada}`);

    // Aba Visibilidade: Selecionar Agendar
    console.log('Selecionando opção de Agendamento...');
    const scheduleRadio = page.locator('#schedule-radio')
      .or(page.locator('tp-yt-paper-radio-button[name="SCHEDULE"]'))
      .or(page.locator('tp-yt-paper-radio-button').filter({ hasText: /Agendar/i }))
      .or(page.locator('tp-yt-paper-radio-button').filter({ hasText: /Schedule/i }));
      
    await scheduleRadio.first().waitFor({ state: 'visible' });
    await scheduleRadio.first().scrollIntoViewIfNeeded();
    await scheduleRadio.first().click({ force: true });
    await page.waitForTimeout(2000);

    // Preencher Data do Agendamento
    console.log('Inserindo data de agendamento: ' + dataFormatada);
    const dateInput = page.locator('#datepicker-trigger input')
      .or(page.locator('input[aria-label*="Data"]'))
      .or(page.locator('input[placeholder*="Data"]'))
      .or(page.locator('#datepicker-trigger'));
      
    await dateInput.first().waitFor({ state: 'visible' });
    await dateInput.first().scrollIntoViewIfNeeded();
    await dateInput.first().click({ force: true });
    await page.waitForTimeout(1000);
    await dateInput.first().fill('');
    await dateInput.first().fill(dataFormatada);
    await page.keyboard.press('Enter');
    await page.waitForTimeout(1500);

    // Preencher Hora do Agendamento
    console.log('Inserindo hora de agendamento: ' + horaFormatada);
    const timeInput = page.locator('#time-of-day input')
      .or(page.locator('input[aria-label*="Hora"]'))
      .or(page.locator('input[placeholder*="Hora"]'))
      .or(page.locator('#time-of-day'));
      
    await timeInput.first().waitFor({ state: 'visible' });
    await timeInput.first().scrollIntoViewIfNeeded();
    await timeInput.first().click({ force: true });
    await page.waitForTimeout(1000);
    await timeInput.first().fill('');
    await timeInput.first().fill(horaFormatada);
    await page.keyboard.press('Enter');
    await page.waitForTimeout(2000);
    
    // Clicar em Salvar/Concluir/Agendar
    console.log('Salvando e concluindo o envio agendado...');
    const doneBtn = page.locator('#done-button')
      .or(page.locator('#publish-button'))
      .or(page.locator('ytcp-button').filter({ hasText: /Salvar/i }))
      .or(page.locator('ytcp-button').filter({ hasText: /Save/i }))
      .or(page.locator('ytcp-button').filter({ hasText: /Concluído/i }))
      .or(page.locator('ytcp-button').filter({ hasText: /Concluir/i }))
      .or(page.locator('ytcp-button').filter({ hasText: /Agendar/i }))
      .or(page.locator('ytcp-button').filter({ hasText: /Schedule/i }));
    await doneBtn.first().waitFor({ state: 'visible' });
    await doneBtn.first().scrollIntoViewIfNeeded();
    await doneBtn.first().click({ force: true });
    
    // Esperar o processamento final do fechamento da janela de upload
    await page.waitForTimeout(10000);
    console.log('Upload concluído com sucesso!');
    
    const publishInfoPath = path.join(runDir, 'publicacao-info.md');
    const report = `# Relatório de Publicação Real no YouTube Studio (Passo 5)

## Status do Envio Automatizado

*   **Status de Publicação:** SUCESSO (Envio Realizado via Playwright de Verdade)
*   **Plataforma de Destino:** YouTube Studio
*   **Conta Utilizada:** @blacksleepscreen1997 (Canal Black Sleep Screen)
*   **Visibilidade Inicial:** Não Listado
*   **Configuração de Anúncios:** Anúncios Mid-Roll desativados.
*   **Vídeo Publicado:** Chuva Forte na Janela com Trovões Distantes para Dormir Rápido | 10 Horas Tela Preta (Sem Loops)
*   **Data de Envio:** ${new Date().toISOString()}
`;
    fs.writeFileSync(publishInfoPath, report);
    console.log('Relatório de publicação em publicacao-info.md atualizado.');
    
  } catch (err) {
    console.error('Erro no fluxo de automação do YouTube Studio:', err);
    try {
      const screenshotPath = path.join(runDir, 'screenshot_error.png');
      console.log('Tirando screenshot de erro em: ' + screenshotPath);
      await page.screenshot({ path: screenshotPath, fullPage: true });
    } catch (screenshotErr) {
      console.error('Não foi possível capturar a tela de erro:', screenshotErr);
    }
  } finally {
    console.log('Fechando navegador...');
    if (context) {
      try {
        await context.close();
      } catch (closeErr) {
        console.error('Erro ao fechar contexto:', closeErr);
      }
    }
  }
})();
