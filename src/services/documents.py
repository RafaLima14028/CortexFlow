from fastapi import HTTPException, UploadFile, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.schemas.documents import ChunkingResponse, DocumentRequest
from src.schemas.embeddings import EmbeddingsResults
from src.services.chuncking import chunck_document
from src.services.database.documents_db import add_new_user_document
from src.services.database.embeddings_db import add_new_embedding
from src.services.embeddings import generate_embedding
from src.services.file_validator import validate_upload_file
from src.services.parsers import extract_text


async def upload_document(
    user_id: str,
    file: UploadFile,
    request_data: DocumentRequest,
    db: AsyncIOMotorDatabase
) -> None:
    binary_content = await validate_upload_file(file)

    text_content = extract_text(
        filename=file.filename,
        content=binary_content
    )

    chunk_response: list[ChunkingResponse] = await chunck_document(
        text_content=text_content,
        filename=file.filename,
        chunking_request=request_data.chunking
    )

    embeddings_data: list[EmbeddingsResults] = await generate_embedding(
        model_id=request_data.embedding.model_id,
        params=request_data.embedding.model_params,
        chunks=chunk_response
    )

    if not embeddings_data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Embedding generation returned no data"
        )

    client = db.client

    async with await client.start_session() as session:
        async with session.start_transaction():
            collection_name = await add_new_embedding(
                embeddings=embeddings_data,
                user_id=user_id,
                model_id=request_data.embedding.model_id,
                db=db,
                session=session
            )

            await add_new_user_document(
                user_id=user_id,
                filename=file.filename,
                model_id=request_data.embedding.model_id,
                embedding_model_params=request_data.embedding.model_params,
                collection_name=collection_name,
                db=db,
                session=session
            )
