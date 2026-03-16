"""
Email MCP server: search Gmail or Outlook via one tool.
Gmail: Google Cloud project, Gmail API, gmail_credentials.json → gmail_token.json.
Outlook: Azure app registration (public client), OUTLOOK_CLIENT_ID → outlook_token_cache.bin.
"""
from __future__ import annotations

import html
import json
import os
import re
import urllib.parse
import urllib.request
from pathlib import Path

from dotenv import load_dotenv
from fastmcp import FastMCP

_BASE = Path(__file__).resolve().parent
load_dotenv(_BASE / ".env")


def _html_to_plain(html_content: str) -> str:
    """Strip tags and decode entities for readable plain text."""
    if not html_content:
        return ""
    text = re.sub(r"<br\s*/?>", "\n", html_content, flags=re.IGNORECASE)
    text = re.sub(r"</(p|div|tr|li|h[1-6])>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _fmt(from_: str, subject: str, date: str, snippet: str) -> str:
    return f"From: {from_}\nSubject: {subject}\nDate: {date}\n{snippet}\n"


def _fmt_email_pretty(from_: str, subject: str, date: str, body: str) -> str:
    """Format one email as markdown for pretty display."""
    body_plain = _html_to_plain(body) if body else ""
    return (
        f"### {subject}\n\n"
        f"**From:** {from_}  \n"
        f"**Date:** {date}\n\n"
        f"{body_plain}\n"
    )


# ---- Gmail ----
def _gmail_service():
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    cred_path = os.environ.get("GMAIL_CREDENTIALS_JSON", str(_BASE / "gmail_credentials.json"))
    token_path = os.environ.get("GMAIL_TOKEN_JSON", str(_BASE / "gmail_token.json"))
    scopes = ["https://www.googleapis.com/auth/gmail.readonly"]

    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, scopes)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(cred_path):
                raise FileNotFoundError(f"Gmail credentials not found at {cred_path}")
            flow = InstalledAppFlow.from_client_secrets_file(cred_path, scopes)
            creds = flow.run_local_server(port=0)
        with open(token_path, "w") as f:
            f.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)


def _gmail_get_body(payload: dict) -> str:
    """Extract plain text body from Gmail message payload."""
    import base64
    body = (payload.get("body") or {}).get("data")
    if body:
        try:
            return base64.urlsafe_b64decode(body).decode("utf-8", errors="replace")
        except Exception:
            pass
    for part in payload.get("parts") or []:
        if part.get("mimeType") == "text/plain":
            b = (part.get("body") or {}).get("data")
            if b:
                try:
                    return base64.urlsafe_b64decode(b).decode("utf-8", errors="replace")
                except Exception:
                    pass
    for part in payload.get("parts") or []:
        if part.get("mimeType") == "text/html":
            b = (part.get("body") or {}).get("data")
            if b:
                try:
                    return _html_to_plain(
                        base64.urlsafe_b64decode(b).decode("utf-8", errors="replace")
                    )
                except Exception:
                    pass
    return ""


def _search_gmail(
    query: str,
    max_results: int,
    after_date: str | None = None,
    include_body: bool = False,
) -> list[str]:
    service = _gmail_service()
    q = query
    if after_date:
        q = f"{query} after:{after_date.replace('-', '/')}"
    limit = min(max_results, 25 if include_body else 100)
    results = (
        service.users()
        .messages()
        .list(userId="me", q=q, maxResults=limit)
        .execute()
    )
    messages = results.get("messages", [])
    out = []
    for m in messages:
        msg = (
            service.users()
            .messages()
            .get(
                userId="me",
                id=m["id"],
                format="full" if include_body else "metadata",
                metadataHeaders=["From", "Subject", "Date"] if not include_body else None,
            )
            .execute()
        )
        payload = msg.get("payload", {}) or {}
        headers = {h["name"].lower(): h["value"] for h in payload.get("headers", [])}
        if include_body:
            body = _gmail_get_body(payload)
            out.append(
                _fmt_email_pretty(
                    headers.get("from", ""),
                    headers.get("subject", ""),
                    headers.get("date", ""),
                    body,
                )
            )
        else:
            out.append(
                _fmt(
                    headers.get("from", ""),
                    headers.get("subject", ""),
                    headers.get("date", ""),
                    (msg.get("snippet") or "").replace("\n", " ")[:200],
                )
            )
    return out


