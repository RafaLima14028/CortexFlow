import json

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Response,
    UploadFile,
    status,
)
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.core.database import get_db
from src.core.security import extract_user_id_by_token, get_token_from_header
from src.schemas.documents import (
    DocumentEmbeddingChunkResponse,
    DocumentRequest,
    DocumentResponse,
    DocumentResponseInternal,
)
from src.services.database.documents_db import (
    delete_document_by_id,
    get_documents_by_user_id,
    get_documents_by_user_id_and_document_id,
)
from src.services.database.embeddings_db import (
    delete_embeddings_by_filename,
    get_embeddings,
)
from src.services.documents import upload_document

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", status_code=status.HTTP_204_NO_CONTENT)
async def post_documents_upload(
    document_data: str = Form(...),
    file: UploadFile = File(...),
    payload: dict = Depends(get_token_from_header),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    try:
        data_dict = json.loads(document_data)
        request_data = DocumentRequest(**data_dict)
    except Exception:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "Invalid JSON in document_data"
        )

    user_id = extract_user_id_by_token(payload)

    await upload_document(request_data=request_data, file=file, user_id=user_id, db=db)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(path="/", response_model=list[DocumentResponse])
async def get_documents(
    payload: dict = Depends(get_token_from_header),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    user_id = payload.get("sub")

    documents: list[DocumentResponse] = await get_documents_by_user_id(
        user_id=user_id, db=db
    )

    return documents


@router.get(path="/{id}", response_model=DocumentEmbeddingChunkResponse)
async def get_document_by_id(
    id: str,
    payload: dict = Depends(get_token_from_header),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    user_id = payload.get("sub")

    result = await get_documents_by_user_id_and_document_id(
        user_id=user_id, document_id=id, db=db
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )

    document, doc_collection = result

    embeddings_data = await get_embeddings(
        user_id=user_id, filename=document.filename, collection=doc_collection, db=db
    )

    return DocumentEmbeddingChunkResponse(infos=document, datas=embeddings_data)


@router.delete(path="/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    id: str,
    payload: dict = Depends(get_token_from_header),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    user_id = payload.get("sub")

    deleted_doc: DocumentResponseInternal | None = await delete_document_by_id(
        user_id=user_id, document_id=id, db=db
    )

    if deleted_doc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )

    await delete_embeddings_by_filename(
        user_id=user_id,
        filename=deleted_doc.filename,
        collection=deleted_doc.collection,
        db=db,
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
