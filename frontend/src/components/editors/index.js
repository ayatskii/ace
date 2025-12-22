// Export all specialized question editors
export { default as CompletionEditor } from './CompletionEditor';
export { default as MatchingEditor } from './MatchingEditor';
export { default as DiagramEditor } from './DiagramEditor';
export { default as TFNGEditor } from './TFNGEditor';
export { default as TableEditor } from './TableEditor';

/**
 * Helper to get the appropriate editor for a question type
 */
export function getEditorForType(questionType) {
  if (!questionType) return null;
  
  const type = questionType.toLowerCase();
  
  // Completion family
  if (type.includes('completion') || type.includes('fill_in')) {
    if (type.includes('table')) {
      return 'TableEditor';
    }
    return 'CompletionEditor';
  }
  
  // Matching family
  if (type.includes('matching') || type.includes('name_matching')) {
    return 'MatchingEditor';
  }
  
  // Diagram/Map family
  if (type.includes('diagram') || type.includes('map') || type.includes('flowchart')) {
    return 'DiagramEditor';
  }
  
  // TFNG family
  if (type.includes('true_false') || type.includes('yes_no') || type.includes('not_given')) {
    return 'TFNGEditor';
  }
  
  // MCQ and Short Answer use simpler forms (handled in parent)
  return null;
}

/**
 * Question type categories for display
 */
export const QUESTION_TYPE_CATEGORIES = {
  listening: {
    completion: [
      { value: 'listening_form_completion', label: 'Form Completion' },
      { value: 'listening_note_completion', label: 'Note Completion' },
      { value: 'listening_table_completion', label: 'Table Completion' },
      { value: 'listening_summary_completion', label: 'Summary Completion' },
      { value: 'listening_sentence_completion', label: 'Sentence Completion' }
    ],
    matching: [
      { value: 'listening_matching_headings', label: 'Matching Headings' },
      { value: 'listening_matching_sentence_endings', label: 'Matching Sentence Endings' },
      { value: 'listening_matching_paragraphs', label: 'Matching Paragraphs' },
      { value: 'listening_name_matching', label: 'Name Matching' }
    ],
    choice: [
      { value: 'listening_multiple_choice', label: 'Multiple Choice' },
      { value: 'listening_short_answer', label: 'Short Answer' }
    ],
    diagram: [
      { value: 'listening_diagram_labeling', label: 'Diagram Labeling' },
      { value: 'listening_map_labeling', label: 'Map Labeling' }
    ]
  },
  reading: {
    completion: [
      { value: 'reading_form_completion', label: 'Form Completion' },
      { value: 'reading_table_completion', label: 'Table Completion' },
      { value: 'reading_note_completion', label: 'Note Completion' },
      { value: 'reading_sentence_completion', label: 'Sentence Completion' },
      { value: 'reading_summary_completion', label: 'Summary Completion' }
    ],
    matching: [
      { value: 'reading_matching_headings', label: 'Matching Headings' },
      { value: 'reading_matching_information', label: 'Matching Information' },
      { value: 'reading_matching_features', label: 'Matching Features' },
      { value: 'reading_matching_sentence_endings', label: 'Matching Sentence Endings' }
    ],
    choice: [
      { value: 'reading_multiple_choice', label: 'Multiple Choice' },
      { value: 'reading_short_answer', label: 'Short Answer' }
    ],
    diagram: [
      { value: 'reading_diagram_labeling', label: 'Diagram Labeling' },
      { value: 'reading_flowchart', label: 'Flowchart' }
    ],
    tfng: [
      { value: 'reading_true_false_not_given', label: 'True/False/Not Given' },
      { value: 'reading_yes_no_not_given', label: 'Yes/No/Not Given' }
    ]
  }
};
