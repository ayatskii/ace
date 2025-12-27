# ACE Platform Data Flow Documentation

This document outlines the data flow for the key tasks within the ACE Platform.

## 1. Authentication Flow

**Goal**: Authenticate users (Student, Teacher, Admin) and issue access tokens.

### Flow Diagram

```mermaid
sequenceDiagram
    participant User
    participant Frontend (Login.jsx)
    participant AuthStore
    participant API (auth.py)
    participant DB (users table)

    User->>Frontend: Enters Email & Password
    Frontend->>AuthStore: login(email, password)
    AuthStore->>API: POST /auth/login
    API->>DB: Query User by Email
    DB-->>API: User Record
    API->>API: Verify Password Hash
    alt Valid Credentials
        API->>API: Create JWT Access Token
        API-->>AuthStore: Return Token & User Info
        AuthStore->>Frontend: Update State (isAuthenticated=true)
        Frontend->>User: Redirect to Dashboard
    else Invalid Credentials
        API-->>Frontend: 401 Unauthorized
        Frontend->>User: Show Error Message
    end
```

### Key Components

- **Frontend**: `src/pages/auth/Login.jsx`, `src/store/authStore.js`
- **Backend**: `app/routers/auth.py`, `app/core/security.py`
- **Database**: `users` table

---

## 2. Test Creation Flow (Admin)

**Goal**: Create a full IELTS test template with sections and questions.

### Flow Diagram

```mermaid
sequenceDiagram
    participant Admin
    participant Frontend (CreateTest/TestEditor)
    participant API (test.py)
    participant DB

    %% Step 1: Create Template
    Admin->>Frontend: Fill Test Details (Title, Type)
    Frontend->>API: POST /tests/templates
    API->>DB: Insert TestTemplate
    API->>DB: Auto-create Sections (L, R, W, S)
    DB-->>API: Created Template
    API-->>Frontend: Return Template ID

    %% Step 2: Add Content (Example: Listening)
    Admin->>Frontend: Open Listening Editor
    Frontend->>API: GET /tests/templates/{id} (with sections)
    Admin->>Frontend: Add Question/Part
    Frontend->>API: POST /listening/parts (or questions)
    API->>DB: Insert ListeningPart/Question
    DB-->>API: Confirmation
    API-->>Frontend: Updated Data
```

### Key Components

- **Frontend**: `src/pages/admin/CreateTest.jsx`, `src/pages/admin/TestEditor.jsx`, `src/pages/admin/editors/*`
- **Backend**: `app/routers/test.py`, `app/routers/listening.py`, `app/routers/reading.py`, etc.
- **Database**: `test_templates`, `test_sections`, `listening_parts`, `reading_passages`, etc.

---

## 3. Test Taking Flow (Student)

**Goal**: Student attempts a test, saves answers, and submits for grading.

### Flow Diagram

```mermaid
sequenceDiagram
    participant Student
    participant Frontend (TestAttempt)
    participant API (test.py)
    participant DB

    %% Start Attempt
    Student->>Frontend: Click "Start Test"
    Frontend->>API: POST /tests/attempts
    API->>DB: Create TestAttempt (status="in_progress")
    DB-->>API: Attempt ID
    API-->>Frontend: Attempt Data

    %% Taking Test
    Frontend->>API: GET /tests/attempts/{id} (fetch questions)
    Student->>Frontend: Answer Questions
    Frontend->>Frontend: Update Local State (answers)

    %% Submit
    Student->>Frontend: Click "Submit"
    Frontend->>API: PUT /tests/attempts/{id}/submit

    %% Backend Processing
    API->>DB: Save Writing/Speaking Submissions
    API->>API: Auto-grade Listening/Reading
    API->>DB: Save Listening/Reading Submissions
    API->>DB: Update Attempt Status ("submitted")
    API->>DB: Create Initial TestResult

    API-->>Frontend: Success
    Frontend->>Student: Redirect to Dashboard
```

### Key Components

- **Frontend**: `src/pages/student/TestAttempt.jsx`
- **Backend**: `app/routers/test.py`
- **Database**: `test_attempts`, `listening_submissions`, `reading_submissions`, `writing_submissions`, `speaking_submissions`

---

## 4. Grading Flow (Teacher)

**Goal**: Teacher grades Writing and Speaking submissions.

### Flow Diagram

```mermaid
sequenceDiagram
    participant Teacher
    participant Frontend (Dashboard)
    participant API (grading.py)
    participant DB

    %% View Queue
    Teacher->>Frontend: View Dashboard
    Frontend->>API: GET /grading/queue
    API->>DB: Query Pending Submissions
    DB-->>API: List of Submissions
    API-->>Frontend: Queue Data

    %% Grade Submission
    Teacher->>Frontend: Select Submission -> Grade
    Frontend->>API: POST /grading/{type}/{id}

    %% Backend Processing
    API->>DB: Create Grade Record (WritingGrade/SpeakingGrade)
    API->>DB: Update Submission Status ("graded")
    API->>API: Calculate Band Score
    API->>DB: Update TestResult

    %% Check Completion
    API->>API: Check if all sections graded
    alt All Graded
        API->>DB: Update TestAttempt Status ("graded")
        API->>DB: Update Overall Band Score
    end

    API-->>Frontend: Success
```

### Key Components

- **Frontend**: `src/pages/teacher/Dashboard.jsx`, `src/pages/teacher/GradeWriting.jsx`
- **Backend**: `app/routers/grading.py`, `app/services/grading_service.py`
- **Database**: `writing_grades`, `speaking_grades`, `test_results`

---

## 5. Student Management Flow (Admin)

**Goal**: Admin manages user accounts (create, update, delete).

### Flow Diagram

```mermaid
sequenceDiagram
    participant Admin
    participant Frontend (UserManagement)
    participant API (users.py)
    participant DB

    %% List Users
    Admin->>Frontend: View Users
    Frontend->>API: GET /admin/users
    API->>DB: Query Users
    DB-->>API: User List
    API-->>Frontend: Display Users

    %% Create User
    Admin->>Frontend: Click "Create User"
    Frontend->>API: POST /users
    API->>DB: Insert User
    DB-->>API: Created User
    API-->>Frontend: Update List

    %% Update Role
    Admin->>Frontend: Edit Role
    Frontend->>API: PUT /admin/users/{id}/role
    API->>DB: Update User Role
    API-->>Frontend: Success
```

### Key Components

- **Frontend**: `src/pages/admin/UserManagement.jsx`
- **Backend**: `app/routers/users.py`
- **Database**: `users` table
