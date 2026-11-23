'use client';

import React, { useState, useEffect } from 'react';
import { bmirApi } from '@/lib/api';
import { KnowledgeDocument } from '@/types/bmir';
import { Database, Search, Upload, BookOpen, ExternalLink, ShieldCheck, Plus } from 'lucide-react';

export default function KnowledgeBaseView() {
  const [documents, setDocuments] = useState<KnowledgeDocument[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [selectedDoc, setSelectedDoc] = useState<KnowledgeDocument | null>(null);
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [uploadForm, setUploadForm] = useState({
    title: '',
    doc_type: 'Research Paper',
    domain: 'Agriculture & Smart Farming',
    abstract: '',
    content: '',
    keywords: '',
  });

  useEffect(() => {
    loadDocs();
  }, [search]);

  const loadDocs = async () => {
    setLoading(true);
    try {
      const data = await bmirApi.searchKnowledge(search || undefined);
      setDocuments(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleUploadSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await bmirApi.uploadKnowledgeDoc(uploadForm);
      setIsUploadOpen(false);
      setUploadForm({
        title: '',
        doc_type: 'Research Paper',
        domain: 'Agriculture & Smart Farming',
        abstract: '',
        content: '',
        keywords: '',
      });
      loadDocs();
    } catch (err: any) {
      alert(`Upload failed: ${err.message}`);
    }
  };

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      {/* Header */}
      <div className="p-6 rounded-3xl bg-gradient-to-r from-[#0C1A2E] to-[#0A1626] border border-[#1E3352] flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="space-y-2">
          <div className="inline-flex items-center space-x-1.5 text-xs text-[#19C7D9] font-bold uppercase tracking-wider">
            <Database className="w-3.5 h-3.5" />
            <span>AI Research Knowledge Base (RAG)</span>
          </div>
          <h2 className="text-2xl font-extrabold text-white font-heading">
            Semantic Document Retrieval & Empirical Grounding
          </h2>
          <p className="text-xs text-gray-400">
            Search research papers, patent specifications, and technical notes indexed with vector embeddings for hallucination-free AI citations.
          </p>
        </div>

        <button
          onClick={() => setIsUploadOpen(true)}
          className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-[#2878FF] to-[#19C7D9] text-white text-xs font-bold shadow-md flex items-center space-x-1.5 shrink-0"
        >
          <Upload className="w-3.5 h-3.5" />
          <span>Upload Document</span>
        </button>
      </div>

      {/* Search Input */}
      <div className="relative">
        <Search className="w-4 h-4 text-gray-400 absolute left-4 top-1/2 -translate-y-1/2" />
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Semantic search across indexed literature, drying kinetics, hydrogen physics, and patent notes..."
          className="w-full pl-11 pr-4 py-3 rounded-2xl bg-[#0D1829] border border-[#1E3352] text-xs text-white placeholder-gray-500 focus:outline-none focus:border-[#2878FF]"
        />
      </div>

      {/* Documents Grid */}
      {loading ? (
        <div className="py-12 text-center text-gray-400">Loading knowledge base records...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {documents.map((doc) => (
            <div
              key={doc.id}
              onClick={() => setSelectedDoc(doc)}
              className="p-6 rounded-3xl bg-[#0D1829] border border-[#1E3352] hover:border-cyan-500/40 cursor-pointer transition-all space-y-3"
            >
              <div className="flex items-center justify-between text-xs">
                <span className="px-2.5 py-0.5 rounded font-bold uppercase bg-[#102A43] text-[#19C7D9] text-[10px]">
                  {doc.doc_type}
                </span>
                {doc.similarity_score !== undefined && (
                  <span className="font-mono text-[10px] text-emerald-400">
                    Relevance: {(doc.similarity_score * 100).toFixed(0)}%
                  </span>
                )}
              </div>

              <h3 className="text-base font-bold text-white font-heading">{doc.title}</h3>
              <p className="text-xs text-gray-300 line-clamp-3 leading-relaxed">{doc.abstract}</p>

              <div className="flex items-center justify-between pt-3 border-t border-[#1E3352] text-[11px] text-gray-400">
                <span>{doc.domain}</span>
                <span className="text-[#19C7D9]">View full text →</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Full Document Viewer Modal */}
      {selectedDoc && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
          <div className="bg-[#0D1829] border border-[#1E3352] rounded-3xl max-w-3xl w-full p-6 sm:p-8 space-y-4 max-h-[85vh] overflow-y-auto">
            <div className="flex items-center justify-between pb-3 border-b border-[#1E3352]">
              <div>
                <span className="text-[10px] font-bold uppercase text-[#19C7D9]">{selectedDoc.doc_type}</span>
                <h3 className="text-xl font-bold text-white font-heading">{selectedDoc.title}</h3>
              </div>
              <button
                onClick={() => setSelectedDoc(null)}
                className="px-3 py-1 rounded-lg bg-[#102A43] text-gray-300 hover:text-white text-xs"
              >
                Close
              </button>
            </div>

            <div className="text-xs text-gray-400">
              <strong>Domain:</strong> {selectedDoc.domain} · <strong>Authors:</strong>{' '}
              {selectedDoc.authors || 'BMIR Research Team'}
            </div>

            <div className="p-4 rounded-xl bg-[#071426] border border-[#1E3352] text-xs text-gray-200 whitespace-pre-wrap leading-relaxed">
              {selectedDoc.content || selectedDoc.abstract}
            </div>
          </div>
        </div>
      )}

      {/* Upload Modal */}
      {isUploadOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
          <div className="bg-[#0D1829] border border-[#1E3352] rounded-3xl max-w-lg w-full p-6 space-y-4">
            <div className="flex justify-between items-center pb-2 border-b border-[#1E3352]">
              <h3 className="text-base font-bold text-white font-heading">Index Document to RAG</h3>
              <button onClick={() => setIsUploadOpen(false)} className="text-xs text-gray-400">
                Cancel
              </button>
            </div>

            <form onSubmit={handleUploadSubmit} className="space-y-3 text-xs">
              <div>
                <label className="block text-gray-300 font-semibold mb-1">Document Title *</label>
                <input
                  type="text"
                  required
                  value={uploadForm.title}
                  onChange={(e) => setUploadForm({ ...uploadForm, title: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl bg-[#071426] border border-[#1E3352] text-white focus:outline-none focus:border-[#2878FF]"
                />
              </div>

              <div>
                <label className="block text-gray-300 font-semibold mb-1">Domain</label>
                <input
                  type="text"
                  value={uploadForm.domain}
                  onChange={(e) => setUploadForm({ ...uploadForm, domain: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl bg-[#071426] border border-[#1E3352] text-white focus:outline-none focus:border-[#2878FF]"
                />
              </div>

              <div>
                <label className="block text-gray-300 font-semibold mb-1">Abstract</label>
                <textarea
                  rows={2}
                  value={uploadForm.abstract}
                  onChange={(e) => setUploadForm({ ...uploadForm, abstract: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl bg-[#071426] border border-[#1E3352] text-white focus:outline-none focus:border-[#2878FF]"
                />
              </div>

              <div>
                <label className="block text-gray-300 font-semibold mb-1">Document Content *</label>
                <textarea
                  rows={4}
                  required
                  value={uploadForm.content}
                  onChange={(e) => setUploadForm({ ...uploadForm, content: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl bg-[#071426] border border-[#1E3352] text-white focus:outline-none focus:border-[#2878FF]"
                  placeholder="Paste research text, experimental findings, or patent disclosure..."
                />
              </div>

              <button
                type="submit"
                className="w-full py-2.5 rounded-xl bg-gradient-to-r from-[#2878FF] to-[#19C7D9] text-white font-bold text-xs"
              >
                Compute Embeddings & Index
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

