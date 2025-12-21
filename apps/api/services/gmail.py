import logging
import re
from datetime import datetime, timezone
import base64
from typing import Optional

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from email.utils import parsedate_to_datetime
from packages.shared.constants import EmailStatus

logger = logging.getLogger(__name__)

def _parse_auth_results(auth_results: str) -> dict[str, str]:
    """Parse Authentication-Results header to extract SPF, DKIM, DMARC status."""
    result = {"spf": None, "dkim": None, "dmarc": None}
    
    if not auth_results:
        return result
    
    auth_lower = auth_results.lower()
    
    # Parse SPF
    if "spf=pass" in auth_lower:
        result["spf"] = "PASS"
    elif "spf=fail" in auth_lower or "spf=softfail" in auth_lower:
        result["spf"] = "FAIL"
    elif "spf=neutral" in auth_lower:
        result["spf"] = "NEUTRAL"
    elif "spf=none" in auth_lower:
        result["spf"] = "NONE"
    
    # Parse DKIM
    if "dkim=pass" in auth_lower:
        result["dkim"] = "PASS"
    elif "dkim=fail" in auth_lower:
        result["dkim"] = "FAIL"
    elif "dkim=neutral" in auth_lower:
        result["dkim"] = "NEUTRAL"
    elif "dkim=none" in auth_lower:
        result["dkim"] = "NONE"
    
    # Parse DMARC
    if "dmarc=pass" in auth_lower:
        result["dmarc"] = "PASS"
    elif "dmarc=fail" in auth_lower:
        result["dmarc"] = "FAIL"
    elif "dmarc=none" in auth_lower:
        result["dmarc"] = "NONE"
    
    return result


def _extract_sender_ip(received_headers: list[str]) -> str | None:
    """Extract originating sender IP from Received headers.
    
    Iterates headers in reverse (bottom-to-top) to find the originating IP,
    as the bottommost Received header is added by the first server to receive
    the email and is most likely to contain the actual sender's IP.
    """
    
    for received in reversed(received_headers):
        # Look for IP patterns in square brackets
        ip_match = re.search(r'\[(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\]', received)
        if ip_match:
            return ip_match.group(1)
    return None


def _extract_attachments(payload: dict) -> str | None:
    """Extract attachment filenames from email payload."""
    attachments = []
    
    def walk_parts(parts):
        for part in parts:
            filename = part.get("filename")
            if filename:
                attachments.append(filename)
            if "parts" in part:
                walk_parts(part["parts"])
    
    if "parts" in payload:
        walk_parts(payload["parts"])
    
    return ", ".join(attachments) if attachments else None


def _parse_email_date(date_str: str) -> datetime | None:
    """Parse email Date header to datetime."""
    
    if not date_str:
        return None
    
    try:
        dt = parsedate_to_datetime(date_str)
        # Convert to naive UTC datetime for PostgreSQL
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    except Exception:
        return None



def _decode_base64url(data: str) -> str:
    """Decode base64url-encoded string safely."""
    if not data:
        return ""

    try:
        # Gmail uses base64url without padding
        padding = "=" * (-len(data) % 4)
        return base64.urlsafe_b64decode(data + padding).decode("utf-8", errors="replace")
    except Exception:
        return ""


def _extract_email_body(payload: dict) -> dict[str, Optional[str]]:
    """
    Extract text/plain and text/html bodies from a Gmail message payload.

    Prefers HTML when available. Ignores attachments and inline images.
    Safe against malformed MIME structures.
    """

    result = {
        "text": None,
        "html": None,
    }

    def walk(part: dict):
        # Stop early if we already have both
        if result["text"] and result["html"]:
            return

        if not isinstance(part, dict):
            return

        mime_type = part.get("mimeType", "").lower()
        body = part.get("body", {}) or {}

        # Skip attachments
        if part.get("filename"):
            return

        # Decode body if present
        data = body.get("data")
        if data and mime_type in ("text/plain", "text/html"):
            decoded = _decode_base64url(data)

            if mime_type == "text/plain" and not result["text"]:
                logger.debug("Selected text/plain body")
                result["text"] = decoded

            elif mime_type == "text/html" and not result["html"]:
                logger.debug("Selected text/html body")
                result["html"] = decoded

        # Recurse into sub-parts
        for subpart in part.get("parts", []) or []:
            walk(subpart)

    # Start traversal from top-level payload
    walk(payload)

    return result

def fetch_gmail_messages(access_token: str, limit: int = 20) -> list[dict]:
    """Fetch emails from Gmail API using batch requests for better performance."""
    try:
        creds = Credentials(token=access_token)
        service = build("gmail", "v1", credentials=creds)

        # List messages (include spam/trash for complete view)
        results = service.users().messages().list(userId="me", maxResults=limit, includeSpamTrash=True).execute()
        messages = results.get("messages", [])

        if not messages:
            return []

        email_data = []

        def callback(request_id, response, exception):
            """Callback for batch request processing."""
            if exception:
                logger.error(f"Error fetching message {request_id}: {exception}")
                return
            
            try:
                payload = response.get("payload", {})
                headers = payload.get("headers", [])
                
                # Create a dict for easier header lookup
                headers_dict = {h["name"].lower(): h["value"] for h in headers}
                
                # Essential fields
                subject = headers_dict.get("subject", "(No Subject)")
                sender = headers_dict.get("from", "Unknown")
                recipient = headers_dict.get("to", "Unknown")
                snippet = response.get("snippet", "")
                
                # Timestamp
                date_str = headers_dict.get("date")
                received_at = _parse_email_date(date_str)
                
                # Authentication status
                auth_results = headers_dict.get("authentication-results", "")
                auth_status = _parse_auth_results(auth_results)
                
                # Sender IP from Received headers
                received_headers = [h["value"] for h in headers if h["name"].lower() == "received"]
                sender_ip = _extract_sender_ip(received_headers)
                
                # Attachments
                attachment_info = _extract_attachments(payload)
                
                # Check if email is in SPAM folder
                status = EmailStatus.PENDING
                if "SPAM" in response.get("labelIds", []):
                    status = EmailStatus.SPAM

                email_data.append({
                    "sender": sender,
                    "recipient": recipient,
                    "subject": subject,
                    "body_preview": snippet,
                    "message_id": response["id"],
                    "received_at": received_at,
                    "spf_status": auth_status["spf"],
                    "dkim_status": auth_status["dkim"],
                    "dmarc_status": auth_status["dmarc"],
                    "sender_ip": sender_ip,
                    "attachment_info": attachment_info,
                    "status": status,
                })
            except Exception as e:
                logger.warning(f"Failed to parse message in batch callback: {e}")

        # Use batch request for better performance
        batch = service.new_batch_http_request(callback=callback)
        for msg in messages:
            batch.add(service.users().messages().get(userId="me", id=msg["id"], format="full"))
        
        batch.execute()
            
        return email_data
    except Exception as e:
        logger.error(f"Failed to fetch Gmail messages: {e}")
        return []
