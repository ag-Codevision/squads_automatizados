'use client';

import { useState, useEffect } from 'react';
import { supabase } from '@/lib/supabase';
import { 
  Loader2, 
  Trash2, 
  XCircle, 
  RefreshCw, 
  CheckCircle, 
  AlertTriangle, 
  ExternalLink, 
  Clock, 
  TrendingUp, 
  BarChart2, 
  Calendar,
  Tv,
  Settings,
  History,
  PlusCircle,
  CalendarDays,
  ChevronLeft,
  ChevronRight,
  X,
  FileText,
  Edit3,
  ChevronDown
} from 'lucide-react';

const CustomSelect = ({ options, value, onChange }) => {
  const [isOpen, setIsOpen] = useState(false);
  return (
    <div className={`custom-select-container ${isOpen ? 'open' : ''}`} onBlur={() => setIsOpen(false)} tabIndex="0">
      <div className="custom-select-trigger" onClick={() => setIsOpen(!isOpen)}>
        {value}
        <span style={{ fontSize: '10px', opacity: 0.5 }}>▼</span>
      </div>
      {isOpen && (
        <div className="custom-select-dropdown">
          {options.map(opt => (
            <div key={opt} className="custom-option" onMouseDown={(e) => { e.preventDefault(); onChange(opt); setIsOpen(false); }}>
              {opt}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

const formatDateTime = (dateVal) => {
  if (!dateVal) return '';
  const d = new Date(dateVal);
  const datePart = `${String(d.getDate()).padStart(2, '0')}/${String(d.getMonth() + 1).padStart(2, '0')}/${d.getFullYear()}`;
  const timePart = d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  return `${datePart} às ${timePart}`;
};

const toLocalDatetimeLocal = (isoString) => {
  if (!isoString) return '';
  const date = new Date(isoString);
  const tzOffset = date.getTimezoneOffset() * 60000;
  const localISOTime = (new Date(date.getTime() - tzOffset)).toISOString().slice(0, 16);
  return localISOTime;
};

const calculateScheduleTimes = (freq, numEpisodes) => {
  const dates = [];
  const now = new Date();

  // 1. Agora mesmo (Imediato)
  if (freq === 'Agora mesmo (Imediato)') {
    for (let i = 0; i < numEpisodes; i++) {
      const d = new Date(now);
      d.setMinutes(now.getMinutes() + i);
      dates.push(d);
    }
    return dates;
  }

  // 2. A cada X horas
  const matchHours = freq.match(/[Aa] cada (\d+)\s*(?:hora|hour)s?/i);
  if (matchHours) {
    const hours = parseInt(matchHours[1], 10);
    for (let i = 0; i < numEpisodes; i++) {
      const d = new Date(now);
      d.setHours(now.getHours() + (i + 1) * hours);
      dates.push(d);
    }
    return dates;
  }

  // 2.1. A cada X minutos
  const matchMinutes = freq.match(/[Aa] cada (\d+)\s*(?:minuto|minute)s?/i);
  if (matchMinutes) {
    const minutes = parseInt(matchMinutes[1], 10);
    for (let i = 0; i < numEpisodes; i++) {
      const d = new Date(now);
      d.setMinutes(now.getMinutes() + (i + 1) * minutes);
      dates.push(d);
    }
    return dates;
  }

  // 3. Diariamente às HH:MM
  const matchDaily = freq.match(/Diariamente às (\d{2}):(\d{2})/);
  if (matchDaily) {
    const targetHour = parseInt(matchDaily[1], 10);
    const targetMin = parseInt(matchDaily[2], 10);
    let baseDate = new Date(now);
    baseDate.setHours(targetHour, targetMin, 0, 0);
    if (baseDate.getTime() < now.getTime()) {
      baseDate.setDate(baseDate.getDate() + 1);
    }
    for (let i = 0; i < numEpisodes; i++) {
      const d = new Date(baseDate);
      d.setDate(baseDate.getDate() + i);
      dates.push(d);
    }
    return dates;
  }

  // 4. Lógicas de dias específicos da semana
  let allowedDays = [];
  let targetHour = 9;
  let targetMin = 0;

  if (freq.includes('Seg, Qua, Sex')) {
    allowedDays = [1, 3, 5];
    const match = freq.match(/às (\d{2}):(\d{2})/);
    if (match) {
      targetHour = parseInt(match[1], 10);
      targetMin = parseInt(match[2], 10);
    }
  } else if (freq.includes('Terça e Quinta')) {
    allowedDays = [2, 4];
    const match = freq.match(/às (\d{2}):(\d{2})/);
    if (match) {
      targetHour = parseInt(match[1], 10);
      targetMin = parseInt(match[2], 10);
    }
  } else if (freq.includes('Finais de Semana')) {
    allowedDays = [0, 6];
    const match = freq.match(/às (\d{2}):(\d{2})/);
    if (match) {
      targetHour = parseInt(match[1], 10);
      targetMin = parseInt(match[2], 10);
    }
  } else if (freq.includes('Semanalmente')) {
    allowedDays = [1]; // Segunda-feira
    targetHour = 8; // default 08:00
    targetMin = 0;
  }

  if (allowedDays.length > 0) {
    let checkDate = new Date(now);
    checkDate.setHours(targetHour, targetMin, 0, 0);
    if (checkDate.getTime() < now.getTime()) {
      checkDate.setDate(checkDate.getDate() + 1);
    }

    while (dates.length < numEpisodes) {
      if (allowedDays.includes(checkDate.getDay())) {
        dates.push(new Date(checkDate));
      }
      checkDate.setDate(checkDate.getDate() + 1);
    }
    return dates;
  }

  // Fallback caso não bata em nenhuma regra
  for (let i = 0; i < numEpisodes; i++) {
    dates.push(new Date(now));
  }
  return dates;
};

export default function Dashboard() {
  const [selectedSquad, setSelectedSquad] = useState('conexao_artificial');
  const [expandedSquads, setExpandedSquads] = useState({
    conexao_artificial: false,
    'youtube-black-screen': false
  });

  const [episodes, setEpisodes] = useState([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [topic, setTopic] = useState('');
  const [activeTab, setActiveTab] = useState('dashboard');
  const [filterStatus, setFilterStatus] = useState('todos');
  const [selectedEpisodeForScript, setSelectedEpisodeForScript] = useState(null);

  // Estados para o Calendário
  const [currentDate, setCurrentDate] = useState(null);
  const [selectedDayEpisodes, setSelectedDayEpisodes] = useState([]);
  const [selectedDateStr, setSelectedDateStr] = useState(null);

  // Estados para Edição de Agendamento (CRUD)
  const [selectedEpisodeForEdit, setSelectedEpisodeForEdit] = useState(null);
  const [editTopic, setEditTopic] = useState('');
  const [editScheduleTime, setEditScheduleTime] = useState('');
  const [isEditing, setIsEditing] = useState(false);
  
  const [settings, setSettings] = useState({
    omni_model: 'g',
    voice_ton: 'google/gemini-3.1-flash-tts',
    voice_bia: 'google/gemini-3.1-flash-tts'
  });
  const [isLoadingSettings, setIsLoadingSettings] = useState(true);
  const [isSavingSettings, setIsSavingSettings] = useState(false);

  // Mapeamentos de chaves/labels do OmniRoute
  const modelLabels = {
    'g': 'Omniroute Combo g',
    'nvidia': 'Combo Nvidia',
    'pollinations': 'Pollinations',
  };
  const modelKeys = {
    'Omniroute Combo g': 'g',
    'Combo Nvidia': 'nvidia',
    'Pollinations': 'pollinations',
  };

  // Mapeamentos de chaves/labels do Ton (TTS Provedor)
  const tonVoiceLabels = {
    'elevenlabs': 'elevenlabs',
    'microsoft': 'Microsoft',
    'google/gemini-3.1-flash-tts': 'Gemini 3.1 TTS',
  };
  const tonVoiceKeys = {
    'elevenlabs': 'elevenlabs',
    'Microsoft': 'microsoft',
    'Gemini 3.1 TTS': 'google/gemini-3.1-flash-tts',
  };

  // Mapeamentos de chaves/labels da Bia (TTS Provedor)
  const biaVoiceLabels = {
    'elevenlabs': 'elevenlabs',
    'microsoft': 'Microsoft',
    'google/gemini-3.1-flash-tts': 'Gemini 3.1 TTS',
  };
  const biaVoiceKeys = {
    'elevenlabs': 'elevenlabs',
    'Microsoft': 'microsoft',
    'Gemini 3.1 TTS': 'google/gemini-3.1-flash-tts',
  };
  
  const freqOptions = [
    'Agora mesmo (Imediato)',
    'A cada 1 hora',
    'A cada 3 horas',
    'A cada 6 horas',
    'A cada 12 horas',
    'Diariamente às 08:00',
    'Diariamente às 12:00',
    'Diariamente às 20:00',
    'Seg, Qua, Sex às 15:00',
    'Terça e Quinta às 18:00',
    'Finais de Semana às 10:00',
    'Semanalmente (Toda Segunda-feira)',
    'Personalizado...'
  ];
  const [freq, setFreq] = useState(freqOptions[0]);
  
  const qtyOptions = [
    '1 Episódio',
    '2 Episódios',
    '3 Episódios',
    '5 Episódios',
    '10 Episódios',
    '20 Episódios',
    '50 Episódios',
    'Infinito (Piloto Automático)',
    'Personalizado...'
  ];
  const [qty, setQty] = useState(qtyOptions[0]);

  const [customFreq, setCustomFreq] = useState('');
  const [customQty, setCustomQty] = useState('');

  // Carregar episódios e configurações do Supabase
  useEffect(() => {
    fetchEpisodes(selectedSquad);
    fetchSettings(selectedSquad);
    setCurrentDate(new Date());
    
    // Atualização em tempo real (Realtime subscriptions) para episódios
    const channel = supabase
      .channel('schema-db-changes')
      .on('postgres_changes', { event: '*', schema: 'public', table: 'episodes_queue' }, payload => {
        fetchEpisodes(selectedSquad);
      })
      .subscribe();

    // Atualização em tempo real (Realtime subscriptions) para configurações
    const settingsChannel = supabase
      .channel('settings-db-changes')
      .on('postgres_changes', { event: '*', schema: 'public', table: 'squad_settings' }, payload => {
        if (payload.new && payload.new.squad === selectedSquad) {
          setSettings(payload.new);
        }
      })
      .subscribe();
      
    return () => {
      supabase.removeChannel(channel);
      supabase.removeChannel(settingsChannel);
    };
  }, [selectedSquad]);

  // Recalcular episódios do dia selecionado em tempo real se a lista de episódios mudar
  useEffect(() => {
    if (selectedDateStr) {
      const filtered = episodes.filter(ep => {
        const epDate = new Date(ep.schedule_time || ep.created_at);
        const epDateStr = `${epDate.getFullYear()}-${String(epDate.getMonth() + 1).padStart(2, '0')}-${String(epDate.getDate()).padStart(2, '0')}`;
        return epDateStr === selectedDateStr;
      });
      setSelectedDayEpisodes(filtered);
    }
  }, [episodes, selectedDateStr]);

  // Polling ativo no frontend enquanto o painel estiver aberto:
  // Se houver algum episódio agendado pendente cujo horário já passou, dispara o robô automaticamente.
  useEffect(() => {
    const checkAndTriggerActiveEpisodes = async () => {
      if (episodes.length === 0) return;
      const now = new Date();
      const hasExpiredEpisodes = episodes.some(ep => {
        if (ep.status !== 'pending') return false;
        const epDate = new Date(ep.schedule_time || ep.created_at);
        return epDate.getTime() <= now.getTime();
      });

      if (hasExpiredEpisodes) {
        console.log('⏰ Detectado episódio com horário de postagem atingido! Disparando robô na nuvem...');
        try {
          await fetch('/api/trigger', { method: 'POST' });
        } catch (err) {
          console.error('Erro ao disparar via polling do frontend:', err);
        }
      }
    };

    // Executa imediatamente e depois a cada 1 minuto
    checkAndTriggerActiveEpisodes();
    const interval = setInterval(checkAndTriggerActiveEpisodes, 60 * 1000);
    return () => clearInterval(interval);
  }, [episodes]);

  const fetchEpisodes = async (squadCode) => {
    const { data, error } = await supabase
      .from('episodes_queue')
      .select('*')
      .eq('squad', squadCode)
      .order('created_at', { ascending: false });
      
    if (!error && data) {
      setEpisodes(data);
    }
  };

  const fetchSettings = async (squadCode) => {
    setIsLoadingSettings(true);
    try {
      const { data, error } = await supabase
        .from('squad_settings')
        .select('*')
        .eq('squad', squadCode)
        .limit(1);
        
      if (!error && data && data.length > 0) {
        setSettings(data[0]);
      }
    } catch (err) {
      console.error('Erro ao buscar configurações:', err);
    }
    setIsLoadingSettings(false);
  };

  const handleSaveSettings = async () => {
    setIsSavingSettings(true);
    try {
      const { error } = await supabase
        .from('squad_settings')
        .update({
          omni_model: settings.omni_model,
          voice_ton: settings.voice_ton,
          voice_bia: settings.voice_bia,
          updated_at: new Date().toISOString()
        })
        .eq('id', settings.id);
        
      if (error) throw error;
      alert('⚙️ Configurações salvas e aplicadas em tempo real com sucesso!');
    } catch (err) {
      console.error('Erro ao salvar configurações:', err);
      alert('Erro ao salvar configurações: ' + err.message);
    }
    setIsSavingSettings(false);
  };

  const handlePrevMonth = () => {
    if (!currentDate) return;
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1));
    setSelectedDayEpisodes([]);
    setSelectedDateStr(null);
  };

  const handleNextMonth = () => {
    if (!currentDate) return;
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1));
    setSelectedDayEpisodes([]);
    setSelectedDateStr(null);
  };

  const handleDayClick = (day) => {
    if (!day || !currentDate) return;
    const dateStr = `${currentDate.getFullYear()}-${String(currentDate.getMonth() + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
    setSelectedDateStr(dateStr);
  };

  const handleSchedule = async () => {
    setIsSubmitting(true);
    
    const finalFreq = freq === 'Personalizado...' ? customFreq : freq;
    const finalQty = qty === 'Personalizado...' ? customQty : qty;

    // Extrai o número da string (ex: "3 Episódios" -> 3), com fallback para 1 (ex: "Infinito")
    let numEpisodes = 1;
    if (finalQty.includes('Episódio') || /\d+/.test(finalQty)) {
      const match = finalQty.match(/\d+/);
      if (match) {
        numEpisodes = parseInt(match[0], 10);
      }
    }
    
    try {
      const inserts = [];
      const scheduledDates = calculateScheduleTimes(finalFreq, numEpisodes);
      for (let i = 0; i < numEpisodes; i++) {
        inserts.push({
          topic: topic || (selectedSquad === 'conexao_artificial' ? 'Aleatório (Notícias do dia)' : 'Som de Chuva para Relaxar'),
          status: 'pending',
          voice_ton: settings.voice_ton || 'google/gemini-3.1-flash-tts',
          voice_bia: settings.voice_bia || 'google/gemini-3.1-flash-tts',
          schedule_time: scheduledDates[i].toISOString(),
          squad: selectedSquad
        });
      }
      
      const { error } = await supabase.from('episodes_queue').insert(inserts);
      if (error) throw error;
      
      setTopic('');
      // Redireciona para a fila após agendar
      setActiveTab('agendamento');

      // Se for execução imediata, tenta disparar o robô no GitHub Actions
      if (finalFreq === 'Agora mesmo (Imediato)') {
        try {
          const triggerRes = await fetch('/api/trigger', { method: 'POST' });
          const triggerData = await triggerRes.json();
          if (!triggerRes.ok) {
            alert(`⚠️ Episódio agendado no banco de dados, mas o robô não pôde ser acionado de forma automática:\n${triggerData.error || 'Erro desconhecido'}`);
          } else {
            console.log('Robô do GitHub Actions disparado com sucesso!');
          }
        } catch (triggerErr) {
          console.error('Erro ao acionar o robô do GitHub Actions:', triggerErr);
          alert('⚠️ Episódio agendado, mas houve uma falha de conexão ao acionar o robô no GitHub Actions.');
        }
      }
    } catch (err) {
      console.error('Erro ao agendar episódios:', err);
      alert('Erro ao agendar: ' + err.message);
    }
    
    setIsSubmitting(false);
  };

  // Excluir permanentemente do Supabase
  const handleDeleteEpisode = async (id) => {
    if (confirm('Tem certeza que deseja excluir permanentemente este episódio? Ele será apagado do banco de dados e da fila de postagem.')) {
      try {
        const { error } = await supabase
          .from('episodes_queue')
          .delete()
          .eq('id', id);
        if (error) throw error;
        await fetchEpisodes();
      } catch (err) {
        console.error('Erro ao deletar episódio:', err);
        alert('Erro ao deletar: ' + err.message);
      }
    }
  };

  // Cancelar (Tirar da fila de postagem)
  const handleCancelEpisode = async (id) => {
    try {
      const { error } = await supabase
        .from('episodes_queue')
        .update({ status: 'cancelled' })
        .eq('id', id);
      if (error) throw error;
      await fetchEpisodes();
    } catch (err) {
      console.error('Erro ao cancelar episódio:', err);
      alert('Erro ao cancelar: ' + err.message);
    }
  };

  // Reagendar (Voltar status para pending)
  const handleRescheduleEpisode = async (id) => {
    try {
      const { error } = await supabase
        .from('episodes_queue')
        .update({ status: 'pending', error_message: null })
        .eq('id', id);
      if (error) throw error;
      await fetchEpisodes();
    } catch (err) {
      console.error('Erro ao reagendar episódio:', err);
      alert('Erro ao reagendar: ' + err.message);
    }
  };

  const renderCronStatus = () => {
    if (!settings || !settings.last_cron_run) {
      return (
        <div className="cron-status-badge">
          <span className="cron-dot cron-gray"></span>
          <span className="cron-text">Cron Não Iniciado</span>
        </div>
      );
    }

    const lastRun = new Date(settings.last_cron_run);
    const now = new Date();
    const diffMs = now - lastRun;
    const diffMin = Math.floor(diffMs / 60000);

    if (diffMin < 0) {
      return (
        <div className="cron-status-badge">
          <span className="cron-dot cron-green"></span>
          <span className="cron-text">Cron Ativo (há menos de 1 minuto)</span>
        </div>
      );
    }

    if (diffMin <= 20) {
      const text = diffMin === 0 ? 'há menos de 1 minuto' : `há ${diffMin} min`;
      return (
        <div className="cron-status-badge">
          <span className="cron-dot cron-green"></span>
          <span className="cron-text">Cron Ativo ({text})</span>
        </div>
      );
    } else {
      let text = `há ${diffMin} min`;
      if (diffMin >= 60) {
        const diffHrs = Math.floor(diffMin / 60);
        const remainingMin = diffMin % 60;
        text = `há ${diffHrs}h ${remainingMin}m`;
      }
      return (
        <div className="cron-status-badge">
          <span className="cron-dot cron-red"></span>
          <span className="cron-text">Cron Inativo ({text})</span>
        </div>
      );
    }
  };

  const handleOpenEditModal = (ep) => {
    setSelectedEpisodeForEdit(ep);
    setEditTopic(ep.topic || '');
    setEditScheduleTime(toLocalDatetimeLocal(ep.schedule_time || ep.created_at));
  };

  const handleSaveEdit = async () => {
    if (!selectedEpisodeForEdit) return;
    setIsEditing(true);
    try {
      const isoString = new Date(editScheduleTime).toISOString();
      const { error } = await supabase
        .from('episodes_queue')
        .update({
          topic: editTopic,
          schedule_time: isoString
        })
        .eq('id', selectedEpisodeForEdit.id);

      if (error) throw error;
      
      setSelectedEpisodeForEdit(null);
      await fetchEpisodes();
      alert('✏️ Agendamento atualizado com sucesso!');
    } catch (err) {
      console.error('Erro ao editar agendamento:', err);
      alert('Erro ao editar agendamento: ' + err.message);
    }
    setIsEditing(false);
  };

  // Estatísticas do Dashboard
  const publishedCount = episodes.filter(ep => ep.status === 'completed').length;
  const failedCount = episodes.filter(ep => ep.status === 'failed').length;
  const queueCount = episodes.filter(ep => ep.status === 'pending' || ep.status === 'processing').length;
  const cancelledCount = episodes.filter(ep => ep.status === 'cancelled').length;
  const successRate = (publishedCount + failedCount) > 0 
    ? Math.round((publishedCount / (publishedCount + failedCount)) * 100) 
    : 0;

  // Filtragem da Fila Ativa (apenas pendentes e processando)
  const activeQueue = episodes.filter(ep => ep.status === 'pending' || ep.status === 'processing');

  // Filtragem do Histórico
  const filteredHistory = episodes.filter(ep => {
    if (filterStatus === 'todos') return true;
    if (filterStatus === 'completed') return ep.status === 'completed';
    if (filterStatus === 'failed') return ep.status === 'failed';
    if (filterStatus === 'cancelled') return ep.status === 'cancelled';
    if (filterStatus === 'queue') return ep.status === 'pending' || ep.status === 'processing';
    return true;
  });

  // Determinar status do pipeline
  const isCurrentlyProcessing = episodes.some(ep => ep.status === 'processing');
  const hasPendingEpisodes = episodes.some(ep => ep.status === 'pending');
  const lastEpisode = episodes[0]; // mais recente criado

  // Lógica da grade do calendário
  let calendarDaysGrid = [];
  let monthYearTitle = "";
  if (currentDate) {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    const monthNames = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"];
    monthYearTitle = `${monthNames[month]} de ${year}`;
    const firstDayIndex = new Date(year, month, 1).getDay();
    const totalDays = new Date(year, month + 1, 0).getDate();
    calendarDaysGrid = [...Array(firstDayIndex).fill(null), ...Array.from({ length: totalDays }, (_, i) => i + 1)];
  }

  return (
    <div className="dashboard-container">
      {/* Barra Lateral */}
      <div className="sidebar glass-panel">
        <div className="logo-area">
          <div className="logo-icon" style={{background: 'white', boxShadow: '0 0 15px rgba(255,255,255,0.2)'}}></div>
          OpenSquad
        </div>
        
        {/* Squad 1: Conexão Artificial */}
        <div className="squad-group">
          <div 
            className="squad-header" 
            onClick={() => {
              setSelectedSquad('conexao_artificial');
              setExpandedSquads({ conexao_artificial: !expandedSquads.conexao_artificial, 'youtube-black-screen': false });
            }}
          >
            <img 
              src="/conexao-artificial-icon.png" 
              alt="Conexão Artificial" 
              className="squad-icon conexao" 
              style={{ objectFit: 'cover' }}
            />
            <span style={{ flex: 1, fontWeight: selectedSquad === 'conexao_artificial' ? 'bold' : 'normal' }}>Conexão Artificial</span>
            <ChevronDown 
              size={14} 
              style={{ 
                transition: 'transform 0.3s cubic-bezier(0.16, 1, 0.3, 1)', 
                transform: expandedSquads.conexao_artificial ? 'rotate(0deg)' : 'rotate(-90deg)',
                opacity: 0.5,
                flexShrink: 0
              }} 
            />
          </div>
          <div 
            className="sub-menu" 
            style={{ 
              maxHeight: expandedSquads.conexao_artificial ? '500px' : '0px',
              overflow: 'hidden',
              opacity: expandedSquads.conexao_artificial ? 1 : 0,
              transition: 'max-height 0.35s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.25s ease',
              marginTop: expandedSquads.conexao_artificial ? '4px' : '0px',
              paddingLeft: '8px'
            }}
          >
            <div 
              className={`nav-item ${selectedSquad === 'conexao_artificial' && activeTab === 'dashboard' ? 'active' : ''}`}
              onClick={() => { setSelectedSquad('conexao_artificial'); setActiveTab('dashboard'); }}
            >
              <BarChart2 size={16} /> Visão Geral
            </div>
            <div 
              className={`nav-item ${selectedSquad === 'conexao_artificial' && activeTab === 'agendamento' ? 'active' : ''}`}
              onClick={() => { setSelectedSquad('conexao_artificial'); setActiveTab('agendamento'); }}
            >
              <PlusCircle size={16} /> Agendar Episódio
            </div>
            <div 
              className={`nav-item ${selectedSquad === 'conexao_artificial' && activeTab === 'crons' ? 'active' : ''}`}
              onClick={() => { setSelectedSquad('conexao_artificial'); setActiveTab('crons'); }}
            >
              <Clock size={16} /> Gerenciar Crons
            </div>
            <div 
              className={`nav-item ${selectedSquad === 'conexao_artificial' && activeTab === 'calendario' ? 'active' : ''}`}
              onClick={() => { setSelectedSquad('conexao_artificial'); setActiveTab('calendario'); }}
            >
              <CalendarDays size={16} /> Calendário
            </div>
            <div 
              className={`nav-item ${selectedSquad === 'conexao_artificial' && activeTab === 'historico' ? 'active' : ''}`}
              onClick={() => { setSelectedSquad('conexao_artificial'); setActiveTab('historico'); }}
            >
              <History size={16} /> Histórico
            </div>
            <div 
              className={`nav-item ${selectedSquad === 'conexao_artificial' && activeTab === 'configuracoes' ? 'active' : ''}`}
              onClick={() => { setSelectedSquad('conexao_artificial'); setActiveTab('configuracoes'); }}
            >
              <Settings size={16} /> Configurações
            </div>
            <div className="nav-item" style={{ opacity: 0.25, cursor: 'not-allowed' }}>Chaves de API</div>
            <div className="nav-item" style={{ opacity: 0.25, cursor: 'not-allowed' }}>Conexões (Spotify/YT)</div>
          </div>
        </div>

        {/* Squad 2: YouTube Black Screen */}
        <div className="squad-group">
          <div 
            className="squad-header" 
            onClick={() => {
              setSelectedSquad('youtube-black-screen');
              setExpandedSquads({ conexao_artificial: false, 'youtube-black-screen': !expandedSquads['youtube-black-screen'] });
            }}
          >
            <span className="squad-icon" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'rgba(255,255,255,0.05)', borderRadius: '6px', fontSize: '14px' }}>💤</span>
            <span style={{ flex: 1, fontWeight: selectedSquad === 'youtube-black-screen' ? 'bold' : 'normal' }}>YouTube Black Screen</span>
            <ChevronDown 
              size={14} 
              style={{ 
                transition: 'transform 0.3s cubic-bezier(0.16, 1, 0.3, 1)', 
                transform: expandedSquads['youtube-black-screen'] ? 'rotate(0deg)' : 'rotate(-90deg)',
                opacity: 0.5,
                flexShrink: 0
              }} 
            />
          </div>
          <div 
            className="sub-menu" 
            style={{ 
              maxHeight: expandedSquads['youtube-black-screen'] ? '500px' : '0px',
              overflow: 'hidden',
              opacity: expandedSquads['youtube-black-screen'] ? 1 : 0,
              transition: 'max-height 0.35s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.25s ease',
              marginTop: expandedSquads['youtube-black-screen'] ? '4px' : '0px',
              paddingLeft: '8px'
            }}
          >
            <div 
              className={`nav-item ${selectedSquad === 'youtube-black-screen' && activeTab === 'dashboard' ? 'active' : ''}`}
              onClick={() => { setSelectedSquad('youtube-black-screen'); setActiveTab('dashboard'); }}
            >
              <BarChart2 size={16} /> Visão Geral
            </div>
            <div 
              className={`nav-item ${selectedSquad === 'youtube-black-screen' && activeTab === 'agendamento' ? 'active' : ''}`}
              onClick={() => { setSelectedSquad('youtube-black-screen'); setActiveTab('agendamento'); }}
            >
              <PlusCircle size={16} /> Agendar Vídeo
            </div>
            <div 
              className={`nav-item ${selectedSquad === 'youtube-black-screen' && activeTab === 'crons' ? 'active' : ''}`}
              onClick={() => { setSelectedSquad('youtube-black-screen'); setActiveTab('crons'); }}
            >
              <Clock size={16} /> Gerenciar Crons
            </div>
            <div 
              className={`nav-item ${selectedSquad === 'youtube-black-screen' && activeTab === 'calendario' ? 'active' : ''}`}
              onClick={() => { setSelectedSquad('youtube-black-screen'); setActiveTab('calendario'); }}
            >
              <CalendarDays size={16} /> Calendário
            </div>
            <div 
              className={`nav-item ${selectedSquad === 'youtube-black-screen' && activeTab === 'historico' ? 'active' : ''}`}
              onClick={() => { setSelectedSquad('youtube-black-screen'); setActiveTab('historico'); }}
            >
              <History size={16} /> Histórico
            </div>
            <div 
              className={`nav-item ${selectedSquad === 'youtube-black-screen' && activeTab === 'configuracoes' ? 'active' : ''}`}
              onClick={() => { setSelectedSquad('youtube-black-screen'); setActiveTab('configuracoes'); }}
            >
              <Settings size={16} /> Configurações
            </div>
          </div>
        </div>

        <div className="squad-group" style={{ opacity: 0.3 }}>
          <div className="squad-header">
            <div className="squad-icon" style={{background: '#333'}}></div>
            + Novo Squad
          </div>
        </div>
      </div>
      
      {/* Conteúdo Principal */}
      <div className="main-content glass-panel">
        {/* Cabeçalho de Conteúdo com Status do Cron */}
        <div className="main-content-header">
          <div className="squad-name-header">Squad {selectedSquad === 'conexao_artificial' ? 'Conexão Artificial' : 'YouTube Black Screen'}</div>
          {renderCronStatus()}
        </div>
        
        {/* ABA: DASHBOARD */}
        {activeTab === 'dashboard' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            <div>
              <h1>Visão Geral</h1>
              <div className="subtitle">Métricas e status em tempo real do squad Conexão Artificial.</div>
            </div>

            {/* Grid de Métricas */}
            <div className="metrics-grid">
              <div className="metric-card">
                <div className="metric-title" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <CheckCircle size={12} className="text-green-500" /> Publicados
                </div>
                <div className="metric-value">{publishedCount}</div>
                <div className="metric-subtitle">Episódios no YouTube</div>
              </div>

              <div className="metric-card">
                <div className="metric-title" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <Clock size={12} className="text-amber-500" /> Fila de Produção
                </div>
                <div className="metric-value">{queueCount}</div>
                <div className="metric-subtitle">Aguardando execução</div>
              </div>

              <div className="metric-card">
                <div className="metric-title" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <TrendingUp size={12} className="text-indigo-500" /> Taxa de Sucesso
                </div>
                <div className="metric-value">{successRate}%</div>
                <div className="metric-subtitle">Geração sem erros</div>
              </div>

              <div className="metric-card">
                <div className="metric-title" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <AlertTriangle size={12} className="text-red-500" /> Falhas / Cancelados
                </div>
                <div className="metric-value">{failedCount + cancelledCount}</div>
                <div className="metric-subtitle">{failedCount} falhas | {cancelledCount} cancelados</div>
              </div>
            </div>

            {/* Visualizador de Pipeline em Tempo Real */}
            <div>
              <label style={{ marginBottom: '12px', display: 'block' }}>Pipeline de Produção</label>
              <div className="pipeline-visualizer">
                <div className={`pipeline-step ${queueCount > 0 ? 'active' : ''}`}>
                  <div className="pipeline-icon">
                    <Calendar size={16} />
                  </div>
                  <div className="pipeline-label">Agendado</div>
                </div>

                <div className={`pipeline-step ${isCurrentlyProcessing ? 'active' : ''}`}>
                  <div className="pipeline-icon">
                    {isCurrentlyProcessing ? <Loader2 size={16} className="animate-spin" /> : <Clock size={16} />}
                  </div>
                  <div className="pipeline-label">Processando</div>
                </div>

                <div className={`pipeline-step ${!isCurrentlyProcessing && lastEpisode?.status === 'completed' ? 'active' : ''}`}>
                  <div className="pipeline-icon">
                    <Tv size={16} />
                  </div>
                  <div className="pipeline-label">Postado</div>
                </div>
              </div>
            </div>

            {/* Atividade Recente */}
            <div className="queue-list" style={{ marginTop: '0' }}>
              <label>Atividade Recente</label>
              {episodes.slice(0, 3).length === 0 ? (
                <div style={{color: 'var(--text-muted)', fontSize: '13px'}}>Nenhuma atividade registrada.</div>
              ) : (
                episodes.slice(0, 3).map(ep => (
                  <div key={ep.id} className="queue-item">
                    <div>
                      <div className="queue-item-title">{ep.topic}</div>
                      <div className="queue-item-time">{new Date(ep.schedule_time || ep.created_at).toLocaleString()}</div>
                    </div>
                    <div className="actions-wrapper">
                      <button 
                        className="action-btn" 
                        title={ep.script_text ? 'Ver Roteiro' : 'Roteiro ainda não gerado'}
                        onClick={() => setSelectedEpisodeForScript(ep)}
                        style={{ marginRight: '4px' }}
                      >
                        <FileText size={14} />
                      </button>
                      <div className={`status-badge status-${ep.status}`}>
                        {ep.status === 'pending' ? 'AGENDADO' : ep.status.toUpperCase()}
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        {/* ABA: GERENCIAR CRONS */}
        {activeTab === 'crons' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <h1>Gerenciar Crons</h1>
                <div className="subtitle">Visualize e gerencie a fila de execuções automatizadas e agendamentos futuros.</div>
              </div>
              <button 
                className="btn-primary" 
                onClick={() => setActiveTab('agendamento')}
                style={{ padding: '10px 18px', fontSize: '13px' }}
              >
                <PlusCircle size={14} /> Novo Agendamento
              </button>
            </div>

            {/* Resumo da Fila */}
            <div className="metrics-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', marginBottom: '8px' }}>
              <div className="metric-card">
                <div className="metric-title" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <Clock size={12} className="text-amber-500" /> Agendados (Fila)
                </div>
                <div className="metric-value">{activeQueue.filter(ep => ep.status === 'pending').length}</div>
                <div className="metric-subtitle">Aguardando disparo do cron</div>
              </div>
              <div className="metric-card">
                <div className="metric-title" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <Loader2 size={12} className="text-indigo-500 animate-spin" /> Processando Agora
                </div>
                <div className="metric-value">{activeQueue.filter(ep => ep.status === 'processing').length}</div>
                <div className="metric-subtitle">Geração de áudio/vídeo ativa</div>
              </div>
            </div>

            {/* Tabela / Lista de Crons */}
            <div className="queue-list" style={{ marginTop: 0 }}>
              <label>Crons Agendados</label>
              {activeQueue.length === 0 ? (
                <div style={{
                  background: 'rgba(255,255,255,0.01)',
                  border: '1px dashed var(--glass-border)',
                  borderRadius: '16px',
                  padding: '40px 20px',
                  textAlign: 'center',
                  color: 'var(--text-muted)',
                  fontSize: '13px'
                }}>
                  Nenhum cron ativo ou agendado na fila de produção.
                </div>
              ) : (
                activeQueue.map(ep => (
                  <div key={ep.id} className="queue-item" style={{ background: 'rgba(255,255,255,0.01)' }}>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                      <div className="queue-item-title" style={{ fontSize: '15px', fontWeight: '600' }}>{ep.topic}</div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
                        <div className="queue-item-time" style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                          <Clock size={12} /> {formatDateTime(ep.schedule_time || ep.created_at)}
                        </div>
                        <span style={{ fontSize: '11px', color: 'var(--text-muted)', background: 'rgba(255,255,255,0.04)', padding: '2px 6px', borderRadius: '4px' }}>
                          Ton: {tonVoiceLabels[ep.voice_ton] || 'Padrão'} | Bia: {biaVoiceLabels[ep.voice_bia] || 'Padrão'}
                        </span>
                      </div>
                    </div>

                    <div className="actions-wrapper">
                      <button 
                        className="action-btn" 
                        title={ep.script_text ? 'Ver Roteiro' : 'Roteiro ainda não gerado'}
                        onClick={() => setSelectedEpisodeForScript(ep)}
                        style={{ marginRight: '4px' }}
                      >
                        <FileText size={14} />
                      </button>
                      <div className={`status-badge status-${ep.status}`} style={{ marginRight: '8px' }}>
                        {ep.status === 'pending' ? 'AGENDADO' : ep.status.toUpperCase()}
                      </div>
                      
                      {ep.status === 'pending' && (
                        <>
                          <button 
                            className="action-btn btn-edit" 
                            title="Editar Cron / Agendamento"
                            onClick={() => handleOpenEditModal(ep)}
                            style={{ marginRight: '4px' }}
                          >
                            <Edit3 size={14} />
                          </button>
                          <button 
                            className="action-btn btn-cancel" 
                            title="Pausar / Tirar da Fila"
                            onClick={() => handleCancelEpisode(ep.id)}
                          >
                            <XCircle />
                          </button>
                          <button 
                            className="action-btn btn-delete" 
                            title="Excluir Permanentemente"
                            onClick={() => handleDeleteEpisode(ep.id)}
                          >
                            <Trash2 />
                          </button>
                        </>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        {/* ABA: AGENDAMENTO (FILA DE PRODUÇÃO) */}
        {activeTab === 'agendamento' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            <div>
              <h1>{selectedSquad === 'conexao_artificial' ? 'Agendar Episódio' : 'Agendar Vídeo'}</h1>
              <div className="subtitle">Configure a pauta e a quantidade para enfileirar na produção do {selectedSquad === 'conexao_artificial' ? 'squad Conexão Artificial' : 'squad YouTube Black Screen'}.</div>
            </div>
            
            <div className="form-group">
              <label>{selectedSquad === 'conexao_artificial' ? 'Pauta do Episódio (Opcional)' : 'Pauta / Cenário da Chuva (Opcional)'}</label>
              <input 
                type="text" 
                placeholder={selectedSquad === 'conexao_artificial' ? "Ex: Robôs que sentem dor física..." : "Ex: Chuva forte na floresta com trovões distantes..."}
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
              />
            </div>

            <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px'}}>
              <div className="form-group">
                <label>Frequência</label>
                <CustomSelect options={freqOptions} value={freq} onChange={setFreq} />
              </div>
              <div className="form-group">
                <label>Quantidade</label>
                <CustomSelect options={qtyOptions} value={qty} onChange={setQty} />
              </div>
            </div>

            {(freq === 'Personalizado...' || qty === 'Personalizado...') && (
              <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginTop: '-12px'}}>
                <div>
                  {freq === 'Personalizado...' ? (
                    <div className="form-group">
                      <label style={{fontSize: '11px', color: 'var(--accent)'}}>Digitar Frequência</label>
                      <input 
                        type="text" 
                        placeholder="Ex: A cada 5 horas, Diariamente às 22:00, etc."
                        value={customFreq}
                        onChange={(e) => setCustomFreq(e.target.value)}
                      />
                    </div>
                  ) : <div />}
                </div>
                <div>
                  {qty === 'Personalizado...' ? (
                    <div className="form-group">
                      <label style={{fontSize: '11px', color: 'var(--accent)'}}>Digitar Quantidade</label>
                      <input 
                        type="text" 
                        placeholder="Ex: 15 Episódios, 100 Episódios, etc."
                        value={customQty}
                        onChange={(e) => setCustomQty(e.target.value)}
                      />
                    </div>
                  ) : <div />}
                </div>
              </div>
            )}

            <button className="btn-primary" onClick={handleSchedule} disabled={isSubmitting}>
              {isSubmitting ? <Loader2 className="animate-spin" size={18} /> : '✨ Agendar Produção'}
            </button>

            <div className="queue-list">
              <label>Fila de Produção Ativa</label>
              {activeQueue.length === 0 ? (
                <div style={{color: 'var(--text-muted)', fontSize: '13px'}}>Nenhum episódio ativo na fila.</div>
              ) : (
                activeQueue.map(ep => (
                  <div key={ep.id} className="queue-item">
                    <div>
                      <div className="queue-item-title">{ep.topic}</div>
                      <div className="queue-item-time">{new Date(ep.schedule_time || ep.created_at).toLocaleString()}</div>
                    </div>
                    
                    <div className="actions-wrapper">
                      <button 
                        className="action-btn" 
                        title={ep.script_text ? 'Ver Roteiro' : 'Roteiro ainda não gerado'}
                        onClick={() => setSelectedEpisodeForScript(ep)}
                        style={{ marginRight: '4px' }}
                      >
                        <FileText size={14} />
                      </button>
                      <div className={`status-badge status-${ep.status}`} style={{ marginRight: '8px' }}>
                        {ep.status === 'pending' ? 'AGENDADO' : ep.status.toUpperCase()}
                      </div>
                      
                      {ep.status === 'pending' && (
                        <>
                          <button 
                            className="action-btn btn-edit" 
                            title="Editar Agendamento"
                            onClick={() => handleOpenEditModal(ep)}
                            style={{ marginRight: '4px' }}
                          >
                            <Edit3 size={14} />
                          </button>
                          <button 
                            className="action-btn btn-cancel" 
                            title="Tirar da Fila de Postagem"
                            onClick={() => handleCancelEpisode(ep.id)}
                          >
                            <XCircle />
                          </button>
                          <button 
                            className="action-btn btn-delete" 
                            title="Excluir Permanentemente"
                            onClick={() => handleDeleteEpisode(ep.id)}
                          >
                            <Trash2 />
                          </button>
                        </>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        {/* ABA: HISTÓRICO */}
        {activeTab === 'historico' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            <div>
              <h1>Histórico de Episódios</h1>
              <div className="subtitle">Acompanhe todos os episódios criados, postados, falhos ou cancelados.</div>
            </div>

            {/* Filtros de Status */}
            <div className="filters-container">
              <button 
                className={`filter-btn ${filterStatus === 'todos' ? 'active' : ''}`}
                onClick={() => setFilterStatus('todos')}
              >
                Todos ({episodes.length})
              </button>
              <button 
                className={`filter-btn ${filterStatus === 'completed' ? 'active' : ''}`}
                onClick={() => setFilterStatus('completed')}
              >
                Publicados ({episodes.filter(ep => ep.status === 'completed').length})
              </button>
              <button 
                className={`filter-btn ${filterStatus === 'queue' ? 'active' : ''}`}
                onClick={() => setFilterStatus('queue')}
              >
                Na Fila ({episodes.filter(ep => ep.status === 'pending' || ep.status === 'processing').length})
              </button>
              <button 
                className={`filter-btn ${filterStatus === 'failed' ? 'active' : ''}`}
                onClick={() => setFilterStatus('failed')}
              >
                Com Erro ({episodes.filter(ep => ep.status === 'failed').length})
              </button>
              <button 
                className={`filter-btn ${filterStatus === 'cancelled' ? 'active' : ''}`}
                onClick={() => setFilterStatus('cancelled')}
              >
                Cancelados ({episodes.filter(ep => ep.status === 'cancelled').length})
              </button>
            </div>

            {/* Lista do Histórico */}
            <div className="history-list">
              {filteredHistory.length === 0 ? (
                <div style={{color: 'var(--text-muted)', fontSize: '13px', padding: '16px 0'}}>
                  Nenhum episódio encontrado para este filtro.
                </div>
              ) : (
                filteredHistory.map(ep => (
                  <div key={ep.id} className="history-item">
                    <div className="history-item-header">
                      <div>
                        <div className="queue-item-title" style={{ fontSize: '15px' }}>{ep.topic}</div>
                        <div className="queue-item-time" style={{ marginTop: '4px' }}>
                          Criado em: {new Date(ep.created_at).toLocaleString()}
                        </div>
                      </div>
                      
                      <div className="actions-wrapper">
                        <div className={`status-badge status-${ep.status}`}>
                          {ep.status === 'pending' ? 'AGENDADO' : ep.status.toUpperCase()}
                        </div>
                        
                        {(ep.status === 'cancelled' || ep.status === 'failed') && (
                          <button 
                            className="action-btn btn-reschedule" 
                            title="Reagendar Postagem"
                            onClick={() => handleRescheduleEpisode(ep.id)}
                          >
                            <RefreshCw />
                          </button>
                        )}
                        
                        {ep.status !== 'processing' && (
                          <button 
                            className="action-btn btn-delete" 
                            title="Excluir Permanentemente"
                            onClick={() => handleDeleteEpisode(ep.id)}
                          >
                            <Trash2 />
                          </button>
                        )}
                      </div>
                    </div>

                    {/* Exibir erro se houver */}
                    {ep.status === 'failed' && ep.error_message && (
                      <div className="error-details">
                        <strong>Erro de Execução:</strong><br />
                        {ep.error_message}
                      </div>
                    )}

                    {/* Rodapé com Links */}
                    <div className="history-item-footer">
                      {ep.status === 'completed' && ep.youtube_url ? (
                        <a 
                          href={ep.youtube_url} 
                          target="_blank" 
                          rel="noopener noreferrer" 
                          className="history-link"
                        >
                          <ExternalLink size={12} /> Assistir no YouTube
                        </a>
                      ) : <div />}
                      
                      <button 
                        onClick={() => setSelectedEpisodeForScript(ep)}
                        className="history-link"
                        style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 0 }}
                      >
                        <FileText size={12} /> {ep.script_text ? 'Ver Roteiro' : 'Roteiro (Aguardando)'}
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        {/* ABA: CALENDÁRIO */}
        {activeTab === 'calendario' && (
          <div className="calendar-container">
            <div>
              <h1>Calendário de Episódios</h1>
              <div className="subtitle">Gerencie e visualize a distribuição dos episódios ao longo dos meses.</div>
            </div>

            {/* Cabeçalho de Navegação do Mês */}
            <div className="calendar-navbar">
              <div className="calendar-month-title">{monthYearTitle}</div>
              <div className="calendar-nav-buttons">
                <button className="calendar-nav-btn" onClick={handlePrevMonth} title="Mês Anterior">
                  <ChevronLeft size={20} />
                </button>
                <button className="calendar-nav-btn" onClick={handleNextMonth} title="Próximo Mês">
                  <ChevronRight size={20} />
                </button>
              </div>
            </div>

            {/* Grid do Calendário */}
            <div>
              <div className="calendar-grid" style={{ marginBottom: '8px' }}>
                {['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'].map(wd => (
                  <div key={wd} className="calendar-weekday">{wd}</div>
                ))}
              </div>
              <div className="calendar-grid">
                {calendarDaysGrid.map((day, idx) => {
                  if (day === null) {
                    return <div key={`empty-${idx}`} className="calendar-cell empty" />;
                  }

                  // Verificar se é hoje
                  const today = new Date();
                  const isToday = currentDate && 
                    today.getDate() === day && 
                    today.getMonth() === currentDate.getMonth() && 
                    today.getFullYear() === currentDate.getFullYear();

                  const dateStr = currentDate ? `${currentDate.getFullYear()}-${String(currentDate.getMonth() + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}` : '';
                  const isSelected = selectedDateStr === dateStr;

                  // Filtrar episódios deste dia
                  const dayEpisodes = episodes.filter(ep => {
                    const epDate = new Date(ep.schedule_time || ep.created_at);
                    const epDateStr = `${epDate.getFullYear()}-${String(epDate.getMonth() + 1).padStart(2, '0')}-${String(epDate.getDate()).padStart(2, '0')}`;
                    return epDateStr === dateStr;
                  });

                  return (
                    <div 
                      key={`day-${day}`} 
                      className={`calendar-cell ${isToday ? 'today' : ''} ${isSelected ? 'selected' : ''}`}
                      onClick={() => handleDayClick(day)}
                    >
                      <div className="calendar-cell-day">{day}</div>
                      {dayEpisodes.length > 0 && (
                        <div className="calendar-cell-indicators">
                          {dayEpisodes.slice(0, 4).map(ep => (
                            <span 
                              key={ep.id} 
                              className={`calendar-dot ${ep.status}`} 
                              title={`${ep.topic} (${ep.status.toUpperCase()})`}
                            />
                          ))}
                          {dayEpisodes.length > 4 && (
                            <span style={{ fontSize: '9px', color: 'var(--text-muted)', fontWeight: '600' }}>
                              +{dayEpisodes.length - 4}
                            </span>
                          )}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Painel de Detalhes do Dia Selecionado em Formato de Popup/Modal */}
            {selectedDateStr && (
              <div className="calendar-modal-overlay" onClick={() => setSelectedDateStr(null)}>
                <div className="calendar-modal-box" onClick={(e) => e.stopPropagation()}>
                  <div className="calendar-modal-header">
                    <div className="calendar-modal-title">
                      Episódios agendados para {selectedDateStr.split('-').reverse().join('/')}
                    </div>
                    <button className="calendar-modal-close" onClick={() => setSelectedDateStr(null)} title="Fechar">
                      <X size={18} />
                    </button>
                  </div>

                  <div className="calendar-modal-content">
                    {selectedDayEpisodes.length === 0 ? (
                      <div style={{ color: 'var(--text-muted)', fontSize: '13px', padding: '8px 0', textAlign: 'center' }}>
                        Nenhum episódio agendado para esta data.
                      </div>
                    ) : (
                      selectedDayEpisodes.map(ep => (
                        <div key={ep.id} className="queue-item" style={{ background: 'rgba(255,255,255,0.01)' }}>
                          <div>
                            <div className="queue-item-title">{ep.topic}</div>
                            <div className="queue-item-time">
                              {ep.status === 'completed' 
                                ? `Publicado em: ${formatDateTime(ep.schedule_time || ep.created_at)}` 
                                : ep.status === 'pending' || ep.status === 'processing'
                                ? `Agendado para: ${formatDateTime(ep.schedule_time || ep.created_at)}`
                                : `Planejado para: ${formatDateTime(ep.schedule_time || ep.created_at)}`
                              }
                            </div>
                          </div>
                          <div className="actions-wrapper">
                            <button 
                              className="action-btn" 
                              title={ep.script_text ? 'Ver Roteiro' : 'Roteiro ainda não gerado'}
                              onClick={() => { setSelectedEpisodeForScript(ep); setSelectedDateStr(null); }}
                              style={{ marginRight: '4px' }}
                            >
                              <FileText size={14} />
                            </button>
                            <div className={`status-badge status-${ep.status}`} style={{ marginRight: '8px' }}>
                              {ep.status === 'pending' ? 'AGENDADO' : ep.status.toUpperCase()}
                            </div>

                            {ep.status === 'pending' && (
                              <>
                                <button 
                                  className="action-btn btn-edit" 
                                  title="Editar Agendamento"
                                  onClick={() => handleOpenEditModal(ep)}
                                  style={{ marginRight: '4px' }}
                                >
                                  <Edit3 size={14} />
                                </button>
                                <button 
                                  className="action-btn btn-cancel" 
                                  title="Tirar da Fila de Postagem"
                                  onClick={() => handleCancelEpisode(ep.id)}
                                >
                                  <XCircle />
                                </button>
                                <button 
                                  className="action-btn btn-delete" 
                                  title="Excluir Permanentemente"
                                  onClick={() => handleDeleteEpisode(ep.id)}
                                >
                                  <Trash2 />
                                </button>
                              </>
                            )}

                            {(ep.status === 'cancelled' || ep.status === 'failed') && (
                              <>
                                <button 
                                  className="action-btn btn-reschedule" 
                                  title="Reagendar Postagem"
                                  onClick={() => handleRescheduleEpisode(ep.id)}
                                >
                                  <RefreshCw />
                                </button>
                                <button 
                                  className="action-btn btn-delete" 
                                  title="Excluir Permanentemente"
                                  onClick={() => handleDeleteEpisode(ep.id)}
                                >
                                  <Trash2 />
                                </button>
                              </>
                            )}
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* ABA: CONFIGURAÇÕES */}
        {activeTab === 'configuracoes' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            <div>
              <h1>Configurações do Squad</h1>
              <div className="subtitle">{selectedSquad === 'conexao_artificial' ? 'Escolha o modelo de IA que servirá como cérebro e as vozes do podcast.' : 'Escolha o modelo de IA que servirá como cérebro para criar os roteiros do vídeo de sono.'}</div>
            </div>
            
            {/* Bloco de Carregamento */}
            {isLoadingSettings ? (
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-muted)' }}>
                <Loader2 className="animate-spin" size={16} /> Carregando configurações...
              </div>
            ) : (
              <>
                 <div className="form-group">
                  <label>Cérebro (Modelo de IA - OmniRoute)</label>
                  <CustomSelect 
                    options={Object.values(modelLabels)} 
                    value={modelLabels[settings.omni_model] || settings.omni_model} 
                    onChange={(label) => setSettings({ ...settings, omni_model: modelKeys[label] })} 
                  />
                </div>

                 {selectedSquad === 'conexao_artificial' && (
                   <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px'}}>
                    <div className="form-group">
                      <label>Modelo de Voz - Ton (Apresentador)</label>
                      <CustomSelect 
                        options={Object.values(tonVoiceLabels)} 
                        value={tonVoiceLabels[settings.voice_ton] || settings.voice_ton} 
                        onChange={(label) => setSettings({ ...settings, voice_ton: tonVoiceKeys[label] })} 
                      />
                    </div>
                    <div className="form-group">
                      <label>Modelo de Voz - Bia (Apresentadora)</label>
                      <CustomSelect 
                        options={Object.values(biaVoiceLabels)} 
                        value={biaVoiceLabels[settings.voice_bia] || settings.voice_bia} 
                        onChange={(label) => setSettings({ ...settings, voice_bia: biaVoiceKeys[label] })} 
                      />
                    </div>
                  </div>
                 )}

                <button className="btn-primary" onClick={handleSaveSettings} disabled={isSavingSettings}>
                  {isSavingSettings ? <Loader2 className="animate-spin" size={18} /> : '💾 Salvar Configurações'}
                </button>
              </>
            )}
          </div>
        )}

      </div>

      {/* Modal de Edição de Agendamento */}
      {selectedEpisodeForEdit && (
        <div 
          className="fixed inset-0 z-[2000] bg-black/85 backdrop-blur-md flex items-center justify-center p-4"
          onClick={() => setSelectedEpisodeForEdit(null)}
        >
          <div 
            className="bg-[#0b0b0e] border border-white/10 w-full max-w-md flex flex-col gap-5 shadow-2xl shadow-indigo-500/10 overflow-hidden"
            style={{ borderRadius: '16px', padding: '28px 32px' }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="flex justify-between items-center border-b border-white/10 pb-4">
              <div className="flex flex-col gap-1">
                <span className="text-[10px] font-bold text-[#8a96ff] uppercase tracking-widest">
                  Editar Agendamento
                </span>
                <span className="text-base font-bold text-white mt-0.5">
                  Modificar Episódio Pendente
                </span>
              </div>
              <button 
                className="text-gray-400 hover:text-white transition-colors duration-200 p-1 hover:bg-white/5 rounded-full"
                onClick={() => setSelectedEpisodeForEdit(null)}
                title="Fechar"
              >
                <X size={18} />
              </button>
            </div>

            {/* Body */}
            <div className="flex flex-col gap-4">
              <div className="form-group" style={{ marginBottom: 0 }}>
                <label style={{ fontSize: '12px', marginBottom: '6px', display: 'block', color: 'var(--text-muted)' }}>
                  Tema / Pauta
                </label>
                <input 
                  type="text" 
                  className="edit-input"
                  placeholder="Pauta do episódio..."
                  value={editTopic}
                  onChange={(e) => setEditTopic(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '10px 14px',
                    background: 'rgba(255,255,255,0.03)',
                    border: '1px solid rgba(255,255,255,0.08)',
                    borderRadius: '8px',
                    color: 'white',
                    fontSize: '14px',
                    outline: 'none',
                    transition: 'all 0.2s'
                  }}
                />
              </div>

              <div className="form-group" style={{ marginBottom: 0 }}>
                <label style={{ fontSize: '12px', marginBottom: '6px', display: 'block', color: 'var(--text-muted)' }}>
                  Data e Horário de Postagem
                </label>
                <input 
                  type="datetime-local" 
                  className="edit-input"
                  value={editScheduleTime}
                  onChange={(e) => setEditScheduleTime(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '10px 14px',
                    background: 'rgba(255,255,255,0.03)',
                    border: '1px solid rgba(255,255,255,0.08)',
                    borderRadius: '8px',
                    color: 'white',
                    fontSize: '14px',
                    outline: 'none',
                    transition: 'all 0.2s'
                  }}
                />
              </div>
            </div>

            {/* Footer */}
            <div className="flex justify-end gap-3 pt-3 border-t border-white/10 mt-2">
              <button 
                className="btn-secondary" 
                onClick={() => setSelectedEpisodeForEdit(null)}
                style={{
                  padding: '8px 16px',
                  background: 'rgba(255,255,255,0.05)',
                  border: '1px solid rgba(255,255,255,0.05)',
                  borderRadius: '8px',
                  color: 'white',
                  fontSize: '13px',
                  cursor: 'pointer'
                }}
              >
                Cancelar
              </button>
              <button 
                className="btn-primary" 
                onClick={handleSaveEdit}
                disabled={isEditing}
                style={{
                  padding: '8px 16px',
                  background: 'linear-gradient(135deg, #6366f1 0%, #a855f7 100%)',
                  border: 'none',
                  borderRadius: '8px',
                  color: 'white',
                  fontSize: '13px',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px'
                }}
              >
                {isEditing ? <Loader2 className="animate-spin" size={14} /> : 'Salvar Alterações'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal / Popup do Roteiro */}
      {selectedEpisodeForScript && (
        <div 
          className="fixed inset-0 z-[2000] bg-black/85 backdrop-blur-md flex items-center justify-center p-4" 
          onClick={() => setSelectedEpisodeForScript(null)}
        >
          <div 
            className="bg-[#0b0b0e] border border-white/10 w-full max-w-3xl max-h-[85vh] flex flex-col gap-6 shadow-2xl shadow-indigo-500/10 overflow-hidden" 
            style={{ borderRadius: '16px', padding: '32px 36px' }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="flex justify-between items-start border-b border-white/10 pb-5" style={{ marginTop: '4px' }}>
              <div className="flex flex-col gap-1.5" style={{ paddingRight: '16px' }}>
                <span className="text-[10px] md:text-xs font-bold text-[#8a96ff] uppercase tracking-widest">
                  Roteiro do Episódio
                </span>
                <span className="text-base md:text-lg font-bold text-white mt-1 leading-snug" style={{ wordBreak: 'break-word' }}>
                  {selectedEpisodeForScript.topic}
                </span>
              </div>
              <button 
                className="text-gray-400 hover:text-white transition-colors duration-200 p-1.5 hover:bg-white/5 rounded-full"
                onClick={() => setSelectedEpisodeForScript(null)} 
                title="Fechar"
                style={{ flexShrink: 0 }}
              >
                <X size={18} />
              </button>
            </div>

            {/* Conteúdo */}
            <div className="flex-1 overflow-y-auto pr-2 flex flex-col gap-5" style={{ paddingLeft: '8px', paddingRight: '8px' }}>
              {selectedEpisodeForScript.script_text ? (
                <div className="flex flex-col gap-5">
                  {(() => {
                    const renderSpeechText = (text) => {
                      const parts = text.split(/(\[[a-z\s]+\])/i);
                      return parts.map((part, pIdx) => {
                        if (part.startsWith('[') && part.endsWith(']')) {
                          return (
                            <span key={pIdx} className="text-emerald-400 font-semibold italic text-xs md:text-sm mx-1 bg-emerald-500/10 px-1.5 py-0.5 rounded inline-block my-0.5">
                              {part}
                            </span>
                          );
                        }
                        return <span key={pIdx}>{part}</span>;
                      });
                    };

                    return selectedEpisodeForScript.script_text.split('\n').map((line, idx) => {
                      const cleanLine = line.trim();
                      if (!cleanLine) return null;

                      // Regex para capturar oradores (Tom e Bia)
                      const match = cleanLine.match(/^(Tom|Bia)\s*:\s*(.*)$/i);
                      if (match) {
                        const speaker = match[1].toLowerCase();
                        const speechText = match[2].strip ? match[2].strip() : match[2].trim();
                        const isTom = speaker === 'tom';
                        
                        return (
                          <div 
                            key={idx} 
                            className={`transition-all border-l-4`}
                            style={{
                              padding: '20px 24px',
                              borderRadius: '0px 12px 12px 0px',
                              backgroundColor: isTom ? 'rgba(99, 102, 241, 0.03)' : 'rgba(236, 72, 153, 0.03)',
                              borderLeftColor: isTom ? '#5E6AD2' : '#ec4899',
                              borderLeftWidth: '4px'
                            }}
                          >
                            <span 
                              className={`font-bold text-xs md:text-sm uppercase tracking-wider mb-2.5 block ${
                                isTom ? 'text-indigo-400' : 'text-pink-400'
                              }`}
                            >
                              {match[1]}
                            </span>
                            <span className="text-gray-200 text-sm md:text-[15px] block" style={{ lineHeight: '1.75' }}>
                              {renderSpeechText(speechText)}
                            </span>
                          </div>
                        );
                      }

                      // Se não bater no formato padrão, exibe a linha bruta
                      return (
                        <div 
                          key={idx} 
                          className="transition-colors text-gray-300 text-sm"
                          style={{
                            padding: '16px 20px',
                            borderRadius: '0px 12px 12px 0px',
                            backgroundColor: 'rgba(255, 255, 255, 0.02)',
                            borderLeft: '4px solid rgba(255, 255, 255, 0.1)',
                            lineHeight: '1.75'
                          }}
                        >
                          {renderSpeechText(cleanLine)}
                        </div>
                      );
                    });
                  })()}
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center text-center py-16 px-4 gap-4">
                  <div className="w-12 h-12 rounded-full bg-indigo-500/10 text-[#5E6AD2] flex items-center justify-center mb-2">
                    <FileText size={24} />
                  </div>
                  <div>
                    <h3 className="text-white font-semibold text-base mb-1">
                      Roteiro em Produção
                    </h3>
                    <p className="text-gray-400 text-xs md:text-sm leading-relaxed max-w-sm">
                      Este episódio ainda está na fila de postagem ou está sendo gerado na nuvem.<br />
                      Assim que o robô iniciar o processamento, o roteiro aparecerá aqui automaticamente!
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
