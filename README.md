# Generative AI Discussion Facilitation System

A system where a group of Generative AI agents function as facilitators and analysts in anonymous online discussions, structurally managing the debate and guiding participants toward a conclusion based on objective data.

## Key Features

* **Anonymous Discussions:** Anyone can participate without user authentication
* **AI Facilitation:** A group of Google ADK-based agents manage the discussion flow.
* **Multi-language Support:** Supports two languages: English and Japanese.
* **Real-time Communication:** Instant information sharing via WebSocket
* **Objective Conclusion Formation:** Structural discussion management based on data collection and opinion summarization.

## Technical Stack

* **Frontend:** Next.js
* **Backend:** Python (FastAPI) + WebSocket
* **Agent Framework:** Google ADK (Agent Development Kit)
* **Database:** PostgreSQL / Firestore / Redis

## Setup

### 1. Install Required Packages

```bash
pip install fastapi uvicorn "google-generativeai>=0.7.0" "google-cloud-aiplatform>=1.52.0"
pip install google-adk
```

### 2. Configure Environment Variables

Create a `.env` file at the project root (same level as the `backend/` directory) and set the following environment variables:

```bash
# Google Generative AI API Key (Required)
GOOGLE_API_KEY=your_google_api_key_here

# Google Custom Search API (Optional: if using data collection features)
GOOGLE_SEARCH_API_KEY=your_search_api_key_here
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id_here
```

**How to Obtain API Keys:**

1. **Google Generative AI API Key (Required)**
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create an API key
   - Add `GOOGLE_API_KEY=your_created_api_key` to the `.env` file

2. **Google Custom Search API (If using search features)**
   
   **Step 1: Create Custom Search Engine**
   - Visit [Google Custom Search Engine](https://programmablesearchengine.google.com/controlpanel/create)
   - Click "Create a new search engine"
   - Enter `*` in "Sites to search" (to search all sites)
   - Enter a search engine name and create
   - After creation, copy the "Search Engine ID" from "Settings" → "Basics"
   
   **Step 2: Enable Custom Search API**
   - Visit [Google Cloud Console](https://console.cloud.google.com/)
   - Select a project (or create a new one)
   - Navigate to "APIs & Services" → "Library"
   - Search for "Custom Search API" and enable it
   
   **Step 3: Create API Key**
   - Navigate to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "API Key"
   - Copy the created API key
   - (Recommended) Set API key restrictions:
     - "API key restrictions" → "Restrict API" → Select "Custom Search API"
   
   **Step 4: Set Environment Variables**
   - Add the following to the `.env` file:
     ```
     GOOGLE_SEARCH_API_KEY=your_created_api_key
     GOOGLE_SEARCH_ENGINE_ID=your_copied_search_engine_id
     ```

**Note:** 
- Add the `.env` file to `.gitignore` and do not commit it to the Git repository.
- Google Custom Search API allows 100 free queries per day. A paid plan is required for more.

## Project Structure

```
/my_project_root (Project root)
├── /frontend/           <-- Next.js (Frontend) http://localhost:3000
│   ├── /app/
│   │   └── page.tsx
│   └── ...
│
├── /backend/            <-- Python (Backend / API) http://localhost:8000
│   ├── agents/
│   ├── i18n/
│   ├── tools/
│   ├── utils/
│   ├── adk_agents.py
│   ├── config.py
│   ├── i18n.py
│   ├── main.py
│   └── model.py
```
