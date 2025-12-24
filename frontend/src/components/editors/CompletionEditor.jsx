import { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkBreaks from 'remark-breaks';
import MarkdownEditor from '../common/MarkdownEditor';

/**
 * CompletionEditor - Editor for completion-type questions
 * (Form, Note, Table, Summary, Sentence Completion)
 * 
 * Features:
 * - Template text editor with [BLANK_X] markers
 * - Auto-detection of blanks
 * - Configuration panel for each blank (max words, case sensitivity)
 * - Answer input for each blank (primary + alternatives)
 * - Live preview showing how the question will appear to students
 */
export default function CompletionEditor({ value, onChange, questionType }) {
  const [template, setTemplate] = useState(value?.template_text || '');
  const [blanks, setBlanks] = useState(value?.blanks || []);
  const [answers, setAnswers] = useState(value?.answers || {});

  // Auto-detect [BLANK_X] markers when template changes
  useEffect(() => {
    const regex = /\[BLANK_(\d+)\]/g;
    const matches = [...template.matchAll(regex)];
    
    const detectedBlanks = matches.map(match => {
      const blankId = `BLANK_${match[1]}`;
      // Preserve existing config if blank already exists
      const existing = blanks.find(b => b.blank_id === blankId);
      return existing || {
        blank_id: blankId,
        max_words: 3,
        case_sensitive: false
      };
    });
    
    setBlanks(detectedBlanks);
  }, [template]);

  // Notify parent when data changes
  useEffect(() => {
    onChange?.({
      type_specific_data: {
        template_text: template,
        blanks: blanks
      },
      answer_data: {
        blanks: answers
      }
    });
  }, [template, blanks, answers]);

  const updateBlankConfig = (blankId, field, value) => {
    setBlanks(blanks.map(b => 
      b.blank_id === blankId ? { ...b, [field]: value } : b
    ));
  };

  const updateAnswer = (blankId, answerList) => {
    setAnswers({ ...answers, [blankId]: answerList });
  };

  // Render preview with input boxes for blanks
  const renderPreview = () => {
    if (!template) return <p className="text-gray-400 italic">Enter template text to see preview</p>;
    
    // Replace [BLANK_X] with markdown links [BLANK_X](blank:X)
    // This allows ReactMarkdown to handle the structure (paragraphs, lists) correctly
    const processedTemplate = template.replace(/\[BLANK_(\d+)\]/g, '[BLANK_$1](blank:$1)');
    
    return (
      <div className="prose max-w-none">
        <ReactMarkdown 
          remarkPlugins={[remarkGfm, remarkBreaks]}
          components={{
            a: ({node, ...props}) => {
              // Check if this is a blank marker
              if (props.href && props.href.startsWith('blank:')) {
                const blankNum = props.href.split(':')[1];
                const blankId = `BLANK_${blankNum}`;
                const config = blanks.find(b => b.blank_id === blankId);
                
                return (
                  <span className="inline-block mx-1">
                    <input
                      type="text"
                      disabled
                      placeholder={`_____ (${config?.max_words || 3} words max)`}
                      className="border-b-2 border-gray-400 bg-gray-100 w-32 text-center text-sm px-1"
                    />
                  </span>
                );
              }
              // Normal link
              return <a target="_blank" rel="noopener noreferrer" {...props} />;
            }
          }}
        >
          {processedTemplate}
        </ReactMarkdown>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Template Editor */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Template Text
          <span className="text-gray-400 font-normal ml-2">
            Use [BLANK_1], [BLANK_2], etc. for answer blanks
          </span>
        </label>
        <MarkdownEditor
          value={template}
          onChange={(e) => setTemplate(e.target.value)}
          rows={6}
          placeholder={`Example templates:
Form: Name: [BLANK_1]  Date: [BLANK_2]
Summary: The company was founded in [BLANK_1] by [BLANK_2].
Sentence: The event starts at [BLANK_1] on [BLANK_2].`}
        />
      </div>

      {/* Blanks Configuration */}
      {blanks.length > 0 && (
        <div className="border rounded-lg overflow-hidden">
          <div className="bg-gray-50 px-4 py-2 border-b">
            <h4 className="font-medium text-gray-900">
              Blanks Configuration ({blanks.length} detected)
            </h4>
          </div>
          <div className="divide-y">
            {blanks.map((blank) => (
              <div key={blank.blank_id} className="p-4 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-primary-600">{blank.blank_id}</span>
                  <div className="flex items-center gap-4">
                    <label className="flex items-center gap-2 text-sm">
                      Max words:
                      <select
                        value={blank.max_words}
                        onChange={(e) => updateBlankConfig(blank.blank_id, 'max_words', parseInt(e.target.value))}
                        className="border rounded px-2 py-1"
                      >
                        {[1, 2, 3, 4, 5].map(n => (
                          <option key={n} value={n}>{n}</option>
                        ))}
                      </select>
                    </label>
                    <label className="flex items-center gap-2 text-sm">
                      <input
                        type="checkbox"
                        checked={blank.case_sensitive}
                        onChange={(e) => updateBlankConfig(blank.blank_id, 'case_sensitive', e.target.checked)}
                        className="rounded"
                      />
                      Case sensitive
                    </label>
                  </div>
                </div>
                
                {/* Answers for this blank */}
                <div>
                  <label className="block text-sm text-gray-600 mb-1">
                    Correct answers (first is primary, add alternatives below)
                  </label>
                  <AnswerInput
                    answers={answers[blank.blank_id] || []}
                    onChange={(ans) => updateAnswer(blank.blank_id, ans)}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Live Preview */}
      <div className="border rounded-lg overflow-hidden">
        <div className="bg-blue-50 px-4 py-2 border-b border-blue-100">
          <h4 className="font-medium text-blue-900">Student Preview</h4>
        </div>
        <div className="p-4 bg-white">
          {renderPreview()}
        </div>
      </div>
    </div>
  );
}

// Sub-component for managing multiple answers per blank
function AnswerInput({ answers, onChange }) {
  const [inputValue, setInputValue] = useState('');

  const handleAddAnswer = () => {
    if (inputValue.trim()) {
      onChange([...answers, inputValue.trim()]);
      setInputValue('');
    }
  };

  const handleRemoveAnswer = (index) => {
    onChange(answers.filter((_, i) => i !== index));
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAddAnswer();
    }
  };

  return (
    <div className="space-y-2">
      {/* Existing answers */}
      <div className="flex flex-wrap gap-2">
        {answers.map((answer, idx) => (
          <span
            key={idx}
            className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm ${
              idx === 0 
                ? 'bg-green-100 text-green-800 border border-green-200' 
                : 'bg-gray-100 text-gray-700 border border-gray-200'
            }`}
          >
            {idx === 0 && <span className="text-xs font-medium">(Primary)</span>}
            {answer}
            <button
              type="button"
              onClick={() => handleRemoveAnswer(idx)}
              className="ml-1 text-gray-400 hover:text-red-500"
            >
              ×
            </button>
          </span>
        ))}
      </div>
      
      {/* Add new answer */}
      <div className="flex gap-2">
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={answers.length === 0 ? "Enter primary answer..." : "Add alternative answer..."}
          className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm"
        />
        <button
          type="button"
          onClick={handleAddAnswer}
          disabled={!inputValue.trim()}
          className="px-4 py-2 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Add
        </button>
      </div>
    </div>
  );
}
