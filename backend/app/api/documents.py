from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import get_current_user
from app.core.database import get_db
from app.models.document import Document
from app.models.user import User
from app.schemas.document import DocumentPage, DocumentResponse, DocumentUploadResponse
from app.services.document_ingestion_db_service import DocumentDatabaseIngestionService

router = APIRouter(prefix="/documents", tags=["Documents"])
UPLOAD_DIR = Path("uploads/documents").resolve()
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
ALLOWED_EXTENSIONS = {".pdf", ".txt"}
MAX_FILE_SIZE = 10 * 1024 * 1024


async def owned_document(db: AsyncSession, document_id: int, user_id: int) -> Document:
    result = await db.execute(select(Document).where(Document.id == document_id, Document.user_id == user_id))
    document = result.scalar_one_or_none()
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
    return document


def stored_path(document: Document) -> Path:
    if not document.storage_url:
        raise HTTPException(status_code=404, detail="The original file is not available.")
    path = Path(document.storage_url).resolve()
    if UPLOAD_DIR not in path.parents or not path.is_file():
        raise HTTPException(status_code=404, detail="The original file is not available.")
    return path


@router.get("", response_model=DocumentPage)
async def list_documents(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    filters = Document.user_id == current_user.id
    total = (await db.execute(select(func.count()).select_from(Document).where(filters))).scalar_one()
    rows = await db.execute(select(Document).where(filters).order_by(Document.created_at.desc()).offset((page - 1) * page_size).limit(page_size))
    return DocumentPage(items=[DocumentResponse.model_validate(item) for item in rows.scalars()], page=page, page_size=page_size, total=total)


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return DocumentResponse.model_validate(await owned_document(db, document_id, current_user.id))


@router.get("/{document_id}/download")
async def download_document(document_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    document = await owned_document(db, document_id, current_user.id)
    return FileResponse(stored_path(document), filename=f"{document.title}{Path(document.storage_url or '').suffix}")


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(document_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    document = await owned_document(db, document_id, current_user.id)
    path = Path(document.storage_url).resolve() if document.storage_url else None
    await db.delete(document)
    await db.commit()
    if path and UPLOAD_DIR in path.parents and path.is_file():
        path.unlink()


@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(file: UploadFile = File(...), current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required.")
    original_name = Path(file.filename).name
    extension = Path(original_name).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported document type. Only PDF and TXT files are allowed.")
    file_path = UPLOAD_DIR / f"{uuid4().hex}{extension}"
    total_size = 0
    try:
        with file_path.open("wb") as destination:
            while data := await file.read(1024 * 1024):
                total_size += len(data)
                if total_size > MAX_FILE_SIZE:
                    raise HTTPException(status_code=413, detail="File is too large. Maximum allowed size is 10 MB.")
                destination.write(data)
        document = await DocumentDatabaseIngestionService().ingest_file(db, file_path, title=Path(original_name).stem, document_type="knowledge", language="en", storage_url=str(file_path), user_id=current_user.id)
        return DocumentUploadResponse(document=document, processing_status=document.processing_status)
    except HTTPException:
        if file_path.exists(): file_path.unlink()
        raise
    except Exception as exc:
        if file_path.exists(): file_path.unlink()
        await db.rollback()
        raise HTTPException(status_code=500, detail="Document processing failed. Please try again.") from exc
    finally:
        await file.close()
