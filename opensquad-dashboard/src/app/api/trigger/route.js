import { NextResponse } from 'next/server';

export async function POST(request) {
  const pat = process.env.GITHUB_PAT;
  
  if (!pat) {
    return NextResponse.json(
      { error: 'GITHUB_PAT não está configurado no arquivo .env.local.' },
      { status: 400 }
    );
  }

  // Tenta ler o squad do body da requisição
  let squad = 'conexao_artificial'; // squad padrão
  try {
    const body = await request.json();
    if (body && body.squad) {
      squad = body.squad;
    }
  } catch (err) {
    console.log('Nenhum body JSON recebido, usando squad padrão conexao_artificial.');
  }

  // Mapeia o squad para seu respectivo arquivo de workflow
  const workflowFile = squad === 'youtube-black-screen' ? 'youtube_black_screen.yml' : 'conexao_artificial.yml';
  
  // URL da API do GitHub para disparo de workflow específico
  const url = `https://api.github.com/repos/ag-Codevision/squads_automatizados/actions/workflows/${workflowFile}/dispatches`;

  console.log(`🚀 API disparando workflow específico: ${workflowFile} para o squad: ${squad}`);

  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${pat}`,
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28',
        'Content-Type': 'application/json',
        'User-Agent': 'OpenSquad-Dashboard'
      },
      body: JSON.stringify({
        ref: 'main'
      })
    });

    if (!res.ok) {
      const errorText = await res.text();
      throw new Error(`GitHub API respondeu com status ${res.status}: ${errorText}`);
    }

    return NextResponse.json({ success: true, message: `Workflow para o squad ${squad} disparado com sucesso!` });
  } catch (error) {
    console.error('Erro ao disparar workflow do GitHub Actions:', error);
    return NextResponse.json(
      { error: `Falha ao acionar o robô no GitHub Actions: ${error.message}` },
      { status: 500 }
    );
  }
}
