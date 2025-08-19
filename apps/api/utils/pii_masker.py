import threading
from typing import Dict, Optional

from presidio_analyzer import AnalyzerEngine, RecognizerResult
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig


class PIIMasker:
    """
    Minimal Presidio wrapper to detect and mask PII in text.

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
                "CREDIT_CARD": OperatorConfig("mask", {"masking_char": "*", "chars_to_mask": -4, "from_end": True}),
                "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "{{EMAIL}}"}),
                "PERSON": OperatorConfig("replace", {"new_value": "{{NAME}}"}),
                "IP_ADDRESS": OperatorConfig("replace", {"new_value": "{{IP}}"}),
                "IBAN_CODE": OperatorConfig("replace", {"new_value": "{{IBAN}}"}),
                "US_SSN": OperatorConfig("mask", {"masking_char": "*", "chars_to_mask": -2, "from_end": True}),
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

        # Build per-entity config map, fallback to DEFAULT
        operators: Dict[str, OperatorConfig] = {}
        for r in results:
            ent = r.entity_type
            if ent in self.anonymizers:
                operators[ent] = self.anonymizers[ent]
            else:
                operators[ent] = self.anonymizers.get("DEFAULT")

        try:
            out = self.anonymizer.anonymize(
                text=text,
                analyzer_results=results,
                operators=operators,
            )
            return out.text
        except Exception:
            return text
