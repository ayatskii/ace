import { useState, useEffect } from 'react';

export default function TableEditor({ value, onChange }) {
  const [headers, setHeaders] = useState(value?.table_structure?.headers || ['Column 1', 'Column 2']);
  const [rows, setRows] = useState(value?.table_structure?.rows || [['', '']]);
  const [blanks, setBlanks] = useState(value?.blanks || []);
  const [answers, setAnswers] = useState(value?.answers || {});

  // Update parent when local state changes
  useEffect(() => {
    onChange?.({
      type_specific_data: {
        table_structure: {
          headers,
          rows
        },
        blanks
      },
      answer_data: {
        blanks: answers
      }
    });
  }, [headers, rows, blanks, answers]);

  // Auto-detect blanks in table cells
  useEffect(() => {
    const detectedBlanks = [];
    const seenIds = new Set();
    
    rows.forEach(row => {
      row.forEach(cell => {
        const matches = [...cell.matchAll(/\[BLANK_(\d+)\]/g)];
        matches.forEach(match => {
          const blankId = `BLANK_${match[1]}`;
          if (!seenIds.has(blankId)) {
            seenIds.add(blankId);
            const existing = blanks.find(b => b.blank_id === blankId);
            detectedBlanks.push(existing || {
              blank_id: blankId,
              max_words: 3,
              case_sensitive: false
            });
          }
        });
      });
    });
    
    // Only update if different to avoid infinite loops
    if (JSON.stringify(detectedBlanks) !== JSON.stringify(blanks)) {
      setBlanks(detectedBlanks);
    }
  }, [rows]);

  const addColumn = () => {
    setHeaders([...headers, `Column ${headers.length + 1}`]);
    setRows(rows.map(row => [...row, '']));
  };

  const removeColumn = (idx) => {
    if (headers.length <= 1) return;
    setHeaders(headers.filter((_, i) => i !== idx));
    setRows(rows.map(row => row.filter((_, i) => i !== idx)));
  };

  const addRow = () => {
    setRows([...rows, new Array(headers.length).fill('')]);
  };

  const removeRow = (idx) => {
    if (rows.length <= 1) return;
    setRows(rows.filter((_, i) => i !== idx));
  };

  const updateHeader = (idx, val) => {
    const newHeaders = [...headers];
    newHeaders[idx] = val;
    setHeaders(newHeaders);
  };

  const updateCell = (rowIdx, colIdx, val) => {
    const newRows = [...rows];
    newRows[rowIdx][colIdx] = val;
    setRows(newRows);
  };

  const updateBlankConfig = (blankId, field, value) => {
    setBlanks(blanks.map(b => 
      b.blank_id === blankId ? { ...b, [field]: value } : b
    ));
  };

  const updateAnswer = (blankId, answerList) => {
    setAnswers({ ...answers, [blankId]: answerList });
  };

  return (
    <div className="space-y-6">
      {/* Table Structure Editor */}
      <div className="border rounded-lg overflow-hidden">
        <div className="bg-gray-50 px-4 py-2 border-b flex justify-between items-center">
          <h4 className="font-medium text-gray-900">Table Structure</h4>
          <div className="space-x-2">
            <button onClick={addColumn} className="text-sm text-primary-600 hover:text-primary-700 font-medium">+ Add Column</button>
            <button onClick={addRow} className="text-sm text-primary-600 hover:text-primary-700 font-medium">+ Add Row</button>
          </div>
        </div>
        
        <div className="p-4 overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead>
              <tr>
                {headers.map((header, idx) => (
                  <th key={idx} className="px-2 py-2">
                    <div className="flex items-center gap-1">
                      <input
                        type="text"
                        value={header}
                        onChange={(e) => updateHeader(idx, e.target.value)}
                        className="w-full border-gray-300 rounded text-sm font-bold"
                        placeholder="Header"
                      />
                      <button onClick={() => removeColumn(idx)} className="text-red-400 hover:text-red-600">×</button>
                    </div>
                  </th>
                ))}
                <th className="w-10"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {rows.map((row, rowIdx) => (
                <tr key={rowIdx}>
                  {row.map((cell, colIdx) => (
                    <td key={colIdx} className="px-2 py-2">
                      <textarea
                        value={cell}
                        onChange={(e) => updateCell(rowIdx, colIdx, e.target.value)}
                        className="w-full border-gray-300 rounded text-sm"
                        rows={2}
                        placeholder="Content or [BLANK_1]"
                      />
                    </td>
                  ))}
                  <td className="px-2 text-center">
                    <button onClick={() => removeRow(rowIdx)} className="text-red-400 hover:text-red-600">×</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Blanks Configuration */}
      {blanks.length > 0 && (
        <div className="border rounded-lg overflow-hidden">
          <div className="bg-gray-50 px-4 py-2 border-b">
            <h4 className="font-medium text-gray-900">Blanks Configuration</h4>
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
                
                <AnswerInput
                  answers={answers[blank.blank_id] || []}
                  onChange={(ans) => updateAnswer(blank.blank_id, ans)}
                />
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

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
      <div className="flex flex-wrap gap-2">
        {answers.map((answer, idx) => (
          <span key={idx} className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm bg-gray-100 text-gray-700 border border-gray-200">
            {answer}
            <button type="button" onClick={() => handleRemoveAnswer(idx)} className="ml-1 text-gray-400 hover:text-red-500">×</button>
          </span>
        ))}
      </div>
      <div className="flex gap-2">
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Add answer..."
          className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm"
        />
        <button
          type="button"
          onClick={handleAddAnswer}
          disabled={!inputValue.trim()}
          className="px-4 py-2 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700 disabled:opacity-50"
        >
          Add
        </button>
      </div>
    </div>
  );
}
