# Weather Advisory Support Bot

A policy-driven weather advisory system that combines **live weather data**, **YAML-based Standard Operating Procedures (SOPs)**, **context-aware conversations**, and a **LangGraph workflow** to provide consistent safety guidance.

## Features

- Live weather lookup by location
- Natural-language weather safety questions
- Context extraction for activity, location, time, and vulnerable groups
- Session-aware follow-up questions
- YAML-based SOP management
- Multiple SOP matching
- Deterministic conflict resolution using severity and priority
- LangGraph workflow orchestration
- FastAPI REST API
- React + Vite frontend
- Backend health checking and configurable API URL
- Automated testing for all 13 implemented SOP scenarios

## Architecture

```text
User
  ↓
React + Vite Frontend
  ↓ POST /chat
FastAPI Backend
  ↓
LangGraph Workflow
  ├── Intake: extract context
  ├── Memory: merge follow-up context
  ├── Weather: retrieve weather data
  ├── SOP Matcher: match intent + weather conditions
  ├── Conflict Resolution: severity → priority
  └── Response: return policy-grounded advisory
```

# LangGraph Workflow

The application uses **LangGraph** to manage the decision-making process and control how different situations are handled.

Conceptually, the workflow is:

```text
START
  |
  v
Intake
  |
  v
Memory Resolution
  |
  v
Location Available?
  |                 \
 Yes                 No
  |                   \
  v                    Ask for Location
Weather Retrieval
  |
  v
SOP Matching
  |
  v
Any SOP Match?
  |              \
 Yes              No
  |                \
  v                 Honest Fallback
Conflict Resolution
  |
  v
Generate Advisory
  |
  v
END
```


# Tech Stack

The project uses the following technologies:

| Technology | Purpose |
|---|---|
| Python | Backend development and core application logic |
| FastAPI | REST API development |
| Uvicorn | ASGI server for running the FastAPI application |
| LangGraph | Workflow orchestration and conditional decision branching |
| Pydantic | Data validation and request/response models |
| PyYAML | Loading and parsing external YAML-based SOP files |
| Open-Meteo | Live weather and forecast data retrieval |
| React | Interactive chat-based frontend |
| Vite | Frontend development server and build tooling |
| TypeScript | Type-safe frontend application logic |
| Tailwind CSS | Frontend styling and responsive user interface |
| Lucide React | User interface icons |

## Project Structure

```text
WASB/
├── backend/
│   ├── nodes/
│   ├── sops/
│   │   ├── outdoor.yaml
│   │   ├── travel.yaml
│   │   └── vulnerable.yaml
│   ├── graph.py
│   ├── loader.py
│   ├── main.py
│   ├── memory.py
│   ├── models.py
│   └── weather.py
├── frontend/
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
├── test_weather.py        //temporary file(not included in github)
├── test_matcher.py        //temporary file
├── test_matcher_severe.py //temporary file
├── test_intake.py         //temporary file
├── test_memory.py         //temporary file
├── test_graph.py          //temporary file
└── test
     ├──test_all_sops.py
```


# 🏗️ System Architecture

```text
                    ┌──────────────────┐
                    │   User Message   │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │   Intake Node    │
                    │                  │
                    │ Extract:         │
                    │ - Activity       │
                    │ - Location       │
                    │ - Time           │
                    │ - Vulnerable grp │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Session Memory   │
                    │                  │
                    │ Restore missing  │
                    │ context from     │
                    │ previous turns   │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Weather Node     │
                    │                  │
                    │ Geocoding +      │
                    │ Live Weather     │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ SOP Matcher      │
                    │                  │
                    │ Load YAML SOPs   │
                    │ Match activity   │
                    │ + weather        │
                    └────────┬─────────┘
                             │
                  ┌──────────┴──────────┐
                  │                     │
                  ▼                     ▼
        ┌─────────────────┐   ┌──────────────────┐
        │ Matching SOPs   │   │ No SOP Matched   │
        └────────┬────────┘   └────────┬─────────┘
                 │                     │
                 ▼                     ▼
        ┌─────────────────┐   ┌──────────────────┐
        │ Conflict        │   │ Honest Fallback  │
        │ Resolution      │   │ Response         │
        └────────┬────────┘   └──────────────────┘
                 │
                 ▼
        ┌─────────────────┐
        │ Advisory Reply  │
        │ + SOP ID        │
        │ + Severity      │
        └─────────────────┘

## How It Works

A user can ask:

```text
Is it safe to go cycling in Hyderabad today?
```

The system extracts:

```text
activity: cycling
location: Hyderabad
time_reference: today
vulnerable_group: None
```

It then retrieves weather conditions, loads the YAML SOPs, finds all applicable policies, and selects the best one.

An SOP matches only when:

1. The activity or user message matches its intent keywords.
2. The weather conditions satisfy all configured thresholds.

## Implemented SOPs

| SOP ID | Scenario | Severity |
|---|---|---|
| WX-001 | Severe rainfall override | Critical |
| EX-001 | Extreme heat during exercise | High |
| EX-002 | High UV exposure | Medium |
| EX-003 | Strong wind while cycling | High |
| EX-004 | Rain during outdoor exercise | High |
| TR-001 | High rain probability during travel | Medium |
| TR-002 | Strong wind during travel | High |
| TR-003 | Rain affecting picnic suitability | Medium |
| TR-004 | Strong wind affecting outdoor events | Medium |
| VG-001 | Child in extreme heat | High |
| VG-002 | Elderly person in extreme heat | High |
| VG-003 | Pet in extreme heat | Medium |
| VG-004 | Vulnerable group in heavy rain | High |

## Conflict Resolution

More than one SOP can match the same situation.

The selection rule is:

```text
1. Higher severity wins.
2. If severity is the same, higher priority wins.
```

Severity ranking:

```text
Critical > High > Medium > Low
```

Example:

```text
WX-001 → Critical, Priority 100
EX-004 → High, Priority 75

