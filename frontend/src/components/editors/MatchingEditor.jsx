import { useState, useEffect, useRef } from 'react';
import MarkdownEditor from '../common/MarkdownEditor';
import MatchingQuestionRenderer from '../test/renderers/MatchingQuestionRenderer';

/**
 * MatchingEditor - Editor for matching questions
 * (Headings, Information, Features, Sentence Endings)
 * 
 * Features:
 * - List of items (questions)
 * - List of options (answers)
 * - Configuration (allow reuse)
 */
export default function MatchingEditor({ value, onChange, questionType }) {
  const [items, setItems] = useState(value?.items || []);
  const [options, setOptions] = useState(value?.options || []);
  const [allowReuse, setAllowReuse] = useState(value?.allow_option_reuse || false);
  const [answers, setAnswers] = useState(value?.answers?.matching || {});

  // Track if we're doing a local update to prevent re-initialization loop
  const isLocalUpdate = useRef(false);

  // Re-initialize state when value changes from EXTERNAL source
  useEffect(() => {
    if (isLocalUpdate.current) {
      isLocalUpdate.current = false;
      return;
    }
    
    if (value?.items) setItems(value.items);
    if (value?.options) setOptions(value.options);
    if (value?.allow_option_reuse !== undefined) setAllowReuse(value.allow_option_reuse);
    if (value?.answers?.matching) setAnswers(value.answers.matching);
  }, [JSON.stringify(value?.items), JSON.stringify(value?.options), value?.allow_option_reuse, JSON.stringify(value?.answers?.matching)]);

  // Notify parent of changes
  useEffect(() => {
    isLocalUpdate.current = true;
    onChange?.({
      type_specific_data: {
        items,
        options,
        allow_option_reuse: allowReuse
      },
      answer_data: {
        matching: answers
      }
    });
  }, [items, options, allowReuse, answers]);

  const addItem = () => {
    setItems([...items, {
      item_number: items.length + 1,
      item_text: ''
    }]);
  };

  const removeItem = (idx) => {
    const newItems = items.filter((_, i) => i !== idx)
      .map((item, i) => ({ ...item, item_number: i + 1 }));
    setItems(newItems);
    
    // Clean up answers
    const newAnswers = { ...answers };
    delete newAnswers[String(items[idx].item_number)];
    setAnswers(newAnswers);
  };

  const updateItem = (idx, text) => {
    const newItems = [...items];
    newItems[idx].item_text = text;
    setItems(newItems);
  };

  const addOption = () => {
    const nextLabel = String.fromCharCode(65 + options.length);
    setOptions([...options, {
      option_label: nextLabel,
      option_text: ''
    }]);
  };

  const removeOption = (idx) => {
    const newOptions = options.filter((_, i) => i !== idx);
    // Re-label options
    const relabeled = newOptions.map((opt, i) => ({
      ...opt,
      option_label: String.fromCharCode(65 + i)
    }));
    setOptions(relabeled);
  };

  const updateOption = (idx, text) => {
    const newOptions = [...options];
    newOptions[idx].option_text = text;
    setOptions(newOptions);
  };

  const updateAnswer = (itemNumber, optionLabel) => {
    setAnswers({ ...answers, [String(itemNumber)]: optionLabel });
  };

  return (
    <div className="space-y-8">
      {/* Configuration */}
      <div className="flex items-center space-x-2">
        <input
          type="checkbox"
          checked={allowReuse}
          onChange={(e) => setAllowReuse(e.target.checked)}
          className="rounded text-primary-600"
        />
        <label className="text-sm font-medium text-gray-700">Allow options to be used more than once</label>
      </div>

      <div className="grid md:grid-cols-2 gap-8">
        {/* Items (Questions) Column */}
        <div className="space-y-4">
          <div className="flex justify-between items-center border-b pb-2">
            <h4 className="font-medium text-gray-900">Questions / Items</h4>
            <button type="button" onClick={addItem} className="text-sm text-primary-600 font-medium">+ Add Item</button>
          </div>
          
          <div className="space-y-4">
            {items.map((item, idx) => (
              <div key={idx} className="bg-gray-50 p-3 rounded-lg border border-gray-200">
                <div className="flex justify-between mb-2">
                  <span className="font-bold text-gray-700">{item.item_number}.</span>
                  <button type="button" onClick={() => removeItem(idx)} className="text-gray-400 hover:text-red-500">×</button>
                </div>
                <MarkdownEditor
                  value={item.item_text}
                  onChange={(e) => updateItem(idx, e.target.value)}
                  rows={2}
                  placeholder="Item text..."
                  label=""
                />
                
                {/* Answer Selection for Auto-grading */}
                <div className="mt-3 pt-3 border-t border-gray-200 flex items-center justify-between">
                  <span className="text-xs text-gray-500">Correct Answer:</span>
                  <select
                    value={answers[String(item.item_number)] || ''}
                    onChange={(e) => updateAnswer(item.item_number, e.target.value)}
                    className="text-sm border-gray-300 rounded-md"
                  >
                    <option value="">Select...</option>
                    {options.map(opt => (
                      <option key={opt.option_label} value={opt.option_label}>
                        {opt.option_label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Options (Answers) Column */}
        <div className="space-y-4">
          <div className="flex justify-between items-center border-b pb-2">
            <h4 className="font-medium text-gray-900">Options</h4>
            <button type="button" onClick={addOption} className="text-sm text-primary-600 font-medium">+ Add Option</button>
          </div>

          <div className="space-y-4">
            {options.map((opt, idx) => (
              <div key={idx} className="bg-white p-3 rounded-lg border border-gray-200 shadow-sm">
                <div className="flex items-center gap-2 mb-2">
                  <span className="font-bold bg-primary-100 text-primary-700 px-2 py-0.5 rounded text-sm">
                    {opt.option_label}
                  </span>
                  <div className="flex-1"></div>
                  <button type="button" onClick={() => removeOption(idx)} className="text-gray-400 hover:text-red-500">×</button>
                </div>
                <MarkdownEditor
                  value={opt.option_text}
                  onChange={(e) => updateOption(idx, e.target.value)}
                  rows={2}
                  placeholder="Option text..."
                  label=""
                />
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Student Preview */}
      <div className="border rounded-lg overflow-hidden mt-8">
        <div className="bg-blue-50 px-4 py-2 border-b border-blue-100">
          <h4 className="font-medium text-blue-900">Student Preview</h4>
        </div>
        <div className="p-4 bg-white">
          <MatchingQuestionRenderer 
            question={{
              type_specific_data: {
                items,
                options,
                allow_option_reuse: allowReuse
              }
            }}
            answer={answers}
            onAnswerChange={(newAnswers) => setAnswers(newAnswers)}
          />
        </div>
      </div>
    </div>
  );
}
