import { useState, useEffect } from 'react';

/**
 * MatchingEditor - Editor for matching-type questions
 * (Matching Headings, Sentence Endings, Paragraphs, Names, Features, Information)
 * 
 * Features:
 * - Two-column layout: Items (numbered) and Options (lettered)
 * - Add/remove items and options
 * - Correct mapping selection per item
 * - Option reuse toggle
 */
export default function MatchingEditor({ value, onChange }) {
  const [items, setItems] = useState(value?.items || [
    { item_number: 1, item_text: '' }
  ]);
  const [options, setOptions] = useState(value?.options || [
    { option_label: 'A', option_text: '' },
    { option_label: 'B', option_text: '' },
    { option_label: 'C', option_text: '' }
  ]);
  const [mappings, setMappings] = useState(value?.mappings || {});
  const [allowReuse, setAllowReuse] = useState(value?.allow_option_reuse || false);

  // Generate next letter label
  const getNextLabel = () => {
    if (options.length === 0) return 'A';
    const lastLabel = options[options.length - 1].option_label;
    return String.fromCharCode(lastLabel.charCodeAt(0) + 1);
  };

  // Notify parent of changes
  useEffect(() => {
    onChange?.({
      type_specific_data: {
        items: items,
        options: options,
        allow_option_reuse: allowReuse
      },
      answer_data: {
        mappings: mappings
      }
    });
  }, [items, options, mappings, allowReuse]);

  const addItem = () => {
    setItems([...items, { 
      item_number: items.length + 1, 
      item_text: '' 
    }]);
  };

  const removeItem = (index) => {
    const newItems = items.filter((_, i) => i !== index)
      .map((item, i) => ({ ...item, item_number: i + 1 }));
    setItems(newItems);
    
    // Clean up mappings
    const newMappings = { ...mappings };
    delete newMappings[String(items[index].item_number)];
    setMappings(newMappings);
  };

  const updateItem = (index, text) => {
    setItems(items.map((item, i) => 
      i === index ? { ...item, item_text: text } : item
    ));
  };

  const addOption = () => {
    setOptions([...options, { 
      option_label: getNextLabel(), 
      option_text: '' 
    }]);
  };

  const removeOption = (index) => {
    const removedLabel = options[index].option_label;
    const newOptions = options.filter((_, i) => i !== index);
    setOptions(newOptions);
    
    // Remove mappings that used this option
    const newMappings = {};
    Object.entries(mappings).forEach(([key, value]) => {
      if (value !== removedLabel) {
        newMappings[key] = value;
      }
    });
    setMappings(newMappings);
  };

  const updateOption = (index, text) => {
    setOptions(options.map((opt, i) => 
      i === index ? { ...opt, option_text: text } : opt
    ));
  };

  const updateMapping = (itemNumber, optionLabel) => {
    setMappings({ ...mappings, [String(itemNumber)]: optionLabel });
  };

  // Track which options are used (for visual feedback)
  const usedOptions = new Set(Object.values(mappings));

  return (
    <div className="space-y-6">
      {/* Settings */}
      <div className="flex items-center gap-4 p-3 bg-gray-50 rounded-lg">
        <label className="flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={allowReuse}
            onChange={(e) => setAllowReuse(e.target.checked)}
            className="rounded"
          />
          Allow options to be used multiple times
        </label>
        {!allowReuse && options.length < items.length && (
          <span className="text-amber-600 text-sm">
            ⚠️ Need at least {items.length} options for {items.length} items
          </span>
        )}
      </div>

      {/* Two Column Layout */}
      <div className="grid grid-cols-2 gap-6">
        {/* Items Column */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h4 className="font-medium text-gray-900">Items</h4>
            <button
              type="button"
              onClick={addItem}
              className="text-sm text-primary-600 hover:text-primary-700 font-medium"
            >
              + Add Item
            </button>
          </div>
          
          <div className="space-y-2">
            {items.map((item, idx) => (
              <div key={idx} className="flex items-start gap-2 p-3 bg-gray-50 rounded-lg">
                <span className="font-bold text-gray-700 w-6 pt-2">{item.item_number}.</span>
                <div className="flex-1 space-y-2">
                  <input
                    type="text"
                    value={item.item_text}
                    onChange={(e) => updateItem(idx, e.target.value)}
                    placeholder="Enter item text..."
                    className="w-full border border-gray-300 rounded px-3 py-2 text-sm"
                  />
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-gray-500">Maps to:</span>
                    <select
                      value={mappings[String(item.item_number)] || ''}
                      onChange={(e) => updateMapping(item.item_number, e.target.value)}
                      className={`border rounded px-2 py-1 text-sm ${
                        mappings[String(item.item_number)] 
                          ? 'border-green-500 bg-green-50' 
                          : 'border-gray-300'
                      }`}
                    >
                      <option value="">Select answer...</option>
                      {options.map(opt => (
                        <option 
                          key={opt.option_label} 
                          value={opt.option_label}
                          disabled={!allowReuse && usedOptions.has(opt.option_label) && mappings[String(item.item_number)] !== opt.option_label}
                        >
                          {opt.option_label}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => removeItem(idx)}
                  className="text-gray-400 hover:text-red-500 pt-2"
                  disabled={items.length <= 1}
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Options Column */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h4 className="font-medium text-gray-900">Options</h4>
            <button
              type="button"
              onClick={addOption}
              className="text-sm text-primary-600 hover:text-primary-700 font-medium"
            >
              + Add Option
            </button>
          </div>
          
          <div className="space-y-2">
            {options.map((opt, idx) => (
              <div 
                key={idx} 
                className={`flex items-center gap-2 p-3 rounded-lg border ${
                  usedOptions.has(opt.option_label) 
                    ? 'bg-green-50 border-green-200' 
                    : 'bg-gray-50 border-transparent'
                }`}
              >
                <span className="font-bold text-gray-700 w-6">{opt.option_label}</span>
                <input
                  type="text"
                  value={opt.option_text}
                  onChange={(e) => updateOption(idx, e.target.value)}
                  placeholder="Enter option text..."
                  className="flex-1 border border-gray-300 rounded px-3 py-2 text-sm"
                />
                <button
                  type="button"
                  onClick={() => removeOption(idx)}
                  className="text-gray-400 hover:text-red-500"
                  disabled={options.length <= 2}
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Summary */}
      <div className="p-3 bg-blue-50 rounded-lg text-sm text-blue-800">
        <strong>Summary:</strong> {items.length} items to match with {options.length} options. 
        {' '}
        {Object.keys(mappings).length} of {items.length} items have answers assigned.
      </div>
    </div>
  );
}