# ---- Outlook (Microsoft Graph) ----
def _outlook_token():
    import msal

    client_id = os.environ.get("OUTLOOK_CLIENT_ID")
    if not client_id:
        raise FileNotFoundError("Set OUTLOOK_CLIENT_ID (Azure app registration, public client).")
    tenant = os.environ.get("OUTLOOK_TENANT_ID", "common")
    cache_path = os.environ.get("OUTLOOK_TOKEN_CACHE", str(_BASE / "outlook_token_cache.bin"))
    scopes = ["https://graph.microsoft.com/Mail.Read"]

    # Redirect port: must match a redirect URI in Azure (e.g. http://localhost:8400).
    # Azure Portal → App registration → Authentication → Mobile and desktop applications → Add http://localhost:PORT
    redirect_port = int(os.environ.get("OUTLOOK_REDIRECT_PORT", "8400"))

    cache = msal.SerializableTokenCache()
    if os.path.exists(cache_path):
        cache.deserialize(open(cache_path, "r").read())
    app = msal.PublicClientApplication(client_id, authority=f"https://login.microsoftonline.com/{tenant}", token_cache=cache)
    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent(scopes, account=accounts[0])
    else:
        result = app.acquire_token_interactive(scopes, port=redirect_port)
    if not result:
        raise RuntimeError("Failed to get Outlook token.")
    open(cache_path, "w").write(cache.serialize())
    return result["access_token"]


def _outlook_get_message_body(token: str, message_id: str) -> str:
    """Fetch a single message's body (Graph often 500s when body is requested with $search)."""
    url = (
        "https://graph.microsoft.com/v1.0/me/messages/"
        + urllib.parse.quote(message_id, safe="")
        + "?$select=body"
    )
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req) as resp:
        data = json.load(resp)
    body_obj = data.get("body") or {}
    return (body_obj.get("content") or "") if isinstance(body_obj, dict) else ""


def _search_outlook(
    query: str,
    max_results: int,
    after_date: str | None = None,
    include_body: bool = False,
) -> list[str]:
    token = _outlook_token()
    # Graph does not support $search and $filter together; we filter by date client-side
    top = min(max_results * 2 if after_date else max_results, 100)  # fetch extra if filtering
    params = [
        ("$search", f'"{query}"'),
        ("$top", str(top)),
        ("$select", "id,from,subject,receivedDateTime,bodyPreview"),
    ]
    url = "https://graph.microsoft.com/v1.0/me/messages?" + urllib.parse.urlencode(
        params, safe="$,()", quote_via=urllib.parse.quote
    )
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req) as resp:
        data = json.load(resp)
    cutoff = f"{after_date}T00:00:00Z" if after_date else None
    out = []
    for m in data.get("value", []):
        received = m.get("receivedDateTime") or ""
        if cutoff and received < cutoff:
            continue
        if len(out) >= max_results:
            break
        from_obj = m.get("from", {}) or {}
        from_addr = from_obj.get("emailAddress", {}) or {}
        from_str = from_addr.get("address", "") or (from_addr.get("name", "") or "")
        if include_body:
            body = _outlook_get_message_body(token, m["id"])
            out.append(
                _fmt_email_pretty(from_str, m.get("subject", ""), received, body)
            )
        else:
            out.append(
                _fmt(
                    from_str,
                    m.get("subject", ""),
                    received,
                    (m.get("bodyPreview") or "").replace("\n", " ")[:200],
                )
            )
    return out


# ---- MCP ----
mcp = FastMCP("Email (Gmail + Outlook)")


@mcp.tool()
def search_emails(
    provider: str,
    query: str,
    max_results: int = 50,
    after_date: str | None = None,
    include_body: bool = False,
) -> str:
    """
    Search email. provider: 'gmail' or 'outlook'. query: search string (e.g. 'tax', 'columbia university').
    after_date: optional YYYY-MM-DD to only include messages on or after this date (e.g. acceptance date).
    include_body: if True, fetch full message body and return pretty-formatted output (max 25 messages).
    Returns From, Subject, Date, and snippet or full body per message.
    """
    try:
        if provider.lower() == "gmail":
            lines = _search_gmail(query, max_results, after_date, include_body)
        elif provider.lower() == "outlook":
            lines = _search_outlook(query, max_results, after_date, include_body)
        else:
            return f"Unknown provider: {provider}. Use 'gmail' or 'outlook'."
    except FileNotFoundError as e:
        return f"Config error: {e}"
    except Exception as e:
        return f"Error: {e}"
    if not lines:
        return "No messages found for that query."
    separator = "\n\n---\n\n" if include_body else "\n---\n"
    return separator.join(lines)


if __name__ == "__main__":
    mcp.run(transport="stdio")
