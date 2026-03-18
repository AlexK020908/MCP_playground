# MCP Playground

A collection of **FastMCP** servers for Cursor: email (Gmail + Outlook), disk/academics (course & quiz materials), and a calculator. Designed to be modular and configurable.

---

## Project structure

```
MCP_PLAYGROUND/
├── .cursor/
│   └── mcp.json              # Cursor MCP server config (which servers to run)
├── .env                      # Secrets and paths (not committed)
├── README.md                 # This file
├── requirements.txt
├── calculator_server.py      # MCP: math tools (add, subtract, etc.)
├── email_server.py           # MCP: Gmail + Outlook search → Excel (uses mcp_email)
├── academics_server.py       # MCP: course/quiz folder listing & reading (uses mcp_disk)
├── mcp_email/                # Modular email logic (no FastMCP)
│   ├── __init__.py
│   ├── config.py             # Base path, Gmail/Outlook env paths
│   ├── gmail_client.py       # Gmail API: auth + search → rows
│   ├── outlook_client.py    # Outlook Graph: token(s) + search → rows
│   ├── filters.py            # e.g. tax_filing_only
│   └── excel_writer.py       # Write rows to .xlsx with links
├── mcp_disk/                 # Modular disk/academics logic (no FastMCP)
│   ├── __init__.py
│   ├── config.py             # ACADEMICS_BASE path from env
│   ├── paths.py              # Course dir & quiz folder resolution
│   └── reader.py             # Read .txt/.md/PDF from a folder
├── filter_tax_filing.py      # Standalone: filter tax Excel to filing-only rows
├── CPSC440_Quiz5_StudyGuide.md
├── CPSC440_Quiz5_StudyGuide_Elaborated.md
├── gmail_credentials.json    # From Google Cloud (not committed)
├── gmail_token.json          # After first OAuth (not committed)
├── outlook_token_cache.bin   # After first Outlook sign-in (not committed)
└── devenv/                   # Python venv (not committed)
```

---

## MCP servers

### 1. **user-calculator** (`calculator_server.py`)

- **What it does:** Math tools (add, subtract, multiply, divide, power, sqrt, sin, cos, tan, log, factorial, etc.).
- **Config:** None.
- **Use in Cursor:** Ask for calculations; the AI can call these tools.

---

### 2. **email** (`email_server.py`) — Gmail + Outlook → Excel

- **What it does:**
  - **`search_emails_to_excel`** — Search Gmail and/or Outlook with a query, write results to an Excel file with columns: Provider, Account, From, Subject, Date, Snippet, Open link, Search query used. Optional `tax_filing_only` to keep only property-tax/filing/official-government style emails.
- **Modular package:** All email logic lives in **`mcp_email/`** (config, Gmail client, Outlook client, filters, Excel writer). The server only wires the tool to FastMCP.
- **Config (`.env`):**
  - `OUTLOOK_CLIENT_ID` — Azure app (public client) client ID.
  - `OUTLOOK_TOKEN_CACHE_2` — (Optional) Second Outlook account cache path for two inboxes.
  - Gmail uses `gmail_credentials.json` and `gmail_token.json` in the project root (paths can be overridden with env vars).
- **Credentials:**
  - **Gmail:** Create a project in Google Cloud, enable Gmail API, create OAuth 2.0 credentials (Desktop), download as `gmail_credentials.json`. First run will open a browser to sign in and create `gmail_token.json`.
  - **Outlook:** Register an app in Azure AD with redirect URI `http://localhost:8400`, use the app’s client ID as `OUTLOOK_CLIENT_ID`. First run will open a browser and create `outlook_token_cache.bin`.

---

### 3. **academics** (`academics_server.py`) — Disk / course materials

- **What it does:**
  - **`school_resources`** — List contents of a course folder (all, or `lectures` / `homework` subdirs).
  - **`get_quiz_materials`** — Find the quiz folder for a course (e.g. “quiz 5”) and return concatenated content of all `.txt`, `.md`, and PDF files (PDF text via `pypdf`).
- **Config (`.env`):**
  - `ACADEMICS_BASE` — (Optional) Base path for academics. Default `E:/`. Course dir is `{ACADEMICS_BASE}/academics/{school}/{course}/` (e.g. `E:/academics/ubc/cpsc440/`).
- **Expected layout (default):**
  - `E:/academics/{school}/{course}/` — course root (e.g. `ubc/cpsc440`).
  - `E:/academics/{school}/{course}/lectures/` — lectures; quiz folders can be `quiz 5`, `quiz/5`, `quiz5`, etc.
  - `E:/academics/{school}/{course}/homework/` — optional.
- **Modular package:** All disk logic lives in **`mcp_disk/`** so it can be reused or tested without FastMCP:
  - `mcp_disk.config` — `get_academics_base()` from env.
  - `mcp_disk.paths` — `get_course_dir()`, `get_quiz_folder()`.
  - `mcp_disk.reader` — `read_folder_contents()` (text + PDF).

---

## Setup

1. **Clone and venv**
   ```bash
   cd MCP_PLAYGROUND
   python -m venv devenv
   .\devenv\Scripts\activate   # Windows
   pip install -r requirements.txt
   ```

2. **Environment**
   - Copy `.env.example` to `.env` if you have one, or create `.env` with at least `OUTLOOK_CLIENT_ID` for email and optionally `ACADEMICS_BASE` for academics.
   - Add Gmail credentials as `gmail_credentials.json` for email search.

3. **Cursor**
   - `.cursor/mcp.json` already points to the three servers. Restart Cursor (or reload MCP) after changing `.env` or adding credentials.

4. **First runs**
   - **Email:** First Gmail/Outlook use will open a browser for OAuth; tokens are then cached.
   - **Academics:** Ensure `E:/academics/...` (or your `ACADEMICS_BASE`) exists and contains your school/course/quiz folders.

---

## Other files

- **`CPSC440_Quiz5_StudyGuide.md`** — Outline for Quiz 5 (slides-style).
- **`CPSC440_Quiz5_StudyGuide_Elaborated.md`** — Filled-in study guide based on course materials and outline.

---

## Adding or changing the email MCP

- **Change credential paths:** Set `GMAIL_CREDENTIALS_JSON`, `GMAIL_TOKEN_JSON`, `OUTLOOK_TOKEN_CACHE`, or `OUTLOOK_TOKEN_CACHE_2` in `.env`.
- **Add another tool:** Add a new `@mcp.tool()` in `email_server.py` and call `mcp_email` helpers (`search_gmail_rows`, `search_outlook_rows`, `write_emails_excel`, etc.).
- **Reuse email logic elsewhere:** `from mcp_email import search_gmail_rows, search_outlook_rows, write_emails_excel` (call `mcp_email.config.set_base_path(...)` first).

---

## Adding or changing the disk MCP

- **Change base path:** Set `ACADEMICS_BASE` in `.env` (e.g. `D:/school`).
- **Add another tool:** Add a new `@mcp.tool()` in `academics_server.py` and call `mcp_disk` helpers (`get_course_dir`, `read_folder_contents`, etc.).
- **Reuse reading elsewhere:** `from mcp_disk import read_folder_contents` and pass any `Path` to read .txt/.md/PDF under that folder.

---

## License / credits

Credentials, tokens, and `.env` are gitignored. MCP servers use FastMCP; email uses Google Gmail API and Microsoft Graph (MSAL).
