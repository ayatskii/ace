import { useParams, useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import Timer from '../../components/test/Timer';
import ProgressBar from '../../components/test/ProgressBar';
import AudioRecorder from '../../components/test/AudioRecorder';
import apiClient from '../../api/client';

export default function TestAttempt() {
  const { attemptId } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [attempt, setAttempt] = useState(null);
  const [testStructure, setTestStructure] = useState(null);
  
  const [currentSectionIndex, setCurrentSectionIndex] = useState(0);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0); // Index within the current section's questions
  const [answers, setAnswers] = useState({}); // { questionId: answerValue }

  useEffect(() => {
    const fetchAttempt = async () => {
      try {
        const response = await apiClient.get(`/tests/attempts/${attemptId}`);
        setAttempt(response.data);
        setTestStructure(response.data.test_structure);
        setLoading(false);
      } catch (err) {
        console.error('Failed to fetch attempt:', err);
        setError('Failed to load test. Please try again.');
        setLoading(false);
      }
    };
    fetchAttempt();
  }, [attemptId]);

  if (loading) return <div className="p-8 text-center">Loading test...</div>;
  if (error) return <div className="p-8 text-center text-red-600">{error}</div>;
  if (!attempt || !testStructure) return <div className="p-8 text-center">Test data not found.</div>;

  const sections = attempt.test_template.sections.sort((a, b) => a.order - b.order);
  const currentSection = sections[currentSectionIndex];

  // Helper to get questions for current section
  const getSectionQuestions = () => {
    if (!testStructure) return [];
    if (currentSection.section_type === 'listening') return testStructure.listening_questions.sort((a, b) => a.order - b.order);
    if (currentSection.section_type === 'reading') return testStructure.reading_questions.sort((a, b) => a.order - b.order);
    // Writing and Speaking have tasks, treat as questions for navigation
    if (currentSection.section_type === 'writing') return testStructure.writing_tasks.sort((a, b) => a.task_number - b.task_number);
    if (currentSection.section_type === 'speaking') return testStructure.speaking_tasks.sort((a, b) => a.order - b.order);
    return [];
  };

  const questions = getSectionQuestions();
  const currentQuestion = questions[currentQuestionIndex];

  const handleNext = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    }
  };

  const handlePrevious = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(currentQuestionIndex - 1);
    }
  };

  const handleSectionFinish = () => {
    if (currentSectionIndex < sections.length - 1) {
      setCurrentSectionIndex(currentSectionIndex + 1);
      setCurrentQuestionIndex(0);
    } else {
      handleSubmitTest();
    }
  };

  const handleSubmitTest = async () => {
    try {
      if (window.confirm("Are you sure you want to submit the test?")) {
        // Categorize answers
        const writingAnswers = [];
        const listeningAnswers = [];
        const readingAnswers = [];

        Object.entries(answers).forEach(([key, value]) => {
            if (key.startsWith('w-')) {
                writingAnswers.push({
                    task_id: parseInt(key.replace('w-', '')),
                    response_text: value
                });
            } else {
                // Check if it's a listening or reading question
                // We need to look up the question ID in the test structure
                const qId = parseInt(key);
                
                // Check Listening
                const isListening = testStructure.listening_questions.some(q => q.id === qId);
                if (isListening) {
                    listeningAnswers.push({
                        question_id: qId,
                        user_answer: value
                    });
                    return;
                }

                // Check Reading
                // Reading questions are nested in passages in the structure we built in backend, 
                // but let's check if we have a flat list or need to search passages
                // The backend get_test_attempt flattens them into reading_questions!
                const isReading = testStructure.reading_questions.some(q => q.id === qId);
                if (isReading) {
                    readingAnswers.push({
                        question_id: qId,
                        user_answer: value
                    });
                }
            }
        });

        const payload = {
          writing_answers: writingAnswers,
          listening_answers: listeningAnswers,
          reading_answers: readingAnswers
        };

        await apiClient.put(`/tests/attempts/${attemptId}/submit`, payload);
        alert("Test submitted successfully!");
        navigate('/student/dashboard');
      }
    } catch (err) {
      console.error("Submission failed:", err);
      alert("Failed to submit test.");
    }
  };

  const handleTimeUp = () => {
    alert("Time is up for this section!");
    handleSectionFinish();
  };

  // Render content based on section type
  const renderContent = () => {
    if (!currentQuestion) return <div>No questions in this section.</div>;

    if (currentSection.section_type === 'listening') {
      // Find the part for this question to show audio
      const part = testStructure.listening_parts.find(p => p.id === currentQuestion.part_id);
      return (
        <div className="space-y-6">
          {part && (
            <div className="bg-blue-50 p-4 rounded-lg mb-4">
              <h3 className="font-semibold mb-2">Part {part.part_number} Audio</h3>
              <audio controls src={part.audio_url} className="w-full" />
            </div>
          )}
          <div className="bg-white p-6 rounded-lg border border-gray-200">
            <h3 className="text-lg font-medium mb-4">{currentQuestion.question_number}. {currentQuestion.question_text}</h3>
            {currentQuestion.image_url && (
               <img src={currentQuestion.image_url} alt="Question Diagram" className="mb-4 max-h-64 object-contain" />
            )}
            {currentQuestion.has_options ? (
              <div className="space-y-2">
                {currentQuestion.options.map((opt, idx) => (
                  <label key={idx} className="flex items-center space-x-3 p-3 border rounded-lg hover:bg-gray-50 cursor-pointer">
                    <input
                      type="radio"
                      name={`q-${currentQuestion.id}`}
                      className="h-4 w-4 text-primary-600"
                      onChange={() => setAnswers({...answers, [currentQuestion.id]: opt.option_label})}
                      checked={answers[currentQuestion.id] === opt.option_label}
                    />
                    <span className="font-bold">{opt.option_label}</span>
                    <span>{opt.option_text}</span>
                  </label>
                ))}
              </div>
            ) : (
              <input
                type="text"
                className="w-full border border-gray-300 rounded-lg px-4 py-2"
                placeholder="Type your answer here..."
                onChange={(e) => setAnswers({...answers, [currentQuestion.id]: e.target.value})}
                value={answers[currentQuestion.id] || ''}
              />
            )}
          </div>
        </div>
      );
    }

    if (currentSection.section_type === 'reading') {
      const passage = testStructure.reading_passages.find(p => p.id === currentQuestion.passage_id);
      return (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-[calc(100vh-300px)]">
          <div className="overflow-y-auto pr-4 border-r border-gray-200">
             <h3 className="font-bold text-xl mb-4">{passage?.title}</h3>
             <div className="prose max-w-none text-gray-800 whitespace-pre-wrap">{passage?.content}</div>
          </div>
          <div className="overflow-y-auto pl-2">
            <div className="bg-white p-6 rounded-lg border border-gray-200">
              <h3 className="text-lg font-medium mb-4">{currentQuestion.question_number}. {currentQuestion.question_text}</h3>
              {currentQuestion.has_options ? (
                <div className="space-y-2">
                  {currentQuestion.options.map((opt, idx) => (
                    <label key={idx} className="flex items-center space-x-3 p-3 border rounded-lg hover:bg-gray-50 cursor-pointer">
                      <input
                        type="radio"
                        name={`q-${currentQuestion.id}`}
                        className="h-4 w-4 text-primary-600"
                        onChange={() => setAnswers({...answers, [currentQuestion.id]: opt.option_label})}
                        checked={answers[currentQuestion.id] === opt.option_label}
                      />
                      <span className="font-bold">{opt.option_label}</span>
                      <span>{opt.option_text}</span>
                    </label>
                  ))}
                </div>
              ) : (
                <input
                  type="text"
                  className="w-full border border-gray-300 rounded-lg px-4 py-2"
                  placeholder="Type your answer here..."
                  onChange={(e) => setAnswers({...answers, [currentQuestion.id]: e.target.value})}
                  value={answers[currentQuestion.id] || ''}
                />
              )}
            </div>
          </div>
        </div>
      );
    }

    if (currentSection.section_type === 'writing') {
      return (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-gray-50 p-6 rounded-lg">
            <h3 className="font-bold text-lg mb-2">Task {currentQuestion.task_number}</h3>
            <p className="whitespace-pre-wrap mb-4">{currentQuestion.prompt_text}</p>
            {currentQuestion.image_url && (
              <img src={currentQuestion.image_url} alt="Task" className="w-full rounded-lg border border-gray-200" />
            )}
            <div className="mt-4 text-sm text-gray-500">
              Min words: {currentQuestion.word_limit_min}
            </div>
          </div>
          <div>
            <textarea
              className="w-full h-96 border border-gray-300 rounded-lg p-4 font-mono"
              placeholder="Type your essay here..."
              onChange={(e) => setAnswers({...answers, [`w-${currentQuestion.id}`]: e.target.value})}
              value={answers[`w-${currentQuestion.id}`] || ''}
            />
            <div className="mt-2 flex justify-between items-center">
              <div className={`text-sm ${
                ((answers[`w-${currentQuestion.id}`] || '').split(/\s+/).filter(w => w.length > 0).length < currentQuestion.word_limit_min)
                  ? 'text-red-600 font-semibold'
                  : 'text-gray-500'
              }`}>
                {((answers[`w-${currentQuestion.id}`] || '').split(/\s+/).filter(w => w.length > 0).length < currentQuestion.word_limit_min) && '⚠️ '}
                Word count: {(answers[`w-${currentQuestion.id}`] || '').split(/\s+/).filter(w => w.length > 0).length}
                {((answers[`w-${currentQuestion.id}`] || '').split(/\s+/).filter(w => w.length > 0).length < currentQuestion.word_limit_min) && 
                  ` (Minimum: ${currentQuestion.word_limit_min})`
                }
              </div>
            </div>
          </div>
        </div>
      );
    }

    if (currentSection.section_type === 'speaking') {
      return (
        <SpeakingSection 
          task={currentQuestion} 
          attemptId={attemptId}
          onComplete={() => {
            if (currentQuestionIndex < questions.length - 1) {
                handleNext();
            } else {
                handleSectionFinish();
            }
          }}
        />
      );
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 shadow-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-xl font-bold text-gray-900 capitalize">
                {currentSection.section_type} Section
              </h1>
              <p className="text-sm text-gray-600">{attempt.test_template.title}</p>
            </div>
            <Timer
              duration={currentSection.duration_minutes * 60}
              onTimeUp={handleTimeUp}
            />
          </div>
        </div>
      </div>
      
      {/* Section Tabs */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex space-x-2 py-2 overflow-x-auto">
            {sections.map((section, index) => {
              const isPast = index < currentSectionIndex;
              const isCurrent = index === currentSectionIndex;
              
              return (
                <div
                  key={section.id}
                  className={`px-4 py-2 rounded-lg font-medium text-sm whitespace-nowrap transition cursor-default ${
                    isCurrent
                      ? 'bg-primary-600 text-white'
                      : isPast
                      ? 'bg-green-100 text-green-700'
                      : 'bg-gray-100 text-gray-400'
                  }`}
                >
                  {section.section_type.charAt(0).toUpperCase() + section.section_type.slice(1)} {isPast && '✓'}
                </div>
              );
            })}
          </div>
        </div>
      </div>
      
      {/* Content Area */}
      <div className="flex-1 max-w-7xl mx-auto px-4 py-6 w-full">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8 h-full">
          <ProgressBar
            current={currentQuestionIndex + 1}
            total={questions.length}
          />
          
          <div className="mt-8">
            {renderContent()}
          </div>
          
          {/* Navigation */}
          <div className="flex justify-between mt-8 pt-6 border-t border-gray-200">
            <button
              onClick={handlePrevious}
              disabled={currentQuestionIndex === 0 || currentSection.section_type === 'speaking'}
              className="px-6 py-3 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-lg font-semibold transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              ← Previous
            </button>
            
            {currentQuestionIndex === questions.length - 1 ? (
              <button
                onClick={handleSectionFinish}
                className="px-6 py-3 bg-green-600 hover:bg-green-700 text-white rounded-lg font-semibold transition"
              >
                {currentSectionIndex === sections.length - 1 ? 'Submit Test' : 'Finish Section'}
              </button>
            ) : (
              <button
                onClick={handleNext}
                disabled={currentSection.section_type === 'speaking'}
                className="px-6 py-3 bg-primary-600 hover:bg-primary-700 text-white rounded-lg font-semibold transition disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next →
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// Sub-component for Speaking Section to handle complex state
function SpeakingSection({ task, attemptId, onComplete }) {
    const [status, setStatus] = useState('idle'); // idle, preparing, recording, uploading, completed
    const [timeLeft, setTimeLeft] = useState(0);
    const [uploadError, setUploadError] = useState(null);

    useEffect(() => {
        // Reset state when task changes
        setStatus('idle');
        setUploadError(null);
    }, [task.id]);

    useEffect(() => {
        let timer;
        if ((status === 'preparing' || status === 'recording') && timeLeft > 0) {
            timer = setInterval(() => {
                setTimeLeft(prev => {
                    if (prev <= 1) {
                        handleTimerComplete();
                        return 0;
                    }
                    return prev - 1;
                });
            }, 1000);
        }
        return () => clearInterval(timer);
    }, [status, timeLeft]);

    const handleTimerComplete = () => {
        if (status === 'preparing') {
            startRecording();
        } else if (status === 'recording') {
            // AudioRecorder handles auto-stop via maxDuration, but we can double check
            setStatus('uploading');
        }
    };

    const startPreparation = () => {
        const prepTime = task.preparation_time_seconds || 10; // Default 10s if null
        setTimeLeft(prepTime);
        setStatus('preparing');
    };

    const startRecording = () => {
        setTimeLeft(task.speaking_time_seconds);
        setStatus('recording');
    };

    const handleRecordingComplete = async (audioBlob) => {
        setStatus('uploading');
        try {
            const formData = new FormData();
            formData.append('file', audioBlob, 'recording.webm');
            
            await apiClient.post(`/tests/attempts/${attemptId}/speaking/${task.id}/upload`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            
            setStatus('completed');
        } catch (err) {
            console.error("Upload failed:", err);
            setUploadError("Failed to upload recording. Please try again.");
            setStatus('completed'); // Allow moving on even if upload fails? Or retry?
        }
    };

    return (
        <div className="max-w-2xl mx-auto text-center py-8">
            <h3 className="text-2xl font-bold mb-6">Speaking Part {task.part_number}</h3>
            
            <div className="bg-blue-50 p-8 rounded-xl mb-8 text-left">
                <p className="text-xl text-gray-800 font-medium mb-4">{task.prompt_text}</p>
                {task.cue_card_points && (
                    <ul className="list-disc list-inside space-y-2 text-gray-700 bg-white p-4 rounded-lg border border-blue-100">
                        {task.cue_card_points.map((point, idx) => (
                            <li key={idx}>{point}</li>
                        ))}
                    </ul>
                )}
            </div>

            <div className="mb-8">
                {status === 'idle' && (
                    <button 
                        onClick={startPreparation}
                        className="px-8 py-4 bg-primary-600 text-white rounded-full text-lg font-bold hover:bg-primary-700 transition shadow-lg"
                    >
                        Start Preparation
                    </button>
                )}

                {status === 'preparing' && (
                    <div className="text-center">
                        <p className="text-gray-500 mb-2 uppercase tracking-wide font-semibold">Preparation Time</p>
                        <div className="text-5xl font-mono font-bold text-yellow-600 mb-4">
                            {Math.floor(timeLeft / 60)}:{String(timeLeft % 60).padStart(2, '0')}
                        </div>
                        <p className="text-sm text-gray-400">Recording will start automatically...</p>
                        <button 
                            onClick={startRecording}
                            className="mt-4 text-primary-600 hover:text-primary-700 underline"
                        >
                            Skip Preparation
                        </button>
                    </div>
                )}

                {status === 'recording' && (
                    <div className="w-full">
                         <p className="text-gray-500 mb-2 uppercase tracking-wide font-semibold">Recording Time</p>
                         <AudioRecorder 
                            isRecording={true}
                            maxDuration={task.speaking_time_seconds}
                            onRecordingComplete={handleRecordingComplete}
                         />
                    </div>
                )}

                {status === 'uploading' && (
                    <div className="flex flex-col items-center justify-center py-8">
                        <div className="w-12 h-12 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin mb-4"></div>
                        <p className="text-gray-600">Uploading your answer...</p>
                    </div>
                )}

                {status === 'completed' && (
                    <div className="bg-green-50 p-6 rounded-lg border border-green-200">
                        <div className="text-green-600 text-5xl mb-2">✓</div>
                        <h4 className="text-xl font-bold text-green-800 mb-2">Answer Recorded</h4>
                        {uploadError ? (
                            <p className="text-red-600">{uploadError}</p>
                        ) : (
                            <p className="text-green-700 mb-6">Your response has been saved successfully.</p>
                        )}
                        <button 
                            onClick={onComplete}
                            className="px-6 py-3 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700 transition"
                        >
                            Continue
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
}
