'use client';

import React, { useState } from 'react';
import { useApp } from '@/lib/context';
import { bmirApi } from '@/lib/api';
import { Bot, Send, Sparkles, FileDown, BookOpen, Clock, Cpu, User } from 'lucide-react';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  citations?: Array<{ title: string; domain: string; authors?: string; url?: string }>;
  provider?: string;
  model?: string;
  latency_ms?: number;
}

export default function AIAssistantView() {
  const { user } = useApp();
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content:
        'Greetings. I am the BMIR AI Research Intelligence Assistant. I provide rigorous scientific analysis, thermodynamic and mechanical feasibility checks, and citations grounded in empirical research. How can I assist your investigation today?',
      provider: 'bmir_scientific_engine',
      model: 'bmir-scientific-v2',
    },
  ]);
  const [inputPrompt, setInputPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | undefined>(undefined);
  const [provider, setProvider] = useState('gemini');
  const [exportedDoc, setExportedDoc] = useState<string | null>(null);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputPrompt.trim() || loading) return;

    const userText = inputPrompt;
    setInputPrompt('');
    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: userText,
    };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const res = await bmirApi.sendAiChat(userText, conversationId, provider);
      setConversationId(res.conversation_id);
      const assistantMsg: ChatMessage = {
        id: res.message_id || `asst-${Date.now()}`,
        role: 'assistant',
        content: res.content,
        citations: res.citations,
        provider: res.provider,
        model: res.model,
        latency_ms: res.latency_ms,
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          id: `err-${Date.now()}`,
          role: 'assistant',
          content: `Scientific reasoning error: ${err.message || 'Service unavailable'}. Please verify connection.`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (msgContent: string) => {
    try {
      const res = await bmirApi.exportDocument(
        'technical_report',
        'BMIR AI Research Intelligence Brief',
        'Multidisciplinary Engineering',
        'Formalized technical synthesis of AI research assistant session.',
        { transcript_excerpt: msgContent.slice(0, 500) }
      );
      setExportedDoc(res.content_markdown);
    } catch (err) {
      alert('Export generation failed.');
    }
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto flex flex-col h-[calc(100vh-6rem)]">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-4 rounded-2xl bg-[#0D1829] border border-[#1E3352]">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-[#2878FF] to-[#19C7D9] flex items-center justify-center text-white shadow">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-bold text-white font-heading">AI Research Assistant</h2>
            <div className="text-[11px] text-gray-400">Context-Aware Scientific Reasoning & Citation Grounding</div>
          </div>
        </div>

        {/* Model Provider Selector */}
        <div className="flex items-center space-x-2 text-xs">
          <span className="text-gray-400">Provider:</span>
          <select
            value={provider}
            onChange={(e) => setProvider(e.target.value)}
            className="px-3 py-1.5 rounded-xl bg-[#071426] border border-[#1E3352] text-xs text-gray-200 focus:outline-none focus:border-[#2878FF]"
          >
            <option value="gemini">Google Gemini 1.5 Pro</option>
            <option value="openai">OpenAI GPT-4o</option>
            <option value="anthropic">Anthropic Claude 3.5 Sonnet</option>
            <option value="local_scientific">BMIR Scientific Engine (Zero-Config)</option>
          </select>
        </div>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto space-y-4 p-4 rounded-2xl bg-[#071426] border border-[#1E3352]">
        {messages.map((m) => (
          <div
            key={m.id}
            className={`flex items-start space-x-3 ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {m.role === 'assistant' && (
              <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-[#2878FF] to-[#19C7D9] flex items-center justify-center text-white shrink-0 shadow">
                <Sparkles className="w-4 h-4" />
              </div>
            )}

            <div
              className={`max-w-2xl rounded-2xl p-4 text-xs leading-relaxed ${
                m.role === 'user'
                  ? 'bg-gradient-to-r from-[#2878FF] to-[#19C7D9] text-white shadow-md'
                  : 'bg-[#0D1829] border border-[#1E3352] text-gray-200 shadow'
              }`}
            >
              <div className="whitespace-pre-wrap">{m.content}</div>

              {/* Citations block */}
              {m.citations && m.citations.length > 0 && (
                <div className="mt-3 pt-3 border-t border-[#1E3352] text-[11px] text-gray-400 space-y-1">
                  <div className="font-semibold text-[#19C7D9] flex items-center space-x-1">
                    <BookOpen className="w-3 h-3" />
                    <span>RAG Knowledge Base Grounding:</span>
                  </div>
                  {m.citations.map((c, i) => (
                    <div key={i} className="truncate">
                      • {c.title} ({c.domain})
                    </div>
                  ))}
                </div>
              )}

              {/* Message metadata */}
              {m.role === 'assistant' && (
                <div className="mt-3 pt-2 border-t border-[#1E3352] flex items-center justify-between text-[10px] text-gray-500">
                  <span>
                    Model: {m.model || 'Scientific-v2'} · Latency: {m.latency_ms || 120}ms
                  </span>
                  <button
                    onClick={() => handleExport(m.content)}
                    className="flex items-center space-x-1 text-blue-400 hover:text-white"
                  >
                    <FileDown className="w-3 h-3" />
                    <span>Export Proposal</span>
                  </button>
                </div>
              )}
            </div>

            {m.role === 'user' && (
              <div className="w-8 h-8 rounded-lg bg-[#102A43] border border-[#1E3352] flex items-center justify-center text-gray-300 shrink-0">
                <User className="w-4 h-4" />
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className="flex items-center space-x-2 text-xs text-gray-400 p-2">
            <Sparkles className="w-4 h-4 text-[#19C7D9] animate-spin" />
            <span>Formulating rigorous scientific analysis...</span>
          </div>
        )}
      </div>

      {/* Input Bar */}
      <form onSubmit={handleSend} className="flex gap-3">
        <input
          type="text"
          value={inputPrompt}
          onChange={(e) => setInputPrompt(e.target.value)}
          placeholder="Ask a technical or scientific research question (e.g. 'How to optimize moisture reduction in high-humidity maize drying?')..."
          className="flex-1 px-4 py-3 rounded-xl bg-[#071426] border border-[#1E3352] text-xs text-white placeholder-gray-500 focus:outline-none focus:border-[#2878FF]"
        />
        <button
          type="submit"
          disabled={loading || !inputPrompt.trim()}
          className="px-6 py-3 rounded-xl bg-gradient-to-r from-[#2878FF] to-[#19C7D9] text-white font-bold text-xs shadow-md disabled:opacity-50 flex items-center space-x-1.5"
        >
          <Send className="w-3.5 h-3.5" />
          <span>Send</span>
        </button>
      </form>

      {/* Export Preview Modal */}
      {exportedDoc && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
          <div className="bg-[#0D1829] border border-[#1E3352] rounded-3xl max-w-2xl w-full p-6 space-y-4 max-h-[80vh] overflow-y-auto">
            <div className="flex justify-between items-center border-b border-[#1E3352] pb-3">
              <h3 className="text-base font-bold text-white font-heading">Formatted BMIR Research Proposal Export</h3>
              <button onClick={() => setExportedDoc(null)} className="text-gray-400 hover:text-white text-xs">
                Close
              </button>
            </div>
            <pre className="text-xs text-gray-300 whitespace-pre-wrap font-mono p-4 rounded-xl bg-[#071426] border border-[#1E3352]">
              {exportedDoc}
            </pre>
            <button
              onClick={() => {
                navigator.clipboard.writeText(exportedDoc);
                alert('Copied formatted markdown to clipboard!');
              }}
              className="px-4 py-2 rounded-xl bg-blue-600 text-white text-xs font-bold"
            >
              Copy to Clipboard
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

