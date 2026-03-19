"""
Outlook (Microsoft Graph) client: token cache(s) and search, return rows with webLink.
"""
from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request

from mcp_email.config import get_all_outlook_cache_paths


def outlook_token_for_cache(cache_path: str) -> tuple[str, str]:
    """Get (access_token, account_email) for one Outlook token cache. Raises if no token."""
    import msal

    client_id = os.environ.get("OUTLOOK_CLIENT_ID")
    if not client_id:
        raise FileNotFoundError("Set OUTLOOK_CLIENT_ID (Azure app registration, public client).")
    tenant = os.environ.get("OUTLOOK_TENANT_ID", "common")
    scopes = ["https://graph.microsoft.com/Mail.Read"]
    redirect_port = int(os.environ.get("OUTLOOK_REDIRECT_PORT", "8400"))

    cache = msal.SerializableTokenCache()
    if os.path.exists(cache_path):
        cache.deserialize(open(cache_path, "r").read())
    app = msal.PublicClientApplication(
        client_id, authority=f"https://login.microsoftonline.com/{tenant}", token_cache=cache
    )
    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent(scopes, account=accounts[0])
    else:
        result = app.acquire_token_interactive(scopes, port=redirect_port)
    if not result:
        raise RuntimeError("Failed to get Outlook token.")
    open(cache_path, "w").write(cache.serialize())
    email = (accounts[0].get("username") or "") if accounts else ""
    return result["access_token"], email


def outlook_all_tokens() -> list[tuple[str, str]]:
    """Returns list of (account_email, access_token) for all configured Outlook caches. Deduplicated by email so the same account is not searched twice."""
    paths = get_all_outlook_cache_paths()
    result: list[tuple[str, str]] = []
    seen_emails: set[str] = set()
    last_error: Exception | None = None
    for cache_path in paths:
        try:
            token, email = outlook_token_for_cache(cache_path)
            key = (email or cache_path).strip().lower()
            if key and key not in seen_emails:
                seen_emails.add(key)
                result.append((email or cache_path, token))
        except Exception as e:
            last_error = e
            if len(paths) == 1:
                raise
            continue
    return result


def get_outlook_account_emails() -> list[str]:
    """Return list of Outlook account emails that will be searched (one per token cache). May trigger re-auth if tokens expired."""
    try:
        tokens = outlook_all_tokens()
        return [email for email, _ in tokens]
    except Exception:
        return []


def search_outlook_rows_with_token(
    token: str,
    account_email: str,
    query: str,
    max_results: int,
    after_date: str | None = None,
) -> list[dict]:
    """Search one Outlook account (given token); returns rows with provider, account, from, subject, etc."""
    top = min(max_results * 2 if after_date else max_results, 100)
    params = [
        ("$search", f'"{query}"'),
        ("$top", str(top)),
        ("$select", "id,from,subject,receivedDateTime,bodyPreview,webLink"),
    ]
    url = "https://graph.microsoft.com/v1.0/me/messages?" + urllib.parse.urlencode(
        params, safe="$,()", quote_via=urllib.parse.quote
    )
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req) as resp:
        data = json.load(resp)
    cutoff = f"{after_date}T00:00:00Z" if after_date else None
    rows: list[dict] = []
    for m in data.get("value", []):
        if len(rows) >= max_results:
            break
        received = m.get("receivedDateTime") or ""
        if cutoff and received < cutoff:
            continue
        from_obj = m.get("from", {}) or {}
        from_addr = from_obj.get("emailAddress", {}) or {}
        from_str = from_addr.get("address", "") or (from_addr.get("name", "") or "")
        mid = m.get("id", "")
        snippet = (m.get("bodyPreview") or "").replace("\n", " ").strip()[:300]
        link = m.get("webLink") or f"https://outlook.live.com/mail/0/inbox/id/{mid}"
        rows.append({
            "provider": "Outlook",
            "account": account_email,
            "from": from_str,
            "subject": m.get("subject", ""),
            "date": received,
            "snippet": snippet,
            "link": link,
            "query_used": query,
        })
    return rows


def search_outlook_rows(
    query: str,
    max_results: int,
    after_date: str | None = None,
) -> list[dict]:
    """Search all configured Outlook accounts; returns merged rows with account column."""
    tokens = outlook_all_tokens()
    if not tokens:
        raise RuntimeError(
            "Outlook: no valid token. One or both caches may have expired. "
            "Run the MCP again and complete browser sign-in when prompted, or run "
            "the email server and trigger an Outlook search to re-auth."
        )
    rows: list[dict] = []
    for account_email, token in tokens:
        rows.extend(
            search_outlook_rows_with_token(token, account_email, query, max_results, after_date)
        )
    return rows
