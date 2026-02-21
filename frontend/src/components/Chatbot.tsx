import { useState, useRef, useEffect } from 'react';
import api from '../lib/api';
import { Button } from './ui/button';
import { Send, Bot, User, Loader2 } from 'lucide-react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface ChatbotProps {
  documentId?: string; // Optional: if not provided, searches all documents
}

interface RAGResult {
  chunk_id?: string;
  similarity?: number;
  text?: string;
  document_id?: string;
  source?: string;
  answer?: string;
}

export default function Chatbot({ documentId }: ChatbotProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: documentId 
        ? 'Ask me anything about this document! I can help you find information, summarize content, and answer questions.' 
        : 'Ask me anything! I can answer questions about banking documents, policies, AML regulations, KYC procedures, transaction monitoring, and more. I search through all documents in the bank_docs directory to provide accurate answers.',
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

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
      const params: any = { q: input };
      if (documentId) {
        params.document_id = documentId;
      }

      const response = await api.get('/rag/query', { params });

      const results: RAGResult[] = response.data.results || [];
      let assistantContent = '';

      if (results.length === 0) {
        // Even if no results, try to show something helpful
        assistantContent = "I couldn't find specific results for this question. Please try:\n\n" +
          "• Asking a more general question (e.g., 'What does the document contain?')\n" +
          "• Using keywords that might be in the documents\n" +
          "• Checking if documents are loaded in the bank_docs directory";
      } else {
        // Use the generated answer if available, otherwise format the results
        const firstResult = results[0];
        if (firstResult.answer) {
          assistantContent = firstResult.answer;
        } else if (firstResult.text) {
          // Fallback: use the text from first result
          assistantContent = "Bazuar në dokumentin, këtu është informacioni që gjetëm:\n\n";
          const text = firstResult.text.length > 500 
            ? firstResult.text.substring(0, 500) + '...' 
            : firstResult.text;
          assistantContent += text;
        } else {
          // Last resort: format all results
          assistantContent = "Bazuar në dokumentin, këtu është informacioni që gjetëm:\n\n";
          results.slice(0, 3).forEach((result: RAGResult, idx: number) => {
            if (result.text) {
              const text = result.text.length > 300 
                ? result.text.substring(0, 300) + '...' 
                : result.text;
              assistantContent += `${idx + 1}. ${text}\n\n`;
            }
          });
        }
      }

      const assistantMessage: Message = {
        role: 'assistant',
        content: assistantContent,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error: any) {
      const errorMessage: Message = {
        role: 'assistant',
        content: `Na vjen keq, pati një gabim: ${error.message || 'Dështoi përpunimi i pyetjes suaj'}. Ju lutem provoni përsëri.`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-full bg-gradient-to-br from-slate-50 to-blue-50 rounded-lg border border-slate-200 shadow-lg">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message, idx) => (
          <div
            key={idx}
            className={`flex gap-3 ${
              message.role === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            {message.role === 'assistant' && (
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-md">
                <Bot className="w-5 h-5 text-white" />
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
                <User className="w-5 h-5 text-white" />
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className="flex gap-3 justify-start">
            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-md">
              <Bot className="w-5 h-5 text-white" />
            </div>
            <div className="bg-white rounded-2xl px-4 py-3 shadow-sm border border-slate-200">
              <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <div className="border-t border-slate-200 p-4 bg-white rounded-b-lg">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={documentId ? "Bëni një pyetje për këtë dokument..." : "Bëni një pyetje për të gjitha dokumentet (bankat, transaksionet, etj.)..."}
            className="flex-1 px-4 py-3 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
            disabled={loading}
          />
          <Button
            onClick={handleSend}
            disabled={loading || !input.trim()}
            className="px-6 rounded-xl bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 shadow-md transition-all"
          >
            {loading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}
