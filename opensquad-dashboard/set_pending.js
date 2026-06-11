const { createClient } = require('@supabase/supabase-js');

const supabaseUrl = 'https://antsgzedxhieqsblcbps.supabase.co';
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFudHNnemVkeGhpZXFzYmxjYnBzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzUzMzk0NzIsImV4cCI6MjA5MDkxNTQ3Mn0.izWLXTyom0ZoS4PBHRBRcUDcdBB7KlNOFAvPmlURrhc';

const supabase = createClient(supabaseUrl, supabaseKey);

async function setPending() {
  const { error } = await supabase
    .from('episodes_queue')
    .update({ 
      status: 'pending', 
      topic: 'Som de Chuva para Relaxar', 
      script_text: null, 
      error_message: null 
    })
    .eq('id', '543b25b9-a9fb-4d7a-acbb-0517135093a8');

  if (error) {
    console.error('Erro ao redefinir status:', error);
  } else {
    console.log('Episódio redefinido com sucesso para pending e tópico restaurado!');
  }
}

setPending();
