# Remedial Scheduler - Testing Guide

This document provides instructions for setting up and testing the Remedial Scheduler application.

## 📋 Prerequisites

*   **Python 3.10+**
*   **Node.js 18+**
*   **Google Gemini API Key**: You need a valid API key from Google AI Studio.

## 🚀 Setup Instructions

### 1. Backend Setup
Navigate to the backend directory and set up the environment:

```bash
cd backend

# Create a virtual environment (optional but recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**Configuration**:
Create a `.env` file in the `backend/` directory:
```env
GEMINI_API_KEY=your_actual_api_key_here
```

### 2. Frontend Setup
Navigate to the frontend directory and install dependencies:

```bash
cd ../frontend
npm install
```

---

## 🏃‍♂️ Running the Application

You need to run both the backend and frontend terminals simultaneously.

**Terminal 1 (Backend):**
```bash
cd backend
# Make sure your venv is activated
uvicorn main:app --reload --port 8000
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev
```

Access the application at: **http://localhost:3000**

---

## 🧪 Testing Strategies

### Option A: Manual Testing (UI)

1.  Open **http://localhost:3000** in your browser.
2.  You will see file upload buttons for **Students**, **Teachers**, **Slots**, and **Busy** data.
3.  Navigate to `backend/test_data/` (or `large_test_data`, `stress_test_data`) to find sample CSV files.
4.  Upload the corresponding files.
5.  Click **"Generate Schedule"**.
6.  Wait for the AI to process (10-30 seconds).
7.  Review the generated table.

### Option B: Automated Metric Evaluation (Script)

We have a Python script that stress-tests the AI model against strict logic constraints (e.g., "Is the teacher actually free?", "Is the student busy?").

**How to run:**
```bash
cd backend
python evaluate_metrics.py
```

**What it does:**
*   It runs against 3 datasets: `test_data` (Small), `large_test_data` (Medium), and `stress_test_data` (High Complexity).
*   It generates a report with 3 metrics:
    *   **CSR (Constraint Satisfaction Rate)**: Percentage of valid assignments.
    *   **Hallucination Rate**: Percentage of fake data invented by AI.
    *   **Intent Recall**: Percentage of failing students successfully scheduled.

**Expected Results:**
*   You should see **100% Intent Recall** and **0% Hallucinations**.
*   **CSR** may vary between 80-100% depending on the complexity of the dataset.

---

## 📂 Test Datasets

We have prepared three levels of testing data in the `backend/` directory:

1.  **`test_data/`**: Small, simple dataset. Ideal for verifying basic functionality.
2.  **`large_test_data/`**: Medium dataset. Tests if the AI covers everyone.
3.  **`stress_test_data/`**: Complex dataset with high conflict density (many busy slots). Tests the AI's reasoning limits.

## ⚠️ Common Issues

*   **"Generate Schedule Failed"**: Check if the backend is running. Check the backend terminal for errors (e.g., API Key invalid).
*   **504 Gateway Timeout**: The AI took too long. We have set the timeout to 600s, but extremely large files might still be slow.
*   **404 Model Not Found**: Ensure you are using `gemini-1.5-flash` or `gemini-2.5-flash` in `backend/main.py`.

---

Happy Testing! 🎯
