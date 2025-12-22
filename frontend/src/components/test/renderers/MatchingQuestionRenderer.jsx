export default function MatchingQuestionRenderer({ question, answer, onAnswerChange }) {
  const { items, options, allow_option_reuse } = question.type_specific_data || {};
  
  // answer is expected to be: { [itemNumber]: optionLabel }

  const handleSelectChange = (itemNumber, optionLabel) => {
    const newAnswer = { ...answer, [itemNumber]: optionLabel };
    onAnswerChange(newAnswer);
  };

  // Track used options to disable them if reuse is not allowed
  const usedOptions = new Set(Object.values(answer || {}));

  if (!items || !options) return <div>Invalid question format</div>;

  return (
    <div className="grid md:grid-cols-2 gap-8">
      {/* Items List */}
      <div className="space-y-4">
        <h4 className="font-semibold text-gray-900 border-b pb-2">Questions</h4>
        <div className="space-y-3">
          {items.map((item) => (
            <div key={item.item_number} className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg border border-gray-100">
              <span className="font-bold text-gray-700 pt-2">{item.item_number}.</span>
              <div className="flex-1 space-y-2">
                <p className="text-gray-800">{item.item_text}</p>
                <div className="flex items-center gap-2">
                  <span className="text-sm text-gray-500">Select answer:</span>
                  <select
                    value={answer?.[item.item_number] || ''}
                    onChange={(e) => handleSelectChange(item.item_number, e.target.value)}
                    className={`border rounded px-3 py-1.5 text-sm font-medium ${
                      answer?.[item.item_number] 
                        ? 'border-primary-500 bg-primary-50 text-primary-700' 
                        : 'border-gray-300'
                    }`}
                  >
                    <option value="">Choose...</option>
                    {options.map((opt) => {
                      const isSelectedHere = answer?.[item.item_number] === opt.option_label;
                      const isUsedElsewhere = usedOptions.has(opt.option_label) && !isSelectedHere;
                      const isDisabled = !allow_option_reuse && isUsedElsewhere;

                      return (
                        <option 
                          key={opt.option_label} 
                          value={opt.option_label}
                          disabled={isDisabled}
                        >
                          {opt.option_label}
                        </option>
                      );
                    })}
                  </select>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Options List */}
      <div className="space-y-4">
        <h4 className="font-semibold text-gray-900 border-b pb-2">Options</h4>
        <div className="space-y-2">
          {options.map((opt) => {
            const isUsed = usedOptions.has(opt.option_label);
            return (
              <div 
                key={opt.option_label} 
                className={`flex items-start gap-3 p-3 rounded-lg border ${
                  isUsed 
                    ? 'bg-gray-100 border-gray-200 opacity-75' 
                    : 'bg-white border-gray-200 shadow-sm'
                }`}
              >
                <span className={`font-bold px-2 py-0.5 rounded text-sm ${
                  isUsed ? 'bg-gray-200 text-gray-600' : 'bg-primary-100 text-primary-700'
                }`}>
                  {opt.option_label}
                </span>
                <p className="text-gray-800 text-sm">{opt.option_text}</p>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
