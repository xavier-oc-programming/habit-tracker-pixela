# Course Notes — Day 37

## Exercise Description

**Course:** 100 Days of Code: The Complete Python Pro Bootcamp — Dr. Angela Yu
**Day:** 37 — Habit Tracking Project: API Post Requests & Headers

The exercise uses the [Pixela](https://pixe.la) API to build a simple habit tracker that
visualises daily activity as a pixel graph. Students learn to make HTTP POST, PUT, and DELETE
requests with custom headers, and work with query parameters and JSON payloads.

## Concepts Covered (Original Build)

- `requests.post()` with a JSON body
- `requests.put()` for updating a resource
- `requests.delete()` for removing a resource
- Custom HTTP headers (`X-USER-TOKEN`)
- Constructing endpoint URLs with f-strings
- Working with `datetime` to produce `YYYYMMDD` date strings
- Reading and interpreting JSON API responses

## Course Files

| File | Status | Notes |
|------|--------|-------|
| `main2.py` | ✅ Committed to `original/` | Uses `os.getenv()` with fallback — preferred over `main.py` |
| `main.py` | Moved to `old_files/` | Verbatim course exercise; all credentials hardcoded |

`main.py` is the raw course exercise (6 sequential steps: create user → create graph →
post three pixels → PUT update → DELETE → print graph URL). `main2.py` is a cleaned-up
variant with functions, a `requests.Session`, and `os.getenv()` for credentials.
`main2.py` was chosen for `original/` per the portfolio rule that prefers env-var usage.

## Hardcoded Credentials Note

Both course files contained a placeholder Pixela token (`fdjlaklfkjsdhfdslkjhh`) in
`TOKEN`/`PIXELA_TOKEN`. This appears to be a course-provided dummy value; it does not
match any known API key format. The advanced build reads credentials exclusively from
`.env` — no fallback defaults are committed.

## Advanced Build Extensions

- OOP refactor: `PixelaClient` class encapsulating all API calls
- Interactive CLI menu (log today / update / delete / show URL)
- Input validation: username regex, graph ID regex, positive-float quantity
- Credentials via `.env` / `python-dotenv` (no hardcoded fallbacks)
- Graceful error handling per action (non-crashing on HTTP errors)
