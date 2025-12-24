import { useState, useEffect } from 'react';
import apiClient from '../../../api/client';
import { 
  CompletionEditor, 
  MatchingEditor, 
  DiagramEditor, 
  TFNGEditor,
  TableEditor,
  getEditorForType,
  QUESTION_TYPE_CATEGORIES 
} from '../../../components/editors';
import MarkdownEditor from '../../../components/common/MarkdownEditor';

export default function ListeningEditor({ sectionId, testId }) {
  const [parts, setParts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddPart, setShowAddPart] = useState(false);
  const [showAddQuestion, setShowAddQuestion] = useState(false);
  const [selectedPartId, setSelectedPartId] = useState(null);
  
  // Part Form State
  const [partForm, setPartForm] = useState({
    part_number: 1,
    audio_url: '',
    transcript: ''
  });

  // Question Form State
  const [questionForm, setQuestionForm] = useState({
    question_number: 1,
    question_type: 'listening_multiple_choice',
    question_text: '',
    marks: 1,
    // Standard fields
    options: [],
    correct_answer: '',
    // New structured fields
    type_specific_data: {},
    answer_data: {}
  });

  useEffect(() => {
    fetchParts();
  }, [sectionId]);

  const fetchParts = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get(`/listening/parts?section_id=${sectionId}`);
      const partsData = response.data;
      
      // Fetch questions for each part
      const partsWithQuestions = await Promise.all(partsData.map(async (part) => {
        const qResponse = await apiClient.get(`/listening/questions?section_id=${sectionId}&part_id=${part.id}`);
        return { ...part, questions: qResponse.data };
      }));
      
      setParts(partsWithQuestions);
    } catch (error) {
      console.error('Failed to fetch parts:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAudioUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await apiClient.post('/upload/audio', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setPartForm(prev => ({ ...prev, audio_url: response.data.url }));
    } catch (error) {
      console.error('Upload failed:', error);
      alert('Failed to upload audio');
    }
  };

  const handleCreatePart = async (e) => {
    e.preventDefault();
    try {
      await apiClient.post('/listening/parts', {
        ...partForm,
        section_id: parseInt(sectionId),
        part_number: parseInt(partForm.part_number)
      });
      setShowAddPart(false);
      fetchParts();
      setPartForm({ part_number: parts.length + 2, audio_url: '', transcript: '' });
    } catch (error) {
      console.error('Failed to create part:', error);
      alert('Failed to create part');
    }
  };

  const handleDeletePart = async (id) => {
    if (!confirm('Delete this part and all its questions?')) return;
    try {
      await apiClient.delete(`/listening/parts/${id}`);
      fetchParts();
    } catch (error) {
      console.error('Failed to delete part:', error);
    }
  };

  const handleCreateQuestion = async (e) => {
    e.preventDefault();
    
    // Construct payload based on question type
    const payload = {
      question: {
        section_id: parseInt(sectionId),
        part_id: selectedPartId,
        question_number: parseInt(questionForm.question_number),
        question_type: questionForm.question_type,
        question_text: questionForm.question_text,
        order: parseInt(questionForm.question_number),
        marks: parseInt(questionForm.marks),
        // Legacy fields for backward compatibility if needed, but we rely on JSON columns now
        has_options: false, 
        options: null,
        image_url: questionForm.type_specific_data?.image_url || null,
        
        // New JSON fields
        type_specific_data: questionForm.type_specific_data,
        answer_data: questionForm.answer_data
      },
      answer: {
        // For simple types, we might still use this, but for complex types it's in answer_data
        correct_answer: questionForm.correct_answer || 'See answer_data',
        case_sensitive: false
      }
    };

    // Handle legacy/simple types (MCQ, Short Answer) if they don't use the new editors yet
    if (questionForm.question_type === 'listening_multiple_choice') {
       payload.question.has_options = true;
       payload.question.options = questionForm.options;
       payload.question.type_specific_data = { 
         options: questionForm.options,
         allow_multiple: questionForm.allow_multiple || false
       };
       
       // Handle correct answer(s)
       let correctOptions = [];
       if (questionForm.allow_multiple) {
          correctOptions = questionForm.correct_answers || [];
       } else {
          correctOptions = [questionForm.correct_answer];
       }
       
       payload.question.answer_data = {
         correct_options: correctOptions
       };
    }

    try {
      await apiClient.post('/listening/questions', payload);
      setShowAddQuestion(false);
      fetchParts();
      
      // Reset form
      setQuestionForm({
        question_number: questionForm.question_number + 1,
        question_type: 'listening_multiple_choice',
        question_text: '',
        marks: 1,
        options: [],
        correct_answer: '',
        correct_answers: [],
        allow_multiple: false,
        type_specific_data: {},
        answer_data: {}
      });
    } catch (error) {
      console.error('Failed to save question:', error);
      alert('Failed to save question');
    }
  };

  const handleDeleteQuestion = async (id) => {
    if (!confirm('Delete this question?')) return;
    try {
      await apiClient.delete(`/listening/questions/${id}`);
      fetchParts();
    } catch (error) {
      console.error('Failed to delete question:', error);
    }
  };

  // Render the appropriate editor based on selected type
  const renderEditor = () => {
    const editorType = getEditorForType(questionForm.question_type);
    
    const commonProps = {
      value: {
        ...questionForm.type_specific_data,
        answers: questionForm.answer_data
      },
      onChange: (data) => {
        setQuestionForm(prev => ({
          ...prev,
          type_specific_data: { ...prev.type_specific_data, ...data.type_specific_data },
          answer_data: { ...prev.answer_data, ...data.answer_data }
        }));
      },
      questionType: questionForm.question_type
    };

    switch (editorType) {
      case 'CompletionEditor':
        return <CompletionEditor {...commonProps} />;
      case 'MatchingEditor':
        return <MatchingEditor {...commonProps} />;
      case 'DiagramEditor':
        return <DiagramEditor {...commonProps} />;
      case 'TFNGEditor':
        return <TFNGEditor {...commonProps} />;
      case 'TableEditor':
        return <TableEditor {...commonProps} />;
      default:
        // Fallback for simple types (MCQ, Short Answer)
        if (questionForm.question_type.includes('multiple_choice')) {
          return renderMCQEditor();
        }
        return (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Correct Answer</label>
            <input
              type="text"
              value={questionForm.correct_answer}
              onChange={(e) => setQuestionForm({...questionForm, correct_answer: e.target.value})}
              className="w-full border border-gray-300 rounded-lg px-3 py-2"
              placeholder="Enter correct answer"
            />
          </div>
        );
    }
  };

  const renderMCQEditor = () => (
    <div className="space-y-3 border-t border-gray-100 pt-4">
      <div className="flex justify-between items-center mb-4">
        <label className="flex items-center space-x-2 text-sm text-gray-700">
          <input
            type="checkbox"
            checked={questionForm.allow_multiple || false}
            onChange={(e) => setQuestionForm({
              ...questionForm, 
              allow_multiple: e.target.checked,
              correct_answers: [] // Reset correct answers when toggling
            })}
            className="rounded text-primary-600"
          />
          <span>Allow Multiple Correct Answers</span>
        </label>
      </div>

      <div className="flex justify-between items-center">
        <label className="block text-sm font-medium text-gray-900">Options</label>
        <button
          type="button"
          onClick={() => {
            const nextLabel = String.fromCharCode(65 + (questionForm.options?.length || 0));
            setQuestionForm(prev => ({
              ...prev,
              options: [...(prev.options || []), { option_label: nextLabel, option_text: '' }]
            }));
          }}
          className="text-xs text-primary-600 hover:text-primary-700 font-medium"
        >
          + Add Option
        </button>
      </div>
      
      {questionForm.options?.map((opt, idx) => (
        <div key={idx} className="flex items-center space-x-2">
          <span className="font-bold w-6">{opt.option_label}</span>
          <input
            type="text"
            value={opt.option_text}
            onChange={(e) => {
              const newOptions = [...questionForm.options];
              newOptions[idx].option_text = e.target.value;
              setQuestionForm({...questionForm, options: newOptions});
            }}
            className="flex-1 border border-gray-300 rounded-lg px-3 py-2"
            placeholder={`Option ${opt.option_label}`}
          />
          
          {questionForm.allow_multiple ? (
            <input
              type="checkbox"
              checked={(questionForm.correct_answers || []).includes(opt.option_label)}
              onChange={(e) => {
                const current = questionForm.correct_answers || [];
                let newCorrect;
                if (e.target.checked) {
                  newCorrect = [...current, opt.option_label];
                } else {
                  newCorrect = current.filter(l => l !== opt.option_label);
                }
                setQuestionForm({...questionForm, correct_answers: newCorrect});
              }}
              className="h-4 w-4 text-primary-600 rounded"
              title="Mark as correct"
            />
          ) : (
            <input
              type="radio"
              name="correct_answer"
              checked={questionForm.correct_answer === opt.option_label}
              onChange={() => setQuestionForm({...questionForm, correct_answer: opt.option_label})}
              className="h-4 w-4 text-primary-600"
              title="Mark as correct"
            />
          )}
          
          <button
            type="button"
            onClick={() => {
              const newOptions = questionForm.options.filter((_, i) => i !== idx);
              const reLabeled = newOptions.map((o, i) => ({ ...o, option_label: String.fromCharCode(65 + i) }));
              setQuestionForm({...questionForm, options: reLabeled});
            }}
            className="text-gray-400 hover:text-red-500"
          >
            ×
          </button>
        </div>
      ))}
    </div>
  );

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-medium text-gray-900">Listening Parts</h3>
        <button
          onClick={() => setShowAddPart(true)}
          className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 text-sm"
        >
          + Add Part
        </button>
      </div>

      {loading ? (
        <div className="text-center py-8 text-gray-500">Loading parts...</div>
      ) : parts.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-200">
          <p className="text-gray-500">No parts added yet. Add a part (audio) to start.</p>
        </div>
      ) : (
        <div className="space-y-6">
          {parts.map((part) => (
            <div key={part.id} className="bg-white border border-gray-200 rounded-lg overflow-hidden">
              <div className="bg-gray-50 px-4 py-3 border-b border-gray-200 flex justify-between items-center">
                <div className="flex items-center space-x-3">
                  <span className="font-bold text-gray-900">Part {part.part_number}</span>
                  <audio controls src={part.audio_url} className="h-8 w-64" />
                </div>
                <button 
                  onClick={() => handleDeletePart(part.id)}
                  className="text-red-600 hover:text-red-800 text-sm"
                >
                  Delete Part
                </button>
              </div>
              
              <div className="p-4">
                <div className="space-y-3">
                  {part.questions && part.questions.map((q) => (
                    <div key={q.id} className="flex justify-between items-start p-3 bg-gray-50 rounded border border-gray-100">
                      <div>
                        <div className="flex items-center space-x-2 mb-1">
                          <span className="font-bold text-sm text-gray-900">Q{q.question_number}</span>
                          <span className="text-xs px-2 py-0.5 bg-white border border-gray-200 rounded text-gray-600">
                            {q.question_type.replace('listening_', '').replace(/_/g, ' ')}
                          </span>
                        </div>
                        <p className="text-sm text-gray-800">{q.question_text}</p>
                      </div>
                      <button 
                        onClick={() => handleDeleteQuestion(q.id)}
                        className="text-gray-400 hover:text-red-600"
                      >
                        ×
                      </button>
                    </div>
                  ))}
                  
                  <button
                    onClick={() => {
                      setSelectedPartId(part.id);
                      // Calculate next question number
                      let maxQ = 0;
                      parts.forEach(p => {
                        if (p.questions) {
                          p.questions.forEach(q => {
                            if (q.question_number > maxQ) maxQ = q.question_number;
                          });
                        }
                      });
                      setQuestionForm(prev => ({ ...prev, question_number: maxQ + 1 }));
                      setShowAddQuestion(true);
                    }}
                    className="w-full py-2 border-2 border-dashed border-gray-300 rounded-lg text-gray-500 hover:border-primary-500 hover:text-primary-600 text-sm font-medium transition-colors"
                  >
                    + Add Question to Part {part.part_number}
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add Part Modal */}
      {showAddPart && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-md w-full p-6 m-4">
            <h3 className="text-xl font-bold text-gray-900 mb-4">Add Listening Part</h3>
            <form onSubmit={handleCreatePart} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Part Number</label>
                <select
                  value={partForm.part_number}
                  onChange={(e) => setPartForm({...partForm, part_number: e.target.value})}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                >
                  <option value={1}>Part 1</option>
                  <option value={2}>Part 2</option>
                  <option value={3}>Part 3</option>
                  <option value={4}>Part 4</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Audio File</label>
                <input
                  type="file"
                  accept="audio/*"
                  onChange={handleAudioUpload}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                />
                {partForm.audio_url && (
                  <p className="text-xs text-green-600 mt-1">Audio uploaded!</p>
                )}
              </div>

              <div className="flex justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowAddPart(false)}
                  className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={!partForm.audio_url}
                  className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
                >
                  Create Part
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Add Question Modal */}
      {showAddQuestion && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 overflow-y-auto">
          <div className="bg-white rounded-xl shadow-xl max-w-2xl w-full p-6 m-4 max-h-[90vh] overflow-y-auto">
            <h3 className="text-xl font-bold text-gray-900 mb-4">Add Question</h3>
            
            <form onSubmit={handleCreateQuestion} className="space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Question Number</label>
                  <input
                    type="number"
                    required
                    value={questionForm.question_number}
                    onChange={(e) => setQuestionForm({...questionForm, question_number: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Marks</label>
                  <input
                    type="number"
                    required
                    value={questionForm.marks}
                    onChange={(e) => setQuestionForm({...questionForm, marks: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Question Type</label>
                <select
                  value={questionForm.question_type}
                  onChange={(e) => setQuestionForm({
                    ...questionForm, 
                    question_type: e.target.value,
                    type_specific_data: {},
                    answer_data: {}
                  })}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                >
                  <optgroup label="Completion">
                    {QUESTION_TYPE_CATEGORIES.listening.completion.map(t => (
                      <option key={t.value} value={t.value}>{t.label}</option>
                    ))}
                  </optgroup>
                  <optgroup label="Matching">
                    {QUESTION_TYPE_CATEGORIES.listening.matching.map(t => (
                      <option key={t.value} value={t.value}>{t.label}</option>
                    ))}
                  </optgroup>
                  <optgroup label="Multiple Choice">
                    {QUESTION_TYPE_CATEGORIES.listening.choice.map(t => (
                      <option key={t.value} value={t.value}>{t.label}</option>
                    ))}
                  </optgroup>
                  <optgroup label="Diagram/Map">
                    {QUESTION_TYPE_CATEGORIES.listening.diagram.map(t => (
                      <option key={t.value} value={t.value}>{t.label}</option>
                    ))}
                  </optgroup>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Question Text / Instructions</label>
                <MarkdownEditor
                  value={questionForm.question_text}
                  onChange={(e) => setQuestionForm({...questionForm, question_text: e.target.value})}
                  rows={4}
                  placeholder="Enter the main question text or instructions..."
                />
              </div>

              {/* Dynamic Editor Area */}
              <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                {renderEditor()}
              </div>

              <div className="flex justify-end space-x-3 pt-4 border-t border-gray-100">
                <button
                  type="button"
                  onClick={() => setShowAddQuestion(false)}
                  className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
                >
                  Save Question
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
