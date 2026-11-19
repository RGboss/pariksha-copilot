// IT Officer Prep Platform - Bookish Scholarly Frontend & AI Tutor
const API_BASE = '/api';

// State Management
let currentStageList = [];
let currentChapter = null;
let currentExamFilter = 'all';
let currentActiveView = 'reader'; // reader | library | qbank | mock | cheatsheets | analytics
let activeQuizAnswers = {};
let isFocusReading = false;
let isBookmarksFilterOnly = false;

// Mock Exam State
let mockExamQuestions = [];
let mockUserAnswers = {};
let mockTimeRemaining = 30 * 60; // 30 minutes in seconds
let mockTimerInterval = null;
let isMockRunning = false;

// Question Bank State
let currentQBankCategory = 'all';
let cachedQBankList = [];

// Document Library & AI RAG Chat State
let cachedDocuments = [];
let currentDocCategory = 'all';
let currentDocSearch = '';
let activeDocumentId = null;
let activeChatSessionId = 'session_global';
let cachedWorkspacePdfs = [];

// DOM Elements
const sidebarCol = document.getElementById('sidebarCol');
const sidebarStagesContainer = document.getElementById('sidebarStages');
const mainContentView = document.getElementById('mainContentView');
const libraryView = document.getElementById('libraryView');
const qbankView = document.getElementById('qbankView');
const mockView = document.getElementById('mockView');
const cheatsheetsView = document.getElementById('cheatsheetsView');
const analyticsView = document.getElementById('analyticsView');
const searchModal = document.getElementById('searchModal');
const searchInput = document.getElementById('searchInput');
const searchResults = document.getElementById('searchResults');
const globalProgressBar = document.getElementById('globalProgressBar');
const globalProgressText = document.getElementById('globalProgressText');
const readingScrollIndicator = document.getElementById('readingScrollIndicator');

// Modals
const uploadModal = document.getElementById('uploadModal');
const workspaceModal = document.getElementById('workspaceModal');
const apiKeyModal = document.getElementById('apiKeyModal');

// Init
document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    loadStages();
    loadGlobalStats();
    checkApiKeyStatus();
    setupEventListeners();
    setupScrollIndicator();
});

// ==============================================================
// THEME & TYPOGRAPHY MANAGEMENT
// ==============================================================
function initTheme() {
    const savedTheme = localStorage.getItem('it_prep_theme') || 'paper';
    setTheme(savedTheme, false);

    const savedFont = localStorage.getItem('it_prep_font') || 'serif';
    setFontFamily(savedFont, false);
}

function setTheme(themeName, persist = true) {
    document.documentElement.classList.remove('theme-paper', 'theme-white', 'theme-dark', 'dark');
    if (themeName === 'dark') {
        document.documentElement.classList.add('theme-dark', 'dark');
    } else if (themeName === 'white') {
        document.documentElement.classList.add('theme-white');
    } else {
        document.documentElement.classList.add('theme-paper');
        themeName = 'paper';
    }

    document.querySelectorAll('.theme-select-btn').forEach(btn => {
        btn.classList.remove('active-theme', 'bg-[var(--accent-primary)]', 'text-white', 'font-semibold');
        btn.classList.add('text-[var(--text-muted)]');
    });
    const activeBtn = document.getElementById(`themeBtn-${themeName}`);
    if (activeBtn) {
        activeBtn.classList.add('active-theme', 'bg-[var(--accent-primary)]', 'text-white', 'font-semibold');
        activeBtn.classList.remove('text-[var(--text-muted)]');
    }

    if (persist) localStorage.setItem('it_prep_theme', themeName);
}

function setFontFamily(family, persist = true) {
    document.body.classList.remove('font-serif-mode', 'font-sans-mode');
    if (family === 'sans') {
        document.body.classList.add('font-sans-mode');
    } else {
        document.body.classList.add('font-serif-mode');
        family = 'serif';
    }

    document.querySelectorAll('.font-family-btn').forEach(btn => {
        btn.classList.remove('active-font', 'bg-[var(--border-main)]', 'font-bold', 'text-[var(--text-heading)]');
        btn.classList.add('text-[var(--text-muted)]');
    });
    const activeBtn = document.getElementById(`fontBtn-${family}`);
    if (activeBtn) {
        activeBtn.classList.add('active-font', 'bg-[var(--border-main)]', 'font-bold', 'text-[var(--text-heading)]');
        activeBtn.classList.remove('text-[var(--text-muted)]');
    }

    if (persist) localStorage.setItem('it_prep_font', family);
}

// Reading Comfort: Font Scaler
function changeFontSize(size) {
    document.body.classList.remove('reading-text-sm', 'reading-text-base', 'reading-text-lg');
    document.body.classList.add(`reading-text-${size}`);
    document.querySelectorAll('.font-size-btn').forEach(b => {
        b.classList.remove('active-size', 'bg-[var(--border-main)]', 'font-bold', 'text-[var(--text-heading)]');
    });
    event.currentTarget.classList.add('active-size', 'bg-[var(--border-main)]', 'font-bold', 'text-[var(--text-heading)]');
}

// Focus / Distraction-Free Reading Mode
function toggleFocusReading() {
    isFocusReading = !isFocusReading;
    const body = document.body;
    const btn = document.getElementById('focusModeBtn');
    if (isFocusReading) {
        body.classList.add('focus-reading-active');
        btn.classList.add('bg-[var(--border-main)]', 'font-bold', 'text-[var(--accent-primary)]');
    } else {
        body.classList.remove('focus-reading-active');
        btn.classList.remove('bg-[var(--border-main)]', 'font-bold', 'text-[var(--accent-primary)]');
    }
}

// Scroll Indicator
function setupScrollIndicator() {
    window.addEventListener('scroll', () => {
        if (!readingScrollIndicator) return;
        const totalHeight = document.documentElement.scrollHeight - window.innerHeight;
        if (totalHeight > 0) {
            const progress = (window.scrollY / totalHeight) * 100;
            readingScrollIndicator.style.width = `${Math.min(100, Math.max(0, progress))}%`;
        }
    });
}

// Event Listeners
function setupEventListeners() {
    // Keyboard Shortcut Ctrl+K
    document.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            openSearchModal();
        } else if (e.key === 'Escape') {
            closeSearchModal();
            closeUploadModal();
            closeWorkspaceModal();
            closeApiKeyModal();
        }
    });

    if (searchInput) searchInput.addEventListener('input', debounce(performSearch, 250));
}

// Debounce helper
function debounce(fn, delay) {
    let timer = null;
    return function (...args) {
        clearTimeout(timer);
        timer = setTimeout(() => fn.apply(this, args), delay);
    };
}

// ==============================================================
// VIEW SWITCHER
// ==============================================================
function switchView(viewName) {
    currentActiveView = viewName;
    
    mainContentView.classList.add('hidden');
    if (libraryView) libraryView.classList.add('hidden');
    qbankView.classList.add('hidden');
    mockView.classList.add('hidden');
    cheatsheetsView.classList.add('hidden');
    analyticsView.classList.add('hidden');

    document.querySelectorAll('.view-tab-btn').forEach(btn => {
        btn.classList.remove('active-view-tab', 'text-[var(--text-heading)]', 'font-bold', 'bg-[var(--bg-sheet)]', 'shadow-xs', 'border', 'border-[var(--border-main)]');
        btn.classList.add('text-[var(--text-muted)]');
    });
    const activeBtn = document.getElementById(`tabBtn-${viewName}`);
    if (activeBtn) {
        activeBtn.classList.add('active-view-tab', 'text-[var(--text-heading)]', 'font-bold', 'bg-[var(--bg-sheet)]', 'shadow-xs', 'border', 'border-[var(--border-main)]');
        activeBtn.classList.remove('text-[var(--text-muted)]');
    }

    // Toggle Sidebar display based on view
    if (sidebarCol) {
        if (viewName === 'reader') {
            sidebarCol.classList.remove('hidden');
        } else {
            sidebarCol.classList.add('hidden');
        }
    }

    if (viewName === 'reader') {
        mainContentView.classList.remove('hidden');
    } else if (viewName === 'library') {
        libraryView.classList.remove('hidden');
        loadDocuments();
    } else if (viewName === 'qbank') {
        qbankView.classList.remove('hidden');
        loadQuestionBank();
    } else if (viewName === 'mock') {
        mockView.classList.remove('hidden');
    } else if (viewName === 'cheatsheets') {
        cheatsheetsView.classList.remove('hidden');
    } else if (viewName === 'analytics') {
        analyticsView.classList.remove('hidden');
        loadGlobalStats();
    }
}

// ==============================================================
// CURRICULUM READER ENGINE
// ==============================================================
async function loadStages(preserveChapter = false) {
    try {
        const res = await fetch(`${API_BASE}/stages?exam=${currentExamFilter}`);
        const data = await res.json();
        currentStageList = data.stages || [];
        renderSidebarStages();
        
        if (!preserveChapter && currentStageList.length > 0 && currentStageList[0].chapters.length > 0) {
            loadChapter(currentStageList[0].chapters[0].id);
        }
    } catch (err) {
        console.error('Failed to load stages:', err);
    }
}

async function loadGlobalStats() {
    try {
        const res = await fetch(`${API_BASE}/stats`);
        const stats = await res.json();
        const pct = Math.round(stats.progress_percentage || 0);
        if (globalProgressBar) globalProgressBar.style.width = `${pct}%`;
        if (globalProgressText) globalProgressText.innerText = `${pct}% (${stats.completed_chapters}/${stats.total_chapters})`;
        
        const stTotal = document.getElementById('statTotalChapters');
        const stCompleted = document.getElementById('statCompletedChapters');
        const stAvgScore = document.getElementById('statAvgScore');
        const stQuizzes = document.getElementById('statQuizzesTaken');
        
        if (stTotal) stTotal.innerText = stats.total_chapters;
        if (stCompleted) stCompleted.innerText = stats.completed_chapters;
        if (stAvgScore) stAvgScore.innerText = `${stats.quiz_average_percentage}%`;
        if (stQuizzes) stQuizzes.innerText = stats.total_quizzes_taken;

        const docTotal = document.getElementById('docStatTotal');
        const docPages = document.getElementById('docStatPages');
        const docChunks = document.getElementById('docStatChunks');
        if (docTotal) docTotal.innerText = stats.total_documents || 0;
        if (docPages) docPages.innerText = stats.total_document_pages || 0;
        if (docChunks) docChunks.innerText = stats.total_chunks_indexed || 0;
    } catch (err) {
        console.error('Failed to load stats:', err);
    }
}

