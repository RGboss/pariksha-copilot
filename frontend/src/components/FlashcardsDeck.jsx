import React, { useState, useEffect } from 'react';
import { 
  Sparkles, 
  RotateCcw, 
  ChevronLeft, 
  ChevronRight, 
  Download, 
  Layers, 
  CheckCircle2, 
  BrainCircuit, 
  AlertCircle,
  Plus
} from 'lucide-react';

export default function FlashcardsDeck({ documents, token }) {
  const [cards, setCards] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);

  // Generation Modal State
  const [showGenModal, setShowGenModal] = useState(false);
  const [selectedDocId, setSelectedDocId] = useState('');
  const [topicInput, setTopicInput] = useState('');
  const [cardCount, setCardCount] = useState(5);

  const fetchCards = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/flashcards', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await res.json();
      setCards(data.flashcards || []);
      setCurrentIndex(0);
      setIsFlipped(false);
    } catch (err) {
      console.error('Failed to fetch flashcards:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCards();
  }, []);

  const handleGenerate = async (e) => {
    e.preventDefault();
    setGenerating(true);
    try {
      const res = await fetch('/api/flashcards/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          document_id: selectedDocId || null,
          topic: topicInput || 'High-Yield Exam Concepts',
          count: parseInt(cardCount, 10) || 5,
          category: 'Revision'
        })
      });
      if (res.ok) {
        setShowGenModal(false);
        setTopicInput('');
        await fetchCards();
      }
    } catch (err) {
      console.error('Generation failed:', err);
    } finally {
      setGenerating(false);
    }
  };

  const handleReview = async (rating) => {
    if (!currentCard) return;
    try {
      const res = await fetch(`/api/flashcards/${currentCard.id}/review`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ rating })
      });
      if (res.ok) {
        const data = await res.json();
        // Update local card state
        const updatedCards = [...cards];
        updatedCards[currentIndex] = data.flashcard;
        setCards(updatedCards);
        // Advance to next card
        if (currentIndex < cards.length - 1) {
          setCurrentIndex(prev => prev + 1);
          setIsFlipped(false);
        } else {
          setIsFlipped(false);
        }
      }
    } catch (err) {
      console.error('Review failed:', err);
    }
  };

  const handleExport = async () => {
    try {
      const res = await fetch('/api/flashcards/export', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await res.json();
      const blob = new Blob([data.markdown], { type: 'text/markdown;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'Pariksha_Flashcards_Deck.md');
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (err) {
      console.error('Export failed:', err);
    }
  };

  const currentCard = cards[currentIndex];

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Top Banner */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full text-xs font-semibold bg-amber-400/10 text-amber-400 border border-amber-400/20 mb-2">
            <Layers className="w-3.5 h-3.5" />
            <span>Leitner Spaced Repetition Engine</span>
          </div>
          <h2 className="text-xl font-bold text-slate-100">Active Recall Revision Deck</h2>
          <p className="text-xs text-slate-400 mt-1">
            Accelerate long-term memory retention of constitutional articles, statutory metrics, and high-yield formulas.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          {cards.length > 0 && (
            <button
              onClick={handleExport}
              className="inline-flex items-center space-x-2 px-3.5 py-2 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-all"
            >
              <Download className="w-4 h-4 text-slate-300" />
              <span>Export Notes</span>
            </button>
          )}

          <button
            onClick={() => setShowGenModal(true)}
            className="inline-flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-bold bg-amber-500 hover:bg-amber-400 text-slate-950 transition-all shadow-md shadow-amber-500/20"
          >
            <Plus className="w-4 h-4" />
            <span>Generate Flashcards</span>
          </button>
        </div>
      </div>

      {/* Main Flashcard Card or Empty State */}
      {loading ? (
        <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-16 text-center text-slate-400 animate-pulse">
          Loading revision deck...
        </div>
      ) : cards.length === 0 ? (
        <div className="bg-slate-900/50 border border-slate-800/80 rounded-2xl p-12 text-center space-y-4">
          <div className="w-14 h-14 mx-auto rounded-2xl bg-amber-400/10 border border-amber-400/20 flex items-center justify-center text-amber-400">
            <BrainCircuit className="w-7 h-7" />
          </div>
          <h3 className="text-base font-semibold text-slate-200">No Flashcards In Deck</h3>
          <p className="text-xs text-slate-400 max-w-md mx-auto">
            Extract high-yield active recall flashcards from your uploaded textbooks or custom syllabus topics using AI.
          </p>
          <button
            onClick={() => setShowGenModal(true)}
            className="inline-flex items-center space-x-2 px-4 py-2.5 rounded-xl text-xs font-bold bg-amber-500 hover:bg-amber-400 text-slate-950 transition-all"
          >
            <Sparkles className="w-4 h-4" />
            <span>Create First Deck</span>
          </button>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Deck Counter & Mastery Level */}
          <div className="flex items-center justify-between text-xs text-slate-400 px-2">
            <span className="font-mono">
              Card {currentIndex + 1} of {cards.length}
            </span>
            <div className="flex items-center space-x-1.5">
              <span className="text-[11px]">Leitner Box:</span>
              <div className="flex space-x-1">
                {[0, 1, 2, 3, 4, 5].map(b => (
                  <div
                    key={b}
                    className={`w-3.5 h-2 rounded-sm ${
                      (currentCard?.mastery_level || 0) >= b
                        ? 'bg-amber-400'
                        : 'bg-slate-800'
                    }`}
                  />
                ))}
              </div>
              <span className="font-semibold text-amber-300 ml-1">
                Box {currentCard?.mastery_level || 0}
              </span>
            </div>
          </div>

          {/* 3D Flip Card Container */}
          <div
            onClick={() => setIsFlipped(!isFlipped)}
            className="cursor-pointer min-h-[260px] bg-slate-900 border border-slate-800 hover:border-amber-500/40 rounded-3xl p-8 flex flex-col justify-between transition-all duration-300 shadow-2xl relative overflow-hidden group select-none"
          >
            {/* Card Badge */}
            <div className="flex items-center justify-between">
              <span className="px-3 py-1 rounded-lg text-[10px] font-bold uppercase tracking-wider bg-slate-800 text-amber-300 border border-slate-700">
                {currentCard?.category || 'Revision'} • {currentCard?.difficulty || 'Medium'}
              </span>
              <span className="text-[11px] text-slate-500 flex items-center space-x-1 group-hover:text-amber-400 transition-colors">
                <RotateCcw className="w-3.5 h-3.5" />
                <span>Click to Flip</span>
              </span>
            </div>

            {/* Prompt or Answer */}
            <div className="my-6 text-center">
              {!isFlipped ? (
                <div className="space-y-3">
                  <div className="text-[11px] font-bold tracking-widest text-slate-500 uppercase">
                    PROMPT / QUESTION
                  </div>
                  <h3 className="text-lg md:text-xl font-semibold text-slate-100 leading-relaxed max-w-2xl mx-auto">
                    {currentCard?.front_prompt}
                  </h3>
                </div>
              ) : (
                <div className="space-y-3">
                  <div className="text-[11px] font-bold tracking-widest text-emerald-400 uppercase">
                    HIGH-YIELD RECALL ANSWER
                  </div>
                  <p className="text-base md:text-lg font-medium text-slate-200 leading-relaxed max-w-2xl mx-auto">
                    {currentCard?.back_answer}
                  </p>
                </div>
              )}
            </div>

            {/* Footer Notice */}
            <div className="text-center text-[11px] text-slate-500">
              Total Reviews: {currentCard?.review_count || 0}
            </div>
          </div>

          {/* Leitner Rating Buttons (Active when flipped) */}
          {isFlipped ? (
            <div className="space-y-2">
              <div className="text-center text-[11px] font-semibold text-slate-400">
                Rate your active recall to schedule spaced repetition:
              </div>
              <div className="grid grid-cols-4 gap-3 max-w-xl mx-auto">
                <button
                  onClick={() => handleReview('again')}
                  className="py-2.5 px-3 rounded-xl text-xs font-bold bg-rose-500/10 text-rose-300 border border-rose-500/30 hover:bg-rose-500 hover:text-white transition-all text-center"
                >
                  <div>Again</div>
                  <div className="text-[10px] font-normal opacity-80">&lt; 1 Day</div>
                </button>
                <button
                  onClick={() => handleReview('hard')}
                  className="py-2.5 px-3 rounded-xl text-xs font-bold bg-amber-500/10 text-amber-300 border border-amber-500/30 hover:bg-amber-500 hover:text-slate-950 transition-all text-center"
                >
                  <div>Hard</div>
                  <div className="text-[10px] font-normal opacity-80">2 Days</div>
                </button>
                <button
                  onClick={() => handleReview('good')}
                  className="py-2.5 px-3 rounded-xl text-xs font-bold bg-emerald-500/10 text-emerald-300 border border-emerald-500/30 hover:bg-emerald-500 hover:text-white transition-all text-center"
                >
                  <div>Good</div>
                  <div className="text-[10px] font-normal opacity-80">4 Days</div>
                </button>
                <button
                  onClick={() => handleReview('easy')}
                  className="py-2.5 px-3 rounded-xl text-xs font-bold bg-sky-500/10 text-sky-300 border border-sky-500/30 hover:bg-sky-500 hover:text-white transition-all text-center"
                >
                  <div>Easy</div>
                  <div className="text-[10px] font-normal opacity-80">7 Days</div>
                </button>
              </div>
            </div>
          ) : (
            /* Navigation Controls */
            <div className="flex items-center justify-center space-x-4">
              <button
                disabled={currentIndex === 0}
                onClick={() => {
                  setCurrentIndex(prev => Math.max(0, prev - 1));
                  setIsFlipped(false);
                }}
                className="px-4 py-2 rounded-xl text-xs font-semibold bg-slate-900 border border-slate-800 text-slate-300 hover:bg-slate-800 disabled:opacity-40 disabled:cursor-not-allowed inline-flex items-center space-x-1"
              >
                <ChevronLeft className="w-4 h-4" />
                <span>Previous</span>
              </button>
              <button
                disabled={currentIndex === cards.length - 1}
                onClick={() => {
                  setCurrentIndex(prev => Math.min(cards.length - 1, prev + 1));
                  setIsFlipped(false);
                }}
                className="px-4 py-2 rounded-xl text-xs font-semibold bg-slate-900 border border-slate-800 text-slate-300 hover:bg-slate-800 disabled:opacity-40 disabled:cursor-not-allowed inline-flex items-center space-x-1"
              >
                <span>Next</span>
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>
      )}

      {/* Generation Modal */}
      {showGenModal && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 max-w-lg w-full space-y-4 shadow-2xl">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center space-x-2 text-slate-100 font-bold text-sm">
                <Sparkles className="w-4 h-4 text-amber-400" />
                <span>AI Flashcard Deck Generator</span>
              </div>
              <button
                onClick={() => setShowGenModal(false)}
                className="text-slate-400 hover:text-slate-200 text-xs px-2 py-1 rounded-lg"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleGenerate} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Source Document (Optional)
                </label>
                <select
                  value={selectedDocId}
                  onChange={e => setSelectedDocId(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-amber-500"
                >
                  <option value="">General Exam Syllabus (No specific doc)</option>
                  {documents.map(d => (
                    <option key={d.id} value={d.id}>
                      {d.filename} ({d.category})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Topic Focus / Keywords
                </label>
                <input
                  type="text"
                  placeholder="e.g. Fundamental Rights, Monetary Policy, Union Budget"
                  value={topicInput}
                  onChange={e => setTopicInput(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-amber-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Number of Cards
                </label>
                <select
                  value={cardCount}
                  onChange={e => setCardCount(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-amber-500"
                >
                  <option value="3">3 High-Yield Cards</option>
                  <option value="5">5 Comprehensive Cards</option>
                  <option value="10">10 Full Module Cards</option>
                </select>
              </div>

              <div className="pt-2 flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => setShowGenModal(false)}
                  className="px-4 py-2 rounded-xl text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={generating}
                  className="px-4 py-2 rounded-xl text-xs font-bold bg-amber-500 hover:bg-amber-400 text-slate-950 disabled:opacity-50 inline-flex items-center space-x-2"
                >
                  {generating ? (
                    <>
                      <span className="w-3 h-3 border-2 border-slate-950 border-t-transparent rounded-full animate-spin" />
                      <span>Extracting Cards...</span>
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4" />
                      <span>Generate Now</span>
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
