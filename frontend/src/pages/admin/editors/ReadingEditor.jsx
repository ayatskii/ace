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

export default function ReadingEditor({ sectionId, testId }) {
  const [passages, setPassages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddPassage, setShowAddPassage] = useState(false);
  const [expandedPassage, setExpandedPassage] = useState(null);
  
  // Passage Form State
  const [passageForm, setPassageForm] = useState({
    passage_number: 1,
    title: '',
    content: '',
    order: 1
  });

  // Question Form State
  const [showAddQuestion, setShowAddQuestion] = useState(false);
  const [editingQuestionId, setEditingQuestionId] = useState(null);
  const [questionForm, setQuestionForm] = useState({
    question_number: 1,
    question_type: 'reading_multiple_choice',
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
    fetchPassages();
  }, [sectionId]);

  const fetchPassages = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get(`/reading/passages?section_id=${sectionId}`);
      setPassages(response.data);
    } catch (error) {
      console.error('Failed to fetch passages:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSavePassage = async (e) => {
    e.preventDefault();
    try {
      await apiClient.post('/reading/passages', {
        ...passageForm,
        section_id: parseInt(sectionId),
        passage_number: parseInt(passageForm.passage_number),
        order: parseInt(passageForm.passage_number)
      });
      setShowAddPassage(false);
      fetchPassages();
      setPassageForm({ passage_number: passages.length + 2, title: '', content: '', order: passages.length + 2 });
    } catch (error) {
      console.error('Failed to save passage:', error);
      alert('Failed to save passage');
    }
  };

  const handleDeletePassage = async (id) => {
    if (!confirm('Delete passage and all its questions?')) return;
    try {
      await apiClient.delete(`/reading/passages/${id}`);
      fetchPassages();
    } catch (error) {
      console.error('Failed to delete passage:', error);
    }
  };

  const fetchPassageDetails = async (passageId) => {
    try {
      const response = await apiClient.get(`/reading/passages/${passageId}`);
      // Update the specific passage in the list with full details (including questions)
      setPassages(prev => prev.map(p => p.id === passageId ? response.data : p));
    } catch (error) {
      console.error('Failed to fetch passage details:', error);
    }
  };

  const togglePassage = (passageId) => {
    if (expandedPassage === passageId) {
      setExpandedPassage(null);
    } else {
      setExpandedPassage(passageId);
      fetchPassageDetails(passageId);
    }
  };

  const handleSaveQuestion = async (e) => {
    e.preventDefault();
    if (!expandedPassage) return;

    const payload = {
      question: {
        passage_id: expandedPassage,
        question_number: parseInt(questionForm.question_number),
        question_type: questionForm.question_type,
        question_text: questionForm.question_text,
        order: parseInt(questionForm.question_number),
        marks: parseInt(questionForm.marks),
        // Legacy fields
        has_options: false,
        options: null,
        
        // New JSON fields
        type_specific_data: questionForm.type_specific_data,
        answer_data: questionForm.answer_data
      },
      answer: {
        correct_answer: questionForm.correct_answer || 'See answer_data',
        case_sensitive: false
      }
    };

    // Handle legacy/simple types (MCQ)
    if (questionForm.question_type === 'reading_multiple_choice') {
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
      if (editingQuestionId) {
        await apiClient.put(`/reading/questions/${editingQuestionId}`, payload);
      } else {
        await apiClient.post('/reading/questions', payload);
      }
      setShowAddQuestion(false);
      setEditingQuestionId(null);
      fetchPassageDetails(expandedPassage);
      // Reset form
      setQuestionForm({
        question_number: questionForm.question_number + 1,
        question_type: 'reading_multiple_choice',
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
    if (!confirm('Delete question?')) return;
    try {
      await apiClient.delete(`/reading/questions/${id}`);
      if (expandedPassage) fetchPassageDetails(expandedPassage);
    } catch (error) {
      console.error('Failed to delete question:', error);
    }
  };

  const handleEditQuestion = (question) => {
    setEditingQuestionId(question.id);
    setQuestionForm({
      question_number: question.question_number,
      question_type: question.question_type,
      question_text: question.question_text,
      marks: question.marks,
      options: question.options || [],
      correct_answer: question.answers?.[0]?.correct_answer || '',
      correct_answers: question.answer_data?.correct_options || [], 
      allow_multiple: question.type_specific_data?.allow_multiple || false,
      type_specific_data: question.type_specific_data || {},
      answer_data: question.answer_data || {}
    });
    setShowAddQuestion(true);
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
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-medium text-gray-900">Reading Passages</h3>
        <button
          onClick={() => setShowAddPassage(true)}
          className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 text-sm"
        >
          + Add Passage
        </button>
      </div>

      {loading ? (
        <div className="text-center py-8 text-gray-500">Loading passages...</div>
      ) : passages.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-200">
          <p className="text-gray-500">No passages added yet</p>
        </div>
      ) : (
        <div className="space-y-4">
          {passages.map((passage) => (
            <div key={passage.id} className="bg-white border border-gray-200 rounded-lg overflow-hidden">
              <div 
                className="p-4 bg-gray-50 flex justify-between items-center cursor-pointer hover:bg-gray-100"
                onClick={() => togglePassage(passage.id)}
              >
                <div>
                  <h4 className="font-bold text-gray-900">Passage {passage.passage_number}: {passage.title}</h4>
                  <p className="text-xs text-gray-500">{passage.word_count || 0} words • {passage.questions?.length || 0} questions</p>
                </div>
                <div className="flex items-center space-x-3">
                  <button 
                    onClick={(e) => { e.stopPropagation(); handleDeletePassage(passage.id); }}
                    className="text-red-600 hover:text-red-800 text-sm"
                  >
                    Delete
                  </button>
                  <span className="text-gray-400">
                    {expandedPassage === passage.id ? '▼' : '▶'}
                  </span>
                </div>
              </div>

              {expandedPassage === passage.id && (
                <div className="p-4 border-t border-gray-200">
                  <div className="mb-6">
                    <h5 className="text-sm font-medium text-gray-700 mb-2">Passage Content</h5>
                    <div className="bg-gray-50 p-3 rounded text-sm text-gray-800 max-h-60 overflow-y-auto whitespace-pre-wrap">
                      {passage.content}
                    </div>
                  </div>

                  <div className="flex justify-between items-center mb-4">
                    <h5 className="text-sm font-medium text-gray-700">Questions</h5>
                    <button
                      onClick={() => {
                        // Calculate next question number
                        let maxQ = 0;
                        passages.forEach(p => {
                          if (p.questions) {
                            p.questions.forEach(q => {
                              if (q.question_number > maxQ) maxQ = q.question_number;
                            });
                          }
                        });
                        setQuestionForm(prev => ({ ...prev, question_number: maxQ + 1 }));
                        setEditingQuestionId(null); // Reset editing state
                        setShowAddQuestion(true);
                      }}
                      className="px-3 py-1 bg-white border border-gray-300 rounded text-sm hover:bg-gray-50"
                    >
                      + Add Question
                    </button>
                  </div>

                  <div className="space-y-3">
                    {passage.questions && passage.questions.map(q => (
                      <div key={q.id} className="border border-gray-200 rounded p-3 flex justify-between">
                        <div>
                          <div className="flex items-center space-x-2 mb-1">
                            <span className="font-bold text-sm">Q{q.question_number}</span>
                            <span className="text-xs px-2 py-0.5 bg-gray-100 rounded-full text-gray-600">
                              {q.question_type.replace('reading_', '').replace(/_/g, ' ')}
                            </span>
                          </div>
                          <p className="text-sm text-gray-800">{q.question_text}</p>
                        </div>
                        <div className="flex items-center space-x-2">
                          <button 
                            onClick={() => handleEditQuestion(q)}
                            className="text-blue-600 hover:text-blue-800 text-xs"
                          >
                            Edit
                          </button>
                          <button 
                            onClick={() => handleDeleteQuestion(q.id)}
                            className="text-red-600 hover:text-red-800 text-xs"
                          >
                            Delete
                          </button>
                        </div>
                      </div>
                    ))}
                    {(!passage.questions || passage.questions.length === 0) && (
                      <p className="text-sm text-gray-500 italic">No questions added to this passage.</p>
                    )}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Add Passage Modal */}
      {showAddPassage && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-2xl w-full p-6">
            <h3 className="text-xl font-bold text-gray-900 mb-4">Add Reading Passage</h3>
            <form onSubmit={handleSavePassage}>
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Passage Number</label>
                    <input
                      type="number"
                      required
                      value={passageForm.passage_number}
                      onChange={(e) => setPassageForm({...passageForm, passage_number: e.target.value})}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
                    <input
                      type="text"
                      required
                      value={passageForm.title}
                      onChange={(e) => setPassageForm({...passageForm, title: e.target.value})}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2"
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Content</label>
                  <MarkdownEditor
                    value={passageForm.content}
                    onChange={(e) => setPassageForm({...passageForm, content: e.target.value})}
                    rows={15}
                    placeholder="Paste passage text here... (Markdown supported)"
                    label=""
                  />
                </div>
              </div>
              <div className="flex justify-end space-x-3 mt-6">
                <button
                  type="button"
                  onClick={() => setShowAddPassage(false)}
                  className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
                >
                  Save Passage
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Add Question Modal */}
      {showAddQuestion && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-2xl w-full p-6 max-h-[90vh] overflow-y-auto">
            <h3 className="text-xl font-bold text-gray-900 mb-4">{editingQuestionId ? 'Edit Question' : 'Add Question to Passage'}</h3>
            <form onSubmit={handleSaveQuestion} className="space-y-6">
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
                    {QUESTION_TYPE_CATEGORIES.reading.completion.map(t => (
                      <option key={t.value} value={t.value}>{t.label}</option>
                    ))}
                  </optgroup>
                  <optgroup label="Matching">
                    {QUESTION_TYPE_CATEGORIES.reading.matching.map(t => (
                      <option key={t.value} value={t.value}>{t.label}</option>
                    ))}
                  </optgroup>
                  <optgroup label="Multiple Choice">
                    {QUESTION_TYPE_CATEGORIES.reading.choice.map(t => (
                      <option key={t.value} value={t.value}>{t.label}</option>
                    ))}
                  </optgroup>
                  <optgroup label="True/False/Not Given">
                    {QUESTION_TYPE_CATEGORIES.reading.tfng.map(t => (
                      <option key={t.value} value={t.value}>{t.label}</option>
                    ))}
                  </optgroup>
                  <optgroup label="Diagram/Map">
                    {QUESTION_TYPE_CATEGORIES.reading.diagram.map(t => (
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
                  placeholder="Enter question text or instructions..."
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