function toggleBookmarkFilter() {
    isBookmarksFilterOnly = !isBookmarksFilterOnly;
    const btnText = document.getElementById('bookmarkFilterText');
    const btn = document.getElementById('bookmarkFilterBtn');
    if (isBookmarksFilterOnly) {
        btnText.innerText = 'Showing Bookmarks';
        btn.classList.add('text-[var(--accent-primary)]', 'font-bold');
    } else {
        btnText.innerText = 'Bookmarks';
        btn.classList.remove('text-[var(--accent-primary)]', 'font-bold');
    }
    renderSidebarStages();
}

function renderSidebarStages() {
    if (!sidebarStagesContainer) return;
    sidebarStagesContainer.innerHTML = '';
    
    currentStageList.forEach((stage, sIdx) => {
        let visibleChapters = stage.chapters;
        if (isBookmarksFilterOnly) {
            visibleChapters = stage.chapters.filter(c => c.bookmarked);
            if (visibleChapters.length === 0) return;
        }
        
        const stageCard = document.createElement('div');
        stageCard.className = 'stage-item';
        
        const isCurrentStage = currentChapter && visibleChapters.some(c => c.id === currentChapter.id);
        const isOpen = isCurrentStage || (sIdx === 0 && !currentChapter) || isBookmarksFilterOnly;
        
        stageCard.innerHTML = `
            <div class="px-3 py-2.5 bg-[var(--bg-subtle)] cursor-pointer flex items-center justify-between text-xs font-semibold text-[var(--text-heading)] select-none hover:bg-[var(--bg-hover)] transition font-serif" onclick="toggleStageAccordion('${stage.id}')">
                <div class="flex items-center gap-2 overflow-hidden">
                    <span class="text-[10px] text-[var(--accent-primary)] font-bold">Part ${sIdx + 1}</span>
                    <span class="truncate font-sans font-medium text-[11px] text-[var(--text-main)]">${stage.title.replace(/^Stage \d+:\s*/, '')}</span>
                </div>
                <i class="fa-solid fa-chevron-down text-[9px] text-[var(--text-faint)] transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}" id="icon-${stage.id}"></i>
            </div>
            <div class="chapter-list ${isOpen ? 'block' : 'hidden'} divide-y divide-[var(--border-light)]" id="list-${stage.id}">
                ${visibleChapters.map(ch => {
                    const isSelected = currentChapter && currentChapter.id === ch.id;
                    const isCompleted = ch.completed;
                    const hasQuizScore = ch.quiz_score !== null;
                    
                    return `
                        <div onclick="selectChapter('${ch.id}')" 
                             class="chapter-item px-3.5 py-2.5 text-xs cursor-pointer flex items-center justify-between transition ${isSelected ? 'bg-[var(--bg-hover)] text-[var(--text-heading)] font-semibold border-l-3 border-[var(--accent-primary)]' : 'text-[var(--text-main)] hover:bg-[var(--bg-subtle)]'}">
                            <div class="flex items-start gap-2 overflow-hidden pr-1">
                                <span class="text-[10px] mt-0.5 ${isCompleted ? 'text-emerald-600' : 'text-[var(--text-faint)]'}">
                                    <i class="fa-solid ${isCompleted ? 'fa-circle-check' : 'fa-circle-dot'}"></i>
                                </span>
                                <span class="truncate font-serif leading-snug">${ch.number}. ${ch.title}</span>
                            </div>
                            <div class="flex items-center gap-1.5 shrink-0 ml-1 font-sans text-[10px]">
                                <span class="text-[var(--text-faint)]">${ch.reading_time_mins}m</span>
                                ${hasQuizScore ? `<span class="px-1.5 py-0.2 rounded font-mono border border-[var(--border-main)] bg-[var(--bg-sheet)] text-[var(--text-muted)]">${Math.round(ch.quiz_score.percentage)}%</span>` : ''}
                                ${ch.bookmarked ? `<i class="fa-solid fa-bookmark text-[var(--accent-primary)] text-[9px]"></i>` : ''}
                            </div>
                        </div>
                    `;
                }).join('')}
            </div>
        `;
        sidebarStagesContainer.appendChild(stageCard);
    });

    if (sidebarStagesContainer.children.length === 0 && isBookmarksFilterOnly) {
        sidebarStagesContainer.innerHTML = '<div class="p-6 text-center text-xs text-[var(--text-muted)] italic font-serif">No bookmarked chapters yet. Click the bookmark button inside any chapter to save it here.</div>';
    }
}

function toggleStageAccordion(stageId) {
    const list = document.getElementById(`list-${stageId}`);
    const icon = document.getElementById(`icon-${stageId}`);
    if (list) {
        list.classList.toggle('hidden');
        if (icon) icon.classList.toggle('rotate-180');
    }
}

function selectChapter(chapterId) {
    switchView('reader');
    loadChapter(chapterId);
}

