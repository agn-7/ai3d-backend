from typing import List, Dict, Any, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from . import crud, schemas, modules
from .database import SessionLocal

router = APIRouter()


def get_db() -> SessionLocal:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@router.get("/", response_model=str)
async def get_root(db: Session = Depends(get_db)) -> str:
    return "Hello from IFSGuid!"


@router.get("/interactions", response_model=List[schemas.Interaction])
async def get_all_interactions(
    page: Optional[int] = None,
    per_page: Optional[int] = None,
    db: Session = Depends(get_db),
) -> List[schemas.Interaction]:
    return [
        schemas.Interaction.model_validate(interaction)
        for interaction in crud.get_interactions(db=db, page=page, per_page=per_page)
    ]


@router.get(
    "/interactions/{id}", response_model=schemas.Interaction, include_in_schema=False
)
async def get_interactions(
    id: UUID, db: Session = Depends(get_db)
) -> schemas.Interaction:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="NotImplementedError"
    )


@router.post("/interactions", response_model=schemas.Interaction)
async def create_interactions(
    settings: schemas.Settings, db: Session = Depends(get_db)
) -> schemas.Interaction:
    return schemas.Interaction.model_validate(
        crud.create_interaction(db=db, settings=settings)
    )


@router.delete("/interactions", response_model=Dict[str, Any], include_in_schema=False)
async def delete_interaction(id: UUID, db: Session = Depends(get_db)) -> None:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="NotImplementedError"
    )


@router.put(
    "/interactions/{id}", response_model=schemas.Interaction, include_in_schema=False
)
async def update_interaction(
    id: UUID, settings: schemas.Settings, db: Session = Depends(get_db)
) -> schemas.Interaction:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="NotImplementedError"
    )


@router.get(
    "/interactions/{interaction_id}/messages", response_model=List[schemas.Message]
)
async def get_all_message_in_interaction(
    interaction_id: UUID,
    page: Optional[int] = None,
    per_page: Optional[int] = None,
    db: Session = Depends(get_db),
) -> List[schemas.Message]:
    return [
        schemas.Message.model_validate(message)
        for message in crud.get_messages(
            db=db, interaction_id=interaction_id, page=page, per_page=per_page
        )
    ]


@router.post(
    "/interactions/{interactions_id}/messages", response_model=List[schemas.Message]
)
async def create_message(
    interaction_id: UUID, message: schemas.MessageCreate, db: Session = Depends(get_db)
) -> schemas.Message:
    interaction = schemas.Interaction.model_validate(
        crud.get_interaction(db=db, id=interaction_id)
    )

    if not interaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Interaction not found"
        )

    messages = []
    if message.role == "human":
        ai_content = modules.generate_ai_response(
            content=message.content, model=interaction.settings.model_name
        )
        ai_message = schemas.MessageCreate(role="ai", content=ai_content)

        messages.append(message)
        messages.append(ai_message)

    return [
        schemas.Message.model_validate(message)
        for message in crud.create_message(
            db=db, messages=messages, interaction_id=interaction_id
        )
    ]