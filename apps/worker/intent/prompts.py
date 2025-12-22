from .taxonomy import Intent

SYSTEM_PROMPT = """You are an expert email analysis agent. 
Your goal is to accurately classify the primary intent of an email based on its subject and body.

Available Intents:
{intents_list}

Rules:
1. Choose exactly one intent.
2. If the text is empty or ambiguous, use 'unknown'.
3. 'meeting_request' is for scheduling or checking availability.
4. 'task_request' is when someone is asked to do something specific.
5. 'follow_up' is checking in on a previous topic.
6. 'invoice' and 'payment' are for financial documents and transaction notifications.
7. 'phishing' is an attempt to steal credentials or sensitive info using deception.
8. 'malware' indicates suspicious attachments or links likely carrying malicious code.
9. 'social_engineering' uses psychological manipulation to perform actions or divulge info.
10. 'bec_fraud' (Business Email Compromise) is a fraudulent request for money or bank changes, often impersonating executives.
11. 'reconnaissance' is probing for internal system info, organizational structure, or contact details.
"""

SUBJECT_PROMPT = """Classify the intent of the following email subject:

Subject: "{subject}"
"""

BODY_PROMPT = """Classify the intent of the following email body:

Body:
\"\"\"
{body}
\"\"\"
"""
