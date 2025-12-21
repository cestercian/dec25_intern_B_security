"""
Unified Gmail Service - Best of Both Worlds

This module combines the best features from:
- apps/api/services/gmail.py: Batch requests, auth parsing, sender IP extraction
- apps/worker/ingest/main.py: Pydantic models, URL extraction, structured output

Design Principles:
1. Type Safety: Pydantic models for all data structures
2. Performance: Batch API requests for fetching multiple emails
3. Security Analysis: SPF/DKIM/DMARC parsing, URL extraction, attachment metadata
4. Reliability: Comprehensive error handling with graceful degradation
5. Observability: Structured logging with trace context support
"""

import base64
import logging
import re
import socket
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Optional

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pydantic import BaseModel, Field

from packages.shared.constants import EmailStatus

# --- Logging Setup ---
logger = logging.getLogger(__name__)


# =============================================================================
# SECTION 1: PYDANTIC MODELS
# =============================================================================
# Using Pydantic provides:
# - Runtime type validation
# - Automatic serialization (model_dump(), model_dump_json())
# - Clear schema documentation
# - IDE autocomplete support
# =============================================================================


class AttachmentMetadata(BaseModel):
    """
    Metadata for an email attachment (content is NOT downloaded for security).
    
    Attributes:
        filename: Original filename of the attachment
        mime_type: MIME type (e.g., "application/pdf", "image/png")
        size: Size in bytes
        attachment_id: Gmail's internal attachment ID (for later retrieval if needed)
    """
    filename: str
    mime_type: str
    size: int
    attachment_id: Optional[str] = None


class EmailAuthenticationStatus(BaseModel):
    """
    Email authentication results from SPF, DKIM, and DMARC checks.
    
    These are critical for detecting spoofed/phishing emails:
    - SPF: Sender Policy Framework (validates sender IP is authorized)
    - DKIM: DomainKeys Identified Mail (validates email wasn't modified)
    - DMARC: Domain-based Message Auth (policy for handling SPF/DKIM failures)
    
    Possible values: "PASS", "FAIL", "NEUTRAL", "NONE", or None if not present
    """
    spf: Optional[str] = None
    dkim: Optional[str] = None
    dmarc: Optional[str] = None


class StructuredEmail(BaseModel):
    """
    Complete structured representation of a Gmail message.
    
    This is the unified output format that combines all extracted data
    needed for security analysis and display.
    """
    # Core identifiers
    message_id: str = Field(description="Gmail's unique message ID")
    
    # Envelope information
    sender: str = Field(description="From header value")
    recipient: str = Field(description="To header value")
    subject: str = Field(description="Email subject line")
    
    # Body content
    body_preview: str = Field(description="Gmail snippet (first ~100 chars)")
    body_text: Optional[str] = Field(default=None, description="Full text/plain body")
    body_html: Optional[str] = Field(default=None, description="Full text/html body")
    
    # Timestamps
    received_at: Optional[datetime] = Field(default=None, description="Parsed Date header")
    
    # Security analysis fields
    auth_status: EmailAuthenticationStatus = Field(
        default_factory=EmailAuthenticationStatus,
        description="SPF/DKIM/DMARC results"
    )
    sender_ip: Optional[str] = Field(default=None, description="Originating IP from Received headers")
    
    # Content analysis
    extracted_urls: list[str] = Field(default_factory=list, description="URLs found in body")
    attachments: list[AttachmentMetadata] = Field(default_factory=list, description="Attachment metadata")
    
    # Classification
    status: EmailStatus = Field(default=EmailStatus.PENDING, description="Email status (PENDING, SPAM, etc.)")
    gmail_labels: list[str] = Field(default_factory=list, description="Gmail label IDs")
    
    # Legacy compatibility fields (for backwards compatibility with existing code)
    @property
    def spf_status(self) -> Optional[str]:
        return self.auth_status.spf
    
    @property
    def dkim_status(self) -> Optional[str]:
        return self.auth_status.dkim
    
    @property
    def dmarc_status(self) -> Optional[str]:
        return self.auth_status.dmarc
    
    @property
    def attachment_info(self) -> Optional[str]:
        """Comma-separated attachment filenames for legacy compatibility."""
        if not self.attachments:
            return None
        return ", ".join(att.filename for att in self.attachments)


