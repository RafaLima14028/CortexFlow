from bson import ObjectId
from fastapi import HTTPException, status


def validate_object_id(id: str) -> ObjectId:
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid id"
        )

    return ObjectId(id)
