import os
import shutil
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.config import settings
from app.models.document import Document
from app.models.user import User
from app.ingestion.processor import process_document, delete_document_vectors

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload", status_code=status.HTTP_201_CREATED)
def upload_document(
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
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File exceeds max size of {settings.max_upload_size_mb}MB.",
            )

        chunk_ids = process_document(
            file_path=tmp_path,
            user_id=str(current_user.id),
            document_id=document_id,
            filename=file.filename,
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process document: {e}",
        )
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    doc = Document(
        id=document_id,
        filename=file.filename,
        file_type=ext.lstrip("."),
        chunk_count=len(chunk_ids),
        user_id=current_user.id,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    return {
        "document_id": doc.id,
        "filename": doc.filename,
        "file_type": doc.file_type,
        "chunk_count": doc.chunk_count,
        "uploaded_at": doc.uploaded_at,
    }


@router.get("")
def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    docs = (
        db.query(Document)
        .filter(Document.user_id == current_user.id)
        .order_by(Document.uploaded_at.desc())
        .all()
    )
    return [
        {
            "document_id": d.id,
            "filename": d.filename,
            "file_type": d.file_type,
            "chunk_count": d.chunk_count,
            "uploaded_at": d.uploaded_at,
        }
        for d in docs
    ]


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

    from app.ingestion.processor import get_document_chunks

    chunks = get_document_chunks(user_id=str(current_user.id), document_id=document_id)
    content = "\n\n".join(c["chunk_text"] for c in chunks)

    return {
        "document_id": doc.id,
        "filename": doc.filename,
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

    delete_document_vectors(user_id=str(current_user.id), document_id=document_id)
    db.delete(doc)
    db.commit()

    return {"message": "Document deleted", "document_id": document_id}
