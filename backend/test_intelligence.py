from app.ai.intent_classifier import (
    IntentClassifier,
)
from app.ai.entity_extractor import (
    EntityExtractor,
)


def main():

    classifier = IntentClassifier()
    extractor = EntityExtractor()

    tests = [
        "How can I file an RTI request?",
        "My landlord has not returned my ₹20,000 deposit.",
        "Am I eligible for a government welfare scheme?",
        "Please explain this government notice.",
    ]

    for text in tests:

        intent = classifier.classify(text)
        entities = extractor.extract(text)

        print()
        print("=" * 60)
        print("QUERY:", text)
        print("INTENT:", intent.value)
        print("ENTITIES:", entities)


if __name__ == "__main__":
    main()