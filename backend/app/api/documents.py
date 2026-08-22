from pathlib import Path
from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.document import (
    DocumentUploadResponse,
)
from app.services.document_ingestion_db_service import (
    DocumentDatabaseIngestionService,
)


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


# ============================================================
# CONFIGURATION
# ============================================================

UPLOAD_DIR = Path(
    "uploads/documents"
)

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


ALLOWED_EXTENSIONS = {
    ".pdf",
    ".txt",
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


# ============================================================
# UPLOAD DOCUMENT
# ============================================================


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(
        get_db
    ),
):
    """
    Upload a PDF/TXT document and automatically
    index it into PostgreSQL + pgvector.

    Pipeline:

        Upload
          ↓
        Validate
          ↓
        Save
          ↓
        Extract text
          ↓
        Chunk
          ↓
        Generate embeddings
          ↓
        Store Document
          ↓
        Store DocumentChunk
    """

    # --------------------------------------------------------
    # Validate filename
    # --------------------------------------------------------

    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required.",
        )

    original_name = Path(
        file.filename
    ).name

    extension = Path(
        original_name
    ).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Unsupported document type. "
                "Only PDF and TXT files are allowed."
            ),
        )

    # --------------------------------------------------------
    # Generate safe filename
    # --------------------------------------------------------

    stored_name = (
        f"{uuid4().hex}{extension}"
    )

    file_path = (
        UPLOAD_DIR / stored_name
    )

    # --------------------------------------------------------
    # Save uploaded file
    # --------------------------------------------------------

    total_size = 0

    try:

        with file_path.open(
            "wb"
        ) as destination:

            while True:

                data = await file.read(
                    1024 * 1024
                )

                if not data:
                    break

                total_size += len(data)

                if total_size > MAX_FILE_SIZE:

                    raise HTTPException(
                        status_code=413,
                        detail=(
                            "File is too large. "
                            "Maximum allowed size is 10 MB."
                        ),
                    )

                destination.write(
                    data
                )

        # ----------------------------------------------------
        # Ingest into database
        # ----------------------------------------------------

        ingestion_service = (
            DocumentDatabaseIngestionService()
        )

        document = (
            await ingestion_service.ingest_file(
                db,
                file_path,
                title=Path(
                    original_name
                ).stem,
                document_type="knowledge",
                language="en",
                storage_url=str(
                    file_path
                ),
            )
        )

        # ----------------------------------------------------
        # Return schema-compatible response
        # ----------------------------------------------------

        return DocumentUploadResponse(
            document=document,
            processing_status="completed",
        )

    except HTTPException:

        if file_path.exists():
            file_path.unlink()

        raise

    except Exception as exc:

        if file_path.exists():
            file_path.unlink()

        await db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "Document processing failed: "
                f"{str(exc)}"
            ),
        ) from exc

    finally:

        await file.close()