# =============================================================================
# SECTION 2: EMAIL PARSING UTILITIES
# =============================================================================
# These pure functions handle parsing different parts of the email.
# They are stateless and can be easily unit tested.
# =============================================================================


def parse_auth_results(auth_results: str) -> EmailAuthenticationStatus:
    """
    Parse the Authentication-Results header to extract SPF, DKIM, DMARC status.
    
    The Authentication-Results header is added by the receiving mail server
    and contains the results of email authentication checks.
    
    Example header:
        Authentication-Results: mx.google.com;
            dkim=pass header.i=@example.com;
            spf=pass smtp.mailfrom=example.com;
            dmarc=pass
    
    Args:
        auth_results: The raw Authentication-Results header value
        
    Returns:
        EmailAuthenticationStatus with parsed results
    """
    result = EmailAuthenticationStatus()
    
    if not auth_results:
        return result
    
    auth_lower = auth_results.lower()
    
    # SPF (Sender Policy Framework)
    # Checks if the sending server's IP is authorized to send for the domain
    if "spf=pass" in auth_lower:
        result.spf = "PASS"
    elif "spf=fail" in auth_lower or "spf=softfail" in auth_lower:
        result.spf = "FAIL"
    elif "spf=neutral" in auth_lower:
        result.spf = "NEUTRAL"
    elif "spf=none" in auth_lower:
        result.spf = "NONE"
    
    # DKIM (DomainKeys Identified Mail)
    # Cryptographic signature to verify email wasn't tampered with
    if "dkim=pass" in auth_lower:
        result.dkim = "PASS"
    elif "dkim=fail" in auth_lower:
        result.dkim = "FAIL"
    elif "dkim=neutral" in auth_lower:
        result.dkim = "NEUTRAL"
    elif "dkim=none" in auth_lower:
        result.dkim = "NONE"
    
    # DMARC (Domain-based Message Authentication)
    # Policy layer that combines SPF and DKIM with domain alignment
    if "dmarc=pass" in auth_lower:
        result.dmarc = "PASS"
    elif "dmarc=fail" in auth_lower:
        result.dmarc = "FAIL"
    elif "dmarc=none" in auth_lower:
        result.dmarc = "NONE"
    
    return result


def extract_sender_ip(received_headers: list[str]) -> Optional[str]:
    """
    Extract the originating sender IP from Received headers.
    
    Email servers add a Received header each time the email passes through.
    The headers are ordered top-to-bottom (newest first), so we iterate
    in REVERSE to find the bottommost header, which was added by the first
    server to receive the email and most likely contains the actual sender's IP.
    
    Example Received header:
        Received: from mail.example.com ([192.168.1.100])
            by mx.google.com with SMTP id abc123
    
    Args:
        received_headers: List of Received header values
        
    Returns:
        IP address string or None if not found
    """
    # IPv4 pattern in square brackets (common format)
    ipv4_pattern = re.compile(r'\[(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\]')
    
    for received in reversed(received_headers):
        match = ipv4_pattern.search(received)
        if match:
            ip = match.group(1)
            # Skip private/local IPs as they're not the actual sender
            if not ip.startswith(('10.', '192.168.', '127.')):
                return ip
    
    return None


def decode_base64url(data: str) -> str:
    """
    Decode Gmail's base64url-encoded data safely.
    
    Gmail uses base64url encoding (URL-safe variant) WITHOUT padding.
    Standard base64 decoders expect padding, so we add it.
    
    Args:
        data: Base64url encoded string
        
    Returns:
        Decoded UTF-8 string, or empty string on error
    """
    if not data:
        return ""
    
    try:
        # Add padding to make length a multiple of 4
        padding = "=" * (-len(data) % 4)
        decoded = base64.urlsafe_b64decode(data + padding)
        return decoded.decode("utf-8", errors="replace")
    except Exception as e:
        logger.debug(f"Base64 decode failed: {e}")
        return ""


def parse_email_date(date_str: str) -> Optional[datetime]:
    """
    Parse RFC 2822 email Date header to a Python datetime.
    
    Email dates can have various timezone formats. We normalize
    to naive UTC datetime for consistent storage in PostgreSQL.
    
    Example date: "Mon, 21 Dec 2025 10:30:00 +0530"
    
    Args:
        date_str: Raw Date header value
        
    Returns:
        Naive UTC datetime, or None if parsing fails
    """
    if not date_str:
        return None
    
    try:
        dt = parsedate_to_datetime(date_str)
        # Convert to UTC and remove timezone info for database storage
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    except Exception as e:
        logger.debug(f"Date parse failed for '{date_str}': {e}")
        return None


