const { Client } = require('pg');
const fs = require('fs');
const path = require('path');

// URL enconding the @ symbol as %40
const connectionString = 'postgresql://postgres:Omeg%40256489%40256489@db.antsgzedxhieqsblcbps.supabase.co:5432/postgres';

const client = new Client({
  connectionString,
});

async function setup() {
  try {
    await client.connect();
    console.log('Conectado ao Supabase com sucesso!');

    // Clean up existing tables safely instead of dropping the whole schema
    console.log('Limpando vestígios antigos...');
    await client.query('DROP TABLE IF EXISTS public.episodes_queue CASCADE;');
    await client.query('DROP TYPE IF EXISTS public.episode_status CASCADE;');
    
    // Read schema.sql
    const sql = fs.readFileSync(path.join(__dirname, '..', 'schema.sql'), 'utf8');
    
    console.log('Criando novas tabelas de Fila de Produção...');
    await client.query(sql);
    
    console.log('Banco de dados inicializado e pronto para o OpenSquad!');
  } catch (err) {
    console.error('Erro na execução do banco:', err);
  } finally {
    await client.end();
  }
}

setup();