async function loadChapter(chapterId) {
    try {
        const res = await fetch(`${API_BASE}/chapters/${chapterId}`);
        if (!res.ok) throw new Error('Chapter not found');
        currentChapter = await res.json();
        activeQuizAnswers = {};
        renderChapterReader();
        renderSidebarStages();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (err) {
        console.error('Failed to load chapter:', err);
    }
}

function renderChapterReader() {
    if (!currentChapter) return;
    
    const ch = currentChapter;
    const isCompleted = ch.user_state?.completed || false;
    const isBookmarked = ch.user_state?.bookmarked || false;
    const savedNotes = ch.user_state?.notes || '';
    
    // Eliminate Duplicate Title: strip leading # Title from lecture_notes
    const cleanNotes = ch.lecture_notes.replace(/^#\s+[^\n]+\n+/, '');
    const formattedNotes = renderMarkdown(cleanNotes);
    
    // Exam Badges
    const badgesHtml = ch.exams.map(e => {
        let label = e.toUpperCase();
        if (e === 'sebi') label = 'SEBI Grade A';
        if (e === 'sbi') label = 'SBI SCO';
        if (e === 'ibps') label = 'IBPS SO';
        return `<span class="px-2 py-0.5 rounded text-[10px] font-sans font-medium border border-[var(--border-main)] bg-[var(--bg-subtle)] text-[var(--text-muted)]">${label}</span>`;
    }).join(' ');

    const allChapters = currentStageList.flatMap(s => s.chapters);
    const currentIndex = allChapters.findIndex(c => c.id === ch.id);
    const prevChapter = currentIndex > 0 ? allChapters[currentIndex - 1] : null;
    const nextChapter = currentIndex < allChapters.length - 1 ? allChapters[currentIndex + 1] : null;

    mainContentView.innerHTML = `
        <article class="max-w-3xl mx-auto space-y-6 pb-20">
            <div class="book-sheet space-y-7">
                <header class="border-b border-[var(--border-main)] pb-5 space-y-3 font-serif">
                    <div class="flex items-center justify-between text-xs text-[var(--text-muted)] tracking-wider uppercase font-sans">
                        <span class="font-medium text-[var(--accent-primary)]">${ch.stage?.title || 'Syllabus Part'}</span>
                        <div class="flex items-center gap-2">
                            <button onclick="toggleBookmark('${ch.id}')" 
                                    class="px-2.5 py-1 rounded text-xs border border-[var(--border-main)] hover:bg-[var(--bg-hover)] transition flex items-center gap-1.5 ${isBookmarked ? 'text-[var(--accent-primary)] font-bold' : 'text-[var(--text-muted)]'}" 
                                    title="${isBookmarked ? 'Bookmarked' : 'Add Bookmark'}">
                                <i class="fa-${isBookmarked ? 'solid' : 'regular'} fa-bookmark"></i>
                                <span>${isBookmarked ? 'Bookmarked' : 'Bookmark'}</span>
                            </button>
                            <button onclick="toggleCompleted('${ch.id}', ${!isCompleted})" 
                                    class="px-3 py-1 rounded text-xs border transition flex items-center gap-1.5 ${isCompleted ? 'bg-[var(--accent-primary)] text-white font-medium border-transparent shadow-xs' : 'border-[var(--border-main)] text-[var(--text-main)] hover:bg-[var(--bg-hover)]'}">
                                <i class="fa-solid ${isCompleted ? 'fa-check' : 'fa-circle-check'}"></i>
                                <span>${isCompleted ? 'Completed' : 'Mark Complete'}</span>
                            </button>
                        </div>
                    </div>

                    <div class="pt-1">
                        <span class="text-xs uppercase tracking-widest text-[var(--accent-primary)] font-bold block mb-1">
                            Chapter ${ch.number}
                        </span>
                        <h1 class="text-2xl sm:text-3xl lg:text-4xl font-serif font-bold text-[var(--text-heading)] tracking-tight leading-tight">
                            ${ch.title}
                        </h1>
                    </div>

                    <div class="flex flex-wrap items-center gap-3 text-xs text-[var(--text-muted)] pt-1 font-sans">
                        <span class="flex items-center gap-1"><i class="fa-regular fa-clock text-[var(--text-faint)]"></i> ~${ch.reading_time_mins} min read</span>
                        <span>•</span>
                        <div class="flex items-center gap-1.5">${badgesHtml}</div>
                    </div>
                </header>

                <div class="border-l-4 border-[var(--border-accent)] bg-[var(--bg-subtle)] p-4 sm:p-5 rounded-r-lg text-sm text-[var(--text-main)] leading-relaxed italic space-y-1 font-serif">
                    <span class="not-italic text-xs font-bold uppercase tracking-wider text-[var(--accent-primary)] font-sans block">Chapter Abstract & Objectives:</span>
                    <p>${ch.summary}</p>
                </div>

                <div id="chapterTocBox" class="p-3.5 rounded-lg border border-[var(--border-main)] bg-[var(--bg-subtle)] text-xs space-y-2 hidden font-sans">
                    <span class="font-bold text-[10px] text-[var(--text-muted)] uppercase tracking-wider block">In This Chapter:</span>
                    <div id="chapterTocLinks" class="flex flex-wrap gap-2 text-xs font-serif"></div>
                </div>

                <div class="markdown-body pt-2" id="markdownContent">
                    ${formattedNotes}
                </div>

                ${ch.checkpoints && ch.checkpoints.length > 0 ? `
                    <div class="pt-8 space-y-4 border-t-2 border-[var(--border-main)] font-serif">
                        <div class="flex items-center gap-2">
                            <span class="text-base text-[var(--accent-primary)] font-serif">§</span>
                            <h3 class="text-base font-serif font-bold text-[var(--text-heading)]">
                                In-Reading Checkpoints (Test Your Understanding)
                            </h3>
                        </div>
                        <p class="text-xs text-[var(--text-muted)] font-sans">Pause and solve these conceptual questions to reinforce chapter mastery.</p>
                        <div class="space-y-3 text-xs">
                            ${ch.checkpoints.map((cp, idx) => `
                                <div class="p-4 rounded-lg border border-[var(--border-main)] bg-[var(--bg-subtle)] space-y-2.5">
                                    <p class="font-serif text-sm font-semibold text-[var(--text-heading)] leading-relaxed">
                                        <span class="text-[var(--accent-primary)] font-bold mr-1">Exercise ${ch.number}.${idx+1}:</span>
                                        ${cp.q}
                                    </p>
                                    <div class="hidden pt-2.5 border-t border-[var(--border-light)] text-[var(--text-main)] leading-relaxed font-serif" id="cp-ans-${idx}">
                                        <strong class="text-[var(--accent-primary)] font-sans text-xs uppercase tracking-wider block mb-1">Solution & Explanation:</strong>
                                        ${cp.a}
                                    </div>
                                    <button onclick="toggleCheckpointAnswer(${idx})" id="cp-btn-${idx}" class="text-xs font-sans font-medium text-[var(--accent-primary)] hover:underline pt-0.5 flex items-center gap-1">
                                        <span>Reveal Answer & Explanation</span>
                                        <i class="fa-solid fa-chevron-down text-[9px]"></i>
                                    </button>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}

                <div class="pt-6 border-t border-[var(--border-main)] space-y-2 font-sans">
                    <div class="flex items-center justify-between text-xs">
                        <span class="font-semibold text-[var(--text-heading)] flex items-center gap-1.5">
                            <i class="fa-solid fa-pen-nib text-[var(--accent-primary)]"></i> Scholar's Chapter Study Notes
                        </span>
                        <span class="text-[10px] text-[var(--text-faint)]" id="notesSaveStatus">Auto-saved to database</span>
                    </div>
                    <textarea id="chapterNotesInput" 
                              oninput="handleNotesInput('${ch.id}')"
                              placeholder="Record personal reflections, tricky formulas, or memory mnemonics for this chapter..."
                              class="w-full h-24 p-3 rounded-lg border border-[var(--border-main)] bg-[var(--bg-sheet)] text-[var(--text-main)] text-xs font-serif leading-relaxed focus:ring-1 focus:ring-[var(--accent-primary)] focus:outline-none transition">${savedNotes}</textarea>
                </div>

                ${ch.quiz && ch.quiz.length > 0 ? `
                    <div class="p-6 rounded-xl border border-[var(--border-main)] bg-[var(--bg-subtle)] space-y-5 font-serif" id="chapterQuizSection">
                        <div class="flex items-center justify-between border-b border-[var(--border-light)] pb-3">
                            <div>
                                <h3 class="text-base font-serif font-bold text-[var(--text-heading)] flex items-center gap-2">
                                    <i class="fa-solid fa-graduation-cap text-[var(--accent-primary)]"></i>
                                    Chapter Assessment Exercises (${ch.quiz.length} Questions)
                                </h3>
                                <p class="text-xs text-[var(--text-muted)] font-sans">Targeted practice questions calibrated to real banking exam difficulty</p>
                            </div>
                            <div id="quizScoreBadgeArea" class="font-sans">
                                ${ch.latest_quiz_score ? `
                                    <span class="px-2.5 py-1 rounded text-xs font-mono border border-[var(--border-main)] bg-[var(--bg-sheet)] text-[var(--text-heading)] font-bold">
                                        Score: ${ch.latest_quiz_score.score}/${ch.latest_quiz_score.total} (${ch.latest_quiz_score.percentage}%)
                                    </span>
                                ` : ''}
                            </div>
                        </div>

                        <div class="space-y-4">
                            ${ch.quiz.map((qItem, qIdx) => `
                                <div class="quiz-item p-4 rounded-lg border border-[var(--border-main)] bg-[var(--bg-sheet)] space-y-2.5 shadow-2xs" id="quizItem-${qItem.id}">
                                    <p class="text-sm font-semibold text-[var(--text-heading)] leading-relaxed">
                                        <span class="text-[var(--accent-primary)] font-sans mr-1">${qIdx + 1}.</span>
                                        ${qItem.q}
                                    </p>
                                    <div class="space-y-1.5 text-xs font-sans">
                                        ${qItem.options.map((opt, optIdx) => `
                                            <label class="flex items-start gap-2.5 p-2.5 rounded border border-[var(--border-main)] bg-[var(--bg-subtle)] cursor-pointer hover:border-[var(--accent-primary)] transition" id="optLabel-${qItem.id}-${optIdx}">
                                                <input type="radio" name="quiz-${qItem.id}" value="${optIdx}" onchange="selectQuizOption(${qItem.id}, ${optIdx})" class="mt-0.5 accent-[var(--accent-primary)]">
                                                <span class="leading-relaxed text-[var(--text-main)]"><strong class="font-mono mr-1">(${String.fromCharCode(65 + optIdx)})</strong> ${opt}</span>
                                            </label>
                                        `).join('')}
                                    </div>
                                    <div class="hidden quiz-feedback p-3 rounded text-xs border font-serif" id="feedback-${qItem.id}"></div>
                                </div>
                            `).join('')}
                        </div>

                        <div class="flex items-center justify-between pt-2 font-sans">
                            <button onclick="submitChapterQuiz('${ch.id}')" 
                                    id="submitQuizBtn"
                                    class="px-5 py-2 rounded-lg bg-[var(--accent-primary)] hover:bg-[var(--accent-primary-hover)] text-white font-semibold text-xs transition shadow-xs">
                                Submit Quiz Answers
                            </button>
                        </div>
                    </div>
                ` : ''}

                <div class="flex items-center justify-between pt-6 border-t border-[var(--border-main)] text-xs font-sans font-medium">
                    ${prevChapter ? `
                        <button onclick="selectChapter('${prevChapter.id}')" class="px-3.5 py-2 rounded-lg border border-[var(--border-main)] hover:bg-[var(--bg-hover)] transition flex items-center gap-1.5 text-[var(--text-main)]">
                            <i class="fa-solid fa-arrow-left text-[10px]"></i>
                            <span>Previous: Ch ${prevChapter.number}</span>
                        </button>
                    ` : '<div></div>'}
                    
                    ${nextChapter ? `
                        <button onclick="selectChapter('${nextChapter.id}')" class="px-3.5 py-2 rounded-lg bg-[var(--accent-primary)] hover:bg-[var(--accent-primary-hover)] text-white transition flex items-center gap-1.5 shadow-xs">
                            <span>Next: Ch ${nextChapter.number}</span>
                            <i class="fa-solid fa-arrow-right text-[10px]"></i>
                        </button>
                    ` : '<div></div>'}
                </div>
            </div>
        </article>
    `;

    postProcessReader();
}

function postProcessReader() {
    const container = document.getElementById('markdownContent');
    if (!container) return;

    if (window.renderMathInElement) {
        try {
            renderMathInElement(container, {
                delimiters: [
                    {left: '$$', right: '$$', display: true},
                    {left: '$', right: '$', display: false}
                ],
                throwOnError: false
            });
        } catch (e) {
            console.error('KaTeX render error:', e);
        }
    }

    const preBlocks = container.querySelectorAll('pre');
    preBlocks.forEach((pre) => {
        pre.classList.add('relative', 'group');
        const copyBtn = document.createElement('button');
        copyBtn.className = 'absolute top-2 right-2 px-2.5 py-1 rounded bg-[var(--bg-sheet)] text-[var(--text-main)] border border-[var(--border-main)] text-[10px] font-mono opacity-0 group-hover:opacity-100 transition-opacity shadow-xs';
        copyBtn.innerText = 'Copy';
        copyBtn.onclick = (e) => {
            e.stopPropagation();
            const codeText = pre.querySelector('code')?.innerText || pre.innerText;
            navigator.clipboard.writeText(codeText).then(() => {
                copyBtn.innerText = 'Copied!';
                setTimeout(() => { copyBtn.innerText = 'Copy'; }, 1500);
            });
        };
        pre.appendChild(copyBtn);
    });

    const h2Elements = container.querySelectorAll('h2');
    const tocBox = document.getElementById('chapterTocBox');
    const tocLinks = document.getElementById('chapterTocLinks');
    if (h2Elements.length >= 2 && tocBox && tocLinks) {
        tocBox.classList.remove('hidden');
        tocLinks.innerHTML = '';
        h2Elements.forEach((h2, idx) => {
            const headingId = `sec-${idx}`;
            h2.id = headingId;
            const link = document.createElement('a');
            link.href = `#${headingId}`;
            link.className = 'px-2.5 py-1 rounded border border-[var(--border-main)] hover:bg-[var(--bg-hover)] text-[var(--text-muted)] hover:text-[var(--text-heading)] transition';
            link.innerText = h2.innerText.replace(/^\d+\.\s*/, '');
            tocLinks.appendChild(link);
        });
    }
}

function toggleCheckpointAnswer(idx) {
    const ans = document.getElementById(`cp-ans-${idx}`);
    const btn = document.getElementById(`cp-btn-${idx}`);
    if (ans.classList.contains('hidden')) {
        ans.classList.remove('hidden');
        btn.innerHTML = '<span>Hide Answer</span> <i class="fa-solid fa-chevron-up text-[9px]"></i>';
    } else {
        ans.classList.add('hidden');
        btn.innerHTML = '<span>Reveal Answer & Explanation</span> <i class="fa-solid fa-chevron-down text-[9px]"></i>';
    }
}

function selectQuizOption(qid, optIdx) {
    activeQuizAnswers[String(qid)] = optIdx;
}

async function submitChapterQuiz(chapterId) {
    if (!currentChapter || !currentChapter.quiz) return;
    
    const totalQ = currentChapter.quiz.length;
    const answeredCount = Object.keys(activeQuizAnswers).length;
    
    if (answeredCount < totalQ) {
        if (!confirm(`You have answered ${answeredCount} of ${totalQ} questions. Submit anyway?`)) {
            return;
        }
    }
    
    try {
        const res = await fetch(`${API_BASE}/chapters/${chapterId}/quiz`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ answers: activeQuizAnswers })
        });
        
        const result = await res.json();
        
        result.evaluations.forEach(ev => {
            const feedbackEl = document.getElementById(`feedback-${ev.id}`);
            const optLabels = document.querySelectorAll(`[id^="optLabel-${ev.id}-"]`);
            
            optLabels.forEach((lbl, idx) => {
                if (idx === ev.correct_answer) {
                    lbl.className = "flex items-start gap-2.5 p-2.5 rounded border-2 border-emerald-600 bg-emerald-50 dark:bg-emerald-950/30 text-emerald-950 dark:text-emerald-100 font-semibold";
                } else if (idx === ev.user_answer && !ev.is_correct) {
                    lbl.className = "flex items-start gap-2.5 p-2.5 rounded border border-rose-400 bg-rose-50 dark:bg-rose-950/30 text-rose-950 dark:text-rose-100";
                }
            });
            
            if (feedbackEl) {
                feedbackEl.classList.remove('hidden');
                if (ev.is_correct) {
                    feedbackEl.className = "p-3.5 rounded text-xs border border-emerald-300 dark:border-emerald-800 bg-emerald-50/60 dark:bg-emerald-950/20 text-emerald-950 dark:text-emerald-100";
                    feedbackEl.innerHTML = `<strong class="text-emerald-700 dark:text-emerald-400 font-sans block mb-1">Correct Answer:</strong> ${ev.explanation}`;
                } else {
                    feedbackEl.className = "p-3.5 rounded text-xs border border-rose-300 dark:border-rose-900 bg-rose-50/60 dark:bg-rose-950/20 text-rose-950 dark:text-rose-100";
                    feedbackEl.innerHTML = `<strong class="text-rose-700 dark:text-rose-400 font-sans block mb-1">Incorrect.</strong> ${ev.explanation}`;
                }
            }
        });
        
        const badgeArea = document.getElementById('quizScoreBadgeArea');
        if (badgeArea) {
            badgeArea.innerHTML = `
                <span class="px-3 py-1 rounded text-xs font-mono border border-[var(--border-main)] bg-[var(--bg-sheet)] text-[var(--accent-primary)] font-bold">
                    Score: ${result.score}/${result.total} (${result.percentage}%)
                </span>
            `;
        }
        
        if (result.percentage >= 70 && !currentChapter.user_state?.completed) {
            toggleCompleted(chapterId, true);
        }
        
        loadStages(true);
        loadGlobalStats();
    } catch (err) {
        console.error('Quiz submission error:', err);
    }
}

async function toggleCompleted(chapterId, status) {
    try {
        await fetch(`${API_BASE}/chapters/${chapterId}/progress`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ completed: status })
        });
        if (currentChapter && currentChapter.id === chapterId) {
            currentChapter.user_state.completed = status;
        }
        renderChapterReader();
        loadStages(true);
        loadGlobalStats();
    } catch (err) {
        console.error('Failed to update completion status:', err);
    }
}

