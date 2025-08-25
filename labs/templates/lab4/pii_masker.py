import threading
from typing import Dict, Optional

from presidio_analyzer import AnalyzerEngine, RecognizerResult
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig


class PIIMasker:
    """
    Minimal Presidio wrapper to detect and mask PII in text.

    Key Features:
    - Detects various PII entities (SSN, credit cards, emails, phones, etc.)
    - Uses context-aware filtering to reduce false positives
    - Handles common abbreviations (US, UK, CA, etc.) intelligently
    - Properly masks sensitive data with appropriate patterns

    """

    _instance: Optional["PIIMasker"] = None
    _lock = threading.Lock()

    def __init__(self, language: str = "en", score_threshold: float = 0.5,
                 anonymizers: Optional[Dict[str, OperatorConfig]] = None):
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()
        self.language = language
        self.score_threshold = score_threshold

        # Default anonymization policy: replace with entity placeholders
        if anonymizers is None:
            self.anonymizers = {
                "DEFAULT": OperatorConfig("replace", {"new_value": "{{PII}}"}),
                "PHONE_NUMBER": OperatorConfig("replace", {"new_value": "{{PHONE}}"}),
                "CREDIT_CARD": OperatorConfig("mask", {"masking_char": "*", "chars_to_mask": 4, "from_end": True}),
                "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "{{EMAIL}}"}),
                "PERSON": OperatorConfig("replace", {"new_value": "{{NAME}}"}),
                "IP_ADDRESS": OperatorConfig("replace", {"new_value": "{{IP}}"}),
                "IBAN_CODE": OperatorConfig("replace", {"new_value": "{{IBAN}}"}),
                "US_SSN": OperatorConfig("mask", {"masking_char": "*", "chars_to_mask": 4, "from_end": True}),
                "US_ITIN": OperatorConfig("mask", {"masking_char": "*", "chars_to_mask": 4, "from_end": True}),
                "US_PASSPORT": OperatorConfig("mask", {"masking_char": "*", "chars_to_mask": 3, "from_end": True}),
                "US_DRIVER_LICENSE": OperatorConfig("mask", {"masking_char": "*", "chars_to_mask": 4, "from_end": True}),
                # Handle common false positives for location entities
                # Keep location entities to avoid masking "US", "UK", etc.
                "LOCATION": OperatorConfig("keep", {}),
            }
        else:
            self.anonymizers = anonymizers

    @classmethod
    def get_instance(cls) -> "PIIMasker":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = PIIMasker()
        return cls._instance

    def mask(self, text: str) -> str:
        if not text:
            return text
        try:
            results: list[RecognizerResult] = self.analyzer.analyze(
                text=text,
                language=self.language,
                score_threshold=self.score_threshold,
            )
        except Exception:
            return text
        if not results:
            return text

        # Filter out common false positives for LOCATION entities
        # that are likely abbreviations in sensitive contexts
        filtered_results = []
        for r in results:
            if r.entity_type == "LOCATION":
                detected_text = text[r.start:r.end].upper()
                # Common country/state abbreviations that are often false positives
                # when appearing near sensitive data like SSN, credit cards, etc.
                common_abbreviations = {"US", "UK", "CA",
                                        "NY", "TX", "FL", "IL", "PA", "OH", "MI"}
                if detected_text in common_abbreviations and r.score < 0.9:
                    # Skip this entity if it's a common abbreviation with low confidence
                    continue
            filtered_results.append(r)

        if not filtered_results:
            return text

        # Build per-entity config map, fallback to DEFAULT
        operators: Dict[str, OperatorConfig] = {}
        for r in filtered_results:
            ent = r.entity_type
            if ent in self.anonymizers:
                operators[ent] = self.anonymizers[ent]
            else:
                operators[ent] = self.anonymizers.get("DEFAULT")

        try:
            out = self.anonymizer.anonymize(
                text=text,
                analyzer_results=filtered_results,
                operators=operators,
            )
            return out.text
        except Exception:
            return text
