import { useState, useEffect } from 'react';
import apiClient from '../../../api/client';

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
  const [questionForm, setQuestionForm] = useState({
    question_number: 1,
    question_type: 'reading_multiple_choice',
    question_text: '',
    marks: 1,
    options: [
      { option_label: 'A', option_text: '' },
      { option_label: 'B', option_text: '' },
      { option_label: 'C', option_text: '' },
      { option_label: 'D', option_text: '' }
    ],
    correct_answer: 'A'
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
        has_options: ['reading_multiple_choice'].includes(questionForm.question_type),
        marks: parseInt(questionForm.marks),
        options: ['reading_multiple_choice'].includes(questionForm.question_type) ? questionForm.options : null
      },
      answer: {
        correct_answer: questionForm.correct_answer,
        case_sensitive: false
      }
    };

    try {
      await apiClient.post('/reading/questions', payload);
      setShowAddQuestion(false);
      fetchPassageDetails(expandedPassage);
      // Reset form
      setQuestionForm({
        question_number: questionForm.question_number + 1,
        question_type: 'reading_multiple_choice',
        question_text: '',
        marks: 1,
        options: [
          { option_label: 'A', option_text: '' },
          { option_label: 'B', option_text: '' },
          { option_label: 'C', option_text: '' },
          { option_label: 'D', option_text: '' }
        ],
        correct_answer: 'A'
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
                      onClick={() => setShowAddQuestion(true)}
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
                        <button 
                          onClick={() => handleDeleteQuestion(q.id)}
                          className="text-red-600 hover:text-red-800 text-xs"
                        >
                          Delete
                        </button>
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
                  <textarea
                    required
                    rows={10}
                    value={passageForm.content}
                    onChange={(e) => setPassageForm({...passageForm, content: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 font-mono text-sm"
                    placeholder="Paste passage text here..."
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
            <h3 className="text-xl font-bold text-gray-900 mb-4">Add Question to Passage</h3>
            <form onSubmit={handleSaveQuestion} className="space-y-4">
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
                  onChange={(e) => setQuestionForm({...questionForm, question_type: e.target.value})}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                >
                  <option value="reading_multiple_choice">Multiple Choice</option>
                  <option value="reading_true_false_not_given">True / False / Not Given</option>
                  <option value="reading_yes_no_not_given">Yes / No / Not Given</option>
                  <option value="reading_matching_headings">Matching Headings</option>
                  <option value="reading_matching_information">Matching Information</option>
                  <option value="reading_sentence_completion">Sentence Completion</option>
                  <option value="reading_summary_completion">Summary Completion</option>
                  <option value="reading_diagram_labeling">Diagram Labeling</option>
                  <option value="reading_short_answer">Short Answer</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Question Text</label>
                <textarea
                  required
                  rows={3}
                  value={questionForm.question_text}
                  onChange={(e) => setQuestionForm({...questionForm, question_text: e.target.value})}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                />
              </div>

              {questionForm.question_type === 'reading_multiple_choice' && (
                <div className="space-y-3 border-t border-gray-100 pt-4">
                  <label className="block text-sm font-medium text-gray-900">Options</label>
                  {questionForm.options.map((opt, idx) => (
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
                      <input
                        type="radio"
                        name="correct_answer"
                        checked={questionForm.correct_answer === opt.option_label}
                        onChange={() => setQuestionForm({...questionForm, correct_answer: opt.option_label})}
                        className="h-4 w-4 text-primary-600"
                      />
                    </div>
                  ))}
                </div>
              )}

              {['reading_true_false_not_given', 'reading_yes_no_not_given'].includes(questionForm.question_type) && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Correct Answer</label>
                  <select
                    value={questionForm.correct_answer}
                    onChange={(e) => setQuestionForm({...questionForm, correct_answer: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  >
                    {questionForm.question_type === 'reading_true_false_not_given' ? (
                      <>
                        <option value="TRUE">TRUE</option>
                        <option value="FALSE">FALSE</option>
                        <option value="NOT GIVEN">NOT GIVEN</option>
                      </>
                    ) : (
                      <>
                        <option value="YES">YES</option>
                        <option value="NO">NO</option>
                        <option value="NOT GIVEN">NOT GIVEN</option>
                      </>
                    )}
                  </select>
                </div>
              )}

              {!['reading_multiple_choice', 'reading_true_false_not_given', 'reading_yes_no_not_given'].includes(questionForm.question_type) && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Correct Answer</label>
                  <input
                    type="text"
                    required
                    value={questionForm.correct_answer}
                    onChange={(e) => setQuestionForm({...questionForm, correct_answer: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                    placeholder="Enter the correct answer text"
                  />
                </div>
              )}

              <div className="flex justify-end space-x-3 pt-4">
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