async function toggleBookmark(chapterId) {
    if (!currentChapter) return;
    const newStatus = !(currentChapter.user_state?.bookmarked);
    try {
        await fetch(`${API_BASE}/chapters/${chapterId}/progress`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ bookmarked: newStatus })
        });
        currentChapter.user_state.bookmarked = newStatus;
        renderChapterReader();
        loadStages(true);
    } catch (err) {
        console.error('Failed to bookmark:', err);
    }
}

const handleNotesInput = debounce(async (chapterId) => {
    const val = document.getElementById('chapterNotesInput').value;
    const statusEl = document.getElementById('notesSaveStatus');
    if (statusEl) statusEl.innerText = 'Saving...';
    try {
        await fetch(`${API_BASE}/chapters/${chapterId}/progress`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ notes: val })
        });
        if (statusEl) statusEl.innerText = 'Saved to database';
    } catch (err) {
        if (statusEl) statusEl.innerText = 'Error saving';
    }
}, 600);

function setExamFilter(exam) {
    currentExamFilter = exam;
    document.querySelectorAll('.exam-filter-btn').forEach(b => {
        b.classList.remove('active-exam-filter', 'bg-[var(--accent-primary)]', 'text-white', 'font-medium', 'shadow-xs');
        b.classList.add('text-[var(--text-muted)]');
    });
    const activeBtn = document.getElementById(`filterBtn-${exam}`);
    if (activeBtn) {
        activeBtn.classList.add('active-exam-filter', 'bg-[var(--accent-primary)]', 'text-white', 'font-medium', 'shadow-xs');
        activeBtn.classList.remove('text-[var(--text-muted)]');
    }
    loadStages();
}

