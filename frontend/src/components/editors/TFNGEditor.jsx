import { useState, useEffect } from 'react';

/**
 * TFNGEditor - Editor for True/False/Not Given and Yes/No/Not Given questions
 * 
 * Features:
 * - Add/remove statements
 * - Select answer type (T/F/NG or Y/N/NG)
 * - Select correct answer per statement
 */
export default function TFNGEditor({ value, onChange, questionType }) {
  const [statements, setStatements] = useState(value?.statements || [
    { statement_number: 1, statement_text: '' }
  ]);
  const [answerType, setAnswerType] = useState(
    value?.answer_type || 
    (questionType?.includes('yes_no') ? 'yes_no_not_given' : 'true_false_not_given')
  );
  const [answers, setAnswers] = useState(value?.answers || {});

  // Get options based on answer type
  const getOptions = () => {
    if (answerType === 'yes_no_not_given') {
      return ['YES', 'NO', 'NOT GIVEN'];
    }
    return ['TRUE', 'FALSE', 'NOT GIVEN'];
  };

  // Notify parent of changes
  useEffect(() => {
    onChange?.({
      type_specific_data: {
        statements: statements,
        answer_type: answerType
      },
      answer_data: {
        answers: answers
      }
    });
  }, [statements, answerType, answers]);

  const addStatement = () => {
    setStatements([...statements, {
      statement_number: statements.length + 1,
      statement_text: ''
    }]);
  };

  const removeStatement = (index) => {
    const removedNum = statements[index].statement_number;
    const newStatements = statements.filter((_, i) => i !== index)
      .map((s, i) => ({ ...s, statement_number: i + 1 }));
    setStatements(newStatements);
    
    const newAnswers = { ...answers };
    delete newAnswers[String(removedNum)];
    setAnswers(newAnswers);
  };

  const updateStatement = (index, text) => {
    setStatements(statements.map((s, i) => 
      i === index ? { ...s, statement_text: text } : s
    ));
  };

  const updateAnswer = (statementNumber, value) => {
    setAnswers({ ...answers, [String(statementNumber)]: value });
  };

  const options = getOptions();

  return (
    <div className="space-y-6">
      {/* Answer Type Selection */}
      <div className="flex items-center gap-4 p-3 bg-gray-50 rounded-lg">
        <span className="text-sm font-medium text-gray-700">Answer Type:</span>
        <div className="flex gap-4">
          <label className="flex items-center gap-2">
            <input
              type="radio"
              name="answerType"
              value="true_false_not_given"
              checked={answerType === 'true_false_not_given'}
              onChange={(e) => setAnswerType(e.target.value)}
              className="text-primary-600"
            />
            <span className="text-sm">True / False / Not Given</span>
          </label>
          <label className="flex items-center gap-2">
            <input
              type="radio"
              name="answerType"
              value="yes_no_not_given"
              checked={answerType === 'yes_no_not_given'}
              onChange={(e) => setAnswerType(e.target.value)}
              className="text-primary-600"
            />
            <span className="text-sm">Yes / No / Not Given</span>
          </label>
        </div>
      </div>

      {/* Statements */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h4 className="font-medium text-gray-900">Statements</h4>
          <button
            type="button"
            onClick={addStatement}
            className="text-sm text-primary-600 hover:text-primary-700 font-medium"
          >
            + Add Statement
          </button>
        </div>

        <div className="space-y-3">
          {statements.map((stmt, idx) => (
            <div key={idx} className="p-4 bg-gray-50 rounded-lg space-y-3">
              <div className="flex items-start gap-3">
                <span className="font-bold text-gray-700 w-6 pt-2">
                  {stmt.statement_number}.
                </span>
                <textarea
                  value={stmt.statement_text}
                  onChange={(e) => updateStatement(idx, e.target.value)}
                  placeholder="Enter statement text..."
                  rows={2}
                  className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm"
                />
                <button
                  type="button"
                  onClick={() => removeStatement(idx)}
                  className="text-gray-400 hover:text-red-500 pt-2"
                  disabled={statements.length <= 1}
                >
                  ×
                </button>
              </div>
              
              {/* Answer Selection */}
              <div className="pl-9">
                <span className="text-xs text-gray-500 mr-2">Correct answer:</span>
                <div className="inline-flex gap-2">
                  {options.map((opt) => (
                    <button
                      key={opt}
                      type="button"
                      onClick={() => updateAnswer(stmt.statement_number, opt)}
                      className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                        answers[String(stmt.statement_number)] === opt
                          ? 'bg-green-600 text-white'
                          : 'bg-white border border-gray-300 text-gray-700 hover:border-primary-500'
                      }`}
                    >
                      {opt}
                    </button>
                  ))}
                </div>
                {!answers[String(stmt.statement_number)] && (
                  <span className="text-amber-600 text-xs ml-2">Select an answer</span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Summary */}
      <div className="p-3 bg-blue-50 rounded-lg text-sm text-blue-800">
        <strong>Summary:</strong> {statements.length} statements. 
        {' '}
        {Object.keys(answers).length} of {statements.length} have answers assigned.
      </div>
    </div>
  );
}
