import asyncio

from app.core.database import AsyncSessionLocal
from app.ai.rag.embeddings import get_embedding_service
from app.models.document import Document
from app.models.document_chunk import DocumentChunk


KNOWLEDGE_BASE = [

    # ============================================================
    # RTI
    # ============================================================

    {
        "title": "Right to Information Act, 2005",
        "document_type": "law",
        "department": "Government of India",
        "language": "English",
        "source_url": "https://www.indiacode.nic.in/handle/123456789/2065",
        "chunks": [
            """
The Right to Information Act, 2005 provides a practical regime
for citizens to secure access to information under the control of
public authorities.

The Act promotes transparency and accountability in the working
of public authorities.

Citizens can seek information held by or under the control of
public authorities, subject to the exemptions provided under
the Act.
""",
            """
An RTI request should identify the information being requested
as clearly as possible.

Citizens should identify the relevant public authority and
describe the records or information they are seeking.

Information may include records, documents and information
stored in electronic form.
""",
            """
The Right to Information framework also provides for Central
and State Information Commissions.

Where applicable, citizens can use the prescribed appeal
mechanisms when an RTI matter is not resolved satisfactorily.
"""
        ],
    },

    # ============================================================
    # TENANT RIGHTS
    # ============================================================

    {
        "title": "Model Tenancy Act, 2021",
        "document_type": "model_act",
        "department": "Ministry of Housing and Urban Affairs",
        "language": "English",
        "source_url": (
            "https://mohua.gov.in/upload/uploadfiles/files/"
            "Model-Tenancy-Act-English-02_06_2021.pdf"
        ),
        "chunks": [
            """
The Model Tenancy Act, 2021 provides a framework intended to
regulate renting of premises and protect the interests of
landlords and tenants.

It proposes a Rent Authority and mechanisms for resolution
of tenancy disputes.

The model framework is intended to be adopted through the
appropriate State or Union Territory legislative process.
""",
            """
Under the Model Tenancy Act framework, a tenancy agreement is
to be signed by both the landlord and tenant, with each retaining
an original signed copy.

Keeping the tenancy agreement and payment records can therefore
be important when documenting a tenancy-related dispute.
""",
            """
Under the Model Tenancy Act, the security deposit for residential
premises should not exceed two months' rent under the model
framework.

The security deposit is to be refunded to the tenant when vacant
possession is taken, after making deductions for liabilities of
the tenant where applicable.
""",
            """
The Model Tenancy Act provides mechanisms involving a Rent
Authority for certain tenancy-related matters.

The exact rules applicable to a tenant depend on the law and
notifications applicable in the relevant State or Union Territory.

Citizens should therefore verify the current local tenancy law
before relying on the model framework.
"""
        ],
    },

    # ============================================================
    # CONSUMER RIGHTS
    # ============================================================

    {
        "title": "Consumer Rights",
        "document_type": "consumer_guidance",
        "department": "Department of Consumer Affairs",
        "language": "English",
        "source_url": "https://consumerhelpline.gov.in/public/consumerrights",
        "chunks": [
            """
The Consumer Protection framework recognizes important rights
for consumers.

These include the Right to Safety, Right to be Informed,
Right to Choose, Right to be Heard, Right to Redressal and
Right to Consumer Education.
""",
            """
The Right to be Informed means consumers should receive
information about relevant qualities and characteristics of
goods and services, including information needed to make an
informed purchasing decision.

Consumers should retain relevant purchase records when dealing
with a consumer grievance.
""",
            """
The Right to Redressal provides consumers a route to seek
redress against unfair trade practices and other eligible
consumer grievances.

The National Consumer Helpline provides a mechanism for
consumers to register grievances and obtain guidance.
""",
            """
The National Consumer Helpline operates under the Department
of Consumer Affairs.

Consumer grievances can be registered through available
official channels, and consumers can use the official portal
for information about grievance handling.
"""
        ],
    },

    # ============================================================
    # GOVERNMENT SCHEMES
    # ============================================================

    {
        "title": "National Portal of India - Government Schemes",
        "document_type": "government_scheme",
        "department": "Government of India",
        "language": "English",
        "source_url": "https://www.india.gov.in/",
        "chunks": [
            """
The National Portal of India provides access to information
about government schemes and services.

Citizens can search government schemes and use available
eligibility-related facilities to identify schemes that may
apply to their circumstances.
""",
            """
Eligibility for a government scheme depends on the official
criteria specified by the responsible government department.

Citizens should compare their circumstances with the official
eligibility requirements before applying.
""",
            """
Government schemes may require supporting documents and
verification.

The required documents, application process and eligibility
conditions can differ between schemes.

Citizens should verify the current requirements through the
official government department or portal responsible for the
scheme.
""",
            """
The National Portal provides information covering government
services and schemes across areas such as education, welfare,
health, agriculture, employment and other citizen services.

The official scheme information should be treated as the source
for current eligibility and application requirements.
"""
        ],
    },

    # ============================================================
    # GOVERNMENT DOCUMENTS
    # ============================================================

    {
        "title": "Government Documents and Citizen Information",
        "document_type": "government_document",
        "department": "Government of India",
        "language": "English",
        "source_url": "https://www.india.gov.in/",
        "chunks": [
            """
Government notices, orders, circulars and other official
documents may contain information about government decisions,
services, procedures or citizen obligations.

A document should be read in its full context before drawing
conclusions about a person's rights or obligations.
""",
            """
When explaining a government document, important information
includes the issuing authority, document type, date, subject,
instructions and any applicable deadlines.

Citizens should verify important requirements against the
original official document or issuing authority.
""",
            """
NyayaSetu should explain government documents in clear
citizen-friendly language while preserving the meaning of the
original material.

Where the available document does not contain enough information
to establish a legal conclusion, the system should clearly state
that additional official verification is required.
"""
        ],
    },
]


async def seed_database():

    embedding_service = get_embedding_service()

    async with AsyncSessionLocal() as db:

        total_documents = 0
        total_chunks = 0

        for item in KNOWLEDGE_BASE:

            # ----------------------------------------------------
            # Check whether document already exists
            # ----------------------------------------------------

            from sqlalchemy import select

            result = await db.execute(
                select(Document).where(
                    Document.title == item["title"]
                )
            )

            document = result.scalar_one_or_none()

            if document is not None:
                print(
                    f"Skipping existing document: "
                    f"{item['title']}"
                )
                continue

            # ----------------------------------------------------
            # Create document
            # ----------------------------------------------------

            document = Document(
                title=item["title"],
                document_type=item["document_type"],
                department=item["department"],
                language=item["language"],
                source_url=item["source_url"],
                storage_url=None,
            )

            db.add(document)

            await db.flush()

            print(
                f"\nCreated document:"
                f" {document.id} - {document.title}"
            )

            total_documents += 1

            # ----------------------------------------------------
            # Create chunks + embeddings
            # ----------------------------------------------------

            texts = item["chunks"]

            embeddings = embedding_service.embed_documents(
                texts
            )

            for index, (text, embedding) in enumerate(
                zip(texts, embeddings)
            ):

                chunk = DocumentChunk(
                    document_id=document.id,
                    content=text.strip(),
                    page_number=None,
                    chunk_index=index,
                    embedding=embedding,
                )

                db.add(chunk)

                total_chunks += 1

            print(
                f"Inserted {len(texts)} chunks "
                f"for document {document.id}"
            )

        await db.commit()

        print("\n" + "=" * 60)
        print("KNOWLEDGE BASE SEED COMPLETE")
        print("=" * 60)
        print(f"Documents created: {total_documents}")
        print(f"Chunks inserted:   {total_chunks}")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(seed_database())