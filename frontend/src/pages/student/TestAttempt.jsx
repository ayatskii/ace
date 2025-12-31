import { useParams, useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkBreaks from 'remark-breaks';
import Timer from '../../components/test/Timer';
import ProgressBar from '../../components/test/ProgressBar';
import AudioRecorder from '../../components/test/AudioRecorder';
import apiClient from '../../api/client';
import {
  CompletionQuestionRenderer,
  MatchingQuestionRenderer,
  DiagramQuestionRenderer,
  TFNGQuestionRenderer,
  MCQQuestionRenderer,
  TableQuestionRenderer,
  ShortAnswerQuestionRenderer
} from '../../components/test/renderers';

export default function TestAttempt() {
  const { attemptId } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [attempt, setAttempt] = useState(null);
  const [testStructure, setTestStructure] = useState(null);
  
  const [currentSectionIndex, setCurrentSectionIndex] = useState(0);
  const [currentItemIndex, setCurrentItemIndex] = useState(0); // Part/Passage/Task index within section
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

  // Get the navigation items for current section (parts, passages, or tasks)
  const getSectionItems = () => {
    if (!testStructure) return [];
    if (currentSection.section_type === 'listening') {
      return testStructure.listening_parts.sort((a, b) => a.part_number - b.part_number);
    }
    if (currentSection.section_type === 'reading') {
      return testStructure.reading_passages.sort((a, b) => a.order - b.order);
    }
    if (currentSection.section_type === 'writing') {
      return testStructure.writing_tasks.sort((a, b) => a.task_number - b.task_number);
    }
    if (currentSection.section_type === 'speaking') {
      return testStructure.speaking_tasks.sort((a, b) => a.order - b.order);
    }
    return [];
  };

  // Get questions for a specific part (listening)
  const getQuestionsForPart = (partId) => {
    return testStructure.listening_questions
      .filter(q => q.part_id === partId)
      .sort((a, b) => a.order - b.order);
  };

  // Get questions for a specific passage (reading)
  const getQuestionsForPassage = (passageId) => {
    return testStructure.reading_questions
      .filter(q => q.passage_id === passageId)
      .sort((a, b) => a.order - b.order);
  };

  const items = getSectionItems();
  const currentItem = items[currentItemIndex];

  const handleNext = () => {
    if (currentItemIndex < items.length - 1) {
      setCurrentItemIndex(currentItemIndex + 1);
    }
  };

  const handlePrevious = () => {
    if (currentItemIndex > 0) {
      setCurrentItemIndex(currentItemIndex - 1);
    }
  };

  const handleSectionFinish = () => {
    if (currentSectionIndex < sections.length - 1) {
      setCurrentSectionIndex(currentSectionIndex + 1);
      setCurrentItemIndex(0);
    } else {
      handleSubmitTest();
    }
  };

  const handleAnswerChange = (questionId, value) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: value
    }));
  };

  const handleSubmitTest = async () => {
    try {
      if (window.confirm("Are you sure you want to submit the test?")) {
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
                const qId = parseInt(key);
                
                const isListening = testStructure.listening_questions.some(q => q.id === qId);
                if (isListening) {
                    listeningAnswers.push({
                        question_id: qId,
                        user_answer: typeof value === 'object' ? JSON.stringify(value) : String(value)
                    });
                    return;
                }

                const isReading = testStructure.reading_questions.some(q => q.id === qId);
                if (isReading) {
                    readingAnswers.push({
                        question_id: qId,
                        user_answer: typeof value === 'object' ? JSON.stringify(value) : String(value)
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

  const renderQuestionContent = (question) => {
    const commonProps = {
      question: question,
      answer: answers[question.id],
      onAnswerChange: (val) => handleAnswerChange(question.id, val)
    };

    switch (question.question_type) {
      case 'listening_fill_in_blank':
      case 'listening_note_completion':
      case 'listening_form_completion':
      case 'listening_sentence_completion':
      case 'listening_summary_completion':
      case 'reading_sentence_completion':
      case 'reading_summary_completion':
      case 'reading_note_completion':
      case 'reading_form_completion':
        return <CompletionQuestionRenderer {...commonProps} />;

      case 'reading_short_answer': 
      case 'listening_short_answer':
        return <ShortAnswerQuestionRenderer {...commonProps} />;
      
      case 'listening_matching':
      case 'listening_matching_headings':
      case 'listening_matching_sentence_endings':
      case 'listening_matching_paragraphs':
      case 'listening_name_matching':
      case 'reading_matching_headings':
      case 'reading_matching_information':
      case 'reading_matching_features':
      case 'reading_matching_sentence_endings':
        return <MatchingQuestionRenderer {...commonProps} />;
      
      case 'listening_map_diagram':
      case 'listening_diagram_labeling':
      case 'listening_map_labeling':
      case 'reading_diagram_labeling':
      case 'reading_flowchart':
        return <DiagramQuestionRenderer {...commonProps} />;
      
      case 'listening_true_false_not_given':
      case 'reading_true_false_not_given':
      case 'reading_yes_no_not_given':
        return <TFNGQuestionRenderer {...commonProps} />;

      case 'listening_table_completion':
      case 'reading_table_completion':
        return <TableQuestionRenderer {...commonProps} />;

      case 'listening_multiple_choice':
      case 'reading_multiple_choice':
        return <MCQQuestionRenderer {...commonProps} />;

      default:
        return (
          <div className="space-y-3">
             <p className="text-red-500">Unknown question type: {question.question_type}</p>
          </div>
        );
    }
  };

  // Render content based on section type
  const renderContent = () => {
    if (!currentItem) return <div>No content in this section.</div>;

    // LISTENING: Show Part with audio + all questions for this part
    if (currentSection.section_type === 'listening') {
      const questions = getQuestionsForPart(currentItem.id);
      return (
        <div className="space-y-6">
          {/* Part Header with Audio */}
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-6 rounded-xl border border-blue-100">
            <h3 className="text-xl font-bold text-blue-900 mb-3">Part {currentItem.part_number}</h3>
            <audio controls src={currentItem.audio_url} className="w-full" />
            {currentItem.transcript && (
              <details className="mt-3">
                <summary className="text-sm text-blue-600 cursor-pointer hover:text-blue-800">Show Transcript</summary>
                <div className="mt-2 p-3 bg-white rounded border text-sm text-gray-700 whitespace-pre-wrap">
                  {currentItem.transcript}
                </div>
              </details>
            )}
          </div>
          
          {/* All Questions for this Part */}
          <div className="space-y-6">
            {questions.map((question, idx) => (
              <div key={question.id} className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
                <div className="flex items-start gap-3 mb-4">
                  <span className="flex-shrink-0 w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold text-sm">
                    {question.question_number}
                  </span>
                  <h4 className="text-lg font-medium text-gray-900">
                    <ReactMarkdown remarkPlugins={[remarkGfm, remarkBreaks]} className="prose prose-sm max-w-none">
                      {question.question_text}
                    </ReactMarkdown>
                  </h4>
                </div>
                {question.image_url && (
                  <img src={question.image_url} alt="Question Diagram" className="mb-4 max-h-64 object-contain rounded-lg" />
                )}
                {renderQuestionContent(question)}
              </div>
            ))}
          </div>
        </div>
      );
    }

    // READING: Show Passage (left) + all questions for this passage (right)
    if (currentSection.section_type === 'reading') {
      const questions = getQuestionsForPassage(currentItem.id);
      return (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-[calc(100vh-300px)]">
          {/* Passage Content */}
          <div className="overflow-y-auto pr-4 border-r border-gray-200">
            <div className="sticky top-0 bg-white pb-2 border-b border-gray-100 mb-4">
              <h3 className="font-bold text-xl text-gray-900">{currentItem.title}</h3>
              <p className="text-sm text-gray-500">Passage {currentItem.passage_number}</p>
            </div>
            <div className="prose max-w-none text-gray-800 leading-relaxed">
              <ReactMarkdown remarkPlugins={[remarkGfm, remarkBreaks]}>
                {currentItem.content}
              </ReactMarkdown>
            </div>
          </div>
          
          {/* All Questions for this Passage */}
          <div className="overflow-y-auto pl-2 space-y-6">
            {questions.map((question, idx) => (
              <div key={question.id} className="bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
                <div className="flex items-start gap-3 mb-4">
                  <span className="flex-shrink-0 w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold text-sm">
                    {question.question_number}
                  </span>
                  <h4 className="text-lg font-medium text-gray-900">
                    <ReactMarkdown remarkPlugins={[remarkGfm, remarkBreaks]} className="prose prose-sm max-w-none">
                      {question.question_text}
                    </ReactMarkdown>
                  </h4>
                </div>
                {renderQuestionContent(question)}
              </div>
            ))}
          </div>
        </div>
      );
    }

    // WRITING: Keep as-is (task by task)
    if (currentSection.section_type === 'writing') {
      return (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-gray-50 p-6 rounded-lg">
            <h3 className="font-bold text-lg mb-2">Task {currentItem.task_number}</h3>
            <p className="whitespace-pre-wrap mb-4">{currentItem.prompt_text}</p>
            {currentItem.image_url && (
              <img src={currentItem.image_url} alt="Task" className="w-full rounded-lg border border-gray-200" />
            )}
            <div className="mt-4 text-sm text-gray-500">
              Min words: {currentItem.word_limit_min}
            </div>
          </div>
          <div>
            <textarea
              className="w-full h-96 border border-gray-300 rounded-lg p-4 font-mono"
              placeholder="Type your essay here..."
              onChange={(e) => setAnswers({...answers, [`w-${currentItem.id}`]: e.target.value})}
              value={answers[`w-${currentItem.id}`] || ''}
            />
            <div className="mt-2 flex justify-between items-center">
              <div className={`text-sm ${
                ((answers[`w-${currentItem.id}`] || '').split(/\s+/).filter(w => w.length > 0).length < currentItem.word_limit_min)
                  ? 'text-red-600 font-semibold'
                  : 'text-gray-500'
              }`}>
                {((answers[`w-${currentItem.id}`] || '').split(/\s+/).filter(w => w.length > 0).length < currentItem.word_limit_min) && '⚠️ '}
                Word count: {(answers[`w-${currentItem.id}`] || '').split(/\s+/).filter(w => w.length > 0).length}
                {((answers[`w-${currentItem.id}`] || '').split(/\s+/).filter(w => w.length > 0).length < currentItem.word_limit_min) && 
                  ` (Minimum: ${currentItem.word_limit_min})`
                }
              </div>
            </div>
          </div>
        </div>
      );
    }

    // SPEAKING: Keep as-is
    if (currentSection.section_type === 'speaking') {
      return (
        <SpeakingSection 
          task={currentItem} 
          attemptId={attemptId}
          onComplete={() => {
            if (currentItemIndex < items.length - 1) {
                handleNext();
            } else {
                handleSectionFinish();
            }
          }}
        />
      );
    }
  };

  // Get label for current item
  const getItemLabel = () => {
    if (currentSection.section_type === 'listening') return `Part ${currentItem?.part_number || 1}`;
    if (currentSection.section_type === 'reading') return `Passage ${currentItem?.passage_number || 1}`;
    if (currentSection.section_type === 'writing') return `Task ${currentItem?.task_number || 1}`;
    if (currentSection.section_type === 'speaking') return `Part ${currentItem?.part_number || 1}`;
    return '';
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 shadow-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-xl font-bold text-gray-900 capitalize">
                {currentSection.section_type} Section - {getItemLabel()}
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
            current={currentItemIndex + 1}
            total={items.length}
          />
          
          <div className="mt-8">
            {renderContent()}
          </div>
          
          {/* Navigation */}
          <div className="flex justify-between mt-8 pt-6 border-t border-gray-200">
            <button
              onClick={handlePrevious}
              disabled={currentItemIndex === 0 || currentSection.section_type === 'speaking'}
              className="px-6 py-3 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-lg font-semibold transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              ← Previous {currentSection.section_type === 'listening' ? 'Part' : 
                         currentSection.section_type === 'reading' ? 'Passage' : 'Task'}
            </button>
            
            {currentItemIndex === items.length - 1 ? (
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
                Next {currentSection.section_type === 'listening' ? 'Part' : 
                      currentSection.section_type === 'reading' ? 'Passage' : 'Task'} →
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
            setStatus('uploading');
        }
    };

    const startPreparation = () => {
        const prepTime = task.preparation_time_seconds || 10;
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
            setStatus('completed');
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
