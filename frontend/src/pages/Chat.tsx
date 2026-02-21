import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import api from '../lib/api';
import { MessageSquare, RefreshCw, ChevronDown, ChevronUp, FileText } from 'lucide-react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: Source[];
  timestamp: Date;
}

interface Source {
  source: string;
  page: number;
  snippet: string;
  score: number;
}

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [indexing, setIndexing] = useState(false);
  const [indexStatus, setIndexStatus] = useState<{ indexed: boolean; num_documents: number; num_chunks: number } | null>(null);
  const [expandedSources, setExpandedSources] = useState<Set<number>>(new Set());

  useEffect(() => {
    fetchStatus();
    setMessages([{
      role: 'assistant',
      content: 'Mund të më bësh çfarëdo pyetjeje! Unë mund t\'u përgjigjem pyetjeve rreth dokumenteve bankare, politikave, rregulloreve AML, procedurave KYC, monitorimit të transaksioneve dhe më shumë. Unë kërkoj nëpër të gjitha PDF-et në dosjen bank_docs.',
      timestamp: new Date()
    }]);
  }, []);

  const fetchStatus = async () => {
    try {
      const res = await api.get('/chat/status');
      setIndexStatus(res.data);
    } catch (err) {
      console.error('Error fetching status:', err);
    }
  };

  const handleReindex = async () => {
    try {
      setIndexing(true);
      const res = await api.post('/chat/reindex');
      await fetchStatus();
      alert(`Indeksimi u përfundua! ${res.data.num_chunks} pjesë nga ${res.data.num_documents} dokumente.`);
    } catch (err: any) {
      alert(`Gabim gjatë indeksimit: ${err.message}`);
    } finally {
      setIndexing(false);
    }
  };

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage: Message = {
      role: 'user',
      content: input,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const res = await api.post('/chat/ask', { question: input });
      
      const assistantMessage: Message = {
        role: 'assistant',
        content: res.data.answer,
        sources: res.data.sources,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (err: any) {
      const errorMessage: Message = {
        role: 'assistant',
        content: `Më vjen keq, pati një gabim: ${err.message || 'Dështoi përpunimi i pyetjes suaj'}. Ju lutem provoni përsëri.`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const toggleSources = (index: number) => {
    const newExpanded = new Set(expandedSources);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedSources(newExpanded);
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-2 flex items-center gap-3">
            <MessageSquare className="w-10 h-10 text-blue-600" />
            Asistent i Dokumenteve
          </h1>
          <p className="text-gray-600">Më bëj çfarëdo pyetjeje rreth dokumenteve bankare, politikave dhe rregulloreve</p>
        </div>
        <div className="flex items-center gap-4">
          {indexStatus && (
            <div className="text-sm text-gray-600">
              {indexStatus.indexed ? (
                <span>{indexStatus.num_chunks} pjesë nga {indexStatus.num_documents} dokumente</span>
              ) : (
                <span className="text-orange-600">Nuk është indeksuar</span>
              )}
            </div>
          )}
          <Button
            onClick={handleReindex}
            disabled={indexing}
            variant="outline"
            className="gap-2"
          >
            <RefreshCw className={`w-4 h-4 ${indexing ? 'animate-spin' : ''}`} />
            {indexing ? 'Po indeksohet...' : 'Indekso Përsëri'}
          </Button>
        </div>
      </div>

      <Card className="shadow-xl border-0 bg-white/80 backdrop-blur-sm">
        <CardHeader className="bg-gradient-to-r from-indigo-50 to-blue-50 rounded-t-lg border-b">
          <CardTitle className="flex items-center gap-2">
            <MessageSquare className="w-5 h-5 text-indigo-600" />
            Bisedë me Dokumentet
          </CardTitle>
          <CardDescription>
            Unë mund t'u përgjigjem pyetjeve rreth politikave bankare, rregulloreve AML, procedurave KYC, monitorimit të transaksioneve dhe më shumë bazuar në PDF-et në dosjen bank_docs.
          </CardDescription>
        </CardHeader>
        <CardContent className="p-0">
          <div className="h-[600px] flex flex-col">
            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((message, idx) => (
                <div key={idx}>
                  <div
                    className={`flex gap-3 ${
                      message.role === 'user' ? 'justify-end' : 'justify-start'
                    }`}
                  >
                    {message.role === 'assistant' && (
                      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-md">
                        <MessageSquare className="w-5 h-5 text-white" />
                      </div>
                    )}
                    <div
                      className={`max-w-[80%] rounded-2xl px-4 py-3 shadow-sm ${
                        message.role === 'user'
                          ? 'bg-gradient-to-br from-blue-600 to-blue-700 text-white'
                          : 'bg-white text-gray-800 border border-slate-200'
                      }`}
                    >
                      <div className="whitespace-pre-wrap text-sm leading-relaxed">
                        {message.content}
                      </div>
                      <div
                        className={`text-xs mt-2 ${
                          message.role === 'user' ? 'text-blue-100' : 'text-gray-400'
                        }`}
                      >
                        {message.timestamp.toLocaleTimeString([], {
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </div>
                    </div>
                    {message.role === 'user' && (
                      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-slate-400 to-slate-500 flex items-center justify-center shadow-md">
                        <MessageSquare className="w-5 h-5 text-white" />
                      </div>
                    )}
                  </div>
                  
                  {/* Sources */}
                  {message.role === 'assistant' && message.sources && message.sources.length > 0 && (
                    <div className="mt-2 ml-11">
                      <button
                        onClick={() => toggleSources(idx)}
                        className="flex items-center gap-2 text-xs text-blue-600 hover:text-blue-700 font-medium"
                      >
                        {expandedSources.has(idx) ? (
                          <ChevronUp className="w-4 h-4" />
                        ) : (
                          <ChevronDown className="w-4 h-4" />
                        )}
                        Burimet ({message.sources.length})
                      </button>
                      {expandedSources.has(idx) && (
                        <div className="mt-2 space-y-2 pl-4 border-l-2 border-blue-200">
                          {message.sources.map((source, srcIdx) => (
                            <div key={srcIdx} className="bg-blue-50 rounded-lg p-3 text-sm">
                              <div className="flex items-center gap-2 mb-1">
                                <FileText className="w-4 h-4 text-blue-600" />
                                <span className="font-semibold text-gray-900">{source.source}</span>
                                <span className="text-gray-500">• Faqja {source.page}</span>
                                <span className="ml-auto text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded">
                                  Rezultati: {source.score}
                                </span>
                              </div>
                              <p className="text-gray-700 text-xs mt-1 italic">
                                "{source.snippet}"
                              </p>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
              {loading && (
                <div className="flex gap-3 justify-start">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-md">
                    <MessageSquare className="w-5 h-5 text-white" />
                  </div>
                  <div className="bg-white rounded-2xl px-4 py-3 shadow-sm border border-slate-200">
                    <div className="inline-block animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-blue-600"></div>
                  </div>
                </div>
              )}
            </div>
            
            {/* Input */}
            <div className="border-t border-slate-200 p-4 bg-white rounded-b-lg">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
                  placeholder="Bëj një pyetje rreth dokumenteve..."
                  className="flex-1 px-4 py-3 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                  disabled={loading}
                />
                <Button
                  onClick={handleSend}
                  disabled={loading || !input.trim()}
                  className="px-6 rounded-xl bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 shadow-md transition-all"
                >
                  Dërgo
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

