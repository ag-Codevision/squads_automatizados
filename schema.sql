-- Supabase Schema for OpenSquad

-- Create custom enum type for status
CREATE TYPE episode_status AS ENUM ('pending', 'processing', 'completed', 'failed');

-- Create episodes queue table
CREATE TABLE public.episodes_queue (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    topic TEXT,
    voice_ton TEXT NOT NULL DEFAULT 'th5FCJmMnbjdtjRCPt3A',
    voice_bia TEXT NOT NULL DEFAULT '7iqXtOF3wl3pomwXFY7G',
    status episode_status DEFAULT 'pending' NOT NULL,
    schedule_time TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    youtube_url TEXT,
    error_message TEXT
);

-- Habilitar Row Level Security (segurança)
ALTER TABLE public.episodes_queue ENABLE ROW LEVEL SECURITY;

-- Permitir leitura/gravação usando a Anon Key (para testes e fase inicial)
CREATE POLICY "Allow anonymous read" ON public.episodes_queue FOR SELECT USING (true);
CREATE POLICY "Allow anonymous insert" ON public.episodes_queue FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow anonymous update" ON public.episodes_queue FOR UPDATE USING (true);

-- Habilitar replicação em tempo real para a fila de episódios
ALTER PUBLICATION supabase_realtime ADD TABLE public.episodes_queue;
