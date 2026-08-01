# MindMend Chatbot — Masquerade '26

A peer-support webapp for students: a chat page with a "breathing orb"
companion (Scyla) that shows emotion, speaks and listens by voice, and
replies in English, Hindi, or Telugu — plus a backend that also satisfies
the Masquerade '26 endpoint spec (`POST /chat/completions`).

Fully offline. No external AI API, no API key, nothing to deploy to try it —
everything runs locally in this folder. Voice is handled entirely by the
browser's built-in Web Speech API (Chrome/Edge), not a paid service.

## What's new in this version

- **Full webpage** at `/` — chat UI, not just a raw endpoint.
- **Breathing orb avatar** — pulses on a slow 16-second box-breathing rhythm
  (4s in, 4s hold, 4s out, 4s hold) and changes color/glow based on Scyla's
  detected emotion for that reply (warm, gentle, concerned, soothing,
  encouraging, celebratory, somber, crisis). It's both a mood display and a
  literal grounding exercise running in the background.
- **Voice in and out** — tap the mic to speak instead of typing (browser
  speech-to-text), and Scyla's replies are read aloud (browser
  text-to-speech). Toggle voice off with the speaker icon top-right.
- **Multilingual** — English, Hindi (हिंदी), and Telugu (తెలుగు), switchable
  mid-conversation from the dropdown. Crisis detection and the safety
  response work in all three.
- **Longer, warmer replies** — every response leads with real validation
  before any question, and occasionally offers a grounding technique
  (5-4-3-2-1, box breathing, or a writing prompt).

## Run it

```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

Then open **http://localhost:8000** in Chrome or Edge (needed for the mic —
other browsers will still work for typed chat and spoken replies, just not
voice input).

## Two backend endpoints

| Endpoint | Used by | Notes |
|---|---|---|
| `POST /chat/completions` | Masquerade judging platform | Exact spec from the participant guide — untouched, always responds in English internally, safe to submit as-is. |
| `POST /api/chat` | The webpage | Richer: takes `{message, history, language}`, returns `{reply, emotion, language}`. The `emotion` field drives the orb. |

Keeping these separate means nothing you add for the webapp (emotion tags,
language switching) can ever break the judging endpoint's exact response
shape.

## Test the judging endpoint (matches the participant guide's spec check)

```bash
curl http://127.0.0.1:8000/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "mindmend-v1", "messages": [{"role": "user", "content": "Hello"}]}'
```

## Files

- `main.py` — FastAPI server: both endpoints, CORS enabled, serves the webpage.
- `engine.py` — conversation logic: crisis check → name memory → intent →
  language-aware response + emotion tag.
- `knowledge.py` — MindMend's actual "voice": the response bank in English,
  Hindi, and Telugu, each variant tagged with an emotion. This is the file
  to grow over time — add more intents or phrasing variety here without
  touching engine logic.
- `static/index.html` — the whole frontend (HTML/CSS/JS in one file): the
  breathing orb, chat log, language selector, voice input/output.
- `test_client.py` — terminal chat loop, still works if you want to test
  without a browser.

## Notes on the translations

The Hindi and Telugu responses were written directly (not machine-translated
after the fact), but a native-speaker pass before a public demo is worth
doing if you have a friend who reads either script — tone matters a lot
for something this personal.

## Where to go from here (optional)

- Persist conversations/mood per user in Firestore (you already have this
  set up for MindMend) so Scyla can reference past check-ins.
- Add more languages by extending `RESPONSES`, `CRISIS_RESPONSE`, and
  `GROUNDING_TECHNIQUES` in `knowledge.py`, plus the `MIC_LANG`/`SPEECH_LANG`
  maps in `index.html`.
- Swap the keyword-based intent detector for embedding similarity if you
  want fuzzier matching later.
- Deploy (Render/Railway/Fly.io) if you want to submit an endpoint for
  judging instead of demoing locally.
