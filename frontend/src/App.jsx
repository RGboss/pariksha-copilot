import React, { useState, useEffect, useRef } from 'react';
import {
  BookOpen,
  FileText,
  Bot,
  Compass,
  UploadCloud,
  FolderPlus,
  Trash2,
  ExternalLink,
  Search,
  Sparkles,
  ChevronRight,
  Clock,
  CheckCircle,
  HelpCircle,
  Settings,
  Layers,
  ArrowLeft,
  Send,
  AlertCircle,
  X,
  FileCheck
} from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState('strategy'); // 'strategy', 'library', 'chat'
  const [user, setUser] = useState({ name: 'Aspirant Rahul', target_exam: 'SEBI Grade A (IT Stream)', email: '' });
  const [settingsStatus, setSettingsStatus] = useState({ gemini_api_configured: false, chat_model: 'gemini-2.5-flash' });
  
  // Strategy State
  const [targetExam, setTargetExam] = useState('SEBI Grade A (IT Stream)');
  const [dailyHours, setDailyHours] = useState(4);
  const [prepLevel, setPrepLevel] = useState('Intermediate');
  const [strategyResult, setStrategyResult] = useState(null);
  const [strategyLoading, setStrategyLoading] = useState(false);
  const [pastStrategies, setPastStrategies] = useState([]);

  // Documents State
  const [documents, setDocuments] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [searchDocQuery, setSearchDocQuery] = useState('');
  const [docsLoading, setDocsLoading] = useState(false);

  // Split-Screen PDF Workspace State
  const [activeWorkspaceDoc, setActiveWorkspaceDoc] = useState(null);

  // Upload Modal State
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [uploadCategory, setUploadCategory] = useState('Study Material');
  const [customCategory, setCustomCategory] = useState('');
  const [uploading, setUploading] = useState(false);
  const [uploadFile, setUploadFile] = useState(null);

  // Workspace Importer Modal State
  const [showWorkspaceModal, setShowWorkspaceModal] = useState(false);
  const [availableWorkspacePdfs, setAvailableWorkspacePdfs] = useState([]);
  const [importingPath, setImportingPath] = useState(null);

  // Chat State
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const [chatMode, setChatMode] = useState('document'); // 'document' or 'general'
  const chatScrollRef = useRef(null);

  // Initial Fetch
  useEffect(() => {
    fetchUserProfile();
    fetchSettings();
    fetchDocuments();
    fetchPastStrategies();
  }, []);

  useEffect(() => {
    if (chatScrollRef.current) {
      chatScrollRef.current.scrollTop = chatScrollRef.current.scrollHeight;
    }
  }, [chatMessages, chatLoading]);

  // Fetch API handlers
  const fetchUserProfile = async () => {
    try {
      const res = await fetch('/api/user');
      if (res.ok) {
        const data = await res.json();
        setUser(data);
        if (data.target_exam) setTargetExam(data.target_exam);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const fetchSettings = async () => {
    try {
      const res = await fetch('/api/settings/status');
      if (res.ok) {
        const data = await res.json();
        setSettingsStatus(data);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const fetchDocuments = async () => {
    setDocsLoading(true);
    try {
      const res = await fetch('/api/documents');
      if (res.ok) {
        const data = await res.json();
        setDocuments(data.documents || []);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setDocsLoading(false);
    }
  };

  const fetchPastStrategies = async () => {
    try {
      const res = await fetch('/api/strategy/history');
      if (res.ok) {
        const data = await res.json();
        setPastStrategies(data || []);
        if (data.length > 0 && !strategyResult) {
          setStrategyResult(data[0].strategy_markdown);
        }
      }
    } catch (e) {
      console.error(e);
    }
  };

  const fetchWorkspacePdfs = async () => {
    try {
      const res = await fetch('/api/documents/workspace-available');
      if (res.ok) {
        const data = await res.json();
        setAvailableWorkspacePdfs(data.available || []);
      }
    } catch (e) {
      console.error(e);
    }
  };

  // Strategy Generator Handler
  const handleGenerateStrategy = async () => {
    setStrategyLoading(true);
    try {
      const res = await fetch('/api/strategy/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          exam_name: targetExam,
          daily_hours: parseFloat(dailyHours),
          prep_level: prepLevel
        })
      });
      if (res.ok) {
        const data = await res.json();
        setStrategyResult(data.strategy_markdown);
        fetchPastStrategies();
      }
    } catch (e) {
      console.error(e);
    } finally {
      setStrategyLoading(false);
    }
  };

  // Upload PDF Handler
  const handleUploadSubmit = async (e) => {
    e.preventDefault();
    if (!uploadFile) return;

    setUploading(true);
    const cat = uploadCategory === 'Custom' ? customCategory : uploadCategory;
    const formData = new FormData();
    formData.append('file', uploadFile);
    formData.append('category', cat || 'Study Material');

    try {
      const res = await fetch('/api/documents/upload', {
        method: 'POST',
        body: formData
      });
      if (res.ok) {
        setShowUploadModal(false);
        setUploadFile(null);
        setCustomCategory('');
        fetchDocuments();
      }
    } catch (err) {
      console.error(err);
    } finally {
      setUploading(false);
    }
  };

  // Workspace Ingest Handler
  const handleImportWorkspace = async (fullPath, suggestedCategory) => {
    setImportingPath(fullPath);
    const formData = new FormData();
    formData.append('full_path', fullPath);
    formData.append('category', suggestedCategory);

    try {
      const res = await fetch('/api/documents/import-workspace', {
        method: 'POST',
        body: formData
      });
      if (res.ok) {
        fetchDocuments();
        fetchWorkspacePdfs();
      }
    } catch (err) {
      console.error(err);
    } finally {
      setImportingPath(null);
    }
  };

  // Delete PDF Handler
  const handleDeleteDocument = async (docId, filename) => {
    if (!window.confirm(`Are you sure you want to delete '${filename}'? This will remove the file, SQLite record, and ChromaDB embeddings.`)) {
      return;
    }
    try {
      const res = await fetch(`/api/documents/${docId}`, { method: 'DELETE' });
      if (res.ok) {
        if (activeWorkspaceDoc?.id === docId) {
          setActiveWorkspaceDoc(null);
        }
        fetchDocuments();
      }
    } catch (e) {
      console.error(e);
    }
  };

  // Open Document Workspace
  const handleOpenWorkspace = (doc) => {
    setActiveWorkspaceDoc(doc);
    setChatMode('document');
    setChatMessages([
      {
        role: 'assistant',
        content: `I am ready to help you analyze **${doc.original_filename}**. You can ask questions about its concepts, key formulas, or specific topics.`,
        sources: []
      }
    ]);
  };

  // Send Chat Query
  const handleSendMessage = async (customPrompt = null) => {
    const textToSend = customPrompt || chatInput;
    if (!textToSend.trim() || chatLoading) return;

    const userMsg = { role: 'user', content: textToSend };
    setChatMessages((prev) => [...prev, userMsg]);
    setChatInput('');
    setChatLoading(true);

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          mode: chatMode,
          document_id: activeWorkspaceDoc?.id || null,
          category: selectedCategory === 'all' ? null : selectedCategory,
          query: textToSend
        })
      });

      if (res.ok) {
        const data = await res.json();
        setChatMessages((prev) => [
          ...prev,
          {
            role: 'assistant',
            content: data.answer,
            sources: data.sources || [],
            model: data.model
          }
        ]);
      }
    } catch (e) {
      setChatMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: 'Error connecting to the AI Tutor. Please check server logs.',
          sources: []
        }
      ]);
    } finally {
      setChatLoading(false);
    }
  };

  // Categories Filter List
  const categories = ['all', 'Study Material', 'Question Bank', 'Previous Year Paper', 'Syllabus & Pattern'];
  const filteredDocs = documents.filter((d) => {
    const matchCat = selectedCategory === 'all' || d.category === selectedCategory;
    const matchSearch = !searchDocQuery || d.original_filename.toLowerCase().includes(searchDocQuery.toLowerCase());
    return matchCat && matchSearch;
  });

  return (
    <div className="flex h-screen bg-slate-50 font-sans text-slate-900 overflow-hidden">
      {/* SIDEBAR NAVIGATION */}
      <aside className="w-64 bg-slate-900 text-slate-200 flex flex-col justify-between shrink-0 shadow-xl border-r border-slate-800">
        <div>
          {/* Logo & Header */}
          <div className="p-5 border-b border-slate-800 flex items-center space-x-3">
            <div className="p-2 bg-indigo-600 rounded-lg shadow-sm text-white">
              <Compass className="w-5 h-5" />
            </div>
            <div>
              <h1 className="font-semibold text-white tracking-wide text-sm">GovtPrep AI</h1>
              <p className="text-xs text-slate-400">Strategy & RAG Tutor</p>
            </div>
          </div>

          {/* User Target Card */}
          <div className="p-4 mx-3 my-3 bg-slate-800/80 rounded-xl border border-slate-700/60">
            <div className="text-[11px] uppercase tracking-wider text-slate-400 font-medium">Aspirant Profile</div>
            <div className="font-medium text-slate-100 text-sm mt-0.5 truncate">{user.name}</div>
            <div className="mt-2 inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
              {user.target_exam}
            </div>
          </div>

          {/* Nav Links */}
          <nav className="p-3 space-y-1">
            <button
              onClick={() => { setActiveTab('strategy'); setActiveWorkspaceDoc(null); }}
              className={`w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all ${
                activeTab === 'strategy' && !activeWorkspaceDoc
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              <Sparkles className="w-4 h-4" />
              <span>Exam Strategy Agent</span>
            </button>

            <button
              onClick={() => { setActiveTab('library'); setActiveWorkspaceDoc(null); }}
              className={`w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all ${
                activeTab === 'library' && !activeWorkspaceDoc
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              <FileText className="w-4 h-4" />
              <span>Resource Library (PDFs)</span>
              <span className="ml-auto text-xs px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 font-mono">
                {documents.length}
              </span>
            </button>

            <button
              onClick={() => { setActiveTab('chat'); setActiveWorkspaceDoc(null); setChatMode('general'); }}
              className={`w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all ${
                activeTab === 'chat' && !activeWorkspaceDoc
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              <Bot className="w-4 h-4" />
              <span>AI Exam Mentor</span>
            </button>
          </nav>
        </div>

        {/* System & Gemini Key Indicator */}
        <div className="p-4 border-t border-slate-800 text-xs">
          <div className="flex items-center justify-between text-slate-400">
            <span className="flex items-center space-x-1.5">
              <span className={`w-2 h-2 rounded-full ${settingsStatus.gemini_api_configured ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'}`} />
              <span>Gemini RAG</span>
            </span>
            <span className="font-mono text-[11px] text-slate-400">{settingsStatus.chat_model}</span>
          </div>
          <div className="mt-1 text-[11px] text-slate-500">ChromaDB • text-embedding-004</div>
        </div>
      </aside>

      {/* MAIN CONTENT AREA */}
      <main className="flex-1 flex flex-col overflow-hidden bg-slate-50">
        {/* TOP BAR */}
        <header className="h-14 bg-white border-b border-slate-200 px-6 flex items-center justify-between shrink-0 shadow-xs">
          <div className="flex items-center space-x-3">
            {activeWorkspaceDoc ? (
              <button
                onClick={() => setActiveWorkspaceDoc(null)}
                className="flex items-center space-x-1.5 text-xs font-medium text-slate-600 hover:text-indigo-600 transition"
              >
                <ArrowLeft className="w-4 h-4" />
                <span>Return to Library</span>
              </button>
            ) : (
              <div className="flex items-center space-x-2 text-sm font-semibold text-slate-800">
                {activeTab === 'strategy' && <span>AI Exam Strategy & Preparation Blueprint</span>}
                {activeTab === 'library' && <span>PDF Resource Manager & Knowledge Base</span>}
                {activeTab === 'chat' && <span>General Exam Mentor & Current Affairs Q&A</span>}
              </div>
            )}
          </div>

          <div className="flex items-center space-x-3">
            {activeTab === 'library' && !activeWorkspaceDoc && (
              <>
                <button
                  onClick={() => { setShowWorkspaceModal(true); fetchWorkspacePdfs(); }}
                  className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg border border-slate-300 text-xs font-medium text-slate-700 bg-white hover:bg-slate-50 shadow-xs transition"
                >
                  <FolderPlus className="w-3.5 h-3.5 text-indigo-600" />
                  <span>Scan Workspace PDFs</span>
                </button>
                <button
                  onClick={() => setShowUploadModal(true)}
                  className="inline-flex items-center space-x-1.5 px-3.5 py-1.5 rounded-lg bg-indigo-600 text-white text-xs font-medium hover:bg-indigo-700 shadow-xs transition"
                >
                  <UploadCloud className="w-3.5 h-3.5" />
                  <span>Upload PDF</span>
                </button>
              </>
            )}
          </div>
        </header>

        {/* WORKSPACE VIEW (SPLIT SCREEN IF DOCUMENT OPENED) */}
        {activeWorkspaceDoc ? (
          <div className="flex-1 flex overflow-hidden">
            {/* Left: Native PDF Viewer */}
            <div className="w-1/2 h-full border-r border-slate-200 bg-slate-100 flex flex-col">
              <div className="h-10 bg-white border-b border-slate-200 px-4 flex items-center justify-between text-xs font-medium text-slate-700 shrink-0">
                <span className="truncate max-w-[70%]">{activeWorkspaceDoc.original_filename}</span>
                <span className="text-slate-400 font-mono text-[11px]">{activeWorkspaceDoc.category}</span>
              </div>
              <div className="flex-1 w-full h-full relative">
                <iframe
                  src={`/api/documents/${activeWorkspaceDoc.id}/raw`}
                  className="w-full h-full border-none"
                  title="PDF Document Viewer"
                />
              </div>
            </div>

            {/* Right: Quick Summary + Dedicated RAG Chat */}
            <div className="w-1/2 h-full flex flex-col bg-white">
              {/* Quick Summary Header */}
              <div className="p-4 border-b border-slate-200 bg-slate-50/60 shrink-0">
                <div className="flex items-center space-x-2 text-xs font-semibold text-indigo-900 uppercase tracking-wider mb-1">
                  <Sparkles className="w-3.5 h-3.5 text-indigo-600" />
                  <span>AI Document Summary & Syllabus Alignment</span>
                </div>
                <div className="text-xs text-slate-700 leading-relaxed whitespace-pre-line bg-white p-3 rounded-lg border border-slate-200 shadow-xs max-h-36 overflow-y-auto">
                  {activeWorkspaceDoc.summary || 'Summary generating...'}
                </div>
              </div>

              {/* RAG Chat Messages */}
              <div ref={chatScrollRef} className="flex-1 p-4 overflow-y-auto space-y-3 bg-slate-50/30">
                {chatMessages.map((msg, i) => (
                  <div
                    key={i}
                    className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}
                  >
                    <div
                      className={`max-w-[85%] rounded-xl px-4 py-3 text-xs leading-relaxed ${
                        msg.role === 'user'
                          ? 'bg-indigo-600 text-white rounded-br-none shadow-xs'
                          : 'bg-white text-slate-800 border border-slate-200 rounded-bl-none shadow-xs'
                      }`}
                    >
                      <div className="whitespace-pre-line">{msg.content}</div>
                      {msg.sources && msg.sources.length > 0 && (
                        <div className="mt-2.5 pt-2 border-t border-slate-100 flex flex-wrap gap-1.5">
                          <span className="text-[10px] text-slate-400 font-medium">Citations:</span>
                          {msg.sources.map((s, idx) => (
                            <span
                              key={idx}
                              className="text-[10px] px-1.5 py-0.5 rounded bg-indigo-50 text-indigo-700 border border-indigo-100 font-medium"
                            >
                              Page {s.page}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
                {chatLoading && (
                  <div className="flex items-center space-x-2 text-xs text-slate-400 p-2">
                    <span className="animate-spin w-3.5 h-3.5 border-2 border-indigo-600 border-t-transparent rounded-full" />
                    <span>Analyzing PDF chunks with ChromaDB...</span>
                  </div>
                )}
              </div>

              {/* Starter Chips */}
              <div className="px-4 py-2 bg-white border-t border-slate-100 flex items-center space-x-2 overflow-x-auto text-xs shrink-0">
                <button
                  onClick={() => handleSendMessage('Explain the top 3 core concepts in this PDF')}
                  className="px-2.5 py-1 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-700 text-[11px] whitespace-nowrap transition"
                >
                  💡 Top 3 Concepts
                </button>
                <button
                  onClick={() => handleSendMessage('What are typical exam questions asked from this material?')}
                  className="px-2.5 py-1 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-700 text-[11px] whitespace-nowrap transition"
                >
                  📝 Typical Exam MCQs
                </button>
                <button
                  onClick={() => handleSendMessage('Provide a concise formula / definition cheat sheet based on this PDF')}
                  className="px-2.5 py-1 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-700 text-[11px] whitespace-nowrap transition"
                >
                  ⚡ Formula Cheat Sheet
                </button>
              </div>

              {/* Chat Input Bar */}
              <div className="p-3 bg-white border-t border-slate-200 shrink-0">
                <form
                  onSubmit={(e) => { e.preventDefault(); handleSendMessage(); }}
                  className="flex items-center space-x-2"
                >
                  <input
                    type="text"
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                    placeholder="Ask a question about this document..."
                    className="flex-1 px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-lg text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:bg-white transition"
                  />
                  <button
                    type="submit"
                    disabled={chatLoading || !chatInput.trim()}
                    className="p-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 transition"
                  >
                    <Send className="w-4 h-4" />
                  </button>
                </form>
              </div>
            </div>
          </div>
        ) : (
          /* REGULAR TABS (STRATEGY, LIBRARY, GENERAL CHAT) */
          <div className="flex-1 overflow-y-auto p-8">
            {/* 1. EXAM STRATEGY VIEW */}
            {activeTab === 'strategy' && (
              <div className="max-w-5xl mx-auto space-y-6">
                {/* Control Card */}
                <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-xs">
                  <h2 className="text-base font-semibold text-slate-900 mb-4 flex items-center space-x-2">
                    <Sparkles className="w-4 h-4 text-indigo-600" />
                    <span>Personalized Study Strategy Blueprint Generator</span>
                  </h2>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
                    <div>
                      <label className="block text-xs font-medium text-slate-700 mb-1.5">Target Examination</label>
                      <input
                        type="text"
                        value={targetExam}
                        onChange={(e) => setTargetExam(e.target.value)}
                        placeholder="e.g. UPSC CSE, SEBI Grade A IT, SBI SCO, SSC CGL"
                        className="w-full px-3.5 py-2 border border-slate-300 rounded-lg text-xs focus:ring-1 focus:ring-indigo-500 focus:outline-none"
                      />
                    </div>

                    <div>
                      <label className="block text-xs font-medium text-slate-700 mb-1.5">
                        Daily Study Hours: <span className="font-semibold text-indigo-600">{dailyHours} hrs</span>
                      </label>
                      <input
                        type="range"
                        min="2"
                        max="10"
                        step="0.5"
                        value={dailyHours}
                        onChange={(e) => setDailyHours(e.target.value)}
                        className="w-full mt-2 accent-indigo-600"
                      />
                    </div>

                    <div>
                      <label className="block text-xs font-medium text-slate-700 mb-1.5">Preparation Level</label>
                      <select
                        value={prepLevel}
                        onChange={(e) => setPrepLevel(e.target.value)}
                        className="w-full px-3.5 py-2 border border-slate-300 rounded-lg text-xs focus:ring-1 focus:ring-indigo-500 focus:outline-none bg-white"
                      >
                        <option value="Beginner">Beginner (Starting syllabus from scratch)</option>
                        <option value="Intermediate">Intermediate (Theory covered, need practice & revision)</option>
                        <option value="Advanced">Advanced (Final revision & mock test optimization)</option>
                      </select>
                    </div>
                  </div>

                  <div className="mt-5 flex justify-end">
                    <button
                      onClick={handleGenerateStrategy}
                      disabled={strategyLoading}
                      className="inline-flex items-center space-x-2 px-5 py-2.5 rounded-xl bg-indigo-600 text-white text-xs font-medium hover:bg-indigo-700 disabled:opacity-50 shadow-sm transition"
                    >
                      {strategyLoading ? (
                        <>
                          <span className="animate-spin w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full" />
                          <span>Generating AI Blueprint...</span>
                        </>
                      ) : (
                        <>
                          <Sparkles className="w-4 h-4" />
                          <span>Generate Strategy Blueprint</span>
                        </>
                      )}
                    </button>
                  </div>
                </div>

                {/* Strategy Result Display */}
                {strategyResult && (
                  <div className="bg-white rounded-2xl border border-slate-200 p-8 shadow-xs">
                    <div className="prose prose-slate max-w-none text-xs leading-relaxed whitespace-pre-line text-slate-800">
                      {strategyResult}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* 2. RESOURCE LIBRARY VIEW */}
            {activeTab === 'library' && (
              <div className="max-w-6xl mx-auto space-y-6">
                {/* Search & Filter Bar */}
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                  <div className="flex items-center space-x-2 overflow-x-auto">
                    {categories.map((cat) => (
                      <button
                        key={cat}
                        onClick={() => setSelectedCategory(cat)}
                        className={`px-3 py-1.5 rounded-lg text-xs font-medium transition ${
                          selectedCategory === cat
                            ? 'bg-slate-900 text-white shadow-xs'
                            : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-100'
                        }`}
                      >
                        {cat === 'all' ? 'All Resources' : cat}
                      </button>
                    ))}
                  </div>

                  <div className="relative w-full md:w-64">
                    <Search className="w-3.5 h-3.5 absolute left-3 top-3 text-slate-400" />
                    <input
                      type="text"
                      value={searchDocQuery}
                      onChange={(e) => setSearchDocQuery(e.target.value)}
                      placeholder="Search PDF documents..."
                      className="w-full pl-9 pr-3.5 py-1.5 bg-white border border-slate-200 rounded-lg text-xs focus:ring-1 focus:ring-indigo-500 focus:outline-none"
                    />
                  </div>
                </div>

                {/* Document Grid */}
                {docsLoading ? (
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
                    {[1, 2, 3].map((n) => (
                      <div key={n} className="h-48 bg-slate-200 animate-pulse rounded-2xl" />
                    ))}
                  </div>
                ) : filteredDocs.length === 0 ? (
                  <div className="text-center py-16 bg-white rounded-2xl border border-slate-200 p-8">
                    <BookOpen className="w-8 h-8 text-slate-400 mx-auto mb-2" />
                    <h3 className="text-sm font-medium text-slate-800">No documents found</h3>
                    <p className="text-xs text-slate-500 mt-1">Upload a PDF or scan your local workspace to populate the library.</p>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
                    {filteredDocs.map((doc) => (
                      <div
                        key={doc.id}
                        className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs flex flex-col justify-between hover:shadow-md transition"
                      >
                        <div>
                          <div className="flex items-start justify-between">
                            <span className="inline-flex px-2 py-0.5 rounded text-[10px] font-medium bg-slate-100 text-slate-700 border border-slate-200">
                              {doc.category}
                            </span>
                            <button
                              onClick={() => handleDeleteDocument(doc.id, doc.original_filename)}
                              className="text-slate-400 hover:text-rose-600 transition p-1"
                              title="Delete PDF and Purge Vectors"
                            >
                              <Trash2 className="w-3.5 h-3.5" />
                            </button>
                          </div>

                          <h4 className="font-semibold text-slate-900 text-sm mt-3 line-clamp-2" title={doc.original_filename}>
                            {doc.original_filename}
                          </h4>

                          <p className="text-xs text-slate-500 mt-2 line-clamp-3 leading-relaxed">
                            {doc.summary ? doc.summary.replace(/[*#]/g, '') : 'Indexed in ChromaDB for semantic retrieval.'}
                          </p>
                        </div>

                        <div className="mt-5 pt-3 border-t border-slate-100 flex items-center justify-between">
                          <span className="text-[11px] text-slate-400 font-mono">
                            {doc.page_count} pgs • {(doc.file_size / 1024).toFixed(0)} KB
                          </span>
                          <button
                            onClick={() => handleOpenWorkspace(doc)}
                            className="inline-flex items-center space-x-1 px-3 py-1.5 rounded-lg bg-indigo-50 text-indigo-700 text-xs font-medium hover:bg-indigo-100 transition"
                          >
                            <span>Read & Ask AI</span>
                            <ChevronRight className="w-3 h-3" />
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* 3. GENERAL AI MENTOR VIEW */}
            {activeTab === 'chat' && (
              <div className="max-w-4xl mx-auto h-[calc(100vh-140px)] flex flex-col bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
                <div className="p-4 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Bot className="w-4 h-4 text-indigo-600" />
                    <span className="text-xs font-semibold text-slate-800">Govt Exam AI Mentor</span>
                  </div>
                  <span className="text-[11px] text-slate-500">General Guidance & Syllabus Doubts</span>
                </div>

                <div ref={chatScrollRef} className="flex-1 p-5 overflow-y-auto space-y-4">
                  {chatMessages.length === 0 ? (
                    <div className="text-center py-16 text-slate-400 space-y-2">
                      <Bot className="w-8 h-8 mx-auto text-indigo-500" />
                      <p className="text-xs text-slate-600 font-medium">Ask any question regarding exam patterns, current affairs, or preparation strategy.</p>
                    </div>
                  ) : (
                    chatMessages.map((msg, i) => (
                      <div
                        key={i}
                        className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}
                      >
                        <div
                          className={`max-w-[80%] rounded-xl px-4 py-3 text-xs leading-relaxed ${
                            msg.role === 'user'
                              ? 'bg-indigo-600 text-white rounded-br-none shadow-xs'
                              : 'bg-slate-100 text-slate-800 rounded-bl-none shadow-xs'
                          }`}
                        >
                          <div className="whitespace-pre-line">{msg.content}</div>
                        </div>
                      </div>
                    ))
                  )}
                  {chatLoading && (
                    <div className="flex items-center space-x-2 text-xs text-slate-400 p-2">
                      <span className="animate-spin w-3.5 h-3.5 border-2 border-indigo-600 border-t-transparent rounded-full" />
                      <span>Consulting AI Mentor...</span>
                    </div>
                  )}
                </div>

                <div className="p-4 bg-white border-t border-slate-200">
                  <form
                    onSubmit={(e) => { e.preventDefault(); handleSendMessage(); }}
                    className="flex items-center space-x-2"
                  >
                    <input
                      type="text"
                      value={chatInput}
                      onChange={(e) => setChatInput(e.target.value)}
                      placeholder="Ask the AI Mentor about exams, strategy, or study schedules..."
                      className="flex-1 px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:ring-1 focus:ring-indigo-500 focus:bg-white focus:outline-none transition"
                    />
                    <button
                      type="submit"
                      disabled={chatLoading || !chatInput.trim()}
                      className="px-4 py-2.5 bg-indigo-600 text-white rounded-xl text-xs font-medium hover:bg-indigo-700 disabled:opacity-50 transition"
                    >
                      <Send className="w-4 h-4" />
                    </button>
                  </form>
                </div>
              </div>
            )}
          </div>
        )}
      </main>

      {/* UPLOAD MODAL */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl border border-slate-200 p-6 max-w-md w-full shadow-xl">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <h3 className="text-sm font-semibold text-slate-900">Upload & Vectorize PDF</h3>
              <button onClick={() => setShowUploadModal(false)} className="text-slate-400 hover:text-slate-600">
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleUploadSubmit} className="mt-4 space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">Select PDF File</label>
                <input
                  type="file"
                  accept="application/pdf"
                  required
                  onChange={(e) => setUploadFile(e.target.files[0])}
                  className="w-full text-xs text-slate-500 file:mr-3 file:py-2 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">Category</label>
                <select
                  value={uploadCategory}
                  onChange={(e) => setUploadCategory(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs bg-white"
                >
                  <option value="Study Material">Study Material</option>
                  <option value="Question Bank">Question Bank</option>
                  <option value="Previous Year Paper">Previous Year Paper</option>
                  <option value="Syllabus & Pattern">Syllabus & Pattern</option>
                  <option value="Custom">Custom Category...</option>
                </select>
              </div>

              {uploadCategory === 'Custom' && (
                <div>
                  <label className="block text-xs font-medium text-slate-700 mb-1">Custom Category Name</label>
                  <input
                    type="text"
                    required
                    value={customCategory}
                    onChange={(e) => setCustomCategory(e.target.value)}
                    placeholder="e.g. Current Affairs, Interview Prep"
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs"
                  />
                </div>
              )}

              <div className="pt-2 flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setShowUploadModal(false)}
                  className="px-3.5 py-2 border border-slate-200 rounded-lg text-xs text-slate-600 hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={uploading || !uploadFile}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-xs font-medium hover:bg-indigo-700 disabled:opacity-50"
                >
                  {uploading ? 'Chunking & Indexing...' : 'Upload & Index'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* WORKSPACE SCANNER MODAL */}
      {showWorkspaceModal && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl border border-slate-200 p-6 max-w-2xl w-full shadow-xl flex flex-col max-h-[80vh]">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div>
                <h3 className="text-sm font-semibold text-slate-900">Workspace Study PDFs ({availableWorkspacePdfs.length})</h3>
                <p className="text-xs text-slate-500">One-click import into ChromaDB & the platform library</p>
              </div>
              <button onClick={() => setShowWorkspaceModal(false)} className="text-slate-400 hover:text-slate-600">
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="mt-4 flex-1 overflow-y-auto space-y-2 pr-1">
              {availableWorkspacePdfs.map((pdf, idx) => (
                <div
                  key={idx}
                  className="p-3 bg-slate-50 rounded-xl border border-slate-200 flex items-center justify-between"
                >
                  <div className="min-w-0 pr-3">
                    <div className="font-medium text-xs text-slate-800 truncate" title={pdf.filename}>
                      {pdf.filename}
                    </div>
                    <div className="text-[11px] text-slate-400 mt-0.5 truncate">
                      {pdf.suggested_category} • {pdf.size_kb} KB • {pdf.rel_path}
                    </div>
                  </div>
                  <button
                    onClick={() => handleImportWorkspace(pdf.full_path, pdf.suggested_category)}
                    disabled={importingPath === pdf.full_path}
                    className="shrink-0 px-3 py-1.5 bg-indigo-600 text-white rounded-lg text-xs font-medium hover:bg-indigo-700 disabled:opacity-50 transition"
                  >
                    {importingPath === pdf.full_path ? 'Indexing...' : 'Import'}
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
