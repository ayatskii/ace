# Manual E2E Test Checklist

This document provides a checklist for manually testing all implemented IELTS question types.

## Prerequisites

1. Start backend: `cd backend && python -m uvicorn app.main:app --reload`
2. Start frontend: `cd frontend && npm run dev`
3. Run migration: `cd backend && alembic upgrade head`

## Test Cases

### 1. Admin - Question Creation

#### Completion Types

- [ ] Create Listening Sentence Completion with [BLANK_1], [BLANK_2]
- [ ] Verify blanks are auto-detected
- [ ] Set max words per blank (1, 2, 3)
- [ ] Add primary answer + 2 alternatives
- [ ] Check live preview shows input boxes
- [ ] Save and verify in database

#### Matching Types

- [ ] Create Reading Matching Headings
- [ ] Add 3 items and 5 options (A-E)
- [ ] Set correct mappings (1→B, 2→D, 3→A)
- [ ] Test "allow option reuse" toggle
- [ ] Verify options disable after selection (when reuse=false)

#### Diagram/Map Types

- [ ] Create Listening Map Labeling
- [ ] Upload image
- [ ] Click to add 3 label points
- [ ] Add answers for each label
- [ ] Verify coordinates saved correctly

#### True/False/Not Given

- [ ] Create Reading TFNG question
- [ ] Add 4 statements
- [ ] Set answers (TRUE, FALSE, NOT GIVEN, TRUE)
- [ ] Toggle between T/F/NG and Y/N/NG modes

#### Multiple Choice

- [ ] Create single-select MCQ
- [ ] Create multi-select MCQ
- [ ] Verify correct answer selection

### 2. Student - Test Taking

#### Completion Questions

- [ ] Input appears inline at blank positions
- [ ] Word count tracking works
- [ ] Answers auto-save

#### Matching Questions

- [ ] Dropdown shows all options
- [ ] Used options disabled (if not reusable)
- [ ] Options panel visible on mobile

#### TFNG Questions

- [ ] TRUE/FALSE/NOT GIVEN buttons work
- [ ] Only one selection per statement
- [ ] Visual feedback for selection

#### Diagram Questions

- [ ] Image displays with label markers
- [ ] Input fields match labels
- [ ] Answers saved correctly

##### Question Navigation

- [ ] Palette shows all question numbers
- [ ] Green = answered
- [ ] Red = visited unanswered
- [ ] Yellow = flagged
- [ ] Gray = not visited
- [ ] Click navigates to question

### 3. Audio Player (Listening)

- [ ] Plays audio once only
- [ ] Play count decrements correctly
- [ ] Cannot seek backward
- [ ] Player locks after play exhausted
- [ ] Warning message displayed when locked

### 4. Timer

- [ ] Countdown displays correctly
- [ ] 5-minute warning banner appears
- [ ] 1-minute critical warning (red, pulsing)
- [ ] Auto-submit triggers at 0:00
- [ ] Dismissible warning (not critical)

### 5. Grading

- [ ] Submit test as student
- [ ] Check completion answers scored correctly
- [ ] Check matching answers scored correctly
- [ ] Check TFNG answers scored correctly
- [ ] Partial scores for multi-blank questions
- [ ] Case-insensitive matching works
- [ ] Alternative answers accepted

## API Endpoints to Test

```bash
# Create completion question
POST /api/v1/listening/questions
{
  "question": {
    "section_id": 1,
    "part_id": 1,
    "question_number": 1,
    "question_type": "listening_sentence_completion",
    "question_text": "Complete the sentence.",
    "type_specific_data": {
      "template_text": "The meeting is at [BLANK_1].",
      "blanks": [{"blank_id": "BLANK_1", "max_words": 2}]
    },
    "answer_data": {
      "blanks": {"BLANK_1": ["9 am", "nine"]}
    }
  }
}

# Submit test answers
PUT /api/v1/test/attempts/{id}/submit
{
  "listening_answers": [
    {
      "question_id": 1,
      "user_answer": {"blanks": {"BLANK_1": "9 am"}}
    }
  ]
}
```

## Run Automated Tests

```bash
cd backend
pip install pytest
pytest tests/ -v
```

Expected: All tests pass (60+ tests)
