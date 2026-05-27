from agno.knowledge.chunking.fixed import FixedSizeChunking
from agno.knowledge.chunking.markdown import MarkdownChunking
from agno.knowledge.chunking.recursive import RecursiveChunking
from agno.knowledge.chunking.semantic import SemanticChunking
from agno.knowledge.document import Document

from src.schemas.documents import ChunkingRequest, ChunkingResponse


async def fixed_size_chunking(
    chunk_size: int, overlap: int, document: Document
) -> list[ChunkingResponse]:
    chunker = FixedSizeChunking(chunk_size=chunk_size, overlap=overlap)

    chunks = await chunker.achunk(document=document)

    chunking_response: list[ChunkingResponse] = []

    for chunk in chunks:
        chunking_response.append(
            ChunkingResponse(
                chunk=chunk.content, id=chunk.id, meta_data=chunk.meta_data
            )
        )

    return chunking_response


async def semantic_chunking(
    similarity_threshold: float, document: Document
) -> list[ChunkingResponse]:
    chunker = SemanticChunking(similarity_threshold=similarity_threshold)

    chunks = await chunker.achunk(document=document)

    chunking_response: list[ChunkingResponse] = []

    for chunk in chunks:
        chunking_response.append(
            ChunkingResponse(
                chunk=chunk.content, id=chunk.id, meta_data=chunk.meta_data
            )
        )

    return chunking_response


async def recursive_chunking(
    chunk_size: int, overlap: int, document: Document
) -> list[ChunkingResponse]:
    chunker = RecursiveChunking(chunk_size=chunk_size, overlap=overlap)

    chunks = await chunker.achunk(document=document)

    chunking_response: list[ChunkingResponse] = []

    for chunk in chunks:
        chunking_response.append(
            ChunkingResponse(
                chunk=chunk.content, id=chunk.id, meta_data=chunk.meta_data
            )
        )

    return chunking_response


async def markdown_chunking(
    chunk_size: int, overlap: int, document: Document
) -> list[ChunkingResponse]:
    chunker = MarkdownChunking(chunk_size=chunk_size, overlap=overlap)

    chunks = await chunker.achunk(document=document)

    chunking_response: list[ChunkingResponse] = []

    for chunk in chunks:
        chunking_response.append(
            ChunkingResponse(
                chunk=chunk.content, id=chunk.id, meta_data=chunk.meta_data
            )
        )

    return chunking_response


async def chunck_document(
    text_content: str,
    filename: str,
    chunking_request: ChunkingRequest,
    extra_meta: dict | None = None,
) -> list[ChunkingResponse]:
    if extra_meta:
        extra_meta["filename"] = filename
    else:
        extra_meta = {"filename": filename}

    document = Document(content=text_content, meta_data=extra_meta)

    strategy = chunking_request.strategy

    if strategy == "fixed":
        return await fixed_size_chunking(
            chunking_request.config.chunk_size,
            chunking_request.config.overlap,
            document=document,
        )
    if strategy == "semantic":
        return await semantic_chunking(
            similarity_threshold=chunking_request.config.similarity_threshold,
            document=document,
        )
    if strategy == "recursive":
        return await recursive_chunking(
            chunking_request.config.chunk_size,
            chunking_request.config.overlap,
            document=document,
        )
    if strategy == "markdown":
        return await markdown_chunking(
            chunking_request.config.chunk_size,
            chunking_request.config.overlap,
            document=document,
        )