def extract_urls(text: str) -> list[str]:
    """
    Extract URLs from email body text for threat analysis.
    
    URLs are a primary vector for phishing attacks. We extract them
    for analysis by security tools (VirusTotal, Google Safe Browsing, etc.).
    
    Args:
        text: Plain text or HTML content
        
    Returns:
        Deduplicated list of URLs found
    """
    if not text:
        return []
    
    # Pattern matches http://, https://, and www. URLs
    # Stops at whitespace, quotes, or angle brackets
    pattern = r'https?://[^\s<>"\']+|www\.[^\s<>"\']+' 
    
    urls = re.findall(pattern, text)
    
    # Clean up trailing punctuation that might be captured
    cleaned = []
    for url in urls:
        # Remove trailing punctuation that's likely not part of the URL
        url = url.rstrip('.,;:!?)>')
        if url:
            cleaned.append(url)
    
    # Return unique URLs while preserving order
    return list(dict.fromkeys(cleaned))


# =============================================================================
# SECTION 3: EMAIL CONTENT EXTRACTION
# =============================================================================
# These functions parse the Gmail message payload structure.
# Gmail uses nested MIME parts for multipart messages.
# =============================================================================


class EmailContentExtractor:
    """
    Extracts all content from a Gmail message payload.
    
    Gmail messages use a nested MIME structure:
    - multipart/mixed (attachments)
        - multipart/alternative (text/html versions)
            - text/plain
            - text/html
        - application/pdf (attachment)
    
    This class walks the entire tree to extract:
    - Text and HTML bodies
    - Attachment metadata (WITHOUT downloading content)
    - URLs from body content
    """
    
    def __init__(self):
        self.text_body: Optional[str] = None
        self.html_body: Optional[str] = None
        self.urls: set[str] = set()
        self.attachments: list[AttachmentMetadata] = []
    
    def walk_parts(self, part: dict) -> None:
        """
        Recursively walk MIME parts to extract content.
        
        Args:
            part: A Gmail payload part dictionary
        """
        if not isinstance(part, dict):
            return
        
        mime_type = part.get("mimeType", "").lower()
        body = part.get("body", {}) or {}
        filename = part.get("filename")
        data = body.get("data")
        
        # 1. Handle attachments (metadata only, NOT content)
        # Security: We never download attachment content to prevent malware execution
        if filename and body.get("attachmentId"):
            self.attachments.append(AttachmentMetadata(
                filename=filename,
                mime_type=mime_type,
                size=body.get("size", 0),
                attachment_id=body.get("attachmentId")
            ))
            return  # Don't process attachment body
        
        # 2. Handle body content
        if data and mime_type in ("text/plain", "text/html"):
            decoded = decode_base64url(data)
            
            if mime_type == "text/plain" and not self.text_body:
                self.text_body = decoded
                # Extract URLs from plain text
                self.urls.update(extract_urls(decoded))
            
            elif mime_type == "text/html" and not self.html_body:
                self.html_body = decoded
                # Extract URLs from HTML
                self.urls.update(extract_urls(decoded))
        
        # 3. Recurse into nested parts
        for subpart in part.get("parts", []) or []:
            self.walk_parts(subpart)
    
    def extract(self, payload: dict) -> tuple[Optional[str], Optional[str], list[str], list[AttachmentMetadata]]:
        """
        Extract all content from a Gmail message payload.
        
        Args:
            payload: The 'payload' field from a Gmail message response
            
        Returns:
            Tuple of (text_body, html_body, urls, attachments)
        """
        self.walk_parts(payload)
        return (
            self.text_body,
            self.html_body,
            list(self.urls),
            self.attachments
        )


# =============================================================================
# SECTION 4: GMAIL SERVICE CLASS
# =============================================================================
# Main class that orchestrates fetching and parsing emails.
# Uses batch requests for performance.
# =============================================================================