Selected: WX-001
```

## API

### Root

```http
GET /
```

Response:

```json
{
  "message": "Weather Advisory Support Bot API is running."
}
```

### Health Check

```http
GET /health
```

Response:

```json
{
  "status": "healthy"
}
```

### Chat

```http
POST /chat
```

Request:

```json
{
  "message": "Is it safe to go cycling in Hyderabad today?",
  "session_id": "demo-session"
}
```

Response:

```json
{
  "reply": "Weather Advisory...",
  "protocol_id": "EX-002",
  "severity": "medium"
}
```

## Installation

### 1. Clone and enter the project

```bash
git clone <your-repository-url>
cd WASB
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

### 3. Install backend dependencies

```bash
pip install -r requirements.txt
```

## Run the Backend

From the project root:

```bash
uvicorn backend.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

Health endpoint:

```text
http://127.0.0.1:8000/health
```

## Run the Frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

The frontend runs at:

```text
http://localhost:3000
```

By default, it connects to:

```text
http://127.0.0.1:8000
```

The backend URL can also be configured using:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

The frontend includes:

- Backend online/offline status
- Retry connection
- Configurable backend target URL
- Browser local storage for the configured API URL
- Session-based chat
- Clear chat functionality
- Structured weather advisory cards

## Testing

### Live Weather

```bash
python test_weather.py
```

### SOP Matching

```bash
python test_matcher.py
```

### Severe Weather Matching

```bash
python test_matcher_severe.py
```

### Context Extraction

```bash
python test_intake.py
```

### Session Memory

```bash
python test_memory.py
```

### Complete LangGraph Workflow

```bash
python test_graph.py
```

### Validate All SOPs

```bash
python test_all_sops.py
```

The full SOP test validates all 13 implemented scenarios and should report:

```text
RESULT: PASS
```

## Example Scenarios

### High UV

```text
Question: Can I go cycling today?
UV Index: 8.0
Expected SOP: EX-002
```

### Extreme Heat

```text
Question: Is it safe to go running today?
Temperature: 40 °C
Expected SOP: EX-001
```

### Strong Wind Cycling

```text
Question: Can I go cycling today?
Wind Speed: 40
Expected SOP: EX-003
```

### Severe Rainfall Override

```text
Question: Is it safe to go cycling outside today?
Precipitation: 10
Expected SOP: WX-001
```

### Elderly Person in Extreme Heat

```text
Question: Can my grandmother go outside today?
Temperature: 38 °C
Expected SOP: VG-002
```

## Technologies

### Backend

- Python
- FastAPI
- Pydantic
- LangGraph
- YAML

### Frontend

- React
- TypeScript
- Vite
- Tailwind CSS
- Lucide Icons

## Key Design Decisions

### Policy-Driven Responses

The system is designed to return guidance grounded in predefined SOPs instead of unrestricted advice.

### Externalized Rules

SOPs are stored in YAML files, allowing policies to be extended without rewriting the core matching logic.

### Separation of Concerns

```text
Input
→ Context Extraction
→ Memory
→ Weather Retrieval
→ SOP Matching
→ Conflict Resolution
→ Response
```

### Deterministic Decisions

The severity and priority rules make SOP selection predictable and testable.

## Current Limitations

- SOP coverage is limited to the 13 implemented scenarios.
- A policy-grounded advisory is only available when an applicable SOP matches.
- Session memory is currently designed for local runtime usage.
- Deployment configuration is not yet included.

## Future Improvements

- PostgreSQL-backed persistent session memory
- Redis caching
- Additional SOP categories
- Docker containerization
- Cloud deployment
- CI/CD testing
- Logging and monitoring
- Admin interface for SOP management

## Demo

Start the backend:

```bash
uvicorn backend.main:app --reload
```

Start the frontend:

```bash
cd frontend
npm run dev
```

Open:

```text
http://localhost:3000
```

Ask:

```text
Is it safe to go cycling in Hyderabad today?
```

The system performs:

```text
Extract Context
      ↓
Retrieve Weather
      ↓
Load and Match SOPs
      ↓
Resolve Conflicts
      ↓
Return Policy-Grounded Advisory
```

## License

This project was created as a technical assignment/project implementation.

## Author

**Kommu Hari Kishan**

Weather Advisory Support Bot — A Policy-Driven Weather Safety Advisory System
