import { useMemo } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkBreaks from 'remark-breaks';

export default function TableQuestionRenderer({ question, answer, onAnswerChange }) {
  const { table_structure, blanks } = question.type_specific_data || {};
  
  // table_structure: {
  //   headers: ["Column 1", "Column 2"],
  //   rows: [
  //     ["Cell 1", "[BLANK_1]"],
  //     ["[BLANK_2]", "Cell 4"]
  //   ]
  // }

  const handleInputChange = (blankId, value) => {
    const newAnswer = { ...answer, [blankId]: value };
    onAnswerChange(newAnswer);
  };

  const renderCellContent = (content) => {
    if (!content) return null;

    // Split by BLANK markers to handle mixed content (text + blanks)
    const parts = content.split(/(\[BLANK_\d+\])/g);
    
    // If no blanks found, just return the text
    if (parts.length === 1) {
      return (
        <ReactMarkdown 
          remarkPlugins={[remarkGfm, remarkBreaks]} 
          components={{ p: 'span' }}
        >
          {content}
        </ReactMarkdown>
      );
    }

    return (
      <>
        {parts.map((part, idx) => {
          const match = part.match(/\[BLANK_(\d+)\]/);
          if (match) {
            const blankId = `BLANK_${match[1]}`;
            const config = blanks?.find(b => b.blank_id === blankId);
            const currentValue = answer?.[blankId] || '';

            return (
              <input
                key={idx}
                type="text"
                value={currentValue}
                onChange={(e) => handleInputChange(blankId, e.target.value)}
                className="inline-block border border-gray-300 rounded px-2 py-1 text-sm focus:ring-2 focus:ring-primary-500 focus:border-transparent min-w-[100px]"
                placeholder={`(${config?.max_words || 3} words)`}
                aria-label={`Blank ${match[1]}`}
              />
            );
          }
          return (
            <span key={idx}>
              <ReactMarkdown 
                remarkPlugins={[remarkGfm, remarkBreaks]} 
                components={{ p: 'span' }}
              >
                {part}
              </ReactMarkdown>
            </span>
          );
        })}
      </>
    );
  };

  if (!table_structure) return <div>Invalid question format</div>;

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200 border border-gray-200">
        {table_structure.headers && table_structure.headers.length > 0 && (
          <thead className="bg-gray-50">
            <tr>
              {table_structure.headers.map((header, idx) => (
                <th 
                  key={idx}
                  scope="col"
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider border-b border-gray-200"
                >
                  <ReactMarkdown 
                    remarkPlugins={[remarkGfm, remarkBreaks]} 
                    components={{ p: 'span' }}
                  >
                    {header}
                  </ReactMarkdown>
                </th>
              ))}
            </tr>
          </thead>
        )}
        <tbody className="bg-white divide-y divide-gray-200">
          {table_structure.rows?.map((row, rowIdx) => (
            <tr key={rowIdx} className={rowIdx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
              {row.map((cell, cellIdx) => (
                <td 
                  key={cellIdx} 
                  className="px-6 py-4 whitespace-normal text-sm text-gray-900 border-r last:border-r-0 border-gray-200"
                >
                  {renderCellContent(cell)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
