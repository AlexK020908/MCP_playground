"""
Email MCP — modular Gmail/Outlook search and Excel export.
"""
from mcp_email.config import get_base_path
from mcp_email.gmail_client import search_gmail_rows
from mcp_email.outlook_client import search_outlook_rows
from mcp_email.filters import filter_tax_filing_only
from mcp_email.excel_writer import write_emails_excel

__all__ = [
    "get_base_path",
    "search_gmail_rows",
    "search_outlook_rows",
    "filter_tax_filing_only",
    "write_emails_excel",
]