function renderMarkdown(md) {
    if (!md) return '';
    let html = md
        .replace(/```([a-z]*)\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>')
        .replace(/`([^`]+)`/g, '<code>$1</code>')
        .replace(/^#### (.*$)/gim, '<h4>$1</h4>')
        .replace(/^### (.*$)/gim, '<h3>$1</h3>')
        .replace(/^## (.*$)/gim, '<h2>$1</h2>')
        .replace(/^# (.*$)/gim, '<h1>$1</h1>')
        .replace(/\*\*([^\*]+)\*\*/g, '<strong>$1</strong>')
        .replace(/\*([^\*]+)\*/g, '<em>$1</em>')
        .replace(/^---$/gim, '<hr class="my-6 border-[var(--border-main)]">')
        .replace(/^\s*\*\s+(.*$)/gim, '<li>$1</li>')
        .replace(/^\s*\d+\.\s+(.*$)/gim, '<li>$1</li>')
        .replace(/\|(.+)\|/g, function(match) {
            let cells = match.split('|').slice(1, -1);
            if (cells.some(c => c.includes('---'))) return '';
            let rowHtml = cells.map(c => `<td>${c.trim()}</td>`).join('');
            return `<tr>${rowHtml}</tr>`;
        })
        .replace(/\n\n+/g, '</p><p>');

    return `<p>${html}</p>`;
}

// ==============================================================
// PDF LIBRARY & RAG AI TUTOR ENGINE
// ==============================================================

async function loadDocuments() {
    const container = document.getElementById('libraryContainer');
    if (!container) return;
    
    if (activeDocumentId) {
        // If viewing an active document split view, re-render it
        renderDocumentSplitView(activeDocumentId);
        return;
    }

    container.innerHTML = `
        <div class="text-center py-16 text-[var(--text-muted)] font-serif italic flex flex-col items-center gap-2">
            <i class="fa-solid fa-spinner fa-spin text-base text-[var(--accent-primary)]"></i>
            <span>Loading document library...</span>
        </div>
    `;

    try {
        let url = `${API_BASE}/documents?category=${currentDocCategory}`;
        if (currentDocSearch) url += `&search=${encodeURIComponent(currentDocSearch)}`;
        
        const res = await fetch(url);
        const data = await res.json();
        cachedDocuments = data.documents || [];
        renderDocumentsGrid(cachedDocuments);
        loadGlobalStats();
    } catch (err) {
        console.error('Failed to load documents:', err);
        container.innerHTML = '<div class="text-center py-12 text-rose-600 text-xs font-serif">Failed to load documents.</div>';
    }
}

function renderDocumentsGrid(docs) {
    const container = document.getElementById('libraryContainer');
    if (!container) return;

    if (docs.length === 0) {
        container.innerHTML = `
            <div class="p-12 text-center border-2 border-dashed border-[var(--border-main)] rounded-xl bg-[var(--bg-sheet)] space-y-4 font-serif">
                <i class="fa-solid fa-folder-open text-4xl text-[var(--text-faint)]"></i>
                <div class="space-y-1">
                    <h3 class="text-lg font-bold text-[var(--text-heading)]">No Study Documents Found</h3>
                    <p class="text-xs text-[var(--text-muted)] max-w-md mx-auto">Upload custom PDFs or import high-yield study materials from your local workspace to enable in-browser viewing and AI tutoring.</p>
                </div>
                <div class="flex items-center justify-center gap-3 pt-2 font-sans">
                    <button onclick="openUploadModal()" class="px-4 py-2 rounded-lg bg-[var(--accent-primary)] hover:bg-[var(--accent-primary-hover)] text-white text-xs font-semibold shadow-xs">
                        Upload First PDF
                    </button>
                    <button onclick="openWorkspaceImportModal()" class="px-4 py-2 rounded-lg border border-[var(--border-main)] bg-[var(--bg-subtle)] text-xs text-[var(--text-heading)] font-medium">
                        Import from Workspace (52 PDFs)
                    </button>
                </div>
            </div>
        `;
        return;
    }

    container.innerHTML = `
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            ${docs.map(doc => {
                const sizeKb = Math.round(doc.file_size / 1024);
                const sizeStr = sizeKb > 1024 ? `${(sizeKb/1024).toFixed(1)} MB` : `${sizeKb} KB`;
                return `
                    <div class="p-5 rounded-xl border border-[var(--border-main)] bg-[var(--bg-sheet)] hover:border-[var(--text-faint)] transition shadow-2xs space-y-3 flex flex-col justify-between">
                        <div class="space-y-2">
                            <div class="flex items-center justify-between text-[11px] font-sans">
                                <span class="px-2 py-0.5 rounded text-[10px] font-semibold bg-[var(--accent-tag)] text-[var(--accent-tag-text)]">
                                    ${doc.category}
                                </span>
                                <span class="text-[var(--text-faint)]">${doc.page_count} Pages • ${sizeStr}</span>
                            </div>

                            <h4 class="font-serif font-bold text-sm text-[var(--text-heading)] leading-snug line-clamp-2" title="${doc.original_filename}">
                                ${doc.original_filename}
                            </h4>

                            <div class="text-xs text-[var(--text-muted)] line-clamp-3 leading-relaxed font-serif italic border-l-2 border-[var(--border-accent)] pl-2.5">
                                ${doc.summary || 'Summary processing...'}
                            </div>
                        </div>

                        <div class="pt-3 border-t border-[var(--border-light)] flex items-center justify-between font-sans text-xs">
                            <button onclick="openDocumentView('${doc.id}')" class="px-3 py-1.5 rounded-lg bg-[var(--accent-primary)] hover:bg-[var(--accent-primary-hover)] text-white font-medium flex items-center gap-1.5 shadow-xs transition">
                                <i class="fa-solid fa-book-open-reader text-[10px]"></i>
                                <span>Read & Ask AI</span>
                            </button>
                            <div class="flex items-center gap-1.5 text-[var(--text-faint)]">
                                <a href="${API_BASE}/documents/${doc.id}/raw" target="_blank" class="p-1.5 rounded hover:bg-[var(--bg-hover)] text-[var(--text-muted)]" title="Open PDF in new tab">
                                    <i class="fa-solid fa-arrow-up-right-from-square text-xs"></i>
                                </a>
                                <button onclick="handleDeleteDocument('${doc.id}', '${doc.original_filename}')" class="p-1.5 rounded hover:bg-rose-50 hover:text-rose-600 transition" title="Delete document">
                                    <i class="fa-regular fa-trash-can text-xs"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                `;
            }).join('')}
        </div>
    `;
}

function filterDocuments(cat) {
    currentDocCategory = cat;
    document.querySelectorAll('.doc-cat-pill').forEach(btn => {
        btn.classList.remove('active-cat-pill', 'bg-[var(--accent-primary)]', 'text-white', 'shadow-xs');
        btn.classList.add('border', 'border-[var(--border-main)]', 'text-[var(--text-muted)]');
    });
    const activeBtn = document.getElementById(`docCat-${cat}`);
    if (activeBtn) {
        activeBtn.classList.add('active-cat-pill', 'bg-[var(--accent-primary)]', 'text-white', 'shadow-xs');
        activeBtn.classList.remove('border', 'border-[var(--border-main)]', 'text-[var(--text-muted)]');
    }
    loadDocuments();
}

const debounceFilterDocuments = debounce(() => {
    currentDocSearch = document.getElementById('docSearchInput').value.trim();
    loadDocuments();
}, 250);

// ==============================================================
// SPLIT VIEW: IN-BROWSER PDF VIEWER & AI TUTOR CHATBOT
// ==============================================================

async function openDocumentView(docId) {
    activeDocumentId = docId;
    activeChatSessionId = `session_${docId}`;
    renderDocumentSplitView(docId);
}

function exitDocumentSplitView() {
    activeDocumentId = null;
    loadDocuments();
}

async function renderDocumentSplitView(docId) {
    const container = document.getElementById('libraryContainer');
    if (!container) return;

    let doc = cachedDocuments.find(d => d.id === docId);
    if (!doc) {
        const res = await fetch(`${API_BASE}/documents/${docId}`);
        doc = await res.json();
    }

    container.innerHTML = `
        <div class="space-y-4">
            
            <!-- Top Navigation & Document Meta Bar -->
            <div class="p-3.5 rounded-lg border border-[var(--border-main)] bg-[var(--bg-sheet)] flex flex-wrap items-center justify-between gap-3 shadow-2xs font-sans text-xs">
                <div class="flex items-center gap-3">
                    <button onclick="exitDocumentSplitView()" class="px-2.5 py-1 rounded-md border border-[var(--border-main)] hover:bg-[var(--bg-hover)] text-[var(--text-heading)] font-medium flex items-center gap-1.5 transition">
                        <i class="fa-solid fa-arrow-left text-[10px]"></i>
                        <span>Library Grid</span>
                    </button>
                    <div class="flex items-center gap-2">
                        <span class="px-2 py-0.5 rounded text-[10px] font-semibold bg-[var(--accent-tag)] text-[var(--accent-tag-text)]">${doc.category}</span>
                        <h3 class="font-serif font-bold text-sm text-[var(--text-heading)] truncate max-w-md">${doc.original_filename}</h3>
                        <span class="text-[var(--text-faint)] text-[11px]">• ${doc.page_count} Pages</span>
                    </div>
                </div>

                <div class="flex items-center gap-2">
                    <a href="${API_BASE}/documents/${doc.id}/raw" target="_blank" class="px-2.5 py-1 rounded border border-[var(--border-main)] hover:bg-[var(--bg-hover)] text-[var(--text-muted)] flex items-center gap-1 text-[11px]">
                        <i class="fa-solid fa-external-link text-[10px]"></i>
                        <span>Open Raw PDF</span>
                    </a>
                    <button onclick="clearCurrentChatSession()" class="px-2.5 py-1 rounded border border-[var(--border-main)] hover:bg-[var(--bg-hover)] text-[var(--text-muted)] flex items-center gap-1 text-[11px]">
                        <i class="fa-solid fa-rotate-left text-[10px]"></i>
                        <span>Reset Chat</span>
                    </button>
                </div>
            </div>

            <!-- Split Workstation: Left PDF Viewer, Right AI Tutor -->
            <div class="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">
                
                <!-- Left Pane: In-Browser Embedded PDF Viewer (7 cols) -->
                <div class="lg:col-span-7 bg-[var(--bg-sheet)] rounded-xl border border-[var(--border-main)] overflow-hidden shadow-xs flex flex-col h-[750px]">
                    <div class="px-3.5 py-2 border-b border-[var(--border-main)] bg-[var(--bg-subtle)] text-[11px] text-[var(--text-muted)] flex items-center justify-between font-sans">
                        <span class="flex items-center gap-1.5">
                            <i class="fa-regular fa-file-pdf text-rose-700"></i>
                            <span>Interactive PDF Viewport</span>
                        </span>
                        <span class="text-[10px] text-[var(--text-faint)]">Native PDF Rendering with Search & Zoom</span>
                    </div>
                    <iframe src="${API_BASE}/documents/${doc.id}/raw#toolbar=1&navpanes=1" class="w-full flex-1 border-0 bg-slate-900" title="PDF Document Viewer"></iframe>
                </div>

                <!-- Right Pane: AI Document Assistant & Contextual Chat (5 cols) -->
                <div class="lg:col-span-5 bg-[var(--bg-sheet)] rounded-xl border border-[var(--border-main)] flex flex-col h-[750px] shadow-xs overflow-hidden">
                    
                    <!-- Chat Header with AI Status -->
                    <div class="p-3.5 border-b border-[var(--border-main)] bg-[var(--bg-subtle)] flex items-center justify-between font-sans text-xs">
                        <div class="flex items-center gap-2">
                            <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                            <span class="font-serif font-bold text-[var(--text-heading)]">AI Document Tutor</span>
                        </div>
                        <span class="text-[10px] text-[var(--text-faint)] font-mono">Gemini 2.5 RAG</span>
                    </div>

                    <!-- Scrollable Conversation & Summary Area -->
                    <div class="flex-1 overflow-y-auto p-4 space-y-4 font-serif text-xs" id="chatMessagesStream">
                        
                        <!-- Document Summary Card -->
                        <div class="p-4 rounded-lg border border-[var(--border-main)] bg-[var(--bg-subtle)] space-y-2">
                            <span class="text-[10px] font-sans font-bold uppercase tracking-wider text-[var(--accent-primary)] block">Document Brief & Scope:</span>
                            <div class="leading-relaxed text-[var(--text-main)] italic">
                                ${doc.summary || 'Summary processing...'}
                            </div>
                        </div>

                        <!-- Suggested Starter Prompt Chips -->
                        <div class="space-y-1.5 font-sans">
                            <span class="text-[10px] text-[var(--text-faint)] uppercase tracking-wider block">Suggested Questions:</span>
                            <div class="flex flex-wrap gap-1.5 text-[11px]">
                                <button onclick="fillAndSendChat('Summarize the top 5 most important technical concepts in this PDF with page citations.')" 
                                        class="px-2.5 py-1 rounded-full border border-[var(--border-main)] bg-[var(--bg-sheet)] hover:border-[var(--accent-primary)] text-[var(--text-muted)] hover:text-[var(--text-heading)] transition text-left">
                                    💡 Top 5 Concepts
                                </button>
                                <button onclick="fillAndSendChat('What are the critical exam formulas or rules mentioned in this document?')" 
                                        class="px-2.5 py-1 rounded-full border border-[var(--border-main)] bg-[var(--bg-sheet)] hover:border-[var(--accent-primary)] text-[var(--text-muted)] hover:text-[var(--text-heading)] transition text-left">
                                    📐 Key Formulas
                                </button>
                                <button onclick="fillAndSendChat('Extract 3 multiple choice questions from this PDF with explanations.')" 
                                        class="px-2.5 py-1 rounded-full border border-[var(--border-main)] bg-[var(--bg-sheet)] hover:border-[var(--accent-primary)] text-[var(--text-muted)] hover:text-[var(--text-heading)] transition text-left">
                                    🎯 Extract MCQs
                                </button>
                            </div>
                        </div>

                        <!-- Chat Messages Container -->
                        <div id="chatMessagesList" class="space-y-3.5 pt-2">
                            <!-- Populated via loadChatHistory() -->
                        </div>
                    </div>

                    <!-- Chat Input Field Bar -->
                    <div class="p-3 border-t border-[var(--border-main)] bg-[var(--bg-chrome)] font-sans">
                        <form onsubmit="handleChatSubmit(event)" class="flex items-center gap-2">
                            <input type="text" id="chatQueryInput" placeholder="Ask any question grounded in this PDF..." 
                                   class="flex-1 p-2 rounded-lg border border-[var(--border-main)] bg-[var(--bg-sheet)] text-xs text-[var(--text-main)] focus:outline-none focus:ring-1 focus:ring-[var(--accent-primary)] font-serif">
                            <button type="submit" id="chatSendBtn" class="px-4 py-2 rounded-lg bg-[var(--accent-primary)] hover:bg-[var(--accent-primary-hover)] text-white text-xs font-semibold shadow-xs transition flex items-center gap-1.5">
                                <span>Ask</span>
                                <i class="fa-solid fa-paper-plane text-[10px]"></i>
                            </button>
                        </form>
                    </div>

                </div>

            </div>

        </div>
    `;

    loadChatHistory();
}

async function loadChatHistory() {
    const list = document.getElementById('chatMessagesList');
    if (!list) return;

    try {
        const res = await fetch(`${API_BASE}/chat/history?session_id=${activeChatSessionId}`);
        const data = await res.json();
        const messages = data.messages || [];

        list.innerHTML = messages.map(msg => renderChatMessageBubble(msg)).join('');
        scrollChatToBottom();
    } catch (err) {
        console.error('Failed to load chat history:', err);
    }
}

function renderChatMessageBubble(msg) {
    const isUser = msg.role === 'user';
    const contentHtml = isUser ? msg.content : renderMarkdown(msg.content);
    
    let sourcesHtml = '';
    if (!isUser && msg.sources && msg.sources.length > 0) {
        sourcesHtml = `
            <div class="mt-2.5 pt-2 border-t border-[var(--border-light)] font-sans text-[11px] space-y-1">
                <span class="font-bold text-[10px] text-[var(--accent-primary)] uppercase tracking-wider block">Referenced Document Citations:</span>
                <div class="space-y-1">
                    ${msg.sources.map(s => `
                        <div class="p-1.5 rounded border border-[var(--border-light)] bg-[var(--bg-sheet)] flex items-start gap-1.5">
                            <span class="px-1.5 py-0.2 rounded bg-[var(--bg-hover)] text-[10px] font-mono text-[var(--accent-primary)] font-semibold shrink-0">P. ${s.page}</span>
                            <span class="text-[var(--text-muted)] line-clamp-2">${s.snippet}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    return `
        <div class="flex gap-2.5 ${isUser ? 'justify-end' : 'justify-start'}">
            ${!isUser ? `<span class="w-6 h-6 rounded-full bg-[var(--accent-primary)] text-white text-[10px] font-serif font-bold flex items-center justify-center shrink-0 mt-0.5">§</span>` : ''}
            <div class="max-w-[85%] p-3.5 rounded-xl border ${isUser ? 'border-[var(--accent-primary)] bg-[var(--accent-primary)] text-white' : 'border-[var(--border-main)] bg-[var(--bg-sheet)] text-[var(--text-main)]'} shadow-2xs leading-relaxed">
                <div class="${isUser ? 'text-white' : 'markdown-body text-xs'}">${contentHtml}</div>
                ${sourcesHtml}
            </div>
            ${isUser ? `<span class="w-6 h-6 rounded-full bg-[var(--bg-hover)] text-[var(--text-muted)] text-[10px] font-bold flex items-center justify-center shrink-0 mt-0.5"><i class="fa-solid fa-user"></i></span>` : ''}
        </div>
    `;
}

function fillAndSendChat(query) {
    const input = document.getElementById('chatQueryInput');
    if (input) {
        input.value = query;
        handleChatSubmit(new Event('submit'));
    }
}

async function handleChatSubmit(e) {
    if (e && e.preventDefault) e.preventDefault();
    const input = document.getElementById('chatQueryInput');
    const query = input.value.trim();
    if (!query) return;

    input.value = '';
    const list = document.getElementById('chatMessagesList');

    // Append user message immediately
    const userMsgHtml = renderChatMessageBubble({ role: 'user', content: query });
    list.innerHTML += userMsgHtml;

    // Append loading bubble
    const loadingId = `thinking-${Date.now()}`;
    list.innerHTML += `
        <div id="${loadingId}" class="flex gap-2.5 justify-start">
            <span class="w-6 h-6 rounded-full bg-[var(--accent-primary)] text-white text-[10px] font-serif font-bold flex items-center justify-center shrink-0 mt-0.5">§</span>
            <div class="p-3.5 rounded-xl border border-[var(--border-main)] bg-[var(--bg-sheet)] text-xs text-[var(--text-muted)] italic font-serif flex items-center gap-2 shadow-2xs">
                <i class="fa-solid fa-spinner fa-spin text-[var(--accent-primary)]"></i>
                <span>Retrieving document vector passages & consulting Gemini...</span>
            </div>
        </div>
    `;
    scrollChatToBottom();

    try {
        const res = await fetch(`${API_BASE}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query: query,
                session_id: activeChatSessionId,
                document_id: activeDocumentId
            })
        });

        const data = await res.json();
        const loadingEl = document.getElementById(loadingId);
        if (loadingEl) loadingEl.remove();

        list.innerHTML += renderChatMessageBubble({
            role: 'model',
            content: data.answer,
            sources: data.sources
        });
        scrollChatToBottom();
    } catch (err) {
        console.error('Chat error:', err);
        const loadingEl = document.getElementById(loadingId);
        if (loadingEl) loadingEl.remove();
        list.innerHTML += `<div class="p-3 rounded border border-rose-300 text-rose-700 text-xs">Error communicating with AI tutor.</div>`;
    }
}

function scrollChatToBottom() {
    const stream = document.getElementById('chatMessagesStream');
    if (stream) stream.scrollTop = stream.scrollHeight;
}

async function clearCurrentChatSession() {
    if (confirm('Clear conversation history for this document?')) {
        await fetch(`${API_BASE}/chat/history?session_id=${activeChatSessionId}`, { method: 'DELETE' });
        loadChatHistory();
    }
}

// ==============================================================
// MODAL INTERACTIONS: UPLOAD, WORKSPACE IMPORT & API KEY
// ==============================================================

function openUploadModal() {
    uploadModal.classList.remove('hidden');
    document.getElementById('uploadStatusMessage').classList.add('hidden');
}
function closeUploadModal() {
    uploadModal.classList.add('hidden');
}

async function handleUploadSubmit(e) {
    e.preventDefault();
    const fileInput = document.getElementById('pdfFileInput');
    const categoryInput = document.getElementById('pdfCategoryInput');
    const statusMsg = document.getElementById('uploadStatusMessage');
    const submitBtn = document.getElementById('uploadSubmitBtn');

    if (!fileInput.files || fileInput.files.length === 0) return;
    const file = fileInput.files[0];

    const formData = new FormData();
    formData.append('file', file);
    formData.append('category', categoryInput.value);

    statusMsg.classList.remove('hidden');
    statusMsg.className = "p-3 rounded-lg text-xs bg-[var(--bg-subtle)] border border-[var(--border-main)] text-[var(--text-main)] flex items-center gap-2";
    statusMsg.innerHTML = `<i class="fa-solid fa-spinner fa-spin text-[var(--accent-primary)]"></i> Parsing PDF pages, creating chunks & generating embeddings...`;
    submitBtn.disabled = true;

    try {
        const res = await fetch(`${API_BASE}/documents/upload`, {
            method: 'POST',
            body: formData
        });

        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Upload failed');

        statusMsg.className = "p-3 rounded-lg text-xs bg-emerald-50 text-emerald-800 border border-emerald-300";
        statusMsg.innerHTML = `<strong>Success!</strong> Indexed "${file.name}" with ${data.document?.chunks_count || 0} chunks.`;
        
        setTimeout(() => {
            closeUploadModal();
            fileInput.value = '';
            submitBtn.disabled = false;
            loadDocuments();
            if (data.document?.id) openDocumentView(data.document.id);
        }, 1200);
    } catch (err) {
        statusMsg.className = "p-3 rounded-lg text-xs bg-rose-50 text-rose-800 border border-rose-300";
        statusMsg.innerHTML = `<strong>Upload Error:</strong> ${err.message}`;
        submitBtn.disabled = false;
    }
}

async function openWorkspaceImportModal() {
    workspaceModal.classList.remove('hidden');
    const list = document.getElementById('workspacePdfsList');
    list.innerHTML = `<div class="text-center py-8 text-xs text-[var(--text-faint)] italic"><i class="fa-solid fa-spinner fa-spin mr-2"></i>Scanning workspace for study PDFs...</div>`;

    try {
        const res = await fetch(`${API_BASE}/documents/workspace-available`);
        const data = await res.json();
        cachedWorkspacePdfs = data.pdfs || [];
        renderWorkspacePdfsList(cachedWorkspacePdfs);
    } catch (err) {
        list.innerHTML = `<div class="text-center py-6 text-xs text-rose-600">Failed to scan workspace files.</div>`;
    }
}

function closeWorkspaceModal() {
    workspaceModal.classList.add('hidden');
}

function filterWorkspacePdfs() {
    const q = document.getElementById('wsSearchInput').value.toLowerCase().trim();
    const filtered = cachedWorkspacePdfs.filter(p => p.filename.toLowerCase().includes(q) || p.folder.toLowerCase().includes(q));
    renderWorkspacePdfsList(filtered);
}

function renderWorkspacePdfsList(pdfs) {
    const list = document.getElementById('workspacePdfsList');
    if (!pdfs || pdfs.length === 0) {
        list.innerHTML = `<div class="text-center py-8 text-xs text-[var(--text-faint)]">No study PDFs matching search.</div>`;
        return;
    }

    list.innerHTML = pdfs.map((pdf, idx) => {
        const sizeMb = (pdf.size_bytes / (1024 * 1024)).toFixed(1);
        return `
            <div class="p-3 rounded-lg border border-[var(--border-main)] bg-[var(--bg-sheet)] hover:bg-[var(--bg-subtle)] flex items-center justify-between gap-3 text-xs">
                <div class="overflow-hidden space-y-0.5">
                    <div class="font-serif font-bold text-[var(--text-heading)] truncate" title="${pdf.filename}">${pdf.filename}</div>
                    <div class="text-[10px] text-[var(--text-faint)] font-sans">${pdf.folder} • ${sizeMb} MB • Category: ${pdf.category}</div>
                </div>
                <button onclick="importSelectedWorkspacePdf('${encodeURIComponent(pdf.path)}', '${pdf.category}', this)" 
                        class="px-3 py-1.5 rounded-md bg-[var(--accent-primary)] hover:bg-[var(--accent-primary-hover)] text-white text-xs font-medium shrink-0 transition shadow-2xs">
                    Import & Index
                </button>
            </div>
        `;
    }).join('');
}

async function importSelectedWorkspacePdf(encodedPath, category, btnElement) {
    const path = decodeURIComponent(encodedPath);
    btnElement.disabled = true;
    btnElement.innerHTML = `<i class="fa-solid fa-spinner fa-spin mr-1"></i>Indexing...`;

    try {
        const res = await fetch(`${API_BASE}/documents/import-workspace`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ file_path: path, category: category })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Import failed');

        btnElement.className = "px-3 py-1.5 rounded-md bg-emerald-700 text-white text-xs font-semibold shrink-0";
        btnElement.innerHTML = `<i class="fa-solid fa-check mr-1"></i>Imported`;
        loadDocuments();
    } catch (err) {
        btnElement.disabled = false;
        btnElement.className = "px-3 py-1.5 rounded-md bg-rose-700 text-white text-xs font-semibold shrink-0";
        btnElement.innerText = "Error";
        alert(`Failed to import: ${err.message}`);
    }
}

async function handleDeleteDocument(docId, filename) {
    if (confirm(`Are you sure you want to delete "${filename}" and its vector chunks?`)) {
        try {
            await fetch(`${API_BASE}/documents/${docId}`, { method: 'DELETE' });
            loadDocuments();
        } catch (err) {
            alert('Failed to delete document');
        }
    }
}

// API Key Modal & Validation
async function checkApiKeyStatus() {
    try {
        const res = await fetch(`${API_BASE}/settings/status`);
        const data = await res.json();
        const label = document.getElementById('apiKeyStatusLabel');
        const currentStatus = document.getElementById('apiKeyCurrentStatus');
        const maskedArea = document.getElementById('apiKeyMaskedArea');

        if (data.gemini_api_configured) {
            if (label) label.innerText = 'AI Active';
            if (currentStatus) {
                currentStatus.innerText = 'Active (Gemini 2.5 Flash)';
                currentStatus.className = 'font-bold text-emerald-600';
            }
            if (maskedArea) maskedArea.innerText = `Key: ${data.masked_key} • Models: ${data.embedding_model}, ${data.chat_model}`;
        } else {
            if (label) label.innerText = 'Set AI Key';
            if (currentStatus) {
                currentStatus.innerText = 'Not Configured (Using Offline Heuristics)';
                currentStatus.className = 'font-bold text-amber-600';
            }
            if (maskedArea) maskedArea.innerText = 'Add your Gemini API Key to enable full neural reasoning & RAG.';
        }
    } catch (err) {
        console.error('Failed to check API status:', err);
    }
}

function openApiKeyModal() {
    apiKeyModal.classList.remove('hidden');
    checkApiKeyStatus();
    document.getElementById('apiKeySaveStatus').classList.add('hidden');
}

function closeApiKeyModal() {
    apiKeyModal.classList.add('hidden');
}

async function saveGeminiApiKey() {
    const input = document.getElementById('geminiApiKeyInput');
    const key = input.value.trim();
    const status = document.getElementById('apiKeySaveStatus');

    if (!key || key.length < 15) {
        status.classList.remove('hidden');
        status.className = "p-2 rounded text-xs bg-rose-50 text-rose-800 border border-rose-300";
        status.innerText = "Please paste a valid Gemini API key (starts with AIzaSy...).";
        return;
    }

    try {
        const res = await fetch(`${API_BASE}/settings/api-key`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ api_key: key })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Save failed');

        status.classList.remove('hidden');
        status.className = "p-2 rounded text-xs bg-emerald-50 text-emerald-800 border border-emerald-300";
        status.innerText = "Key saved and validated successfully!";
        input.value = '';
        checkApiKeyStatus();

        setTimeout(() => {
            closeApiKeyModal();
        }, 1200);
    } catch (err) {
        status.classList.remove('hidden');
        status.className = "p-2 rounded text-xs bg-rose-50 text-rose-800 border border-rose-300";
        status.innerText = `Error: ${err.message}`;
    }
}

// ==============================================================
// QUESTION BANK ENGINE
// ==============================================================
async function loadQuestionBank() {
    const qListContainer = document.getElementById('qbankListContainer');
    qListContainer.innerHTML = '<div class="text-center py-8 text-[var(--text-faint)] text-xs italic font-serif">Loading Question Bank...</div>';
    
    try {
        const res = await fetch(`${API_BASE}/questions?category=${currentQBankCategory}&limit=300`);
        const data = await res.json();
        cachedQBankList = data.questions || [];
        
        document.getElementById('qbankTotalCount').innerText = `${data.total} Questions`;
        renderQBankList(cachedQBankList);
    } catch (err) {
        console.error('Failed to load questions:', err);
    }
}

function renderQBankList(questions) {
    const qListContainer = document.getElementById('qbankListContainer');
    if (!questions || questions.length === 0) {
        qListContainer.innerHTML = '<div class="text-center py-10 text-[var(--text-faint)] text-xs font-serif italic">No matching questions found.</div>';
        return;
    }
    
    qListContainer.innerHTML = questions.map((q, idx) => `
        <div class="p-4 rounded-lg border border-[var(--border-main)] bg-[var(--bg-sheet)] space-y-2 shadow-2xs">
            <div class="flex items-center justify-between text-[11px] font-sans text-[var(--text-faint)]">
                <span class="font-bold text-[var(--accent-primary)]">${q.category}</span>
                <span>Question #${q.id} • ${q.exam}</span>
            </div>
            <p class="text-sm font-semibold text-[var(--text-heading)] leading-relaxed font-serif">
                ${q.question}
            </p>
            <div class="hidden pt-2 text-xs text-[var(--text-main)] leading-relaxed border-t border-[var(--border-light)] font-serif" id="qbank-ans-${idx}">
                <strong class="text-[var(--accent-primary)] font-sans text-[11px] uppercase tracking-wider block mb-1">Answer & Explanation:</strong>
                ${q.answer}
            </div>
            <button onclick="toggleQBankAns(${idx})" id="qbank-btn-${idx}" class="text-[11px] font-sans font-medium text-[var(--accent-primary)] hover:underline pt-0.5 flex items-center gap-1">
                <span>Reveal Answer</span>
                <i class="fa-solid fa-chevron-down text-[9px]"></i>
            </button>
        </div>
    `).join('');
}

function filterQBank(category) {
    currentQBankCategory = category;
    document.querySelectorAll('.qbank-cat-pill').forEach(btn => {
        btn.classList.remove('active-cat-pill', 'bg-[var(--accent-primary)]', 'text-white', 'font-medium', 'shadow-xs');
        btn.classList.add('text-[var(--text-muted)]', 'border', 'border-[var(--border-main)]');
    });
    const activeBtn = document.getElementById(`qbankCat-${category}`);
    if (activeBtn) {
        activeBtn.classList.add('active-cat-pill', 'bg-[var(--accent-primary)]', 'text-white', 'font-medium', 'shadow-xs');
        activeBtn.classList.remove('text-[var(--text-muted)]', 'border', 'border-[var(--border-main)]');
    }
    loadQuestionBank();
}

const debounceFilterQBank = debounce(() => {
    const query = document.getElementById('qbankSearchInput').value.toLowerCase().trim();
    if (!query) {
        renderQBankList(cachedQBankList);
        return;
    }
    const filtered = cachedQBankList.filter(q => 
        q.question.toLowerCase().includes(query) || q.answer.toLowerCase().includes(query)
    );
    renderQBankList(filtered);
}, 200);

function toggleQBankAns(idx) {
    const el = document.getElementById(`qbank-ans-${idx}`);
    const btn = document.getElementById(`qbank-btn-${idx}`);
    if (el.classList.contains('hidden')) {
        el.classList.remove('hidden');
        btn.innerHTML = '<span>Hide Answer</span> <i class="fa-solid fa-chevron-up text-[9px]"></i>';
    } else {
        el.classList.add('hidden');
        btn.innerHTML = '<span>Reveal Answer</span> <i class="fa-solid fa-chevron-down text-[9px]"></i>';
    }
}

// ==============================================================
// TIMED MOCK EXAM SIMULATOR
// ==============================================================
async function startOrResetMockExam() {
    if (isMockRunning) {
        if (confirm('A mock exam is currently in progress. Do you wish to restart?')) {
            clearInterval(mockTimerInterval);
            isMockRunning = false;
        } else {
            return;
        }
    }

    const container = document.getElementById('mockQuestionsContainer');
    container.innerHTML = `
        <div class="text-center py-12 text-[var(--text-muted)] text-sm italic font-serif flex flex-col items-center gap-2">
            <i class="fa-solid fa-spinner fa-spin text-base text-[var(--accent-primary)]"></i>
            <span>Compiling 30 randomized questions across the curriculum...</span>
        </div>
    `;

    try {
        const examParam = (currentExamFilter && currentExamFilter !== 'all') ? `&exam=${currentExamFilter}` : '';
        const res = await fetch(`${API_BASE}/mock-exam?count=30${examParam}`);
        const data = await res.json();
        mockExamQuestions = data.questions || [];

        if (mockExamQuestions.length === 0) {
            container.innerHTML = '<div class="text-center py-12 text-[var(--text-muted)] text-xs font-serif">No questions available for this filter. Please select "All Exams" to view all.</div>';
            return;
        }

        mockUserAnswers = {};
        mockTimeRemaining = 30 * 60; // 30 minutes
        isMockRunning = true;

        document.getElementById('mockStartBtn').innerText = 'Submit Mock Exam';
        document.getElementById('mockStartBtn').onclick = submitMockExam;
        document.getElementById('mockResultsCard').classList.add('hidden');

        renderMockQuestions();
        startMockTimer();
    } catch (err) {
        console.error('Failed to load mock exam questions:', err);
        container.innerHTML = '<div class="text-center py-12 text-rose-600 text-xs">Failed to load mock exam. Please try again.</div>';
    }
}

function startMockTimer() {
    clearInterval(mockTimerInterval);
    updateMockTimerDisplay();
    mockTimerInterval = setInterval(() => {
        mockTimeRemaining--;
        updateMockTimerDisplay();
        if (mockTimeRemaining <= 0) {
            clearInterval(mockTimerInterval);
            alert('Time has expired! Submitting your exam automatically.');
            submitMockExam();
        }
    }, 1000);
}

function updateMockTimerDisplay() {
    const mins = Math.floor(mockTimeRemaining / 60);
    const secs = mockTimeRemaining % 60;
    const formatted = `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
    document.getElementById('mockTimerDisplay').innerText = formatted;
}

function renderMockQuestions() {
    const container = document.getElementById('mockQuestionsContainer');
    container.innerHTML = mockExamQuestions.map((q, idx) => `
        <div class="p-5 rounded-lg border border-[var(--border-main)] bg-[var(--bg-sheet)] space-y-3 shadow-2xs font-serif" id="mockCard-${idx}">
            <div class="flex items-center justify-between text-[11px] font-sans text-[var(--text-faint)]">
                <span class="font-bold text-[var(--accent-primary)]">Question ${idx + 1} of ${mockExamQuestions.length}</span>
                <span>${q.chapterTitle || 'Core IT Knowledge'}</span>
            </div>
            <p class="text-sm font-semibold text-[var(--text-heading)] leading-relaxed">
                ${q.q}
            </p>
            <div class="space-y-1.5 text-xs font-sans">
                ${q.options.map((opt, optIdx) => `
                    <label class="flex items-start gap-2.5 p-2.5 rounded border border-[var(--border-main)] bg-[var(--bg-subtle)] cursor-pointer hover:border-[var(--accent-primary)] transition" id="mockLabel-${idx}-${optIdx}">
                        <input type="radio" name="mock-${idx}" value="${optIdx}" onchange="recordMockAnswer(${idx}, ${optIdx})" class="mt-0.5 accent-[var(--accent-primary)]">
                        <span class="leading-relaxed text-[var(--text-main)]"><strong class="font-mono mr-1">(${String.fromCharCode(65 + optIdx)})</strong> ${opt}</span>
                    </label>
                `).join('')}
            </div>
            <div class="hidden mock-feedback p-3.5 rounded text-xs border font-serif" id="mockFeedback-${idx}"></div>
        </div>
    `).join('');
}

function recordMockAnswer(qIdx, optIdx) {
    mockUserAnswers[qIdx] = optIdx;
}

function submitMockExam() {
    clearInterval(mockTimerInterval);
    isMockRunning = false;

    let correct = 0;
    let incorrect = 0;
    let unattempted = 0;

    mockExamQuestions.forEach((q, idx) => {
        const userChoice = mockUserAnswers[idx];
        const feedbackEl = document.getElementById(`mockFeedback-${idx}`);

        if (userChoice === undefined) {
            unattempted++;
        } else if (userChoice === q.answer) {
            correct++;
        } else {
            incorrect++;
        }

        q.options.forEach((_, optIdx) => {
            const lbl = document.getElementById(`mockLabel-${idx}-${optIdx}`);
            if (lbl) {
                if (optIdx === q.answer) {
                    lbl.className = "flex items-start gap-2.5 p-2.5 rounded border-2 border-emerald-600 bg-emerald-50 dark:bg-emerald-950/30 text-emerald-950 dark:text-emerald-100 font-semibold";
                } else if (optIdx === userChoice && userChoice !== q.answer) {
                    lbl.className = "flex items-start gap-2.5 p-2.5 rounded border border-rose-400 bg-rose-50 dark:bg-rose-950/30 text-rose-950 dark:text-rose-100";
                }
            }
        });

        if (feedbackEl) {
            feedbackEl.classList.remove('hidden');
            if (userChoice === q.answer) {
                feedbackEl.className = "p-3.5 rounded text-xs border border-emerald-300 dark:border-emerald-800 bg-emerald-50/60 dark:bg-emerald-950/20 text-emerald-950 dark:text-emerald-100";
                feedbackEl.innerHTML = `<strong class="text-emerald-700 dark:text-emerald-400 font-sans block mb-1">Correct (+1.0):</strong> ${q.explanation}`;
            } else if (userChoice !== undefined) {
                feedbackEl.className = "p-3.5 rounded text-xs border border-rose-300 dark:border-rose-900 bg-rose-50/60 dark:bg-rose-950/20 text-rose-950 dark:text-rose-100";
                feedbackEl.innerHTML = `<strong class="text-rose-700 dark:text-rose-400 font-sans block mb-1">Incorrect (-0.25):</strong> ${q.explanation}`;
            } else {
                feedbackEl.className = "p-3.5 rounded text-xs border border-[var(--border-main)] bg-[var(--bg-subtle)] text-[var(--text-muted)]";
                feedbackEl.innerHTML = `<strong class="font-sans block mb-1">Unattempted (0.0):</strong> Correct Answer: Option (${String.fromCharCode(65 + q.answer)}). ${q.explanation}`;
            }
        }
    });

    const rawScore = (correct * 1.0) - (incorrect * 0.25);
    const finalScore = Math.max(0, rawScore).toFixed(2);
    const totalAttempted = correct + incorrect;
    const accuracy = totalAttempted > 0 ? Math.round((correct / totalAttempted) * 100) : 0;

    const resultsCard = document.getElementById('mockResultsCard');
    resultsCard.classList.remove('hidden');
    document.getElementById('mockScoreNum').innerText = `${finalScore} / ${mockExamQuestions.length}`;
    document.getElementById('mockAccuracyNum').innerText = `${accuracy}%`;
    document.getElementById('mockCorrectNum').innerText = `${correct}`;
    document.getElementById('mockIncorrectNum').innerText = `${incorrect}`;

    document.getElementById('mockStartBtn').innerText = 'Retake Mock Exam';
    document.getElementById('mockStartBtn').onclick = startOrResetMockExam;

    resultsCard.scrollIntoView({ behavior: 'smooth' });
}

// ==============================================================
// SEARCH POPUP
// ==============================================================
function openSearchModal() {
    searchModal.classList.remove('hidden');
    searchInput.focus();
}

function closeSearchModal() {
    searchModal.classList.add('hidden');
    searchInput.value = '';
    searchResults.innerHTML = '';
}

async function performSearch() {
    const q = searchInput.value.trim();
    if (q.length < 2) {
        searchResults.innerHTML = '<div class="text-center py-6 text-[var(--text-faint)] text-xs font-serif italic">Type at least 2 characters to search index...</div>';
        return;
    }
    
    try {
        const res = await fetch(`${API_BASE}/search?q=${encodeURIComponent(q)}`);
        const data = await res.json();
        
        let html = '';
        
        if (data.chapters.length > 0) {
            html += `<div class="text-[10px] font-bold text-[var(--text-faint)] uppercase tracking-wider mb-1.5 font-sans">Chapters (${data.chapters.length})</div>`;
            html += data.chapters.map(ch => `
                <div onclick="selectChapter('${ch.chapter_id}'); closeSearchModal();" 
                     class="p-2.5 rounded-lg hover:bg-[var(--bg-hover)] cursor-pointer space-y-0.5 transition">
                    <div class="font-serif font-semibold text-xs text-[var(--text-heading)]">Ch ${ch.number}: ${ch.title}</div>
                    <div class="text-[11px] text-[var(--text-muted)] line-clamp-1 font-serif">${ch.summary}</div>
                </div>
            `).join('');
        }
        
        if (data.questions.length > 0) {
            html += `<div class="text-[10px] font-bold text-[var(--text-faint)] uppercase tracking-wider mt-3 mb-1.5 font-sans">Question Bank (${data.questions.length})</div>`;
            html += data.questions.map(qItem => `
                <div class="p-2.5 rounded-lg hover:bg-[var(--bg-hover)] cursor-pointer space-y-0.5 transition" onclick="switchView('qbank'); closeSearchModal();">
                    <div class="text-xs text-[var(--text-main)] font-serif">${qItem.question}</div>
                    <div class="text-[10px] text-[var(--text-faint)] font-sans">${qItem.category} • ${qItem.exam}</div>
                </div>
            `).join('');
        }
        
        if (!html) {
            html = '<div class="text-center py-6 text-[var(--text-faint)] text-xs font-serif italic">No matching concepts or questions found.</div>';
        }
        
        searchResults.innerHTML = html;
    } catch (err) {
        console.error('Search error:', err);
    }
}
