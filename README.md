# Habit Tracker — Pixela

Posts daily habit pixels to Pixela to track activity like running distance over time.

---

## Table of Contents

0. [Prerequisites](#0-prerequisites)
1. [Quick start](#1-quick-start)
2. [Builds comparison](#2-builds-comparison)
3. [Usage](#3-usage)
4. [Data flow](#4-data-flow)
5. [Features](#5-features)
6. [Navigation flow](#6-navigation-flow)
7. [Architecture](#7-architecture)
8. [Module reference](#8-module-reference)
9. [Configuration reference](#9-configuration-reference)
10. [Data schema](#10-data-schema)
11. [Environment variables](#11-environment-variables)
12. [Design decisions](#12-design-decisions)
13. [Course context](#13-course-context)
14. [Dependencies](#14-dependencies)

---

## 0. Prerequisites

### Python

Python 3.8 or higher is required. Check your version:

```bash
python --version   # or python3 --version
```

Download from [python.org](https://www.python.org/downloads/) if needed.

---

### Pixela account

Pixela is an API-based habit graph service — there is no web sign-up form. Your account is created by making a POST request to the API, which the script does for you automatically on first run. Before running anything, you need to decide two things:

#### 1. Choose a username

Your Pixela username must:
- Start with a lowercase letter (`a`–`z`)
- Contain only lowercase letters, digits (`0`–`9`), and hyphens (`-`)
- Be between 2 and 33 characters total
- Be globally unique across all Pixela users — if it is already taken, the API returns a 409 and asks you to pick another

Examples of valid usernames: `johndoe`, `jane-smith`, `runner42`

#### 2. Choose a token

Your token is a password used to authenticate every API request via the `X-USER-TOKEN` header. It must:
- Be between 8 and 128 characters
- Contain only printable ASCII characters (letters, digits, symbols)
- Be kept secret — anyone with your token can post, update, or delete your pixels

Pick any strong string, e.g. `myS3cur3T0k3n!`. There is no recovery mechanism — if you lose your token, you cannot access your account. Store it somewhere safe.

#### 3. What the script creates on first run

When you run either build for the first time, it will:

1. **Create your Pixela user account** using the username and token you provide. This only needs to happen once — on subsequent runs the API returns "already exists" and the script skips it silently.
2. **Create a graph** (`graph1` by default, named "Running Graph" with unit "Km"). Again, only happens once — subsequent runs skip it silently.
3. **Post today's pixel** using the quantity you enter.

You do not need to do anything on the Pixela website. The entire setup is handled via the API.

#### 4. View your graph

After the first successful run, your graph is publicly visible at:

```
https://pixe.la/v1/users/{your-username}/graphs/graph1.html
```

The script prints this URL at the end of every run (option 4 in the advanced build).

---

### Environment setup

Copy `.env.example` to `.env` and fill in the username and token you chose above:

```bash
cp .env.example .env
```

Open `.env` and set:

```
PIXELA_USERNAME=your-chosen-username
PIXELA_TOKEN=your-chosen-token
```

The `.env` file is gitignored and will never be committed. The advanced build validates both values before making any network request — an invalid username format or a token shorter than 8 characters will raise an error immediately with an explanation.

---

## 1. Quick start

```bash
pip install -r requirements.txt
cp .env.example .env   # fill in your Pixela username and token
python menu.py         # select 1 (original) or 2 (advanced)
```

You can also run either build directly:

```bash
python original/main2.py
python advanced/main.py
```

---

## 2. Builds comparison

| Feature | Original | Advanced |
|---------|----------|---------|
| POST a pixel | ✓ (hardcoded dates) | ✓ (today, interactive) |
| PUT (update) a pixel | ✓ | ✓ (any date) |
| DELETE a pixel | ✓ | ✓ (with confirmation) |
| Create user | ✓ | ✓ |
| Create graph | ✓ | ✓ |
| Show graph URL | ✓ | ✓ |
| Custom HTTP headers | ✓ | ✓ |
| Credentials from `.env` | Partial (os.getenv with fallback) | ✓ (no fallback) |
| Input validation | ✗ | ✓ (regex + positive-float check) |
| Interactive CLI menu | ✗ | ✓ |
| OOP (`PixelaClient`) | ✗ | ✓ |
| Graceful HTTP error handling | Partial | ✓ |
| `requests.Session` | ✓ | ✓ |

---

## 3. Usage

### Original build

```bash
python original/main2.py
```

Runs sequentially: create user → create graph → prompt for today's quantity → post pixel → show graph URL. If the user or graph already exist, skips them silently. Edit the constants at the top of the file to change graph settings.

### Advanced build

```bash
python advanced/main.py
```

Launches an interactive CLI:

```
Pixela Habit Tracker — Running Graph (Km)
User: yourname  |  Graph: graph1

What would you like to do?
  1 — Log today's activity
  2 — Update a past entry
  3 — Delete a past entry
  4 — Show graph URL
  q — Quit

> 1
  Today's quantity (Km): 8.5
  Logged: Success.
```

---

## 4. Data flow

**Single execution (advanced build):**

```
.env file
  → load_dotenv() reads PIXELA_USERNAME, PIXELA_TOKEN
  → _validate_credentials() checks username regex, token length
  → PixelaClient.__init__() builds a requests.Session with X-USER-TOKEN header

User input (menu choice + quantity/date)
  → input validation (_prompt_quantity loops until valid number; _prompt_date loops until valid YYYYMMDD)
  → PixelaClient method called with validated params
  → HTTP request sent to https://pixe.la/v1/users/{username}/graphs/{graph_id}[/{date}]
  → Pixela API returns JSON {"isSuccess": true, "message": "..."} or error
  → _call() prints message or error to terminal
```

Data at each stage:
- **Input:** String from `input()` — date as `YYYYMMDD`, quantity as numeric string
- **Fetch:** JSON payload `{"date": "20260407", "quantity": "8.5"}` sent as POST body
- **Response:** JSON `{"isSuccess": true, "message": "Success."}` or HTTP 4xx/5xx

---

## 5. Features

### Both builds

**POST a pixel.** Sends a JSON payload with a date and quantity to Pixela's graph endpoint, creating a coloured pixel on the graph for that day.

**PUT (update) a pixel.** Sends a JSON payload to the date-specific endpoint with a new quantity, overwriting the existing pixel value.

**DELETE a pixel.** Sends a DELETE request to remove the pixel for a given date entirely.

**Custom HTTP headers.** The Pixela API authenticates via an `X-USER-TOKEN` header rather than a query parameter. Both builds use a `requests.Session` to attach this header to every request automatically.

**Create user and graph.** Registers the Pixela account and creates the graph (idempotent — Pixela returns an "already exists" message on repeat calls).

### Advanced only

**Interactive CLI.** A looping menu lets the user choose an action on each run instead of editing the script directly. Labels are unit-agnostic — set `GRAPH_UNIT` in `config.py` and all prompts update automatically.

**Input validation.** Username checked against Pixela's documented regex. Date prompts loop until a valid `YYYYMMDD` string is entered. Quantity prompts loop until a positive number is entered.

**409 handling (original build).** Pixela returns 409 when a user or graph already exists. Both builds treat this as a silent skip rather than an error, so re-running never produces spurious failure output.

**Graceful error handling.** Each API call is wrapped in a try/except that prints the HTTP status and body on failure without crashing the program.

**OOP encapsulation.** All HTTP logic lives in `PixelaClient`. `main.py` orchestrates; `client.py` fetches and mutates.

**Credentials from `.env`.** No hardcoded fallback defaults — missing env vars raise a `ValueError` with an actionable message before any network request is made.

---

## 6. Navigation flow

### a) Terminal menu tree

```
python menu.py
├── 1 → python original/main2.py   (runs, then "Press Enter to return")
├── 2 → python advanced/main.py    (runs, then "Press Enter to return")
└── q → exit
```

### b) Advanced build execution flow

```
Start
  └─ load .env
  └─ validate credentials
       ├─ invalid → ValueError, exit
       └─ valid → build PixelaClient
            └─ show menu loop
                 ├─ 1: Log today's activity
                 │     └─ prompt quantity (retry until positive number)
                 │           → POST /graphs/{id}
                 │                 ├─ 2xx → "Logged: Success."
                 │                 └─ 4xx/5xx → print error, continue loop
                 ├─ 2: Update a past entry
                 │     └─ prompt date (retry until valid YYYYMMDD)
                 │           → prompt quantity → PUT /graphs/{id}/{date}
                 │                 ├─ 2xx → "Updated: Success."
                 │                 └─ error → print error, continue
                 ├─ 3: Delete a past entry
                 │     └─ prompt date → prompt confirmation
                 │           ├─ y → DELETE /graphs/{id}/{date}
                 │           └─ other → "Cancelled."
                 ├─ 4: Show graph URL → print URL, continue
                 └─ q → exit
```

---

## 7. Architecture

```
habit-tracker-pixela/
│
├── menu.py              # root launcher — draws menu, forks to builds
├── art.py               # LOGO constant (ASCII art)
├── requirements.txt     # pip dependencies
├── .env.example         # template for credentials (committed)
├── .gitignore
│
├── original/
│   └── main2.py         # verbatim course file — sequential API calls
│
├── advanced/
│   ├── config.py        # all constants and validation regexes
│   ├── client.py        # PixelaClient — all HTTP calls, no I/O
│   └── main.py          # orchestrator — interactive menu, error handling
│
└── docs/
    └── COURSE_NOTES.md  # original exercise description and file history
```

---

## 8. Module reference

### `advanced/client.py` — `PixelaClient`

| Method | Returns | Description |
|--------|---------|-------------|
| `__init__(username, token)` | — | Creates a `requests.Session` with `X-USER-TOKEN` header |
| `create_user()` | `dict` | Registers the Pixela account (idempotent) |
| `create_graph(graph_id, name, unit, type_, color)` | `dict` | Creates a new graph |
| `graph_url(graph_id)` | `str` | Returns the public HTML URL for the graph |
| `post_pixel(graph_id, date_str, quantity)` | `dict` | Adds a pixel for the given date |
| `update_pixel(graph_id, date_str, quantity)` | `dict` | Overwrites a pixel's quantity |
| `delete_pixel(graph_id, date_str)` | `dict` | Removes a pixel for the given date |

All methods raise `requests.HTTPError` on non-2xx responses.

---

## 9. Configuration reference

| Constant | Default | Description |
|----------|---------|-------------|
| `PIXELA_BASE` | `https://pixe.la/v1/users` | Pixela API root URL |
| `GRAPH_ID` | `graph1` | Pixela graph identifier (1–16 alphanumeric chars, starts with a letter) |
| `GRAPH_NAME` | `Running Graph` | Display name shown on the graph page |
| `GRAPH_UNIT` | `Km` | Unit label for pixel quantities |
| `GRAPH_TYPE` | `float` | Value type — `"int"` or `"float"` |
| `GRAPH_COLOR` | `sora` | Graph colour — see `VALID_COLORS` |
| `VALID_COLORS` | `[shibafu, momiji, sora, ichou, ajisai, kuro]` | All accepted Pixela colour names |
| `USERNAME_RULE` | `^[a-z][a-z0-9-]{1,32}$` | Pixela username validation regex |
| `GRAPH_ID_RULE` | `^[a-zA-Z][a-zA-Z0-9]{0,15}$` | Pixela graph ID validation regex |
| `MIN_TOKEN_LEN` | `8` | Minimum token length enforced before any API call |
| `DATE_FORMAT` | `%Y%m%d` | strptime/strftime format for Pixela date strings |
| `DATE_DISPLAY` | `%Y-%m-%d` | Human-readable date format used in prompts |

---

## 10. Data schema

### API request — POST pixel

```json
{
  "date": "20260407",
  "quantity": "8.5"
}
```

### API request — PUT pixel (update)

```json
{
  "quantity": "10.0"
}
```

### API response (success)

```json
{
  "message": "Success.",
  "isSuccess": true
}
```

### API response (error)

```json
{
  "message": "User already exist.",
  "isSuccess": false
}
```

### API request — create user

```json
{
  "token": "your_token",
  "username": "yourname",
  "agreeTermsOfService": "yes",
  "notMinor": "yes"
}
```

### API request — create graph

```json
{
  "id": "graph1",
  "name": "Running Graph",
  "unit": "Km",
  "type": "float",
  "color": "sora"
}
```

---

## 11. Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `PIXELA_USERNAME` | Yes | Your Pixela account username (`[a-z][a-z0-9-]{1,32}`) |
| `PIXELA_TOKEN` | Yes | Your Pixela authentication token (min 8 chars) |

Copy `.env.example` to `.env` and fill in values:

```bash
cp .env.example .env
```

`.env` is gitignored and never committed.

---

## 12. Design decisions

**`config.py` — zero magic numbers.**
All constants live in one file. Changing the graph name, colour, or API base URL requires editing exactly one place. This also makes the constants visible as documentation.

**Separate `client.py` from `main.py`.**
`PixelaClient` handles HTTP; `main.py` handles orchestration and user interaction. Each is testable in isolation. Swapping the HTTP client (e.g. to `httpx`) requires touching only `client.py`.

**Pure-logic modules raise exceptions instead of `sys.exit()`.**
`PixelaClient` raises `requests.HTTPError` on bad responses. `main.py` decides how to handle it — print the error and continue the loop, rather than crashing. This keeps the interactive experience intact even after a failed API call.

**Credentials via `.env`, never hardcoded.**
Environment variables keep secrets out of source control. `.env.example` documents what is required without leaking values. `load_dotenv()` is a no-op when `.env` is absent (useful in CI), and `os.getenv()` then reads from the process environment directly.

**`.env.example` committed, `.env` gitignored.**
Any new developer (or CI environment) can see exactly what credentials are needed without exposing real values.

**`Path(__file__).parent` for all file paths.**
Scripts locate their own directory at runtime rather than assuming a working directory. This is required for correct behaviour when launched from `menu.py` via `subprocess.run(..., cwd=...)`.

**`sys.path.insert` pattern in advanced modules.**
Both `client.py` and `main.py` insert their own directory at the front of `sys.path`. This allows sibling imports (`from client import PixelaClient`) to work whether the script is launched from `menu.py` or directly.

**`subprocess.run` + `cwd=` in `menu.py`.**
Setting `cwd` to the script's parent directory ensures that any relative imports or file operations within the build work correctly regardless of where `menu.py` is invoked from.

**`while True` in `menu.py` instead of recursion.**
Looping avoids unbounded stack growth. The menu redraws after every `subprocess.run()` returns without calling itself.

**Console cleared before every valid menu render, not on invalid input.**
Invalid input prints an error message that must remain visible. The `clear` flag is set to `False` only after invalid input, so the error survives the next iteration.

**Input validation loops instead of crashing.**
`_prompt_date` and `_prompt_quantity` retry until valid input is given. This matches the interactive nature of the build — a typo should not end the session.

**`requests.Session` for shared headers.**
Creating one session and setting `X-USER-TOKEN` once means no risk of forgetting the header on a later call. The session also enables connection reuse across multiple API calls in a single run.

---

## 13. Course context

Built as Day 37 of 100 Days of Code by Dr. Angela Yu.

**Concepts covered in the original build:**
- HTTP POST requests with JSON bodies
- HTTP PUT and DELETE requests
- Custom request headers (`X-USER-TOKEN`)
- Constructing REST endpoint URLs
- `datetime` formatting for API date strings
- Reading JSON API responses

**The advanced build extends into:**
- Object-oriented design (`PixelaClient` class)
- `requests.Session` for header management
- Input validation with regex and type coercion
- Interactive CLI with a `while True` menu loop
- Graceful per-action error handling
- Credential management via `.env` / `python-dotenv`

See [docs/COURSE_NOTES.md](docs/COURSE_NOTES.md) for full concept breakdown and file history.

---

## 14. Dependencies

| Module | Used in | Purpose |
|--------|---------|---------|
| `requests` | `original/main2.py`, `advanced/client.py` | HTTP POST/PUT/DELETE to Pixela API |
| `python-dotenv` | `advanced/main.py` | Load credentials from `.env` at startup |
| `os` | `original/main2.py`, `advanced/main.py`, `menu.py` | Read env vars; detect OS for `clear` command |
| `re` | `advanced/config.py` | Compile username and graph ID validation regexes |
| `datetime` | `original/main2.py`, `advanced/main.py` | Generate `YYYYMMDD` date strings |
| `pathlib.Path` | `advanced/client.py`, `advanced/main.py`, `menu.py` | Resolve file paths relative to `__file__` |
| `sys` | `advanced/client.py`, `advanced/main.py`, `menu.py` | `sys.path` manipulation; `sys.executable` |
| `subprocess` | `menu.py` | Launch builds as child processes |
