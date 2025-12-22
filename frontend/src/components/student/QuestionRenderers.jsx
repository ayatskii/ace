/**
 * Question Renderers - Type-specific components for rendering questions during tests
 * These are the student-facing question views
 */

/**
 * Helper to parse template text and create input elements for blanks
 */
export function renderCompletionTemplate(template, blanks, answers, onChange)  {
  if (!template) return null;
  
  const parts = template.split(/(\[BLANK_\d+\])/g);
  
  return (
    <div className="prose max-w-none text-gray-800 leading-relaxed">
      {parts.map((part, idx) => {
        const match = part.match(/\[BLANK_(\d+)\]/);
        if (match) {
          const blankId = `BLANK_${match[1]}`;
          const blankConfig = blanks?.find(b => b.blank_id === blankId) || {};
          const value = answers?.[blankId] || '';
          
          return (
            <span key={idx} className="inline-block mx-1 align-middle">
              <input
                type="text"
                value={value}
                onChange={(e) => onChange(blankId, e.target.value)}
                placeholder={`(${blankConfig.max_words || 3} words)`}
                className="border-b-2 border-primary-400 focus:border-primary-600 bg-primary-50 w-28 sm:w-36 text-center px-2 py-1 outline-none transition-colors"
              />
            </span>
          );
        }
        return <span key={idx}>{part}</span>;
      })}
    </div>
  );
}

/**
 * Render matching question with dropdowns
 */
