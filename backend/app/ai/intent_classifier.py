from enum import Enum
import re


class Intent(str, Enum):
    RIGHTS = "rights"
    RTI = "rti"
    SCHEME = "scheme"
    DOCUMENT = "document"
    UNKNOWN = "unknown"


class IntentClassifier:
    """
    Lightweight deterministic intent classifier.

    Rule-based routing is intentionally used before an LLM
    so that core routing remains reliable even when the LLM
    is unavailable.
    """

    RTI_KEYWORDS = {
        "rti",
        "right to information",
        "information act",
        "public authority",
        "pio",
        "public information officer",
        "government records",
        "government information",
        "file rti",
        "submit rti",
        "rti application",
    }

    SCHEME_KEYWORDS = {
        "scheme",
        "government scheme",
        "welfare scheme",
        "subsidy",
        "benefit",
        "pension",
        "scholarship",
        "eligibility",
        "eligible",
        "ration",
        "financial assistance",
    }

    DOCUMENT_KEYWORDS = {
        "document",
        "notice",
        "letter",
        "order",
        "circular",
        "pdf",
        "form",
        "document says",
        "explain this notice",
        "explain this document",
        "read this",
    }

    RIGHTS_KEYWORDS = {
        "right",
        "rights",
        "landlord",
        "tenant",
        "rent",
        "security deposit",
        "consumer",
        "refund",
        "workplace",
        "employer",
        "salary",
        "wages",
        "harassment",
        "eviction",
        "consumer complaint",
        "consumer dispute",
    }

    def classify(self, text: str) -> Intent:
        if not text or not text.strip():
            return Intent.UNKNOWN

        normalized = self._normalize(text)

        scores = {
            Intent.RTI: self._score(
                normalized,
                self.RTI_KEYWORDS,
            ),
            Intent.SCHEME: self._score(
                normalized,
                self.SCHEME_KEYWORDS,
            ),
            Intent.DOCUMENT: self._score(
                normalized,
                self.DOCUMENT_KEYWORDS,
            ),
            Intent.RIGHTS: self._score(
                normalized,
                self.RIGHTS_KEYWORDS,
            ),
        }

        best_intent = max(
            scores,
            key=scores.get,
        )

        if scores[best_intent] == 0:
            return Intent.UNKNOWN

        return best_intent

    @staticmethod
    def _normalize(text: str) -> str:
        text = text.lower()
        text = re.sub(
            r"\s+",
            " ",
            text,
        )
        return text.strip()

    @staticmethod
    def _score(
        text: str,
        keywords: set[str],
    ) -> int:

        score = 0

        for keyword in keywords:

            if keyword in text:
                # Multi-word phrases are stronger signals.
                if " " in keyword:
                    score += 2
                else:
                    score += 1

        return score