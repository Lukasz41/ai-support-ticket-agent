# AI Support Ticket Agent

A Python portfolio project demonstrating **LLM function calling**, SQLite ticket retrieval, structured AI classification, and basic reliability practices. Built with Google Gemini, Streamlit, SQLite and pytest.

## What it does

1. A user enters a fictional IT support ticket in Streamlit.
2. The Gemini model may call the Python tool `lookup_previous_tickets(query)` (Google Gen AI SDK automatic function calling).
3. The tool uses `search_tickets()` to search similar historical tickets stored locally in SQLite.
4. A separate Gemini request returns structured JSON with category, priority, and suggested solution.
5. The application shows the tool usage, matched tickets and AI recommendation, then saves the ticket.

Ticket search currently uses **keyword overlap**, not embeddings or vector search. This is a learning project, not a production helpdesk product. An agent can elect not to call the tool.

## Requirements

- Python 3.11–3.13
- Google Gemini API key with access to the model set in `agent.py`
- Free-tier quotas depend on the provider's current policy

## Setup on Windows 11 (VS Code PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Replace `put_your_key_here` in `.env` with your own API key. Never commit or share this file.

```powershell
python -m pytest -q
python -m streamlit run app.py
```

Example ticket: `My laptop cannot connect to WiFi after a Windows update.`

## Model choice

The current code uses `gemini-3.5-flash-lite` because it worked in the original development environment. Model availability changes. If you receive a 404, consult the models available to your Gemini project and update the `MODEL` constant in `agent.py`.

## Reliability and tests

`generate_with_retry()` retries temporary HTTP **503** errors at most twice (three requests total, waits of 1s and 2s). Non-retryable errors (including 404) are raised immediately. See `tests/test_agent.py` for offline tests with fake API clients: **no actual Gemini API key or network access is required** to run pytest.

GitHub Actions runs the same tests on push and pull request.

## Privacy and safety

- Use **fictional** tickets only. Ticket descriptions and previous matching tickets are transmitted to Google Gemini during analysis.
- Never enter credentials, personal data or real business incident information.
- Historical tickets are untrusted context and model-generated advice requires human verification.
- `.env`, the local database `tickets.db`, and virtual environments are ignored by Git.

## Future improvements

Semantic search, improved evaluation of ticket classifications, better priority heuristics, more meaningful ticket metadata, and deployment.
