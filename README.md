# Debu — AI Debate Platform

Two LLM personas, **Proposition** and **Opposition**, debate any topic in real time. Arguments stream token-by-token to the client over WebSockets, and every turn is persisted to PostgreSQL as a replayable transcript.

> **Status:** Backend core loop complete and verified end-to-end. Human interjection, summarization, and the frontend are in progress. See the [Roadmap](#roadmap).

---

## How it works

1. A client creates a debate with `POST /debates/` (topic, model, `max_turns`).
2. The server generates a title with the LLM and stores the topic as the first message.
3. The client opens a WebSocket at `/ws/debates/{debate_id}`.
4. The orchestrator alternates between the two personas, streaming each response to the client and committing it to the database after every turn.
5. When `max_turns` is reached, the debate is marked `COMPLETE` and the client receives a completion signal.

```mermaid
flowchart LR
    C[Client] -- POST /debates/ --> R[REST routes]
    C <-- WebSocket --> W[WS endpoint]
    R --> S[Debate service]
    W --> S
    S --> F[Provider factory]
    F --> G[GeminiProvider - stateless]
    S --> DB[(PostgreSQL)]
```

---

## Tech stack

| Layer | Technology |
|---|---|
| API | FastAPI, Pydantic v2 |
| Realtime | WebSockets |
| Database | PostgreSQL via asyncpg, async SQLAlchemy |
| Migrations | Alembic |
| LLM | Google Gemini (`google-genai` SDK, streaming) |
| Tooling | uv, Git |

---

## Design decisions

- **Unified transcript table.** One `Message` table with `role`, `message_type`, and `sequence_number` instead of separate tables for each speaker. Human interjections will fit into the same model without a schema change.
- **Stateless providers.** `GeminiProvider` never touches history or the database. The orchestrator owns history and all DB writes, which keeps providers swappable.
- **Provider abstraction.** An `LLMProvider` ABC plus a factory resolves model names to provider instances, so adding another provider means adding a class and a factory branch.
- **Real persona enforcement.** Personas are set through the model's system instruction config, not by prepending text to the prompt.
- **Database-driven stop condition.** The loop stops based on `sequence_number` versus `max_turns` read from the database, not an in-memory counter. History is re-fetched after each commit.
- **Trigger-owned `modified_at`.** A PostgreSQL trigger (`AFTER INSERT ON messages`) updates the parent debate's timestamp, so it stays correct regardless of which code path inserts a message.
- **Fixed model enum.** Clients choose from an allowlist rather than passing free-text model names.
- **Interrupt policy (v1).** In-flight generations finish before an interrupt is applied. This avoids incoherent context and asyncio task-cancellation complexity.

---

## Project structure

```
app/
├── api/routes/      # REST and WebSocket endpoints
├── services/        # Debate orchestration
├── providers/       # LLMProvider ABC, Gemini implementation, factory
├── models/          # SQLAlchemy models
├── schemas/         # Pydantic request/response schemas
└── prompts.py       # Persona system prompts
alembic/             # Database migrations
```

---

## Getting started

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/)
- PostgreSQL running locally or remotely
- A [Gemini API key](https://aistudio.google.com/apikey)

### Setup

```bash
git clone https://github.com/Pranav-Pardeshii/<repo-name>.git
cd <repo-name>
uv sync
```

Create a `.env` file:

```env
GEMINI_API_KEY=your_key_here
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/debu
```

Apply migrations and start the server:

```bash
uv run alembic upgrade head
uv run uvicorn app.api.main:app --reload
```

Interactive API docs are available at `http://localhost:8000/docs`.

---

## API

### `POST /debates/`

Creates a debate.

```json
{
  "topic": "Social media does more harm than good",
  "model": "gemini-2.5-flash",
  "max_turns": 6
}
```

`max_turns` is optional and defaults to 6.

### `WS /ws/debates/{debate_id}`

Starts the debate loop and streams each persona's response as it is generated. When the debate reaches `max_turns`, the server sends `__DEBATE_COMPLETE__` and marks the debate `COMPLETE`.

---

## Roadmap

**Done**
- [x] Async data layer with Alembic migrations
- [x] Provider abstraction with Gemini streaming
- [x] Two-persona debate loop over WebSockets
- [x] Auto-generated debate titles
- [x] Configurable turn limit with automatic completion

**In progress**
- [ ] Human interjection mid-debate
- [ ] On-demand summarizer

**Planned**
- [ ] AI judge that scores both sides on logic, evidence, and rhetoric
- [ ] Human vs AI mode
- [ ] React + TypeScript frontend
- [ ] Multi-provider debates (different models on each side)
- [ ] Bring-your-own-key support
- [ ] Test suite, Docker, and CI

---

## Known limitations

- Multiple simultaneous WebSocket connections to the same debate are not yet handled and can cause sequence-number collisions.
- Debates currently use a server-side API key.

---

## Author

**Pranav Pardeshi**: [GitHub](https://github.com/Pranav-Pardeshii)
