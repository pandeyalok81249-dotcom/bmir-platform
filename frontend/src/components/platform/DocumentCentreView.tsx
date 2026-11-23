'use client';

import React, { useState, useEffect } from 'react';
import { useApp } from '@/lib/context';
import { bmirApi } from '@/lib/api';
import { KnowledgeDocument } from '@/types/bmir';
import {
  FileText,
  Search,
  Download,
  Upload,
  BookOpen,
  Lock,
  CheckCircle2,
  ExternalLink,
  ShieldAlert,
} from 'lucide-react';

export default function DocumentCentreView() {
  const { user } = useApp();
  const [documents, setDocuments] = useState<KnowledgeDocument[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDoc, setSelectedDoc] = useState<KnowledgeDocument | null>(null);

  useEffect(() => {
    bmirApi
      .searchKnowledge()
      .then((data) => {
        setDocuments(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  const filtered = documents.filter(
    (d) =>
      searchQuery === '' ||
      d.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      d.domain.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (d.keywords && d.keywords.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="bg-[#0C1A2E] border border-[#1E3352] rounded-3xl p-6 sm:p-8 flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-xl">
        <div>
          <div className="inline-flex items-center space-x-1.5 text-xs text-[#19C7D9] font-bold uppercase tracking-wider mb-2">
            <FileText className="w-3.5 h-3.5" />
            <span>Research Repository</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white font-heading">
            Document & Knowledge Centre
          </h1>
          <p className="text-xs text-gray-400 mt-1 max-w-2xl">
            Centralized scientific documentation repository housing peer-reviewed publications, technical
            white papers, and experimental test dossiers indexed for semantic retrieval.
          </p>
        </div>
      </div>

      {/* Search Bar */}
      <div className="bg-[#0D1829] border border-[#1E3352] rounded-2xl p-4 flex items-center space-x-3">
        <Search className="w-4 h-4 text-gray-400" />
        <input
          type="text"
          placeholder="Search research papers, technical reports, keywords..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full bg-transparent text-xs text-white focus:outline-none"
        />
      </div>

      {/* Documents Grid */}
      {loading ? (
        <div className="py-20 text-center text-gray-400 text-xs">Loading indexed documents...</div>
      ) : filtered.length === 0 ? (
        <div className="py-16 text-center bg-[#0D1829] border border-[#1E3352] rounded-3xl p-8 space-y-2">
          <ShieldAlert className="w-8 h-8 text-gray-500 mx-auto" />
          <h4 className="text-sm font-bold text-white">No Documents Found</h4>
          <p className="text-xs text-gray-400">
            No research papers or technical dossiers matched your search query.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filtered.map((doc) => (
            <div
              key={doc.id}
              onClick={() => setSelectedDoc(doc)}
              className="bg-[#0D1829] border border-[#1E3352] hover:border-[#2878FF]/60 rounded-2xl p-5 space-y-4 cursor-pointer transition-all shadow-md group flex flex-col justify-between"
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="font-mono text-[10px] font-bold px-2 py-0.5 rounded bg-[#102A43] text-gray-300">
                    {doc.doc_type}
                  </span>
                  <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                    <CheckCircle2 className="w-3 h-3" />
                    <span>Verified Document</span>
                  </span>
                </div>

                <div>
                  <div className="text-[11px] text-[#19C7D9] font-medium">{doc.domain}</div>
                  <h3 className="text-sm font-bold text-white group-hover:text-[#2878FF] transition-colors line-clamp-2">
                    {doc.title}
                  </h3>
                </div>

                <p className="text-xs text-gray-400 line-clamp-3 leading-relaxed">
                  {doc.abstract || doc.content}
                </p>
              </div>

              <div className="pt-3 border-t border-[#1E3352] flex items-center justify-between text-[11px] text-gray-400">
                <span>Authors: <strong className="text-gray-300">{doc.authors || 'BMIR'}</strong></span>
                <span className="text-[#19C7D9] font-semibold flex items-center space-x-1">
                  <span>View Content</span>
                  <ExternalLink className="w-3 h-3" />
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Document Reader Modal */}
      {selectedDoc && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
          <div className="bg-[#0D1829] border border-[#1E3352] rounded-3xl max-w-2xl w-full p-6 sm:p-8 space-y-5 max-h-[90vh] overflow-y-auto text-white shadow-2xl">
            <div className="flex items-center justify-between border-b border-[#1E3352] pb-4">
              <div className="space-y-1">
                <span className="font-mono text-[10px] font-bold px-2 py-0.5 rounded bg-[#102A43] text-gray-300">
                  {selectedDoc.doc_type} · {selectedDoc.domain}
                </span>
                <h3 className="text-lg font-bold font-heading text-white">{selectedDoc.title}</h3>
                <div className="text-xs text-gray-400">Authors: {selectedDoc.authors}</div>
              </div>
              <button
                onClick={() => setSelectedDoc(null)}
                className="p-2 rounded-xl text-gray-400 hover:text-white bg-[#102A43]"
              >
                ✕
              </button>
            </div>

            <div className="space-y-4 text-xs">
              {selectedDoc.abstract && (
                <div className="space-y-1">
                  <div className="font-semibold text-gray-300">Abstract</div>
                  <p className="text-gray-400 leading-relaxed bg-[#071426] p-3 rounded-xl border border-[#1E3352]">
                    {selectedDoc.abstract}
                  </p>
                </div>
              )}

              <div className="space-y-1">
                <div className="font-semibold text-gray-300">Full Text / Findings</div>
                <div className="text-gray-300 leading-relaxed bg-[#071426] p-4 rounded-xl border border-[#1E3352] whitespace-pre-wrap max-h-60 overflow-y-auto">
                  {selectedDoc.content}
                </div>
              </div>

              {selectedDoc.keywords && (
                <div className="flex flex-wrap gap-1.5 pt-1">
                  {selectedDoc.keywords.split(',').map((kw) => (
                    <span
                      key={kw}
                      className="px-2 py-0.5 rounded-lg bg-[#102A43] text-[10px] text-gray-300"
                    >
                      #{kw.trim()}
                    </span>
                  ))}
                </div>
              )}
            </div>

            <div className="pt-3 border-t border-[#1E3352] flex justify-end">
              <button
                onClick={() => setSelectedDoc(null)}
                className="px-4 py-2 rounded-xl bg-[#102A43] text-xs font-semibold"
              >
                Close Document
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

