import React, { useState, useEffect, useRef } from 'react';
import {
  BookOpen,
  FileText,
  Bot,
  Compass,
  UploadCloud,
  FolderPlus,
  Trash2,
  Search,
  Sparkles,
  ChevronRight,
  Settings,
  ArrowLeft,
  Send,
  X,
  User,
  LogOut,
  Lock,
  Mail,
  GraduationCap,
  ShieldCheck,
  CheckCircle2,
  AlertCircle,
  Award,
  Target,
  Flame,
  BookMarked,
  FileQuestion,
  TrendingUp,
  Bookmark
} from 'lucide-react';

export default function App() {
  // Authentication State
  const [token, setToken] = useState(() => localStorage.getItem('gov_exam_auth_token') || '');
  const [user, setUser] = useState(null);
  const [authView, setAuthView] = useState('login'); // 'login' or 'signup'
  const [authLoading, setAuthLoading] = useState(false);
  const [authError, setAuthError] = useState('');

  // Sign In / Sign Up Form State
  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [signupName, setSignupName] = useState('');
  const [signupEmail, setSignupEmail] = useState('');
  const [signupPassword, setSignupPassword] = useState('');
  const [signupTargetExam, setSignupTargetExam] = useState('SEBI Grade A (IT Stream)');

  // Main App Navigation State
  const [activeTab, setActiveTab] = useState('strategy'); // 'strategy', 'library', 'chat'
  const [settingsStatus, setSettingsStatus] = useState({ gemini_api_configured: false, chat_model: 'gemini-2.5-flash' });

  // Strategy State
  const [targetExam, setTargetExam] = useState('SEBI Grade A (IT Stream)');
  const [dailyHours, setDailyHours] = useState(5);
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
  const [uploadCategory, setUploadCategory] = useState('High-Yield Notes');
  const [customCategory, setCustomCategory] = useState('');
  const [uploading, setUploading] = useState(false);
  const [uploadFile, setUploadFile] = useState(null);

  // Workspace Importer Modal State
  const [showWorkspaceModal, setShowWorkspaceModal] = useState(false);
  const [availableWorkspacePdfs, setAvailableWorkspacePdfs] = useState([]);
  const [importingPath, setImportingPath] = useState(null);

  // Settings Modal State
  const [showSettingsModal, setShowSettingsModal] = useState(false);
  const [newApiKey, setNewApiKey] = useState('');
  const [savingKey, setSavingKey] = useState(false);
  const [keySaveMsg, setKeySaveMsg] = useState(null);

  // Chat State
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const [chatMode, setChatMode] = useState('document'); // 'document' or 'general'
  const chatScrollRef = useRef(null);

  const authHeaders = () => {
    return token ? { 'Authorization': `Bearer ${token}` } : {};
  };

  useEffect(() => {
    if (token) {
      fetchUserProfile();
      fetchSettings();
    }
  }, [token]);

  useEffect(() => {
    if (user && token) {
      fetchDocuments();
      fetchPastStrategies();
    }
  }, [user, token]);

  useEffect(() => {
    if (chatScrollRef.current) {
      chatScrollRef.current.scrollTop = chatScrollRef.current.scrollHeight;
    }
  }, [chatMessages, chatLoading]);

  // ==========================================
  // AUTHENTICATION HANDLERS
  // ==========================================

  const fetchUserProfile = async () => {
    try {
      const res = await fetch('/api/auth/me', { headers: authHeaders() });
      if (res.ok) {
        const data = await res.json();
        setUser(data.user);
        if (data.user.target_exam) setTargetExam(data.user.target_exam);
      } else {
        handleLogout();
      }
    } catch (e) {
      console.error(e);
      handleLogout();
    }
  };

  const handleLogin = async (e) => {
    if (e) e.preventDefault();
    setAuthLoading(true);
    setAuthError('');

    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: loginEmail, password: loginPassword })
      });
      const data = await res.json();
      if (res.ok) {
        localStorage.setItem('gov_exam_auth_token', data.token);
        setToken(data.token);
        setUser(data.user);
        if (data.user.target_exam) setTargetExam(data.user.target_exam);
      } else {
        setAuthError(data.detail || 'Sign in failed. Please check your email & password.');
      }
    } catch (err) {
      setAuthError('Connection error to examination portal.');
    } finally {
      setAuthLoading(false);
    }
  };

  const handleSignup = async (e) => {
    e.preventDefault();
    setAuthLoading(true);
    setAuthError('');

    try {
      const res = await fetch('/api/auth/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: signupName,
          email: signupEmail,
          password: signupPassword,
          target_exam: signupTargetExam
        })
      });
      const data = await res.json();
      if (res.ok) {
        localStorage.setItem('gov_exam_auth_token', data.token);
        setToken(data.token);
        setUser(data.user);
        setTargetExam(data.user.target_exam);
      } else {
        setAuthError(data.detail || 'Registration could not be completed.');
      }
    } catch (err) {
      setAuthError('Connection error to examination portal.');
    } finally {
      setAuthLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      await fetch('/api/auth/logout', { method: 'POST', headers: authHeaders() });
    } catch (e) {}
    localStorage.removeItem('gov_exam_auth_token');
    setToken('');
    setUser(null);
    setDocuments([]);
    setPastStrategies([]);
    setStrategyResult(null);
    setActiveWorkspaceDoc(null);
  };

  const handleDemoLogin = () => {
    setLoginEmail('rahul.aspirant@examportal.in');
    setLoginPassword('DemoPassword123');
    setTimeout(() => {
      fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: 'rahul.aspirant@examportal.in', password: 'DemoPassword123' })
      })
      .then(res => res.json())
      .then(data => {
        if (data.token) {
          localStorage.setItem('gov_exam_auth_token', data.token);
          setToken(data.token);
          setUser(data.user);
        }
      });
    }, 100);
  };

  // ==========================================
  // DATA FETCHING & API HANDLERS
  // ==========================================

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
      const res = await fetch('/api/documents', { headers: authHeaders() });
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
      const res = await fetch('/api/strategy/history', { headers: authHeaders() });
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
      const res = await fetch('/api/documents/workspace-available', { headers: authHeaders() });
      if (res.ok) {
        const data = await res.json();
        setAvailableWorkspacePdfs(data.available || []);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleGenerateStrategy = async () => {
    setStrategyLoading(true);
    try {
      const res = await fetch('/api/strategy/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...authHeaders()
        },
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

  const handleUploadSubmit = async (e) => {
    e.preventDefault();
    if (!uploadFile) return;

    setUploading(true);
    const cat = uploadCategory === 'Custom' ? customCategory : uploadCategory;
    const formData = new FormData();
    formData.append('file', uploadFile);
    formData.append('category', cat || 'High-Yield Notes');

    try {
      const res = await fetch('/api/documents/upload', {
        method: 'POST',
        headers: authHeaders(),
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

  const handleImportWorkspace = async (fullPath, suggestedCategory) => {
    setImportingPath(fullPath);
    const formData = new FormData();
    formData.append('full_path', fullPath);
    formData.append('category', suggestedCategory);

    try {
      const res = await fetch('/api/documents/import-workspace', {
        method: 'POST',
        headers: authHeaders(),
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

  const handleDeleteDocument = async (docId, filename) => {
    if (!window.confirm(`Remove '${filename}' from your Study Vault? This will delete the book and all its saved notes.`)) {
      return;
    }
    try {
      const res = await fetch(`/api/documents/${docId}`, {
        method: 'DELETE',
        headers: authHeaders()
      });
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

  const handleOpenWorkspace = (doc) => {
    setActiveWorkspaceDoc(doc);
    setChatMode('document');
    setChatMessages([
      {
        role: 'assistant',
        content: `I am your Faculty Mentor for **${doc.original_filename}**. Ask me any conceptual doubt, formula explanation, or exam-style question from this book.`,
        sources: []
      }
    ]);
  };

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
        headers: {
          'Content-Type': 'application/json',
          ...authHeaders()
        },
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
          content: 'Unable to reach your Faculty Mentor. Please verify server connection.',
          sources: []
        }
      ]);
    } finally {
      setChatLoading(false);
    }
  };

  const handleSaveApiKey = async (e) => {
    e.preventDefault();
    if (!newApiKey.trim()) return;
    setSavingKey(true);
    setKeySaveMsg(null);
    try {
      const res = await fetch('/api/settings/api-key', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...authHeaders()
        },
        body: JSON.stringify({ api_key: newApiKey.trim() })
      });
      const data = await res.json();
      if (res.ok) {
        setKeySaveMsg({ type: 'success', text: 'Mentor key updated! Live cloud faculties are active.' });
        fetchSettings();
        setTimeout(() => { setShowSettingsModal(false); setKeySaveMsg(null); setNewApiKey(''); }, 1500);
      } else {
        setKeySaveMsg({ type: 'error', text: data.detail || 'Could not validate key.' });
      }
    } catch (err) {
      setKeySaveMsg({ type: 'error', text: 'Connection error.' });
    } finally {
      setSavingKey(false);
    }
  };

  // User-Friendly Scholarly Category Labels
  const categories = ['all', 'Study Material', 'Question Bank', 'Previous Year Paper', 'Syllabus & Pattern'];
  const filteredDocs = documents.filter((d) => {
    const matchCat = selectedCategory === 'all' || d.category === selectedCategory;
    const matchSearch = !searchDocQuery || d.original_filename.toLowerCase().includes(searchDocQuery.toLowerCase());
    return matchCat && matchSearch;
  });

  // ==========================================
  // 1. SCHOLARLY AUTHENTICATION PORTAL
  // ==========================================
  if (!token || !user) {
    return (
      <div className="min-h-screen bg-slate-950 flex flex-col justify-center items-center px-4 sm:px-6 lg:px-8 font-sans">
        <div className="max-w-md w-full space-y-6 bg-slate-900/95 p-8 rounded-3xl border border-slate-800 shadow-2xl backdrop-blur-md">
          {/* Academy Brand Header */}
          <div className="text-center">
            <div className="mx-auto w-12 h-12 bg-amber-500/10 border border-amber-500/30 rounded-2xl flex items-center justify-center text-amber-400 shadow-md mb-3">
              <GraduationCap className="w-7 h-7" />
            </div>
            <h2 className="text-xl font-bold text-slate-100 tracking-tight">Sankalp Exam Academy</h2>
            <p className="mt-1 text-xs text-amber-400 font-medium tracking-wide uppercase">
              Target All India Rank (AIR) • 24/7 Faculty Mentorship
            </p>
            <p className="mt-1 text-xs text-slate-400">
              Personalized Topper's Study Routines & Smart Digital Book Vault
            </p>
          </div>

          {/* Tab Selector */}
          <div className="grid grid-cols-2 p-1 bg-slate-950/80 rounded-xl border border-slate-800 text-xs font-semibold">
            <button
              onClick={() => { setAuthView('login'); setAuthError(''); }}
              className={`py-2 rounded-lg transition ${authView === 'login' ? 'bg-amber-500 text-slate-950 shadow-sm' : 'text-slate-400 hover:text-slate-200'}`}
            >
              Aspirant Sign In
            </button>
            <button
              onClick={() => { setAuthView('signup'); setAuthError(''); }}
              className={`py-2 rounded-lg transition ${authView === 'signup' ? 'bg-amber-500 text-slate-950 shadow-sm' : 'text-slate-400 hover:text-slate-200'}`}
            >
              Start Free Preparation
            </button>
          </div>

          {/* Error Message */}
          {authError && (
            <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center space-x-2">
              <AlertCircle className="w-4 h-4 shrink-0 text-rose-400" />
              <span>{authError}</span>
            </div>
          )}

          {/* SIGN IN FORM */}
          {authView === 'login' ? (
            <form onSubmit={handleLogin} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Registered Email</label>
                <div className="relative">
                  <Mail className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
                  <input
                    type="email"
                    required
                    value={loginEmail}
                    onChange={(e) => setLoginEmail(e.target.value)}
                    placeholder="aspirant@examportal.in"
                    className="w-full pl-9 pr-3.5 py-2.5 bg-slate-950/80 border border-slate-700/80 rounded-xl text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-amber-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Password</label>
                <div className="relative">
                  <Lock className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
                  <input
                    type="password"
                    required
                    value={loginPassword}
                    onChange={(e) => setLoginPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full pl-9 pr-3.5 py-2.5 bg-slate-950/80 border border-slate-700/80 rounded-xl text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-amber-500"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={authLoading}
                className="w-full py-2.5 px-4 bg-amber-500 text-slate-950 rounded-xl text-xs font-bold hover:bg-amber-400 disabled:opacity-50 shadow-md transition"
              >
                {authLoading ? 'Verifying Credentials...' : 'Enter Study Desk'}
              </button>

              <div className="pt-2 text-center">
                <button
                  type="button"
                  onClick={handleDemoLogin}
                  className="text-xs text-amber-400/90 hover:text-amber-300 font-medium underline"
                >
                  ⚡ Quick Demo Login (Aspirant Rahul • SEBI Grade A)
                </button>
              </div>
            </form>
          ) : (
            /* CREATE ACCOUNT FORM */
            <form onSubmit={handleSignup} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Aspirant Name</label>
                <div className="relative">
                  <User className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
                  <input
                    type="text"
                    required
                    value={signupName}
                    onChange={(e) => setSignupName(e.target.value)}
                    placeholder="e.g. Vikram Sharma"
                    className="w-full pl-9 pr-3.5 py-2.5 bg-slate-950/80 border border-slate-700/80 rounded-xl text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-amber-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Email Address</label>
                <div className="relative">
                  <Mail className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
                  <input
                    type="email"
                    required
                    value={signupEmail}
                    onChange={(e) => setSignupEmail(e.target.value)}
                    placeholder="vikram@portal.in"
                    className="w-full pl-9 pr-3.5 py-2.5 bg-slate-950/80 border border-slate-700/80 rounded-xl text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-amber-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Target Examination (Mission)</label>
                <div className="relative">
                  <Target className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
                  <select
                    value={signupTargetExam}
                    onChange={(e) => setSignupTargetExam(e.target.value)}
                    className="w-full pl-9 pr-3.5 py-2.5 bg-slate-950/80 border border-slate-700/80 rounded-xl text-xs text-slate-100 focus:outline-none focus:ring-1 focus:ring-amber-500"
                  >
                    <option value="SEBI Grade A (IT Stream)">SEBI Grade A (IT Stream Officer)</option>
                    <option value="SBI SCO (Deputy Manager IT)">SBI Specialist Cadre Officer (SCO IT)</option>
                    <option value="IBPS SO (IT Officer)">IBPS Specialist Officer (IT Scale-I)</option>
                    <option value="UPSC CSE 2027">UPSC Civil Services Examination (IAS/IPS)</option>
                    <option value="SSC CGL">Staff Selection Commission (SSC CGL)</option>
                    <option value="Railways RRB NTPC">Railways RRB Recruitment</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Password</label>
                <div className="relative">
                  <Lock className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
                  <input
                    type="password"
                    required
                    minLength={6}
                    value={signupPassword}
                    onChange={(e) => setSignupPassword(e.target.value)}
                    placeholder="Create a secure password"
                    className="w-full pl-9 pr-3.5 py-2.5 bg-slate-950/80 border border-slate-700/80 rounded-xl text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-amber-500"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={authLoading}
                className="w-full py-2.5 px-4 bg-amber-500 text-slate-950 rounded-xl text-xs font-bold hover:bg-amber-400 disabled:opacity-50 shadow-md transition"
              >
                {authLoading ? 'Setting up Your Desk...' : 'Create Aspirant Profile & Start'}
              </button>
            </form>
          )}

          <div className="pt-2 text-center text-[11px] text-slate-500">
            🎓 Dedicated to ambitious aspirants aiming for final merit selection.
          </div>
        </div>
      </div>
    );
  }

  // ==========================================
  // 2. MAIN SCHOLARLY DESK (AUTHENTICATED)
  // ==========================================
  return (
    <div className="flex h-screen bg-[#fcfbf9] font-sans text-slate-900 overflow-hidden">
      {/* SIDEBAR NAVIGATION */}
      <aside className="w-64 bg-slate-950 text-slate-200 flex flex-col justify-between shrink-0 shadow-2xl border-r border-slate-800">
        <div>
          {/* Logo & Header */}
          <div className="p-5 border-b border-slate-800/80 flex items-center space-x-3">
            <div className="p-2 bg-amber-500/10 border border-amber-500/30 rounded-xl text-amber-400">
              <GraduationCap className="w-5 h-5" />
            </div>
            <div>
              <h1 className="font-bold text-slate-100 tracking-wide text-sm">Sankalp Academy</h1>
              <p className="text-[11px] text-amber-400/90 font-medium">Topper's Study Platform</p>
            </div>
          </div>

          {/* User Target Card with Logout */}
          <div className="p-4 mx-3 my-3 bg-slate-900/90 rounded-2xl border border-slate-800 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between">
                <span className="text-[10px] uppercase tracking-wider text-amber-400 font-semibold flex items-center space-x-1">
                  <Flame className="w-3 h-3 text-amber-400" />
                  <span>Aspiring Officer</span>
                </span>
                <button
                  onClick={handleLogout}
                  className="text-slate-400 hover:text-rose-400 p-1 transition"
                  title="Sign Out"
                >
                  <LogOut className="w-3.5 h-3.5" />
                </button>
              </div>
              <div className="font-semibold text-slate-100 text-sm mt-1 truncate">{user.name}</div>
              <div className="text-[11px] text-slate-400 truncate">{user.email}</div>
              <div className="mt-2.5 inline-flex items-center space-x-1 px-2.5 py-1 rounded-lg text-[10px] font-semibold bg-amber-400/10 text-amber-300 border border-amber-400/20">
                <Target className="w-3 h-3 shrink-0" />
                <span className="truncate">{user.target_exam}</span>
              </div>
            </div>
          </div>

          {/* Nav Links */}
          <nav className="p-3 space-y-1">
            <button
              onClick={() => { setActiveTab('strategy'); setActiveWorkspaceDoc(null); }}
              className={`w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all ${
                activeTab === 'strategy' && !activeWorkspaceDoc
                  ? 'bg-amber-500 text-slate-950 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
              }`}
            >
              <Award className="w-4 h-4" />
              <span>Topper's Strategy Blueprint</span>
            </button>

            <button
              onClick={() => { setActiveTab('library'); setActiveWorkspaceDoc(null); }}
              className={`w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all ${
                activeTab === 'library' && !activeWorkspaceDoc
                  ? 'bg-amber-500 text-slate-950 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
              }`}
            >
              <BookOpen className="w-4 h-4" />
              <span>Study Vault & Solved PYQs</span>
              <span className="ml-auto text-xs px-2 py-0.5 rounded-full bg-slate-800 text-amber-400 font-mono">
                {documents.length}
              </span>
            </button>

            <button
              onClick={() => { setActiveTab('chat'); setActiveWorkspaceDoc(null); setChatMode('general'); }}
              className={`w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all ${
                activeTab === 'chat' && !activeWorkspaceDoc
                  ? 'bg-amber-500 text-slate-950 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
              }`}
            >
              <Bot className="w-4 h-4" />
              <span>24/7 Faculty Mentor</span>
            </button>
          </nav>
        </div>

        {/* System & Gemini Key Indicator */}
        <div className="p-4 border-t border-slate-800/80 text-xs">
          <div className="flex items-center justify-between text-slate-400">
            <span className="flex items-center space-x-1.5">
              <span className={`w-2 h-2 rounded-full ${settingsStatus.gemini_api_configured ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'}`} />
              <span className="text-[11px] font-medium text-slate-300">AI Faculty Engine</span>
            </span>
            <button
              onClick={() => setShowSettingsModal(true)}
              className="font-mono text-[11px] text-amber-400 hover:text-amber-300 underline"
            >
              Settings
            </button>
          </div>
          <div className="mt-1 text-[11px] text-slate-500">Personalized Aspirant Vault Active</div>
        </div>
      </aside>

      {/* MAIN CONTENT AREA */}
      <main className="flex-1 flex flex-col overflow-hidden bg-[#fcfbf9]">
        {/* TOP BAR */}
        <header className="h-14 bg-white border-b border-amber-900/10 px-6 flex items-center justify-between shrink-0 shadow-xs">
          <div className="flex items-center space-x-3">
            {activeWorkspaceDoc ? (
              <button
                onClick={() => setActiveWorkspaceDoc(null)}
                className="flex items-center space-x-1.5 text-xs font-semibold text-slate-700 hover:text-amber-600 transition"
              >
                <ArrowLeft className="w-4 h-4" />
                <span>Return to Study Vault</span>
              </button>
            ) : (
              <div className="flex items-center space-x-2 text-sm font-bold text-slate-800">
                {activeTab === 'strategy' && <span>🎯 Strategic All India Rank (AIR) Preparation Blueprint</span>}
                {activeTab === 'library' && <span>📚 My Digital Study Vault ({documents.length} Books & Solved Papers)</span>}
                {activeTab === 'chat' && <span>🎓 Personal Examination Faculty Mentor & Doubt Solver</span>}
              </div>
            )}
          </div>

          <div className="flex items-center space-x-3">
            <button
              onClick={() => setShowSettingsModal(true)}
              className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg border border-slate-200 text-xs font-medium text-slate-700 bg-white hover:bg-slate-50 transition"
              title="Mentor Settings"
            >
              <Settings className="w-3.5 h-3.5 text-slate-600" />
              <span>Mentor Settings</span>
            </button>

            {activeTab === 'library' && !activeWorkspaceDoc && (
              <>
                <button
                  onClick={() => { setShowWorkspaceModal(true); fetchWorkspacePdfs(); }}
                  className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg border border-amber-200 text-xs font-semibold text-amber-900 bg-amber-50/60 hover:bg-amber-100/60 transition"
                >
                  <FolderPlus className="w-3.5 h-3.5 text-amber-600" />
                  <span>Curated Question Banks & Notes</span>
                </button>
                <button
                  onClick={() => setShowUploadModal(true)}
                  className="inline-flex items-center space-x-1.5 px-3.5 py-1.5 rounded-lg bg-slate-900 text-white text-xs font-semibold hover:bg-slate-800 shadow-xs transition"
                >
                  <UploadCloud className="w-3.5 h-3.5" />
                  <span>Add Book to Vault</span>
                </button>
              </>
            )}

            <button
              onClick={handleLogout}
              className="inline-flex items-center space-x-1 px-3 py-1.5 rounded-lg border border-rose-200 text-rose-600 text-xs font-medium hover:bg-rose-50 transition"
              title="Sign Out"
            >
              <LogOut className="w-3.5 h-3.5" />
              <span>Sign Out</span>
            </button>
          </div>
        </header>

        {/* WORKSPACE VIEW (SPLIT SCREEN IF DOCUMENT OPENED) */}
        {activeWorkspaceDoc ? (
          <div className="flex-1 flex overflow-hidden">
            {/* Left: Native PDF Viewer */}
            <div className="w-1/2 h-full border-r border-slate-200 bg-slate-100 flex flex-col">
              <div className="h-10 bg-white border-b border-slate-200 px-4 flex items-center justify-between text-xs font-semibold text-slate-700 shrink-0">
                <span className="truncate max-w-[70%] flex items-center space-x-1.5">
                  <BookMarked className="w-3.5 h-3.5 text-amber-600 shrink-0" />
                  <span className="truncate">{activeWorkspaceDoc.original_filename}</span>
                </span>
                <span className="text-amber-800 bg-amber-50 border border-amber-200 px-2 py-0.5 rounded text-[10px] font-semibold">{activeWorkspaceDoc.category}</span>
              </div>
              <div className="flex-1 w-full h-full relative">
                <iframe
                  src={`/api/documents/${activeWorkspaceDoc.id}/raw?token=${encodeURIComponent(token)}`}
                  className="w-full h-full border-none"
                  title="Reading Desk"
                />
              </div>
            </div>

            {/* Right: Quick Summary + Dedicated RAG Chat */}
            <div className="w-1/2 h-full flex flex-col bg-white">
              {/* Quick Summary Header */}
              <div className="p-4 border-b border-amber-900/10 bg-amber-50/40 shrink-0">
                <div className="flex items-center space-x-2 text-xs font-bold text-amber-900 uppercase tracking-wider mb-1">
                  <Sparkles className="w-3.5 h-3.5 text-amber-600" />
                  <span>High-Yield Chapter Digest & Core Takeaways</span>
                </div>
                <div className="text-xs text-slate-700 leading-relaxed whitespace-pre-line bg-white p-3.5 rounded-xl border border-amber-900/10 shadow-xs max-h-36 overflow-y-auto">
                  {activeWorkspaceDoc.summary || 'Analyzing chapter contents...'}
                </div>
              </div>

              {/* RAG Chat Messages */}
              <div ref={chatScrollRef} className="flex-1 p-4 overflow-y-auto space-y-3 bg-[#fcfbf9]/60">
                {chatMessages.map((msg, i) => (
                  <div
                    key={i}
                    className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}
                  >
                    <div
                      className={`max-w-[85%] rounded-2xl px-4 py-3 text-xs leading-relaxed ${
                        msg.role === 'user'
                          ? 'bg-slate-900 text-white rounded-br-none shadow-xs'
                          : 'bg-white text-slate-800 border border-amber-900/10 rounded-bl-none shadow-xs'
                      }`}
                    >
                      <div className="whitespace-pre-line">{msg.content}</div>
                      {msg.sources && msg.sources.length > 0 && (
                        <div className="mt-2.5 pt-2 border-t border-slate-100 flex flex-wrap gap-1.5">
                          <span className="text-[10px] text-amber-700 font-bold">Verified References:</span>
                          {msg.sources.map((s, idx) => (
                            <span
                              key={idx}
                              className="text-[10px] px-2 py-0.5 rounded-md bg-amber-50 text-amber-900 border border-amber-200 font-semibold"
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
                  <div className="flex items-center space-x-2 text-xs text-amber-800 p-2">
                    <span className="animate-spin w-3.5 h-3.5 border-2 border-amber-600 border-t-transparent rounded-full" />
                    <span>Faculty Mentor is examining the reference book...</span>
                  </div>
                )}
              </div>

              {/* Starter Chips */}
              <div className="px-4 py-2 bg-white border-t border-slate-100 flex items-center space-x-2 overflow-x-auto text-xs shrink-0">
                <button
                  onClick={() => handleSendMessage('Explain the top 3 core high-yield concepts in this book')}
                  className="px-3 py-1 rounded-full bg-amber-50 hover:bg-amber-100 text-amber-900 text-[11px] font-semibold border border-amber-200 whitespace-nowrap transition"
                >
                  ⭐ Top 3 Core Concepts
                </button>
                <button
                  onClick={() => handleSendMessage('What are typical tricky exam questions and MCQs asked from this material?')}
                  className="px-3 py-1 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-800 text-[11px] font-medium whitespace-nowrap transition"
                >
                  🎯 Exam Traps & Tricky MCQs
                </button>
                <button
                  onClick={() => handleSendMessage('Provide a concise rapid revision formula and definition sheet based on this material')}
                  className="px-3 py-1 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-800 text-[11px] font-medium whitespace-nowrap transition"
                >
                  ⚡ Rapid Revision Cheat Sheet
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
                    placeholder="Ask your Mentor anything from this reference book..."
                    className="flex-1 px-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:outline-none focus:ring-1 focus:ring-amber-500 focus:bg-white transition"
                  />
                  <button
                    type="submit"
                    disabled={chatLoading || !chatInput.trim()}
                    className="p-2 bg-slate-900 text-white rounded-xl hover:bg-slate-800 disabled:opacity-50 transition"
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
            {/* 1. TOUGHEST TOPPER'S STRATEGY VIEW */}
            {activeTab === 'strategy' && (
              <div className="max-w-5xl mx-auto space-y-6">
                {/* Motivation Banner */}
                <div className="p-4 bg-gradient-to-r from-amber-500/10 via-amber-500/5 to-transparent border-l-4 border-amber-500 rounded-r-2xl">
                  <div className="text-xs font-bold text-amber-900 uppercase tracking-wide flex items-center space-x-1.5">
                    <Flame className="w-4 h-4 text-amber-600" />
                    <span>Aspirant's Daily Creed</span>
                  </div>
                  <p className="mt-1 text-xs text-slate-700 italic">
                    "Success in competitive examinations is not about studying 15 hours one day; it is about studying 5 disciplined hours every single day without fail."
                  </p>
                </div>

                {/* Strategy Generator Card */}
                <div className="bg-white rounded-2xl border border-amber-900/10 p-6 shadow-xs">
                  <h2 className="text-base font-bold text-slate-900 mb-1 flex items-center space-x-2">
                    <Award className="w-5 h-5 text-amber-500" />
                    <span>Topper's Strategic Roadmap & Daily Routine Generator</span>
                  </h2>
                  <p className="text-xs text-slate-500 mb-5">
                    Calibrated for competitive exams to ensure syllabus coverage, active question bank drilling, and timely revision cycles.
                  </p>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
                    <div>
                      <label className="block text-xs font-semibold text-slate-700 mb-1.5">Target Examination (Mission)</label>
                      <input
                        type="text"
                        value={targetExam}
                        onChange={(e) => setTargetExam(e.target.value)}
                        placeholder="e.g. SEBI Grade A, UPSC CSE, SBI SCO, SSC CGL"
                        className="w-full px-3.5 py-2.5 border border-slate-300 rounded-xl text-xs focus:ring-1 focus:ring-amber-500 focus:outline-none"
                      />
                    </div>

                    <div>
                      <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                        Daily Study Hours Commitment: <span className="font-bold text-amber-600">{dailyHours} Hours/Day</span>
                      </label>
                      <input
                        type="range"
                        min="2"
                        max="10"
                        step="0.5"
                        value={dailyHours}
                        onChange={(e) => setDailyHours(e.target.value)}
                        className="w-full mt-2 accent-amber-500"
                      />
                    </div>

                    <div>
                      <label className="block text-xs font-semibold text-slate-700 mb-1.5">Current Stage of Preparation</label>
                      <select
                        value={prepLevel}
                        onChange={(e) => setPrepLevel(e.target.value)}
                        className="w-full px-3.5 py-2.5 border border-slate-300 rounded-xl text-xs focus:ring-1 focus:ring-amber-500 focus:outline-none bg-white font-medium"
                      >
                        <option value="Beginner">Beginner (Starting syllabus from Day 1)</option>
                        <option value="Intermediate">Intermediate (Theory studied, focusing on MCQs & Revision)</option>
                        <option value="Advanced">Advanced (Final revision, high-volume mocks & rank push)</option>
                      </select>
                    </div>
                  </div>

                  <div className="mt-6 flex justify-end">
                    <button
                      onClick={handleGenerateStrategy}
                      disabled={strategyLoading}
                      className="inline-flex items-center space-x-2 px-6 py-2.5 rounded-xl bg-slate-900 text-white text-xs font-bold hover:bg-slate-800 disabled:opacity-50 shadow-md transition"
                    >
                      {strategyLoading ? (
                        <>
                          <span className="animate-spin w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full" />
                          <span>Synthesizing Strategy Blueprint...</span>
                        </>
                      ) : (
                        <>
                          <Sparkles className="w-4 h-4 text-amber-400" />
                          <span>Generate AIR Strategy Blueprint</span>
                        </>
                      )}
                    </button>
                  </div>
                </div>

                {/* Strategy Result Display */}
                {strategyResult && (
                  <div className="bg-white rounded-2xl border border-amber-900/10 p-8 shadow-xs">
                    <div className="prose prose-slate max-w-none text-xs leading-relaxed whitespace-pre-line text-slate-800 font-sans">
                      {strategyResult}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* 2. RESOURCE LIBRARY (STUDY VAULT) */}
            {activeTab === 'library' && (
              <div className="max-w-6xl mx-auto space-y-6">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                  <div className="flex items-center space-x-2 overflow-x-auto">
                    {categories.map((cat) => (
                      <button
                        key={cat}
                        onClick={() => setSelectedCategory(cat)}
                        className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold transition ${
                          selectedCategory === cat
                            ? 'bg-slate-900 text-white shadow-xs'
                            : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50'
                        }`}
                      >
                        {cat === 'all' ? 'All My Study Vault' : cat}
                      </button>
                    ))}
                  </div>

                  <div className="relative w-full md:w-64">
                    <Search className="w-3.5 h-3.5 absolute left-3 top-3 text-slate-400" />
                    <input
                      type="text"
                      value={searchDocQuery}
                      onChange={(e) => setSearchDocQuery(e.target.value)}
                      placeholder="Search books, notes, PYQs..."
                      className="w-full pl-9 pr-3.5 py-1.5 bg-white border border-slate-200 rounded-xl text-xs focus:ring-1 focus:ring-amber-500 focus:outline-none"
                    />
                  </div>
                </div>

                {docsLoading ? (
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
                    {[1, 2, 3].map((n) => (
                      <div key={n} className="h-48 bg-slate-200 animate-pulse rounded-2xl" />
                    ))}
                  </div>
                ) : filteredDocs.length === 0 ? (
                  <div className="text-center py-16 bg-white rounded-2xl border border-amber-900/10 p-8 shadow-xs">
                    <BookOpen className="w-10 h-10 text-amber-500/60 mx-auto mb-3" />
                    <h3 className="text-sm font-bold text-slate-800">Your Study Vault is currently empty</h3>
                    <p className="text-xs text-slate-500 mt-1 max-w-md mx-auto">
                      Add reference books, notes, or import curated question banks above to start interactive reading and doubt solving.
                    </p>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
                    {filteredDocs.map((doc) => (
                      <div
                        key={doc.id}
                        className="bg-white rounded-2xl border border-amber-900/10 p-5 shadow-xs flex flex-col justify-between hover:shadow-md hover:border-amber-500/40 transition"
                      >
                        <div>
                          <div className="flex items-start justify-between">
                            <span className="inline-flex px-2.5 py-0.5 rounded-md text-[10px] font-bold bg-amber-50 text-amber-900 border border-amber-200">
                              {doc.category}
                            </span>
                            <button
                              onClick={() => handleDeleteDocument(doc.id, doc.original_filename)}
                              className="text-slate-400 hover:text-rose-600 transition p-1"
                              title="Remove from My Vault"
                            >
                              <Trash2 className="w-3.5 h-3.5" />
                            </button>
                          </div>

                          <h4 className="font-bold text-slate-900 text-sm mt-3 line-clamp-2" title={doc.original_filename}>
                            {doc.original_filename}
                          </h4>

                          <p className="text-xs text-slate-500 mt-2 line-clamp-3 leading-relaxed">
                            {doc.summary ? doc.summary.replace(/[*#]/g, '') : 'Ready on your reading desk for instant concept lookup.'}
                          </p>
                        </div>

                        <div className="mt-5 pt-3 border-t border-slate-100 flex items-center justify-between">
                          <span className="text-[11px] text-slate-400 font-mono">
                            {doc.page_count} Pages • {(doc.file_size / 1024).toFixed(0)} KB
                          </span>
                          <button
                            onClick={() => handleOpenWorkspace(doc)}
                            className="inline-flex items-center space-x-1 px-3 py-1.5 rounded-lg bg-slate-900 text-white text-xs font-semibold hover:bg-slate-800 transition shadow-xs"
                          >
                            <span>Open Reading Desk</span>
                            <ChevronRight className="w-3 h-3" />
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* 3. 24/7 FACULTY MENTOR */}
            {activeTab === 'chat' && (
              <div className="max-w-4xl mx-auto h-[calc(100vh-140px)] flex flex-col bg-white rounded-2xl border border-amber-900/10 shadow-xs overflow-hidden">
                <div className="p-4 border-b border-amber-900/10 bg-amber-50/30 flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Bot className="w-5 h-5 text-amber-600" />
                    <div>
                      <div className="text-xs font-bold text-slate-900">Senior Faculty Exam Mentor</div>
                      <div className="text-[10px] text-slate-500">Ask any conceptual doubt, subject weightage question, or revision tip</div>
                    </div>
                  </div>
                  <span className="text-[11px] font-semibold text-emerald-700 bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-200">
                    Faculty Online
                  </span>
                </div>

                <div ref={chatScrollRef} className="flex-1 p-5 overflow-y-auto space-y-4 bg-[#fcfbf9]/40">
                  {chatMessages.length === 0 ? (
                    <div className="text-center py-16 text-slate-400 space-y-2">
                      <GraduationCap className="w-10 h-10 mx-auto text-amber-500/50" />
                      <p className="text-xs text-slate-700 font-bold">Have a doubt in your syllabus or preparation strategy?</p>
                      <p className="text-xs text-slate-500 max-w-sm mx-auto">
                        Ask your Faculty Mentor about high-weightage topics, time management, or tricky exam concepts.
                      </p>
                    </div>
                  ) : (
                    chatMessages.map((msg, i) => (
                      <div
                        key={i}
                        className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}
                      >
                        <div
                          className={`max-w-[80%] rounded-2xl px-4 py-3 text-xs leading-relaxed ${
                            msg.role === 'user'
                              ? 'bg-slate-900 text-white rounded-br-none shadow-xs'
                              : 'bg-white text-slate-800 border border-amber-900/10 rounded-bl-none shadow-xs'
                          }`}
                        >
                          <div className="whitespace-pre-line">{msg.content}</div>
                        </div>
                      </div>
                    ))
                  )}
                  {chatLoading && (
                    <div className="flex items-center space-x-2 text-xs text-amber-800 p-2">
                      <span className="animate-spin w-3.5 h-3.5 border-2 border-amber-600 border-t-transparent rounded-full" />
                      <span>Faculty Mentor is formulating the answer...</span>
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
                      placeholder="Ask your Mentor about exam patterns, subject doubts, or daily schedules..."
                      className="flex-1 px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:ring-1 focus:ring-amber-500 focus:bg-white focus:outline-none transition"
                    />
                    <button
                      type="submit"
                      disabled={chatLoading || !chatInput.trim()}
                      className="px-5 py-2.5 bg-slate-900 text-white rounded-xl text-xs font-bold hover:bg-slate-800 disabled:opacity-50 transition shadow-xs"
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
        <div className="fixed inset-0 bg-slate-950/60 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-3xl border border-slate-200 p-6 max-w-md w-full shadow-2xl">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <h3 className="text-sm font-bold text-slate-900">Add Book or Notes to Study Vault</h3>
              <button onClick={() => setShowUploadModal(false)} className="text-slate-400 hover:text-slate-600">
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleUploadSubmit} className="mt-4 space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Select PDF File</label>
                <input
                  type="file"
                  accept="application/pdf"
                  required
                  onChange={(e) => setUploadFile(e.target.files[0])}
                  className="w-full text-xs text-slate-500 file:mr-3 file:py-2 file:px-3 file:rounded-xl file:border-0 file:text-xs file:font-bold file:bg-amber-50 file:text-amber-900 hover:file:bg-amber-100"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Material Category</label>
                <select
                  value={uploadCategory}
                  onChange={(e) => setUploadCategory(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-xl text-xs bg-white font-medium"
                >
                  <option value="Study Material">Study Material & Theory Notes</option>
                  <option value="Question Bank">Question Bank & Sectional MCQs</option>
                  <option value="Previous Year Paper">Previous Year Solved Papers (PYQs)</option>
                  <option value="Syllabus & Pattern">Official Syllabus & Guidelines</option>
                  <option value="Custom">Custom Category...</option>
                </select>
              </div>

              {uploadCategory === 'Custom' && (
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Custom Category Name</label>
                  <input
                    type="text"
                    required
                    value={customCategory}
                    onChange={(e) => setCustomCategory(e.target.value)}
                    placeholder="e.g. Current Affairs, Interview Notes"
                    className="w-full px-3 py-2 border border-slate-300 rounded-xl text-xs"
                  />
                </div>
              )}

              <div className="pt-2 flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setShowUploadModal(false)}
                  className="px-3.5 py-2 border border-slate-200 rounded-xl text-xs font-semibold text-slate-600 hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={uploading || !uploadFile}
                  className="px-5 py-2 bg-slate-900 text-white rounded-xl text-xs font-bold hover:bg-slate-800 disabled:opacity-50"
                >
                  {uploading ? 'Analyzing & Indexing...' : 'Add to My Vault'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* CURATED STUDY MATERIAL SCANNER MODAL */}
      {showWorkspaceModal && (
        <div className="fixed inset-0 bg-slate-950/60 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-3xl border border-slate-200 p-6 max-w-2xl w-full shadow-2xl flex flex-col max-h-[80vh]">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div>
                <h3 className="text-sm font-bold text-slate-900">Curated Study Materials & Question Banks ({availableWorkspacePdfs.length})</h3>
                <p className="text-xs text-slate-500">Add standard university lecture notes and question banks to your personal vault with 1 click.</p>
              </div>
              <button onClick={() => setShowWorkspaceModal(false)} className="text-slate-400 hover:text-slate-600">
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="mt-4 flex-1 overflow-y-auto space-y-2 pr-1">
              {availableWorkspacePdfs.map((pdf, idx) => (
                <div
                  key={idx}
                  className="p-3 bg-slate-50 rounded-2xl border border-slate-200 flex items-center justify-between hover:bg-amber-50/40 hover:border-amber-200 transition"
                >
                  <div className="min-w-0 pr-3">
                    <div className="font-bold text-xs text-slate-800 truncate" title={pdf.filename}>
                      {pdf.filename}
                    </div>
                    <div className="text-[11px] text-slate-500 mt-0.5 truncate">
                      {pdf.suggested_category} • {pdf.size_kb} KB
                    </div>
                  </div>
                  <button
                    onClick={() => handleImportWorkspace(pdf.full_path, pdf.suggested_category)}
                    disabled={importingPath === pdf.full_path}
                    className="shrink-0 px-3.5 py-1.5 bg-slate-900 text-white rounded-xl text-xs font-bold hover:bg-slate-800 disabled:opacity-50 transition"
                  >
                    {importingPath === pdf.full_path ? 'Adding...' : 'Add to Vault'}
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* SETTINGS / API KEY MODAL */}
      {showSettingsModal && (
        <div className="fixed inset-0 bg-slate-950/60 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-3xl border border-slate-200 p-6 max-w-md w-full shadow-2xl">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div className="flex items-center space-x-2">
                <Settings className="w-4 h-4 text-amber-600" />
                <h3 className="text-sm font-bold text-slate-900">AI Faculty Mentor Settings</h3>
              </div>
              <button onClick={() => setShowSettingsModal(false)} className="text-slate-400 hover:text-slate-600">
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleSaveApiKey} className="mt-4 space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Google Gemini API Key (Optional)</label>
                <input
                  type="password"
                  value={newApiKey}
                  onChange={(e) => setNewApiKey(e.target.value)}
                  placeholder="Paste your Gemini API key here..."
                  className="w-full px-3 py-2 border border-slate-300 rounded-xl text-xs font-mono focus:ring-1 focus:ring-amber-500 focus:outline-none"
                />
                <p className="mt-1 text-[11px] text-slate-500">
                  You can get a free key at{' '}
                  <a
                    href="https://aistudio.google.com/apikey"
                    target="_blank"
                    rel="noreferrer"
                    className="text-amber-600 underline font-semibold"
                  >
                    Google AI Studio
                  </a>. If left blank, our offline curriculum engine provides answers automatically.
                </p>
              </div>

              <div className="p-3 bg-slate-50 rounded-2xl border border-slate-200 text-xs text-slate-600 space-y-1">
                <div className="font-semibold text-slate-800">Faculty Engine Status:</div>
                <div className="flex items-center space-x-2">
                  <span className={`w-2 h-2 rounded-full ${settingsStatus.gemini_api_configured ? 'bg-emerald-500' : 'bg-amber-500'}`} />
                  <span>{settingsStatus.gemini_api_configured ? 'Cloud AI Faculty Active' : 'Offline Curriculum Knowledge Base Active'}</span>
                </div>
                {settingsStatus.masked_key && (
                  <div className="text-[11px] font-mono text-slate-500">Key: {settingsStatus.masked_key}</div>
                )}
              </div>

              {keySaveMsg && (
                <div className={`p-3 rounded-xl text-xs ${keySaveMsg.type === 'success' ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' : 'bg-rose-50 text-rose-800 border border-rose-200'}`}>
                  {keySaveMsg.text}
                </div>
              )}

              <div className="pt-2 flex justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setShowSettingsModal(false)}
                  className="px-3.5 py-2 border border-slate-200 rounded-xl text-xs font-semibold text-slate-600 hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={savingKey || !newApiKey.trim()}
                  className="px-5 py-2 bg-slate-900 text-white rounded-xl text-xs font-bold hover:bg-slate-800 disabled:opacity-50"
                >
                  {savingKey ? 'Testing...' : 'Save & Activate'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
