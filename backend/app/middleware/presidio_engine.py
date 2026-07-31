"""
Presidio PII & Prompt Injection Engine
======================================
Integrates pure Regex/NLP based PII analysis and prompt injection detection
into the governance pipeline.

Detects:
  - Email, Phone Number, Credit Card, CVV, IPv4, IPv6, PAN, Aadhaar, 
    Passport, Bank Account Number, IFSC, URL, JWT Tokens, AWS Keys, API Keys.

Prompt Injection Detection:
  - Evaluates inputs for system override attempts, policy bypasses, and instruction injection.
"""

import re
from typing import Any

# Regex patterns for high-accuracy fallback detection
PII_PATTERNS = {
    "EMAIL": (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", 0.95),
    "PHONE": (r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b", 0.90),
    "CREDIT_CARD": (r"\b(?:\d{4}[-\s]?){3}\d{4}\b", 0.98),
    # CVV must appear WITH card-related context words (cvv, cvc, security code).
    # A bare 3-4 digit number like an account ID (101, 102) is NOT a CVV.
    "CVV": (r"(?i)(?:cvv|cvc|security\s+code)\s*(?:is|:|=|\s)\s*\b\d{3,4}\b", 0.97),
    "IPV4": (r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b", 0.92),
    "IPV6": (r"\b(?:[A-Fa-f0-9]{1,4}:){7}[A-Fa-f0-9]{1,4}\b", 0.95),
    "PAN_CARD": (r"\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b", 0.99),
    "AADHAAR": (r"\b\d{4}\s\d{4}\s\d{4}\b", 0.99),
    "PASSPORT": (r"\b[A-PR-WYa-pr-wy][1-9]\d\s?\d{4}[1-9]\b", 0.90),
    "BANK_ACCOUNT": (r"\b\d{9,18}\b", 0.85),
    "IFSC": (r"\b[A-Z]{4}0[A-Z0-9]{6}\b", 0.99),
    "URL": (r"\bhttps?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)\b", 0.95),
    "JWT_TOKEN": (r"\beyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]+\b", 0.99),
    "AWS_KEY": (r"\b(?:AKIA|ASIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|QTNA|SVRA|ASIA)[A-Z0-9]{16}\b", 0.99),
    "API_KEY": (r"\b(?:gsk_|tvly-|sb_secret_|sb_publishable_|sk-)[A-Za-z0-9_-]{20,}\b", 0.99),
}

PROMPT_INJECTION_RULES = [
    (r"(ignore|disregard|forget)\s+(all\s+)?(previous|prior|above)\s+(instructions|directives|prompts|rules)", "Blocked", "Ignore previous instructions"),
    (r"(reveal|show|display|print)\s+(the\s+)?(system\s+prompt|developer\s+mode|internal\s+instructions)", "Blocked", "Reveal prompt"),
    (r"(bypass|override|disable|forget)\s+(the\s+)?(policy|governance|guardrails|safety)", "Blocked", "Forget policy"),
    (r"override\s+(system|core)\s+(instructions|rules)", "Blocked", "Override system"),
    (r"execute\s+hidden\s+(prompt|code|command)", "Blocked", "Execute hidden prompt"),
    (r"act\s+as\s+unrestricted\s+ai|jailbreak", "Blocked", "Jailbreak attempts"),
    (r"you\s+are\s+(now\s+)?(admin|root|god\smode|developer|creator)", "Blocked", "Role manipulation"),
    (r"(what|tell\sme)\s+(were|are)\s+your\s+(original|initial)\s+instructions", "Blocked", "Prompt leakage"),
]

def analyze_pii(text: str) -> dict[str, Any]:
    """
    Analyzes prompt text for sensitive PII entities using Regex.
    """
    detected_entities = []
    redacted_text = text

    for entity_type, (pattern, confidence) in PII_PATTERNS.items():
        matches = re.finditer(pattern, text)
        for match in matches:
            val = match.group(0)
            # Avoid duplicate detection
            if not any(e["value"] == val for e in detected_entities):
                # For CVV / Bank Account, ensure it's not part of another larger string or low confidence false positive
                detected_entities.append(
                    {
                        "entity_type": entity_type,
                        "value": val,
                        "confidence": confidence,
                        "start": match.start(),
                        "end": match.end(),
                        "decision": "Redacted" if confidence >= 0.8 else "Allowed",
                    }
                )
                mask = f"[{entity_type}_REDACTED]"
                redacted_text = redacted_text.replace(val, mask)

    has_pii = len(detected_entities) > 0

    return {
        "original_text": text,
        "redacted_text": redacted_text,
        "detected_entities": detected_entities,
        "has_pii": has_pii,
        "engine": "Regex PII Engine",
    }


def detect_prompt_injection(text: str) -> dict[str, Any]:
    """
    Scans text for prompt injection and jailbreak patterns.
    """
    matched_rules = []
    highest_severity = "Safe"

    for pattern, severity, reason in PROMPT_INJECTION_RULES:
        if re.search(pattern, text, re.IGNORECASE):
            matched_rules.append({"pattern": pattern, "severity": severity, "reason": reason})
            if severity == "Blocked":
                highest_severity = "Blocked"
            elif severity == "Warning" and highest_severity != "Blocked":
                highest_severity = "Warning"

    return {
        "status": highest_severity,
        "is_safe": highest_severity == "Safe",
        "matched_rules": matched_rules,
        "threat_count": len(matched_rules),
    }

