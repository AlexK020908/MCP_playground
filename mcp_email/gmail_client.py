"""
Gmail API client: authenticate and search, return rows with link/snippet.
"""
from __future__ import annotations

import os

from mcp_email.config import get_gmail_cred_path, get_gmail_token_path


def get_gmail_service():
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    cred_path = get_gmail_cred_path()
    token_path = get_gmail_token_path()
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


def search_gmail_rows(
    query: str,
    max_results: int,
    after_date: str | None = None,
) -> list[dict]:
    """Search Gmail; return list of dicts with provider, from, subject, date, snippet, link, query_used, account."""
    import os
    service = get_gmail_service()
    q = query
    if after_date:
        q = f"{query} after:{after_date.replace('-', '/')}"
    limit = min(max_results, 100)
    results = (
        service.users()
        .messages()
        .list(userId="me", q=q, maxResults=limit)
        .execute()
    )
    rows: list[dict] = []
    for m in results.get("messages", []):
        mid = m["id"]
        try:
            msg = (
                service.users()
                .messages()
                .get(
                    userId="me",
                    id=mid,
                    format="metadata",
                    metadataHeaders=["From", "Subject", "Date"],
                )
                .execute()
            )
        except Exception:
            continue
        payload = msg.get("payload", {}) or {}
        headers = {h["name"].lower(): h["value"] for h in payload.get("headers", [])}
        snippet = (msg.get("snippet") or "").replace("\n", " ").strip()[:300]
        rows.append({
            "provider": "Gmail",
            "account": "",
            "from": headers.get("from", ""),
            "subject": headers.get("subject", ""),
            "date": headers.get("date", ""),
            "snippet": snippet,
            "link": f"https://mail.google.com/mail/u/0/#inbox/{mid}",
            "query_used": query,
        })
    return rows
