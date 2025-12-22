export default function TFNGQuestionRenderer({ question, answer, onAnswerChange }) {
  const { statements, answer_type } = question.type_specific_data || {};
  
  // answer is expected to be: { [statementNumber]: "TRUE" | "FALSE" | "NOT GIVEN" }

  const handleOptionChange = (statementNumber, value) => {
    const newAnswer = { ...answer, [statementNumber]: value };
    onAnswerChange(newAnswer);
  };

  const options = answer_type === 'yes_no_not_given' 
    ? ['YES', 'NO', 'NOT GIVEN']
    : ['TRUE', 'FALSE', 'NOT GIVEN'];

  if (!statements) return <div>Invalid question format</div>;

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-[1fr,auto] gap-4 items-end border-b pb-2 mb-4">
        <h4 className="font-semibold text-gray-900">Statements</h4>
        <div className="flex gap-8 px-4 text-sm font-bold text-gray-500">
          {options.map(opt => (
            <span key={opt} className="w-16 text-center">{opt}</span>
          ))}
        </div>
      </div>

      <div className="space-y-4">
        {statements.map((stmt) => (
          <div key={stmt.statement_number} className="grid grid-cols-[1fr,auto] gap-4 items-center p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
            <div className="flex items-start gap-3">
              <span className="font-bold text-gray-700 pt-0.5">{stmt.statement_number}.</span>
              <p className="text-gray-800 leading-relaxed">{stmt.statement_text}</p>
            </div>
            
            <div className="flex gap-8 px-4">
              {options.map((opt) => (
                <label key={opt} className="w-16 flex justify-center cursor-pointer">
                  <input
                    type="radio"
                    name={`q-${question.id}-s-${stmt.statement_number}`}
                    value={opt}
                    checked={answer?.[stmt.statement_number] === opt}
                    onChange={() => handleOptionChange(stmt.statement_number, opt)}
                    className="w-5 h-5 text-primary-600 border-gray-300 focus:ring-primary-500 cursor-pointer"
                  />
                </label>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
