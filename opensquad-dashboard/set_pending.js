const { createClient } = require('@supabase/supabase-js');

const supabaseUrl = 'https://antsgzedxhieqsblcbps.supabase.co';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFudHNnemVkeGhpZXFzYmxjYnBzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzUzMzk0NzIsImV4cCI6MjA5MDkxNTQ3Mn0.izWLXTyom0ZoS4PBHRBRcUDcdBB7KlNOFAvPmlURrhc';

const supabase = createClient(supabaseUrl, supabaseKey);

async function setPending() {
  const { error } = await supabase
    .from('episodes_queue')
    .update({ status: 'pending', error_message: null })
    .eq('id', '0f9a54bf-130f-4d3f-8793-7c12bde7314a');

  if (error) {
    console.error('Erro ao redefinir status:', error);
  } else {
    console.log('Episódio redefinido com sucesso para pending!');
  }
}

setPending();