class GmailService:
    """
    Unified Gmail service for fetching and parsing emails.
    
    Combines the best features from both implementations:
    - Batch requests for fetching multiple emails efficiently
    - Full security header parsing (SPF, DKIM, DMARC)
    - URL extraction for threat analysis  
    - Pydantic models for type safety
    - Comprehensive error handling
    
    Usage:
        service = GmailService(access_token="user_oauth_token")
        emails = service.fetch_emails(limit=50)
        for email in emails:
            print(email.subject, email.auth_status.spf)
    """
    
    def __init__(
        self,
        access_token: str,
        timeout: float = 10.0,
        trace_context: Optional[str] = None
    ):
        """
        Initialize the Gmail service.
        
        Args:
            access_token: OAuth2 access token from user authentication
            timeout: Socket timeout for API calls (default 10s)
            trace_context: Cloud Trace context for distributed tracing
        """
        self.access_token = access_token
        self.timeout = timeout
        self.trace_context = trace_context
        
        # Set socket timeout to prevent hanging connections
        socket.setdefaulttimeout(timeout)
        
        # Build the Gmail API service
        creds = Credentials(token=access_token)
        self.service = build("gmail", "v1", credentials=creds)
        
        logger.info("GmailService initialized", extra={"trace_context": trace_context})
    
    def _parse_message(self, response: dict) -> Optional[StructuredEmail]:
        """
        Parse a Gmail API message response into a StructuredEmail.
        
        Args:
            response: Raw Gmail API message.get() response
            
        Returns:
            StructuredEmail or None if parsing fails
        """
        try:
            payload = response.get("payload", {})
            headers = payload.get("headers", [])
            
            # Build headers dict for easy lookup (case-insensitive)
            headers_dict = {h["name"].lower(): h["value"] for h in headers}
            
            # === Core Fields ===
            message_id = response.get("id", "unknown")
            subject = headers_dict.get("subject", "(No Subject)")
            sender = headers_dict.get("from", "Unknown")
            recipient = headers_dict.get("to", "Unknown")
            snippet = response.get("snippet", "")
            
            # === Timestamp ===
            date_str = headers_dict.get("date")
            received_at = parse_email_date(date_str)
            
            # === Security: Authentication Status ===
            auth_header = headers_dict.get("authentication-results", "")
            auth_status = parse_auth_results(auth_header)
            
            # === Security: Sender IP ===
            received_headers = [h["value"] for h in headers if h["name"].lower() == "received"]
            sender_ip = extract_sender_ip(received_headers)
            
            # === Content Extraction ===
            extractor = EmailContentExtractor()
            text_body, html_body, urls, attachments = extractor.extract(payload)
            
            # === Classification ===
            label_ids = response.get("labelIds", [])
            status = EmailStatus.PENDING
            if "SPAM" in label_ids:
                status = EmailStatus.SPAM
            
            return StructuredEmail(
                message_id=message_id,
                sender=sender,
                recipient=recipient,
                subject=subject,
                body_preview=snippet,
                body_text=text_body,
                body_html=html_body,
                received_at=received_at,
                auth_status=auth_status,
                sender_ip=sender_ip,
                extracted_urls=urls,
                attachments=attachments,
                status=status,
                gmail_labels=label_ids,
            )
            
        except Exception as e:
            logger.warning(f"Failed to parse message: {e}", exc_info=True)
            return None
    
    def fetch_emails(
        self,
        limit: int = 20,
        include_spam_trash: bool = True
    ) -> list[StructuredEmail]:
        """
        Fetch emails from Gmail using batch requests for performance.
        
        Batch requests send multiple API calls in a single HTTP request,
        significantly reducing latency compared to sequential calls.
        
        Args:
            limit: Maximum number of emails to fetch (1-100)
            include_spam_trash: Whether to include SPAM and TRASH folders
            
        Returns:
            List of StructuredEmail objects
        """
        try:
            logger.info(
                f"Fetching up to {limit} emails",
                extra={"trace_context": self.trace_context, "include_spam_trash": include_spam_trash}
            )
            
            # Step 1: List message IDs
            results = (
                self.service.users()
                .messages()
                .list(userId="me", maxResults=limit, includeSpamTrash=include_spam_trash)
                .execute()
            )
            
            messages = results.get("messages", [])
            if not messages:
                logger.info("No messages found")
                return []
            
            logger.info(f"Found {len(messages)} messages, fetching full content")
            
            # Step 2: Batch fetch full message content
            email_data: list[StructuredEmail] = []
            errors: list[str] = []
            
            def batch_callback(request_id: str, response: dict, exception: Exception):
                """Callback for each message in the batch request."""
                if exception:
                    logger.error(f"Error fetching message {request_id}: {exception}")
                    errors.append(request_id)
                    return
                
                parsed = self._parse_message(response)
                if parsed:
                    email_data.append(parsed)
            
            # Create batch request
            batch = self.service.new_batch_http_request(callback=batch_callback)
            
            for msg in messages:
                batch.add(
                    self.service.users().messages().get(
                        userId="me",
                        id=msg["id"],
                        format="full"
                    )
                )
            
            # Execute batch (single HTTP request for all messages!)
            batch.execute()
            
            logger.info(
                f"Fetched {len(email_data)} emails successfully, {len(errors)} errors",
                extra={"trace_context": self.trace_context}
            )
            
            return email_data
            
        except HttpError as e:
            logger.error(f"Gmail API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to fetch Gmail messages: {e}")
            return []
    
    def fetch_by_history(self, history_id: int) -> list[StructuredEmail]:
        """
        Fetch only new messages since a specific history ID.
        
        This is used for incremental sync via Gmail push notifications.
        More efficient than fetching all emails when you only need new ones.
        
        Args:
            history_id: Gmail history ID from push notification
            
        Returns:
            List of new StructuredEmail objects
        """
        try:
            logger.info(f"Fetching history since {history_id}")
            
            # Step 1: Get history changes
            history_response = (
                self.service.users()
                .history()
                .list(userId="me", startHistoryId=history_id)
                .execute()
            )
            
            if "history" not in history_response:
                logger.info("No new history found")
                return []
            
            # Step 2: Collect unique message IDs from history
            message_ids = set()
            for record in history_response.get("history", []):
                if "messagesAdded" in record:
                    for msg in record["messagesAdded"]:
                        if "message" in msg and "id" in msg["message"]:
                            message_ids.add(msg["message"]["id"])
            
            if not message_ids:
                logger.info("No new messages in history")
                return []
            
            logger.info(f"Found {len(message_ids)} new messages in history")
            
            # Step 3: Batch fetch the new messages
            email_data: list[StructuredEmail] = []
            
            def batch_callback(request_id: str, response: dict, exception: Exception):
                if exception:
                    logger.error(f"Error fetching message {request_id}: {exception}")
                    return
                parsed = self._parse_message(response)
                if parsed:
                    email_data.append(parsed)
            
            batch = self.service.new_batch_http_request(callback=batch_callback)
            for msg_id in message_ids:
                batch.add(
                    self.service.users().messages().get(
                        userId="me",
                        id=msg_id,
                        format="full"
                    )
                )
            
            batch.execute()
            
            return email_data
            
        except HttpError as e:
            if e.resp.status == 404:
                logger.warning(f"History ID {history_id} not found (too old)")
                return []
            raise


