# Airline Disruption Resolution Agent

An AI-powered customer support agent for handling airline flight disruptions (cancellations and delays).

## Project Structure

```
airline-agent/
├── backend/
│   ├── main.py                 # FastAPI app entry point
│   ├── requirements.txt         # Python dependencies
│   ├── config.py               # Configuration
│   ├── models/
│   │   ├── customer.py         # Customer data models
│   │   ├── booking.py          # Booking/flight data models
│   │   └── agent_state.py      # Agent conversation state
│   ├── data/
│   │   ├── customers.json      # Customer profiles
│   │   ├── bookings.json       # Booking/flight data
│   │   └── policies.json       # Service rules and policies
│   ├── services/
│   │   ├── agent.py            # Main agent logic
│   │   ├── policy_engine.py    # Policy compliance and decisions
│   │   ├── groq_service.py     # Groq LLM integration
│   │   └── audit_logger.py     # Audit trail logging
│   └── api/
│       ├── routes.py           # API endpoints
│       └── schemas.py          # Request/response schemas
├── frontend/
│   ├── index.html              # Chat interface
│   ├── style.css               # Styling
│   └── script.js               # Frontend logic
└── .env.example                # Example environment variables
```

## Tech Stack
- **Backend:** Python + FastAPI
- **AI/LLM:** Groq API (fast inference)
- **Frontend:** Vanilla JS + HTML/CSS
- **Data:** JSON files

## Setup

1. Clone repo and navigate to project
2. Create `.env` file with your Groq API key
3. Install dependencies: `pip install -r backend/requirements.txt`
4. Run backend: `python backend/main.py`
5. Open frontend in browser

