const { createClient } = require('@supabase/supabase-js');

const supabaseUrl = 'https://antsgzedxhieqsblcbps.supabase.co';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFudHNnemVkeGhpZXFzYmxjYnBzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzUzMzk0NzIsImV4cCI6MjA5MDkxNTQ3Mn0.izWLXTyom0ZoS4PBHRBRcUDcdBB7KlNOFAvPmlURrhc';

const supabase = createClient(supabaseUrl, supabaseKey);

async function check() {
  const { data, error } = await supabase
    .from('episodes_queue')
    .select('*')
    .order('created_at', { ascending: false });

  if (error) {
    console.error('Erro ao consultar Supabase:', error);
    return;
  }

  console.log('--- LISTA DE EPISÓDIOS NO SUPABASE ---');
  data.forEach(ep => {
    console.log(`ID: ${ep.id}`);
    console.log(`Tópico: ${ep.topic}`);
    console.log(`Status: ${ep.status}`);
    console.log(`Erro: ${ep.error_message || 'Nenhum'}`);
    console.log(`YouTube: ${ep.youtube_url || 'Nenhum'}`);
    console.log('------------------------------------');
  });
}

check();
