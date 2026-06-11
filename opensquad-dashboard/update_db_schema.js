const { Client } = require('pg');

const connectionString = 'postgresql://postgres:Omeg%40256489%40256489@db.antsgzedxhieqsblcbps.supabase.co:5432/postgres';

const client = new Client({
  connectionString,
});

async function run() {
  try {
    await client.connect();
    console.log('Conectado ao Supabase com sucesso para atualização!');

    // Adiciona o status 'cancelled' ao enum de status
    // Usamos um bloco try/catch interno porque se 'cancelled' já existir, o Postgres lançará um erro
    try {
      console.log('Adicionando status "cancelled" ao enum episode_status...');
      await client.query("ALTER TYPE public.episode_status ADD VALUE 'cancelled';");
      console.log('Status "cancelled" adicionado com sucesso!');
    } catch (enumErr) {
      if (enumErr.message.includes('already exists')) {
        console.log('O status "cancelled" já existe no enum.');
      } else {
        throw enumErr;
      }
    }

    // Adiciona a política de RLS para DELETE
    try {
      console.log('Habilitando política RLS para exclusão (DELETE)...');
      await client.query('DROP POLICY IF EXISTS "Allow anonymous delete" ON public.episodes_queue;');
      await client.query('CREATE POLICY "Allow anonymous delete" ON public.episodes_queue FOR DELETE USING (true);');
      console.log('Política de exclusão criada com sucesso!');
    } catch (policyErr) {
      console.error('Erro ao criar política de exclusão:', policyErr);
      throw policyErr;
    }

    // Habilita o Realtime para a tabela episodes_queue
    try {
      console.log('Habilitando replicação Realtime para a tabela episodes_queue...');
      await client.query('ALTER PUBLICATION supabase_realtime ADD TABLE public.episodes_queue;');
      console.log('Realtime habilitado com sucesso!');
    } catch (realtimeErr) {
      console.log('Realtime já estava ativo ou ocorreu um erro ignorável:', realtimeErr.message);
    }

    // Adiciona a coluna script_text à tabela episodes_queue
    try {
      console.log('Adicionando a coluna script_text à tabela episodes_queue...');
      await client.query('ALTER TABLE public.episodes_queue ADD COLUMN IF NOT EXISTS script_text TEXT;');
      console.log('Coluna script_text verificada/adicionada com sucesso!');
    } catch (colErr) {
      console.error('Erro ao adicionar coluna script_text:', colErr);
      throw colErr;
    }

    // Adiciona a coluna squad à tabela episodes_queue
    try {
      console.log('Adicionando a coluna squad à tabela episodes_queue...');
      await client.query("ALTER TABLE public.episodes_queue ADD COLUMN IF NOT EXISTS squad TEXT NOT NULL DEFAULT 'conexao_artificial';");
      console.log('Coluna squad verificada/adicionada à tabela episodes_queue com sucesso!');
    } catch (colErr) {
      console.error('Erro ao adicionar coluna squad à tabela episodes_queue:', colErr);
      throw colErr;
    }

    // Adiciona a coluna last_cron_run à tabela squad_settings
    try {
      console.log('Adicionando a coluna last_cron_run à tabela squad_settings...');
      await client.query('ALTER TABLE public.squad_settings ADD COLUMN IF NOT EXISTS last_cron_run TIMESTAMP WITH TIME ZONE;');
      console.log('Coluna last_cron_run verificada/adicionada com sucesso!');
    } catch (colErr) {
      console.error('Erro ao adicionar coluna last_cron_run:', colErr);
      throw colErr;
    }

    // Adiciona a coluna squad à tabela squad_settings
    try {
      console.log('Adicionando a coluna squad à tabela squad_settings...');
      await client.query("ALTER TABLE public.squad_settings ADD COLUMN IF NOT EXISTS squad TEXT NOT NULL DEFAULT 'conexao_artificial';");
      console.log('Coluna squad verificada/adicionada à tabela squad_settings com sucesso!');
    } catch (colErr) {
      console.error('Erro ao adicionar coluna squad à tabela squad_settings:', colErr);
      throw colErr;
    }

    // Certifica-se de que há registros de configurações padrão para ambos os squads na tabela squad_settings
    try {
      // 1. Conexão Artificial
      const resConexao = await client.query("SELECT COUNT(*) FROM public.squad_settings WHERE squad = 'conexao_artificial';");
      if (parseInt(resConexao.rows[0].count, 10) === 0) {
        console.log('Inserindo registro de configurações padrão para conexao_artificial...');
        await client.query(`
          INSERT INTO public.squad_settings (omni_model, voice_ton, voice_bia, squad) 
          VALUES ('g', 'google/gemini-3.1-flash-tts', 'google/gemini-3.1-flash-tts', 'conexao_artificial');
        `);
      }

      // 2. YouTube Black Screen
      const resBlack = await client.query("SELECT COUNT(*) FROM public.squad_settings WHERE squad = 'youtube-black-screen';");
      if (parseInt(resBlack.rows[0].count, 10) === 0) {
        console.log('Inserindo registro de configurações padrão para youtube-black-screen...');
        await client.query(`
          INSERT INTO public.squad_settings (omni_model, voice_ton, voice_bia, squad) 
          VALUES ('g', 'google/gemini-3.1-flash-tts', 'google/gemini-3.1-flash-tts', 'youtube-black-screen');
        `);
      }
      console.log('Configurações padrão verificadas/inseridas com sucesso!');
    } catch (settErr) {
      console.error('Erro ao verificar/inserir configurações padrão:', settErr);
    }

    console.log('Atualização do banco de dados concluída com sucesso!');
  } catch (err) {
    console.error('Erro durante a execução do script de atualização:', err);
  } finally {
    await client.end();
  }
}

run();
