'use client';

import React, { useState } from 'react';
import { bmirApi } from '@/lib/api';
import { BookOpen, Search, Sparkles, ExternalLink, FileText, CheckCircle2 } from 'lucide-react';

export default function LiteratureAssistantView() {
  const [inputText, setInputText] = useState(
    'Rapid microwave and warm-air drying kinetics in Zea mays grain to prevent mold formation under humid tropical harvest conditions.'
  );
  const [loading, setLoading] = useState(false);
  const [analysis, setAnalysis] = useState<any>(null);

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim() || loading) return;
    setLoading(true);

    try {
      const data = await bmirApi.analyzeLiterature(inputText);
      setAnalysis(data);
    } catch (err: any) {
      alert(`Literature analysis failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      {/* Header */}
      <div className="p-6 rounded-3xl bg-gradient-to-r from-[#0C1A2E] to-[#0A1626] border border-[#1E3352] space-y-2">
        <div className="inline-flex items-center space-x-1.5 text-xs text-[#19C7D9] font-bold uppercase tracking-wider">
          <BookOpen className="w-3.5 h-3.5" />
          <span>AI Research Literature Assistant</span>
        </div>
        <h2 className="text-2xl font-extrabold text-white font-heading">
          Paper Deconstruction, Methodology Extraction & Gap Analysis
        </h2>
        <p className="text-xs text-gray-400">
          Upload or paste scientific abstracts and research reports to automatically dissect methodology, extract key quantitative findings, and discover unaddressed research gaps cross-referenced with OpenAlex, Crossref, and PubMed.
        </p>
      </div>

      {/* Input */}
      <form onSubmit={handleAnalyze} className="p-6 rounded-2xl bg-[#0D1829] border border-[#1E3352] space-y-4">
        <div>
          <label className="block text-xs font-semibold text-gray-300 mb-1.5">
            Research Paper Title, Abstract, or Full-Text Excerpt
          </label>
          <textarea
            rows={4}
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            className="w-full px-4 py-3 rounded-xl bg-[#071426] border border-[#1E3352] text-xs text-white focus:outline-none focus:border-[#2878FF]"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-[#2878FF] to-[#19C7D9] text-white font-bold text-xs shadow-md disabled:opacity-50 flex items-center space-x-2"
        >
          <Sparkles className="w-3.5 h-3.5" />
          <span>{loading ? 'Deconstructing Literature...' : 'Analyze Scientific Paper'}</span>
        </button>
      </form>

      {/* Output Results */}
      {analysis && (
        <div className="space-y-6">
          <div className="p-6 rounded-2xl bg-[#0D1829] border border-[#1E3352] space-y-3">
            <span className="text-xs font-bold text-[#19C7D9] uppercase tracking-wider">
              Extracted Experimental Methodology
            </span>
            <p className="text-xs text-gray-200 leading-relaxed">{analysis.extracted_methodology}</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="p-6 rounded-2xl bg-[#0D1829] border border-[#1E3352] space-y-3">
              <span className="text-xs font-bold text-emerald-400 uppercase tracking-wider">
                Key Quantitative Findings
              </span>
              <ul className="space-y-2 text-xs text-gray-300">
                {analysis.key_scientific_findings?.map((f: string, i: number) => (
                  <li key={i} className="flex items-start space-x-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                    <span>{f}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="p-6 rounded-2xl bg-[#0D1829] border border-[#1E3352] space-y-3">
              <span className="text-xs font-bold text-amber-400 uppercase tracking-wider">
                Unresolved Research Gaps
              </span>
              <ul className="space-y-2 text-xs text-gray-300">
                {analysis.unresolved_research_gaps?.map((g: string, i: number) => (
                  <li key={i} className="flex items-start space-x-2">
                    <span className="text-amber-400">→</span>
                    <span>{g}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Verified Database Cross References */}
          <div className="p-6 rounded-2xl bg-[#071426] border border-[#1E3352] space-y-3">
            <span className="text-xs font-bold text-white uppercase tracking-wider">
              Verified Scientific Database Cross-References
            </span>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              {analysis.verified_database_cross_references?.map((ref: any, idx: number) => (
                <a
                  key={idx}
                  href={ref.identifier}
                  target="_blank"
                  rel="noreferrer"
                  className="p-3 rounded-xl bg-[#0D1829] border border-[#1E3352] hover:border-cyan-500/40 text-xs flex items-center justify-between text-gray-300 hover:text-white"
                >
                  <span className="font-semibold">{ref.source} Database</span>
                  <ExternalLink className="w-3.5 h-3.5 text-[#19C7D9]" />
                </a>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

