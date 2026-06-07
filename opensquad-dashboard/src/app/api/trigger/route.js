import { NextResponse } from 'next/server';

export async function POST() {
  const pat = process.env.GITHUB_PAT;
  
  if (!pat) {
    return NextResponse.json(
      { error: 'GITHUB_PAT não está configurado no arquivo .env.local.' },
      { status: 400 }
    );
  }

  // URL da API do GitHub para disparo de workflow
  const url = 'https://api.github.com/repos/ag-Codevision/conexao-artificial-cloud/actions/workflows/robocast.yml/dispatches';

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

    return NextResponse.json({ success: true, message: 'Workflow disparado com sucesso!' });
  } catch (error) {
    console.error('Erro ao disparar workflow do GitHub Actions:', error);
    return NextResponse.json(
      { error: `Falha ao acionar o robô no GitHub Actions: ${error.message}` },
      { status: 500 }
    );
  }
}