export function MatchingQuestionRenderer({ 
  items, 
  options, 
  answers, 
  onChange,
  allowReuse = false
}) {
  const usedOptions = new Set(Object.values(answers || {}));
  
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Items with dropdowns */}
      <div className="space-y-3">
        <h4 className="font-medium text-gray-700 text-sm uppercase tracking-wide">Questions</h4>
        {items?.map((item) => (
          <div 
            key={item.item_number} 
            className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg"
          >
            <span className="font-bold text-primary-600 w-6">{item.item_number}.</span>
            <div className="flex-1">
              <p className="text-gray-800 mb-2">{item.item_text}</p>
              <select
                value={answers?.[String(item.item_number)] || ''}
                onChange={(e) => onChange(String(item.item_number), e.target.value)}
                className={`w-full border rounded-lg px-3 py-2 ${
                  answers?.[String(item.item_number)]
                    ? 'border-green-500 bg-green-50'
                    : 'border-gray-300'
                }`}
              >
                <option value="">-- Select an answer --</option>
                {options?.map((opt) => (
                  <option 
                    key={opt.option_label} 
                    value={opt.option_label}
                    disabled={!allowReuse && usedOptions.has(opt.option_label) && answers?.[String(item.item_number)] !== opt.option_label}
                  >
                    {opt.option_label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        ))}
      </div>

      {/* Options reference */}
      <div className="bg-blue-50 rounded-lg p-4 h-fit lg:sticky lg:top-4">
        <h4 className="font-medium text-blue-900 mb-3 text-sm uppercase tracking-wide">Options</h4>
        <div className="space-y-2">
          {options?.map((opt) => (
            <div 
              key={opt.option_label} 
              className={`flex gap-2 p-2 rounded ${
                usedOptions.has(opt.option_label) ? 'bg-blue-100 opacity-60' : ''
              }`}
            >
              <span className="font-bold text-blue-700">{opt.option_label}</span>
              <span className="text-blue-900">{opt.option_text}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

/**
 * Render True/False/Not Given question
 */
export function TFNGQuestionRenderer({ 
  statements, 
  answerType,
  answers, 
  onChange 
}) {
  const options = answerType === 'yes_no_not_given'
    ? ['YES', 'NO', 'NOT GIVEN']
    : ['TRUE', 'FALSE', 'NOT GIVEN'];

  return (
    <div className="space-y-4">
      {statements?.map((stmt) => (
        <div key={stmt.statement_number} className="p-4 bg-gray-50 rounded-lg">
          <p className="text-gray-800 mb-3">
            <span className="font-bold text-primary-600 mr-2">{stmt.statement_number}.</span>
            {stmt.statement_text}
          </p>
          <div className="flex flex-wrap gap-2">
            {options.map((opt) => (
              <button
                key={opt}
                type="button"
                onClick={() => onChange(String(stmt.statement_number), opt)}
                className={`px-4 py-2 rounded-full font-medium transition-all ${
                  answers?.[String(stmt.statement_number)] === opt
                    ? 'bg-primary-600 text-white shadow-md scale-105'
                    : 'bg-white border border-gray-300 text-gray-700 hover:border-primary-400 hover:bg-primary-50'
                }`}
              >
                {opt}
              </button>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

/**
 * Render Diagram/Map labeling question
 */
export function DiagramQuestionRenderer({ 
  imageUrl, 
  labels, 
  answers, 
  onChange,
  maxWords = 2
}) {
  return (
    <div className="space-y-6">
      {/* Image with labels */}
      <div className="relative inline-block border rounded-lg overflow-hidden">
        <img 
          src={imageUrl} 
          alt="Diagram" 
          className="max-w-full"
          style={{ maxHeight: '400px' }}
        />
        {labels?.map((label) => (
          <div
            key={label.label_id}
            className="absolute w-7 h-7 bg-red-500 rounded-full text-white text-sm font-bold flex items-center justify-center transform -translate-x-1/2 -translate-y-1/2 shadow-lg"
            style={{ left: `${label.x}%`, top: `${label.y}%` }}
          >
            {label.label_id}
          </div>
        ))}
      </div>

      {/* Answer inputs */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {labels?.map((label) => (
          <div key={label.label_id} className="flex items-center gap-3">
            <div className="w-8 h-8 bg-red-500 rounded-full text-white font-bold flex items-center justify-center flex-shrink-0">
              {label.label_id}
            </div>
            <input
              type="text"
              value={answers?.[label.label_id] || ''}
              onChange={(e) => onChange(label.label_id, e.target.value)}
              placeholder={`Answer (max ${maxWords} words)`}
              className="flex-1 border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
        ))}
      </div>
    </div>
  );
}

/**
 * Render Multiple Choice question
 */
export function MCQQuestionRenderer({ 
  options, 
  allowMultiple = false,
  selected, 
  onChange 
}) {
  const handleSelect = (optionLabel) => {
    if (allowMultiple) {
      const current = selected || [];
      if (current.includes(optionLabel)) {
        onChange(current.filter(s => s !== optionLabel));
      } else {
        onChange([...current, optionLabel]);
      }
    } else {
      onChange([optionLabel]);
    }
  };

  const isSelected = (optionLabel) => {
    return (selected || []).includes(optionLabel);
  };

  return (
    <div className="space-y-2">
      {allowMultiple && (
        <p className="text-sm text-gray-500 mb-3">Select all that apply</p>
      )}
      {options?.map((opt) => (
        <label 
          key={opt.option_label}
          className={`flex items-start gap-3 p-4 border rounded-lg cursor-pointer transition-all ${
            isSelected(opt.option_label)
              ? 'border-primary-500 bg-primary-50'
              : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
          }`}
        >
          <input
            type={allowMultiple ? 'checkbox' : 'radio'}
            name="mcq-answer"
            checked={isSelected(opt.option_label)}
            onChange={() => handleSelect(opt.option_label)}
            className="mt-1 h-4 w-4 text-primary-600"
          />
          <span className="font-bold text-gray-700">{opt.option_label}</span>
          <span className="text-gray-800">{opt.option_text}</span>
        </label>
      ))}
    </div>
  );
}

/**
 * Render Short Answer question
 */
export function ShortAnswerRenderer({ 
  maxWords = 3, 
  value, 
  onChange 
}) {
  const wordCount = value ? value.trim().split(/\s+/).filter(w => w).length : 0;
  const isOverLimit = wordCount > maxWords;

  return (
    <div className="space-y-2">
      <input
        type="text"
        value={value || ''}
        onChange={(e) => onChange(e.target.value)}
        placeholder={`Type your answer (max ${maxWords} words)`}
        className={`w-full border rounded-lg px-4 py-3 text-lg ${
          isOverLimit 
            ? 'border-red-500 bg-red-50' 
            : 'border-gray-300 focus:ring-2 focus:ring-primary-500'
        }`}
      />
      <div className={`text-sm ${isOverLimit ? 'text-red-600 font-medium' : 'text-gray-500'}`}>
        {wordCount} / {maxWords} words
        {isOverLimit && ' - Over limit!'}
      </div>
    </div>
  );
}
