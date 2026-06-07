# Doctor Appointment MultiAgent

> A conversational AI system for managing doctor appointments — check availability, book, cancel, or reschedule — powered by LangGraph agents, Groq LLM, FastAPI, and Streamlit.

---

## Motivation & Architecture

Scheduling appointments through traditional interfaces is tedious. This project replaces that with a natural-language agent that understands requests like *"Book me with Dr. Sharma on Friday afternoon"* and handles the full workflow autonomously.

The system uses **two specialised agents** orchestrated by LangGraph:

- **Info Agent** — handles availability lookups by doctor name or specialization (read-only)
- **Booking Agent** — handles set, cancel, and reschedule operations (read-write)
- **LangGraph** (`agent.py`) routes each user intent to the right agent
- **Groq LLM** (`llms.py`) drives agent reasoning with fast inference
- **FastAPI** (`main.py`) exposes the `/execute` REST endpoint
- **Streamlit** (`streamlit_ui.py`) provides the chat UI

### ASCII Architecture

```
┌──────────┐     ┌─────────────────┐     ┌──────────────────────┐
│   User   │────▶│  Streamlit UI   │────▶│   FastAPI Backend    │
│          │     │ streamlit_ui.py │     │  main.py · /execute  │
└──────────┘     └─────────────────┘     └──────────┬───────────┘
                                                     │
                                         ┌───────────▼────────────────────────┐
                                         │      LangGraph Orchestrator        │
                                         │   agent.py · routes user intent    │◀── Groq LLM
                                         └──────────┬──────────────┬──────────┘    (llms.py)
                                                    │              │
                            ┌───────────────────────▼──┐  ┌───────▼────────────────────┐
                            │       🔍 Info Agent       │  │      📅 Booking Agent       │
                            │  Availability lookups     │  │  Set · Cancel · Reschedule  │
                            └───────────┬───────────────┘  └───────┬────────────────────┘
                                        │                           │
                            ┌───────────▼───────────┐  ┌───────────▼────────────────────┐
                            │   toolkit/toolkits.py  │  │     toolkit/toolkits.py        │
                            │ check_availability_by  │  │  book · cancel · reschedule    │
                            │  doctor / specializ.   │  │       _appointment()           │
                            └───────────┬────────────┘  └───────────┬────────────────────┘
                                        │                           │
                            ┌───────────▼───────────┐  ┌───────────▼────────────────────┐
                            │   data/doctors.json    │  │    data/appointments.json      │
                            └────────────────────────┘  └────────────────────────────────┘
```

---

## Key Features

- **Availability lookup** — query by doctor name or medical specialization
- **Book appointments** — specify doctor, date, and time slot
- **Cancel appointments** — by appointment ID or patient + doctor combination
- **Reschedule** — move an existing appointment to a new date/time
- **Input validation** — enforces correct date formats (`YYYY-MM-DD`) and valid doctor names before any tool is called
- **Graceful error handling** — friendly messages for Groq rate limits, schema mismatches, and invalid inputs

---

## Repository Structure

```
doctor-appointment-multiagent/
├── agent.py              # LangGraph agent definition and graph compilation
├── main.py               # FastAPI app; exposes /execute endpoint
├── streamlit_ui.py       # Streamlit chat interface
├── llms.py               # Groq LLM client initialization and model config
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (not committed)
│
├── toolkit/
│   ├── toolkits.py       # Core tool functions (availability, book, cancel, reschedule)
│   └── __init__.py
│
├── data/
│   ├── doctors.json      # Doctor profiles, specializations, and available slots
│   └── appointments.json # Persisted appointment records
│
├── data_models/
│   └── models.py         # Pydantic models for request/response validation
│
├── prompt_library/
│   └── prompts.py        # System prompts and few-shot examples for agents
│
└── utils/
    └── helpers.py        # Date parsing, slot formatting, error message utilities
```

---

## Prerequisites

