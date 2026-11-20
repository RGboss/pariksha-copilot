import React, { useState, useEffect } from 'react';
import { 
  FileQuestion, 
  Clock, 
  CheckCircle2, 
  XCircle, 
  Award, 
  ChevronRight, 
  ChevronLeft, 
  RotateCcw, 
  Plus, 
  Sparkles,
  BookOpen,
  HelpCircle,
  TrendingUp
} from 'lucide-react';

export default function MockExamSimulator({ documents, token, targetExam }) {
  const [quizzes, setQuizzes] = useState([]);
  const [activeQuiz, setActiveQuiz] = useState(null);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);

  // Active Test State
  const [currentQIndex, setCurrentQIndex] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState({});
  const [timeLeft, setTimeLeft] = useState(600); // 10 minutes default
  const [timerActive, setTimerActive] = useState(false);
  const [attemptResult, setAttemptResult] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  // Generation Modal
  const [showGenModal, setShowGenModal] = useState(false);
  const [selectedDocId, setSelectedDocId] = useState('');
  const [quizTopic, setQuizTopic] = useState('');
  const [questionCount, setQuestionCount] = useState(5);

  const fetchQuizzes = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/quiz', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await res.json();
      setQuizzes(data.quizzes || []);
    } catch (err) {
      console.error('Failed to load quizzes:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQuizzes();
  }, []);

  // Timer Countdown Effect
  useEffect(() => {
    let interval = null;
    if (timerActive && timeLeft > 0 && !attemptResult) {
      interval = setInterval(() => {
        setTimeLeft(prev => prev - 1);
      }, 1000);
    } else if (timeLeft === 0 && timerActive && !attemptResult) {
      handleSubmitTest();
    }
    return () => clearInterval(interval);
  }, [timerActive, timeLeft, attemptResult]);

  const handleStartQuiz = (quiz) => {
    setActiveQuiz(quiz);
    setCurrentQIndex(0);
    setSelectedAnswers({});
    setAttemptResult(null);
    setTimeLeft((quiz.questions?.length || 5) * 120); // 2 minutes per question
    setTimerActive(true);
  };

  const handleSelectOption = (optIndex) => {
    if (attemptResult) return; // Prevent changing after submission
    setSelectedAnswers(prev => ({
      ...prev,
      [currentQIndex.toString()]: optIndex
    }));
  };

  const handleSubmitTest = async () => {
    if (!activeQuiz) return;
    setSubmitting(true);
    setTimerActive(false);
    const timeSpent = ((activeQuiz.questions?.length || 5) * 120) - timeLeft;

    try {
      const res = await fetch(`/api/quiz/${activeQuiz.id}/submit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          answers: selectedAnswers,
          time_spent_seconds: Math.max(1, timeSpent)
        })
      });
      if (res.ok) {
        const data = await res.json();
        setAttemptResult(data.attempt);
        await fetchQuizzes();
      }
    } catch (err) {
      console.error('Submission failed:', err);
    } finally {
      setSubmitting(false);
    }
  };

  const handleGenerateQuiz = async (e) => {
    e.preventDefault();
    setGenerating(true);
    try {
      const res = await fetch('/api/quiz/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          document_id: selectedDocId || null,
          topic: quizTopic || 'General Exam Core Syllabus',
          exam_name: targetExam || 'Competitive Exam',
          question_count: parseInt(questionCount, 10) || 5
        })
      });
      if (res.ok) {
        const data = await res.json();
        setShowGenModal(false);
        setQuizTopic('');
        await fetchQuizzes();
        handleStartQuiz(data.quiz);
      }
    } catch (err) {
      console.error('Quiz creation failed:', err);
    } finally {
      setGenerating(false);
    }
  };

  const formatTime = (secs) => {
    const m = Math.floor(secs / 60);
    const s = secs % 60;
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  const currentQ = activeQuiz?.questions?.[currentQIndex];

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Top Banner */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full text-xs font-semibold bg-sky-400/10 text-sky-400 border border-sky-400/20 mb-2">
            <FileQuestion className="w-3.5 h-3.5" />
            <span>CBT Computer-Based Examination Simulator</span>
          </div>
          <h2 className="text-xl font-bold text-slate-100">Timed Mock Tests & PYQ Assessment</h2>
          <p className="text-xs text-slate-400 mt-1">
            Simulate real exam pressure with negative marking analysis, detailed rationales, and exact page citations.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          {activeQuiz && (
            <button
              onClick={() => { setActiveQuiz(null); setAttemptResult(null); setTimerActive(false); }}
              className="px-3.5 py-2 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-all"
            >
              Back to Test Library
            </button>
          )}

          <button
            onClick={() => setShowGenModal(true)}
            className="inline-flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-bold bg-amber-500 hover:bg-amber-400 text-slate-950 transition-all shadow-md shadow-amber-500/20"
          >
            <Plus className="w-4 h-4" />
            <span>New Mock Test</span>
          </button>
        </div>
      </div>

      {/* Main View: Active Test vs Test Library */}
      {activeQuiz ? (
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Left 3 Cols: Question Area & Analysis */}
          <div className="lg:col-span-3 space-y-6">
            {/* Exam Header Bar */}
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 flex items-center justify-between">
              <div>
                <h3 className="font-bold text-sm text-slate-100">{activeQuiz.title}</h3>
                <span className="text-[11px] text-slate-400 font-mono">
                  Question {currentQIndex + 1} of {activeQuiz.questions?.length}
                </span>
              </div>

              {!attemptResult && (
                <div className="flex items-center space-x-2 px-3 py-1.5 rounded-xl bg-slate-950 border border-slate-800">
                  <Clock className={`w-4 h-4 ${timeLeft < 120 ? 'text-rose-400 animate-pulse' : 'text-amber-400'}`} />
                  <span className={`font-mono text-xs font-bold ${timeLeft < 120 ? 'text-rose-300' : 'text-slate-200'}`}>
                    {formatTime(timeLeft)}
                  </span>
                </div>
              )}
            </div>

            {/* Score Summary Box (Appears after submission) */}
            {attemptResult && (
              <div className="bg-gradient-to-r from-amber-500/10 via-slate-900 to-emerald-500/10 border border-slate-700 rounded-2xl p-6 space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-12 h-12 rounded-2xl bg-amber-500/20 border border-amber-500/30 flex items-center justify-center text-amber-400">
                      <Award className="w-6 h-6" />
                    </div>
                    <div>
                      <h4 className="text-base font-bold text-slate-100">Exam Scorecard</h4>
                      <p className="text-xs text-slate-400">
                        Completed in {attemptResult.time_spent_seconds} seconds
                      </p>
                    </div>
                  </div>

                  <div className="text-right">
                    <div className="text-2xl font-black text-amber-400 font-mono">
                      {attemptResult.percentage}%
                    </div>
                    <div className="text-xs text-slate-400">
                      {attemptResult.score} / {attemptResult.total_questions} Correct
                    </div>
                  </div>
                </div>

                <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-amber-500 to-emerald-400 transition-all duration-1000"
                    style={{ width: `${attemptResult.percentage}%` }}
                  />
                </div>
              </div>
            )}

            {/* Question Card */}
            {currentQ && (
              <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-6 shadow-xl">
                <div className="text-sm md:text-base font-semibold text-slate-100 leading-relaxed">
                  <span className="text-amber-400 mr-2 font-mono">Q{currentQIndex + 1}.</span>
                  {currentQ.question}
                </div>

                {/* Options List */}
                <div className="space-y-3">
                  {currentQ.options?.map((opt, oIdx) => {
                    const isSelected = selectedAnswers[currentQIndex.toString()] === oIdx;
                    const feedback = attemptResult?.detailed_feedback?.[currentQIndex];
                    const isCorrectOpt = feedback ? feedback.correct_choice === oIdx : false;
                    const isUserWrong = feedback && isSelected && !feedback.is_correct;

                    let optStyle = 'border-slate-800 bg-slate-950/60 hover:bg-slate-800/60 text-slate-300';
                    if (isSelected && !attemptResult) {
                      optStyle = 'border-amber-500 bg-amber-500/10 text-amber-200 shadow-sm';
                    }
                    if (attemptResult) {
                      if (isCorrectOpt) {
                        optStyle = 'border-emerald-500 bg-emerald-500/10 text-emerald-200 font-semibold';
                      } else if (isUserWrong) {
                        optStyle = 'border-rose-500 bg-rose-500/10 text-rose-200';
                      }
                    }

                    return (
                      <div
                        key={oIdx}
                        onClick={() => handleSelectOption(oIdx)}
                        className={`cursor-pointer p-4 rounded-xl border text-xs md:text-sm flex items-center justify-between transition-all ${optStyle}`}
                      >
                        <div className="flex items-center space-x-3">
                          <span className="w-6 h-6 rounded-lg bg-slate-800 border border-slate-700 flex items-center justify-center font-mono text-xs font-bold shrink-0">
                            {['A', 'B', 'C', 'D'][oIdx]}
                          </span>
                          <span>{opt}</span>
                        </div>

                        {attemptResult && (
                          <div>
                            {isCorrectOpt && <CheckCircle2 className="w-5 h-5 text-emerald-400" />}
                            {isUserWrong && <XCircle className="w-5 h-5 text-rose-400" />}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>

                {/* Post-Submit Rationale & Page Citation Box */}
                {attemptResult && (
                  <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 space-y-2 mt-4">
                    <div className="flex items-center space-x-2 text-xs font-bold text-amber-400">
                      <HelpCircle className="w-4 h-4" />
                      <span>Official Faculty Rationale & References:</span>
                    </div>
                    <p className="text-xs text-slate-300 leading-relaxed">
                      {currentQ.explanation}
                    </p>
                    {currentQ.reference_doc && (
                      <div className="text-[11px] text-slate-400 flex items-center space-x-2 pt-2 border-t border-slate-800/80">
                        <BookOpen className="w-3.5 h-3.5 text-amber-400" />
                        <span>Source: Page {currentQ.reference_page || 1} of <i>{currentQ.reference_doc}</i></span>
                      </div>
                    )}
                  </div>
                )}

                {/* Bottom Navigation */}
                <div className="flex items-center justify-between pt-4 border-t border-slate-800">
                  <button
                    disabled={currentQIndex === 0}
                    onClick={() => setCurrentQIndex(prev => Math.max(0, prev - 1))}
                    className="px-4 py-2 rounded-xl text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed inline-flex items-center space-x-1"
                  >
                    <ChevronLeft className="w-4 h-4" />
                    <span>Previous</span>
                  </button>

                  {!attemptResult ? (
                    currentQIndex === activeQuiz.questions?.length - 1 ? (
                      <button
                        onClick={handleSubmitTest}
                        disabled={submitting}
                        className="px-5 py-2.5 rounded-xl text-xs font-bold bg-emerald-500 hover:bg-emerald-400 text-slate-950 transition-all shadow-md shadow-emerald-500/20"
                      >
                        {submitting ? 'Evaluating Test...' : 'Final Submit Exam'}
                      </button>
                    ) : (
                      <button
                        onClick={() => setCurrentQIndex(prev => Math.min(activeQuiz.questions.length - 1, prev + 1))}
                        className="px-4 py-2 rounded-xl text-xs font-semibold bg-amber-500 hover:bg-amber-400 text-slate-950 inline-flex items-center space-x-1"
                      >
                        <span>Save & Next</span>
                        <ChevronRight className="w-4 h-4" />
                      </button>
                    )
                  ) : (
                    <button
                      onClick={() => setCurrentQIndex(prev => Math.min(activeQuiz.questions.length - 1, prev + 1))}
                      disabled={currentQIndex === activeQuiz.questions?.length - 1}
                      className="px-4 py-2 rounded-xl text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700 disabled:opacity-40 inline-flex items-center space-x-1"
                    >
                      <span>Next Analysis</span>
                      <ChevronRight className="w-4 h-4" />
                    </button>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Right Col: Question Palette */}
          <div className="space-y-4">
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-4">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                Question Palette
              </h4>

              <div className="grid grid-cols-5 gap-2">
                {activeQuiz.questions?.map((_, qIdx) => {
                  const isAnswered = selectedAnswers[qIdx.toString()] !== undefined;
                  const isCurrent = currentQIndex === qIdx;
                  const feedback = attemptResult?.detailed_feedback?.[qIdx];

                  let btnStyle = 'bg-slate-950 text-slate-400 border-slate-800';
                  if (isAnswered && !attemptResult) {
                    btnStyle = 'bg-amber-500/20 text-amber-300 border-amber-500/40 font-bold';
                  }
                  if (isCurrent) {
                    btnStyle += ' ring-2 ring-amber-400';
                  }
                  if (attemptResult) {
                    if (feedback?.is_correct) {
                      btnStyle = 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40 font-bold';
                    } else {
                      btnStyle = 'bg-rose-500/20 text-rose-300 border-rose-500/40';
                    }
                  }

                  return (
                    <button
                      key={qIdx}
                      onClick={() => setCurrentQIndex(qIdx)}
                      className={`h-9 rounded-xl border text-xs font-mono transition-all flex items-center justify-center ${btnStyle}`}
                    >
                      {qIdx + 1}
                    </button>
                  );
                })}
              </div>

              {/* Status Legend */}
              <div className="pt-3 border-t border-slate-800 space-y-2 text-[11px] text-slate-400">
                <div className="flex items-center space-x-2">
                  <span className="w-3 h-3 rounded-md bg-amber-500/20 border border-amber-500/40" />
                  <span>Answered</span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="w-3 h-3 rounded-md bg-slate-950 border border-slate-800" />
                  <span>Unanswered</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      ) : (
        /* Test Library View */
        <div className="space-y-4">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-400 px-1">
            <span>Available Mock Tests & Past Attempts ({quizzes.length})</span>
          </div>

          {loading ? (
            <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-12 text-center text-slate-400 animate-pulse">
              Loading examinations...
            </div>
          ) : quizzes.length === 0 ? (
            <div className="bg-slate-900/50 border border-slate-800/80 rounded-2xl p-12 text-center space-y-4">
              <div className="w-14 h-14 mx-auto rounded-2xl bg-sky-400/10 border border-sky-400/20 flex items-center justify-center text-sky-400">
                <FileQuestion className="w-7 h-7" />
              </div>
              <h3 className="text-base font-semibold text-slate-200">No Tests Generated Yet</h3>
              <p className="text-xs text-slate-400 max-w-md mx-auto">
                Generate custom timed mock tests from your uploaded materials or official syllabus guidelines.
              </p>
              <button
                onClick={() => setShowGenModal(true)}
                className="inline-flex items-center space-x-2 px-4 py-2.5 rounded-xl text-xs font-bold bg-amber-500 hover:bg-amber-400 text-slate-950 transition-all"
              >
                <Sparkles className="w-4 h-4" />
                <span>Create First Mock Test</span>
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {quizzes.map(q => {
                const latestAttempt = q.attempts?.[0];
                return (
                  <div
                    key={q.id}
                    className="bg-slate-900 border border-slate-800 hover:border-slate-700 rounded-2xl p-5 space-y-4 transition-all shadow-md flex flex-col justify-between"
                  >
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="px-2.5 py-0.5 rounded-md text-[10px] font-bold bg-sky-400/10 text-sky-300 border border-sky-400/20">
                          {q.exam_name}
                        </span>
                        <span className="text-[11px] text-slate-400 font-mono">
                          {q.question_count} Questions
                        </span>
                      </div>
                      <h4 className="font-bold text-sm text-slate-100">{q.title}</h4>
                      {latestAttempt && (
                        <div className="mt-2 flex items-center space-x-2 text-xs text-slate-400">
                          <TrendingUp className="w-3.5 h-3.5 text-amber-400" />
                          <span>Last Score: <b className="text-amber-400">{latestAttempt.percentage}%</b> ({latestAttempt.score}/{latestAttempt.total_questions})</span>
                        </div>
                      )}
                    </div>

                    <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between">
                      <span className="text-[11px] text-slate-400">
                        {q.attempts?.length || 0} Attempts Recorded
                      </span>
                      <button
                        onClick={() => handleStartQuiz(q)}
                        className="px-3.5 py-1.5 rounded-xl text-xs font-bold bg-amber-500 hover:bg-amber-400 text-slate-950 inline-flex items-center space-x-1.5 transition-all"
                      >
                        <span>{latestAttempt ? 'Retake Exam' : 'Start Exam'}</span>
                        <ChevronRight className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* Quiz Generation Modal */}
      {showGenModal && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 max-w-lg w-full space-y-4 shadow-2xl">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center space-x-2 text-slate-100 font-bold text-sm">
                <Sparkles className="w-4 h-4 text-amber-400" />
                <span>AI Mock Test Generator</span>
              </div>
              <button
                onClick={() => setShowGenModal(false)}
                className="text-slate-400 hover:text-slate-200 text-xs px-2 py-1 rounded-lg"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleGenerateQuiz} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Source Study Document (Optional)
                </label>
                <select
                  value={selectedDocId}
                  onChange={e => setSelectedDocId(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-amber-500"
                >
                  <option value="">General Syllabus Questions</option>
                  {documents.map(d => (
                    <option key={d.id} value={d.id}>
                      {d.filename} ({d.category})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Syllabus Topic / Subject Focus
                </label>
                <input
                  type="text"
                  placeholder="e.g. Monetary Policy, Fiscal Devolution, Constitutional Amendments"
                  value={quizTopic}
                  onChange={e => setQuizTopic(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-amber-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Question Count
                </label>
                <select
                  value={questionCount}
                  onChange={e => setQuestionCount(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-amber-500"
                >
                  <option value="3">3 Questions (Rapid Assessment)</option>
                  <option value="5">5 Questions (Standard Mini-Test)</option>
                  <option value="10">10 Questions (Full Section Mock)</option>
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
                      <span>Synthesizing Exam...</span>
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4" />
                      <span>Generate & Launch Test</span>
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
