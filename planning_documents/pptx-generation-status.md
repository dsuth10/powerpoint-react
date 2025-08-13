## Current Status: End-to-End PPTX Generation and Download

### What’s implemented
- Frontend sends `title`, `bullets`, `notes`, and `image` to `POST /api/v1/slides/build`.
- Backend accepts `image` as a string or object and normalizes it to `ImageMeta`.
- PPTX builder writes bullets to slides and full `notes` into the speaker notes pane.
- LLM prompt strengthened to require robust speaker notes and structured images.
- Strict mode: when `OPENROUTER_REQUIRE_UPSTREAM=1`, the API refuses placeholder fallbacks if the LLM call fails.

### Environment status (confirmed in container)
- `OPENROUTER_API_KEY` present.
- `OPENROUTER_DEFAULT_MODEL=openai/gpt-4o-mini`.
- `OPENROUTER_REQUIRE_UPSTREAM=1`.
- Frontend model selector updated; use “GPT‑4o mini” or “GPT‑4o”.

### Observed behavior to date
- Initial placeholders were due to a malformed `.env` (flags placed on one line with literal `\n`).
- After fixing `.env`, outline requests returned `502` with message “LLM upstream required and failed,” meaning upstream failed and fallback is disabled (by design).
- Implemented a more tolerant JSON extractor for LLM responses and restarted the backend.

### Current state
- Backend/env is correct and running.
- Outline generation depends on a successful OpenRouter response; any upstream auth/rate/format issue now yields `502`.
- PPTX files created during the placeholder phase contain minimal content; once upstream succeeds, slides will have full text, notes, and images.

### Likely causes of `502`
- Invalid/expired OpenRouter key or account restrictions.
- Rate limiting (`429`) from provider.
- Provider/model returning non‑JSON or fenced JSON; parser is now lenient, but totally non‑JSON responses will still fail.
- Model mismatch is unlikely now (allowlist includes `openai/gpt-4o-mini` and `openai/gpt-4o`).

### Expected outcome after upstream success
- Chat returns real `SlidePlan[]` with bullets/notes/images.
- “Start Generation” produces a PPTX with slide text and full speaker notes; images included when provided.

### Next steps
1. In Chat, select “GPT‑4o mini” (or “GPT‑4o”).
2. Send the prompt and verify the outline appears in the UI (no placeholders).
3. Click “Start Generation,” then “Download PPTX.”
4. If any error persists, capture fresh backend logs around the request (see below) and adjust accordingly.

### Repro and validation
- Clean restart:
  - PowerShell:
    - `docker compose down -v`
    - `docker compose up -d`
- Verify env inside backend container:
  - `docker compose exec backend sh -lc "printenv | egrep 'OPENROUTER_API_KEY|OPENROUTER_REQUIRE_UPSTREAM|OPENROUTER_DEFAULT_MODEL'"`
- Generate outline via UI (Chat) and confirm bullets/notes in the assistant message.
- Build/download PPTX and confirm speaker notes in the Notes pane in PowerPoint.

### Troubleshooting snippets
- Backend logs (last 200 lines):
  - `docker compose logs backend --no-log-prefix --tail=200`
- Common issues:
  - `502` “LLM upstream required and failed”: provider error, auth, rate limit, or malformed output.
  - `401/403` from provider: rotate/fix `OPENROUTER_API_KEY`.
  - `429`: retry later or adjust usage/model.