- **Python 3.10+**
- `pip` and `venv` (standard library)
- A **Groq API key** — get one free at [console.groq.com](https://console.groq.com)
- All Python packages listed in `requirements.txt`

---

## Configuration

Create a `.env` file in the project root:

```env
GROQ_API_KEY=gsk_your_key_here
GROQ_MODEL=llama3-8b-8192        # or mixtral-8x7b-32768
FASTAPI_PORT=8002
```

`llms.py` reads `GROQ_API_KEY` via `python-dotenv` at startup. Never commit `.env` to version control — it is listed in `.gitignore`.

---

## Setup

```bash
# 1. Clone the repository
git clone https://github.com/DevByShree/doctor-appointment-multiagent.git
cd doctor-appointment-multiagent

# 2. Create a virtual environment
python -m venv .myenv

# 3. Activate it
# Windows
.myenv\Scripts\activate
# macOS / Linux
source .myenv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Add your environment variables
cp .env.example .env   # then edit .env with your GROQ_API_KEY
```

---

## Running the App

Open **two terminals** (both with the virtualenv activated):

**Terminal 1 — Backend**
```bash
uvicorn main:app --port 8002
```

**Terminal 2 — Frontend**
```bash
streamlit run streamlit_ui.py
```

Then open [http://localhost:8501](http://localhost:8501) in your browser.

---

## API Usage

### Request — `/execute`

```bash
curl -X POST http://localhost:8002/execute \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "Is Dr. Sharma available on 2025-08-15?"
  }'
```

### Success Response

```json
{
  "status": "success",
  "response": "Dr. Sharma has the following slots available on 2025-08-15: 10:00 AM, 2:00 PM, and 4:30 PM."
}
```

### Rate Limit Error Response

```json
{
  "status": "error",
  "error_type": "rate_limit",
  "response": "The AI model is temporarily rate-limited. Please wait 30 seconds and try again, or switch to a different model in your .env file."
}
```

---

## Streamlit UI

Users type natural-language requests in the chat input (e.g., *"Book an appointment with a cardiologist next Monday"*). The UI sends the message to `/execute` and renders the returned JSON, displaying:

- The agent's plain-English reply
- A collapsible **Raw JSON** section for debugging tool calls and intermediate steps

No additional formatting or special syntax is required from the user.

---

## Troubleshooting

**Tool-call schema errors (wrong date format or invalid doctor name)**
The agent validates inputs before invoking any tool. If the LLM produces a date like `"August 15"` instead of `"2025-08-15"`, the validator catches it and asks the model to reformat. Allowed doctor names are loaded from `data/doctors.json`; an unrecognized name returns a list of valid options rather than a hard crash.

**Groq rate limit (`429 Too Many Requests`)**
Groq's free tier has per-minute token limits. The app catches this exception and returns the friendly error JSON shown above. Options: wait ~30 seconds, or change `GROQ_MODEL` in `.env` to a model with a higher rate limit (e.g., `gemma2-9b-it`).

**Uvicorn reload logs**
If you start uvicorn with `--reload`, you will see `WatchFiles detected changes` messages in the terminal whenever a `.py` file is saved. This is normal development behavior — the server restarts automatically. Remove `--reload` in production.

---

## Local Tool Checks

Test individual tools directly from the Python REPL without starting the server:

```python
# Check availability by doctor
from toolkit.toolkits import check_availability_by_doctor
print(check_availability_by_doctor(doctor_name="Dr. Sharma", date="2025-08-15"))

# Check availability by specialization
from toolkit.toolkits import check_availability_by_specialization
print(check_availability_by_specialization(specialization="cardiologist", date="2025-08-15"))

# Book an appointment
from toolkit.toolkits import book_appointment
print(book_appointment(doctor_name="Dr. Sharma", date="2025-08-15", time_slot="10:00 AM", patient_name="Shree"))
```

---

## Contributing

1. Fork the repository and create a feature branch (`git checkout -b feature/my-feature`).
2. Write clear, tested code and update docstrings where relevant.
3. Open a pull request with a concise description of the change.

Please follow [PEP 8](https://peps.python.org/pep-0008/) and keep functions small and single-purpose.

---

## License

MIT License. See [`LICENSE`](LICENSE) for details.

---

## Contact

**Shree Joshi** — [shreejoshi1805@gmail.com](mailto:shreejoshi1805@gmail.com) · [GitHub: DevByShree](https://github.com/DevByShree)

---

## Next Steps

- [ ] Add `pytest` unit tests for each tool in `toolkit/toolkits.py` with mocked data
- [ ] Set up a GitHub Actions CI pipeline to run tests and lint on every push
- [ ] Persist appointments to a lightweight database (SQLite or Supabase) instead of JSON files
- [ ] Add authentication to the `/execute` endpoint for multi-user deployments
