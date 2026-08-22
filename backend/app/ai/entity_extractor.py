import re
from typing import Any


class EntityExtractor:
    """
    Lightweight entity extractor for civic/legal queries.

    This intentionally extracts high-value entities without
    making the entire pipeline dependent on an LLM.
    """

    MONEY_PATTERN = re.compile(
        r"(?:₹|rs\.?|inr)\s?"
        r"[\d,]+(?:\.\d+)?",
        re.IGNORECASE,
    )

    PHONE_PATTERN = re.compile(
        r"\b(?:\+91[-\s]?)?[6-9]\d{9}\b"
    )

    PINCODE_PATTERN = re.compile(
        r"\b[1-9][0-9]{5}\b"
    )

    def extract(
        self,
        text: str,
    ) -> dict[str, Any]:

        if not text:
            return {}

        entities: dict[str, Any] = {}

        money = self.MONEY_PATTERN.findall(
            text
        )

        if money:
            entities["amounts"] = money

        phone_numbers = self.PHONE_PATTERN.findall(
            text
        )

        if phone_numbers:
            entities["phone_numbers"] = phone_numbers

        pincodes = self.PINCODE_PATTERN.findall(
            text
        )

        if pincodes:
            entities["pincodes"] = pincodes

        entities["keywords"] = self._extract_keywords(
            text
        )

        return entities

    @staticmethod
    def _extract_keywords(
        text: str,
    ) -> list[str]:

        keyword_patterns = [
            "landlord",
            "tenant",
            "security deposit",
            "rent",
            "consumer",
            "refund",
            "salary",
            "wages",
            "employer",
            "rti",
            "government scheme",
            "welfare scheme",
            "notice",
            "document",
            "pension",
            "scholarship",
            "subsidy",
        ]

        normalized = text.lower()

        return [
            keyword
            for keyword in keyword_patterns
            if keyword in normalized
        ]