import { useMemo } from 'react';

export default function ShortAnswerQuestionRenderer({ question, answer, onAnswerChange }) {
  const maxWords = question.type_specific_data?.max_words || 3;
  const value = answer || '';
  
  const wordCount = useMemo(() => {
    return value.trim().split(/\s+/).filter(w => w).length;
  }, [value]);
  
  const isOverLimit = wordCount > maxWords;

  return (
    <div className="space-y-2">
      <input
        type="text"
        value={value}
        onChange={(e) => onAnswerChange(e.target.value)}
        placeholder={`Type your answer (max ${maxWords} words)`}
        className={`w-full border rounded-lg px-4 py-3 text-lg ${
          isOverLimit 
            ? 'border-red-500 bg-red-50' 
            : 'border-gray-300 focus:ring-2 focus:ring-primary-500 focus:border-transparent'
        }`}
        aria-label="Short answer input"
      />
      <div className={`text-sm ${isOverLimit ? 'text-red-600 font-medium' : 'text-gray-500'}`}>
        {wordCount} / {maxWords} words
        {isOverLimit && ' - Over limit!'}
      </div>
    </div>
  );
}
