export default function MCQQuestionRenderer({ question, answer, onAnswerChange }) {
  const { allow_multiple } = question.type_specific_data || {};
  const options = question.type_specific_data?.options || question.options;
  
  // answer structure:
  // Single select: "A" (string)
  // Multi select: ["A", "C"] (array of strings)

  const handleOptionChange = (optionLabel) => {
    if (allow_multiple) {
      // Multi-select logic
      let currentSelected = [];
      if (Array.isArray(answer)) {
        currentSelected = [...answer];
      } else if (typeof answer === 'string' && answer) {
        currentSelected = [answer];
      } else if (typeof answer === 'object' && answer?.selected) {
         // Handle legacy object format if present
         currentSelected = answer.selected;
      }

      const isSelected = currentSelected.includes(optionLabel);
      let newSelected;
      
      if (isSelected) {
        newSelected = currentSelected.filter(l => l !== optionLabel);
      } else {
        newSelected = [...currentSelected, optionLabel];
      }
      
      // Sort for consistency
      newSelected.sort();
      onAnswerChange(newSelected);
    } else {
      // Single-select logic
      onAnswerChange(optionLabel);
    }
  };

  const isOptionSelected = (optionLabel) => {
    if (allow_multiple) {
      if (Array.isArray(answer)) {
        return answer.includes(optionLabel);
      }
      // Handle legacy formats
      if (typeof answer === 'string') return answer === optionLabel;
      if (typeof answer === 'object' && answer?.selected) return answer.selected.includes(optionLabel);
      return false;
    } else {
      return answer === optionLabel;
    }
  };

  if (!options) return <div>Invalid question format</div>;

  return (
    <div className="space-y-3">
      {options.map((opt, idx) => {
        const isSelected = isOptionSelected(opt.option_label);
        return (
          <label 
            key={idx} 
            className={`flex items-start space-x-3 p-3 border rounded-lg cursor-pointer transition-colors ${
              isSelected 
                ? 'bg-primary-50 border-primary-500' 
                : 'hover:bg-gray-50 border-gray-200'
            }`}
          >
            <div className="flex-shrink-0 mt-0.5">
              <input
                type={allow_multiple ? "checkbox" : "radio"}
                name={`q-${question.id}`}
                className={`h-5 w-5 text-primary-600 focus:ring-primary-500 border-gray-300 ${
                  allow_multiple ? 'rounded' : 'rounded-full'
                }`}
                onChange={() => handleOptionChange(opt.option_label)}
                checked={isSelected}
              />
            </div>
            <div className="flex-1">
              <span className="font-bold text-gray-900 mr-2">{opt.option_label}</span>
              <span className="text-gray-800">{opt.option_text}</span>
            </div>
          </label>
        );
      })}
      {allow_multiple && (
        <p className="text-sm text-gray-500 italic mt-2">
          Select all that apply
        </p>
      )}
    </div>
  );
}
