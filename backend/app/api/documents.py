import os
import shutil
import traceback
import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, UploadFile, File, status
from sqlalchemy.orm import Session

from app.core.database import get_db, SessionLocal
from app.core.dependencies import get_current_user
from app.core.config import settings
from app.models.document import Document, DocumentStatus
from app.models.user import User
from app.ingestion.processor import process_document, delete_document_vectors, get_document_chunks

router = APIRouter(prefix="/documents", tags=["Documents"])


def _process_document_background(document_id: str, tmp_path: str, user_id: str, filename: str):
    db = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            return

        doc.status = DocumentStatus.PROCESSING
        db.commit()

        try:
            chunk_ids = process_document(
                file_path=tmp_path,
                user_id=user_id,
                document_id=document_id,
                filename=filename,
            )
            doc.status = DocumentStatus.INDEXED
            doc.chunk_count = len(chunk_ids)
            doc.error_message = None
        except ValueError as e:
            doc.status = DocumentStatus.FAILED
            doc.error_message = str(e)
        except Exception as e:
            doc.status = DocumentStatus.FAILED
            doc.error_message = f"{type(e).__name__}: {e}"
            print("=" * 60)
            print("BACKGROUND DOCUMENT PROCESSING FAILED — FULL TRACEBACK:")
            traceback.print_exc()
            print("=" * 60)

        db.commit()
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        db.close()


@router.post("/upload", status_code=status.HTTP_201_CREATED)
def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in settings.allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '{ext}'. Allowed: "
            f"{', '.join(settings.allowed_extensions)}",
        )

    os.makedirs(settings.upload_dir, exist_ok=True)
    document_id = uuid.uuid4().hex
    tmp_path = os.path.join(settings.upload_dir, f"{document_id}{ext}")

    try:
        with open(tmp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        if os.path.getsize(tmp_path) > settings.max_upload_size_mb * 1024 * 1024:
            os.remove(tmp_path)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File exceeds max size of {settings.max_upload_size_mb}MB.",
            )
    except HTTPException:
        raise
    except Exception as e:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not save uploaded file: {e}",
        )

    doc = Document(
        id=document_id,
        filename=file.filename,
        file_type=ext.lstrip("."),
        chunk_count=0,
        status=DocumentStatus.UPLOADING,
        user_id=current_user.id,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    background_tasks.add_task(
        _process_document_background,
        document_id=document_id,
        tmp_path=tmp_path,
        user_id=str(current_user.id),
        filename=file.filename,
    )

    return {
        "document_id": doc.id,
        "filename": doc.filename,
        "file_type": doc.file_type,
        "chunk_count": doc.chunk_count,
        "status": doc.status,
        "uploaded_at": doc.uploaded_at,
    }


@router.get("")
def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(default=20, ge=1, le=100, description="Max documents to return"),
    offset: int = Query(default=0, ge=0, description="Number of documents to skip"),
    file_type: str | None = Query(default=None, description="Filter by file type, e.g. 'pdf'"),
    status_filter: str | None = Query(
        default=None,
        alias="status",
        description="Filter by status: uploading, processing, indexed, failed",
    ),
):
    query = db.query(Document).filter(Document.user_id == current_user.id)

    if file_type:
        query = query.filter(Document.file_type == file_type.lstrip("."))
    if status_filter:
        query = query.filter(Document.status == status_filter)

    total = query.count()

    docs = (
        query.order_by(Document.uploaded_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "documents": [
            {
                "document_id": d.id,
                "filename": d.filename,
                "file_type": d.file_type,
                "chunk_count": d.chunk_count,
                "status": d.status,
                "error_message": d.error_message,
                "uploaded_at": d.uploaded_at,
            }
            for d in docs
        ],
    }


@router.get("/{document_id}")
def get_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    doc = (
        db.query(Document)
        .filter(Document.id == document_id, Document.user_id == current_user.id)
        .first()
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    content = ""
    if doc.status == DocumentStatus.INDEXED:
        chunks = get_document_chunks(user_id=str(current_user.id), document_id=document_id)
        content = "\n\n".join(c["chunk_text"] for c in chunks)

    return {
        "document_id": doc.id,
        "filename": doc.filename,
        "status": doc.status,
        "error_message": doc.error_message,
        "content": content,
    }


@router.delete("/{document_id}")
def delete_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    doc = (
        db.query(Document)
        .filter(Document.id == document_id, Document.user_id == current_user.id)
        .first()
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if doc.status == DocumentStatus.INDEXED:
        delete_document_vectors(user_id=str(current_user.id), document_id=document_id)

    db.delete(doc)
    db.commit()

    return {"message": "Document deleted", "document_id": document_id}