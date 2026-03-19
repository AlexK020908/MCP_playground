"""
Email MCP server: search Gmail or Outlook and export results to Excel (with links).
Uses the mcp_email package for all logic. Gmail: gmail_credentials.json → gmail_token.json.
Outlook: OUTLOOK_CLIENT_ID → outlook_token_cache.bin. Optional second account: OUTLOOK_TOKEN_CACHE_2.
"""
from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv
from fastmcp import FastMCP

from mcp_email import (
    filter_tax_filing_only,
    get_base_path,
    search_gmail_rows,
    search_outlook_rows,
    write_emails_excel,
)
from mcp_email.config import set_base_path
from mcp_email.gmail_client import get_gmail_account_email
from mcp_email.outlook_client import get_outlook_account_emails

_BASE = Path(__file__).resolve().parent
load_dotenv(_BASE / ".env")
set_base_path(_BASE)

mcp = FastMCP("Email (Gmail + Outlook)")


@mcp.tool()
def search_emails_to_excel(
    provider: str,
    query: str,
    max_results: int = 50,
    after_date: str | None = None,
    output_path: str | None = None,
    tax_filing_only: bool = False,
) -> str:
    """
    Search Gmail and/or Outlook and write an Excel file with: Provider, Account, From, Subject, Date, Snippet, Open link, Search query used.
    provider: 'gmail', 'outlook', or 'both'. query: search string (e.g. 'tax return OR property tax OR IRS').
    tax_filing_only: if True, keep only emails about property tax, tax filing, or official government tax; drop payment/receipt tax.
    output_path: optional path for the .xlsx file; default is search_emails.xlsx in the server directory.
    Returns the absolute path to the saved file and the number of emails included, or an error message.
    """
    path = Path(output_path).resolve() if output_path else get_base_path() / "search_emails.xlsx"
    if path.suffix.lower() != ".xlsx":
        path = path.with_suffix(".xlsx")
    all_rows: list[dict] = []
    errors: list[str] = []
    p = provider.lower()
    if p in ("gmail", "both"):
        try:
            all_rows.extend(search_gmail_rows(query, max_results, after_date))
        except FileNotFoundError as e:
            errors.append(f"Gmail: {e}")
        except Exception as e:
            errors.append(f"Gmail: {e}")
    if p in ("outlook", "both"):
        try:
            all_rows.extend(search_outlook_rows(query, max_results, after_date))
        except FileNotFoundError as e:
            errors.append(f"Outlook: {e}")
        except Exception as e:
            errors.append(f"Outlook: {e}")
    if p not in ("gmail", "outlook", "both"):
        return f"Unknown provider: {provider}. Use 'gmail', 'outlook', or 'both'."
    before_count = 0
    if tax_filing_only and all_rows:
        before_count = len(all_rows)
        all_rows = filter_tax_filing_only(all_rows)
    if not all_rows:
        return "No messages found for that query. " + (" ".join(errors) if errors else "")
    try:
        write_emails_excel(all_rows, path)
        msg = f"Saved {len(all_rows)} emails to {path}"
        if tax_filing_only and before_count and before_count != len(all_rows):
            msg += f" (filtered from {before_count} to filing/official tax only)"
        return msg
    except Exception as e:
        return f"Error writing Excel: {e}"


@mcp.tool()
def list_email_accounts() -> str:
    """
    Return the email addresses that the MCP uses when searching: Outlook account(s) and Gmail account (if configured).
    Use this to see which mailboxes are included when you run search_emails_to_excel. Outlook may prompt for sign-in if tokens expired.
    """
    parts: list[str] = []
    try:
        outlook_emails = get_outlook_account_emails()
        if outlook_emails:
            parts.append("Outlook: " + ", ".join(outlook_emails))
        else:
            parts.append("Outlook: (none or not configured)")
    except Exception as e:
        parts.append(f"Outlook: error — {e}")
    try:
        gmail_email = get_gmail_account_email()
        if gmail_email:
            parts.append("Gmail: " + gmail_email)
        else:
            parts.append("Gmail: (none or not configured)")
    except Exception as e:
        parts.append(f"Gmail: error — {e}")
    return " ".join(parts)


if __name__ == "__main__":
    mcp.run(transport="stdio")
