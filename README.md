# Kisan-Mitra (Crop Management System)

Kisan-Mitra is an intelligent, multi-agent agricultural assistant built with modern web technologies and Google's Agentic Development Kit (ADK) using the Gemini 2.5 Flash model. The platform is designed to provide highly specific, context-aware agricultural advice to farmers.

## Features

- **Multimodal AI Assistant:** Upload images of damaged crops, and the AI will analyze the disease/pest, identify the crop type, and provide immediate actionable fixes and safe practices.
- **Context-Aware Advice:** The chat agent integrates seamlessly with local weather data (using MCP tools) to adapt agricultural advice based on current live weather conditions in your district.
- **Agentic Workflow:** Utilizes a dual-agent workflow consisting of a `crop_doctor` (for diagnostics) and a `cycle_planner` (for strategic, weather-aware planning).
- **Modern User Interface:** A sleek, glassmorphic React frontend built with Vite, featuring markdown rendering for easy-to-read advisory reports.

## Technology Stack

- **Backend:** Python, FastAPI, Google GenAI SDK, Google ADK (Agentic Development Kit)
- **Frontend:** React, TypeScript, Vite, Vanilla CSS
- **AI Model:** Gemini 2.5 Flash

## Setup Instructions

### Prerequisites
- Node.js (v18+)
- Python (3.9+)

### 1. Environment Setup

Clone the repository and set up your environment variables:
Create a `.env` file in the root directory and add your API key:
```env
GEMINI_API_KEY="your_api_key_here"
```

### 2. Backend Setup
1. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```
2. Activate the virtual environment:
   - Windows: `.\.venv\Scripts\activate`
   - Linux/Mac: `source .venv/bin/activate`
3. Install dependencies:
   ```bash
   pip install fastapi uvicorn pydantic python-dotenv google-genai
   # Install the ADK libraries
   ```
4. Run the backend server:
   ```bash
   python backend.py
   ```
   The backend will start on `http://localhost:8000`.

### 3. Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```
   The frontend will start on `http://localhost:5173`.

## Usage
Open `http://localhost:5173` in your browser. Type a question or upload a photo of your crop to receive personalized, AI-driven agricultural advice!