# =============================================================================
# SECTION 5: CONVENIENCE FUNCTION
# =============================================================================
# Backwards-compatible function for existing code that uses the old interface.
# =============================================================================


def fetch_gmail_messages(
    access_token: str,
    limit: int = 20,
    trace_context: Optional[str] = None
) -> list[dict]:
    """
    Convenience function for backwards compatibility.
    
    Returns dict format compatible with the original gmail.py interface.
    For new code, use GmailService class directly for full features.
    
    Args:
        access_token: OAuth2 access token
        limit: Maximum emails to fetch
        trace_context: Optional trace context for logging
        
    Returns:
        List of email dictionaries in legacy format
    """
    service = GmailService(access_token, trace_context=trace_context)
    emails = service.fetch_emails(limit=limit)
    
    # Convert to legacy dict format
    return [
        {
            "sender": email.sender,
            "recipient": email.recipient,
            "subject": email.subject,
            "body_preview": email.body_preview,
            "message_id": email.message_id,
            "received_at": email.received_at,
            "spf_status": email.spf_status,
            "dkim_status": email.dkim_status,
            "dmarc_status": email.dmarc_status,
            "sender_ip": email.sender_ip,
            "attachment_info": email.attachment_info,
            "status": email.status,
            # New fields available in unified version
            "extracted_urls": email.extracted_urls,
            "gmail_labels": email.gmail_labels,
        }
        for email in emails
    ]
