from typing import List, Dict, Any, Optional, Annotated
from uuid import UUID
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from . import crud, schemas, modules, utils, auth
from .database import AsyncSession, get_db

router = APIRouter()

ID = Annotated[UUID, Depends(utils.uuid_to_str)]
InteractionID = Annotated[UUID, Depends(utils.interaction_id_to_str)]
AsyncDB = Annotated[AsyncSession, Depends(get_db)]


@router.get("/", response_model=str)
async def get_root(db: AsyncSession = Depends(get_db)) -> str:
    return "Hello from Ai3D!"


@router.post("/token", response_model=schemas.Token)
async def login(
    db: AsyncDB, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = await auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(days=auth.TOKEN_EXPIRATION)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/interactions", response_model=List[schemas.Interaction])
async def get_all_interactions(
    db: AsyncDB,
    page: Optional[int] = None,
    per_page: Optional[int] = None,
) -> List[schemas.Interaction]:
    interactions = await crud.get_interactions(db=db, page=page, per_page=per_page)

    return [
        schemas.Interaction.model_validate(interaction) for interaction in interactions
    ]


@router.get("/interactions/{id}", response_model=schemas.Interaction)
async def get_interactions(id: ID, db: AsyncDB) -> schemas.Interaction:
    interaction = await crud.get_interaction(db=db, id=id)

    if not interaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Interaction not found"
        )

    return schemas.Interaction.model_validate(interaction)


@router.post("/interactions", response_model=schemas.Interaction)
async def create_interactions(
    instruction: schemas.Instruction,
    db: AsyncDB,
    user: Annotated[schemas.User, Depends(auth.get_current_active_user)],
    chat_model: schemas.ChatModel = Depends(),
) -> schemas.Interaction:
    settings = schemas.Settings(
        model=chat_model.model, prompt=instruction.prompt, role=instruction.role
    )
    interaction = await crud.create_interaction(db=db, settings=settings)

    return schemas.Interaction.model_validate(interaction)


@router.delete("/interactions", response_model=Dict[str, Any], include_in_schema=False)
async def delete_interaction(id: ID, db: AsyncDB) -> None:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="NotImplementedError"
    )


@router.put("/interactions/{id}", response_model=schemas.Interaction)
async def update_interaction(
    id: ID,
    instruction: schemas.Instruction,
    db: AsyncDB,
    chat_model: schemas.ChatModel = Depends(),
) -> schemas.Interaction:
    settings = schemas.Settings(
        model=chat_model.model, prompt=instruction.prompt, role=instruction.role
    )
    interaction = await crud.update_interaction(db=db, id=id, settings=settings)

    if not interaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Interaction not found"
        )

    return schemas.Interaction.model_validate(interaction)


@router.get(
    "/interactions/{interaction_id}/messages", response_model=List[schemas.Message]
)
async def get_all_message_in_interaction(
    interaction_id: InteractionID,
    db: AsyncDB,
    page: Optional[int] = None,
    per_page: Optional[int] = None,
) -> List[schemas.Message]:
    interaction = await crud.get_interaction(db=db, id=interaction_id)

    if not interaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Interaction not found"
        )

    messages = await crud.get_messages(
        db=db, interaction_id=interaction_id, page=page, per_page=per_page
    )

    return [schemas.Message.model_validate(message) for message in messages]


@router.post("/interactions/{interaction_id}/messages", response_model=schemas.Message)
async def create_message(
    interaction_id: InteractionID,
    message: schemas.MessageCreate,
    db: AsyncDB,
) -> schemas.Message:
    interaction = await crud.get_interaction(db=db, id=interaction_id)

    if not interaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Interaction not found"
        )

    interaction = schemas.Interaction.model_validate(interaction)

    messages = []
    if message.role == "user":
        response = await modules.generate_ai_response(
            db=db,
            content=message.content,
            interaction=interaction,
        )
        ai_message = schemas.MessageCreate(role="assistant", content=response)

        messages.append(message)
        messages.append(ai_message)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Role must be user"
        )

    messages = await crud.create_message(
        db=db, messages=messages, interaction_id=interaction_id
    )

    messages[1].content = utils.jsonify(messages[1].content)

    return schemas.Message.model_validate(messages[1])


@router.get("/user/me", response_model=schemas.User)
async def read_users_me(
    current_user: Annotated[schemas.User, Depends(auth.get_current_active_user)]
) -> schemas.User:
    return current_user


@router.get("/user/{id}", response_model=schemas.User)
async def get_user(id: ID, db: AsyncDB) -> schemas.User:
    user = await crud.get_user_by_id(db=db, id=id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return schemas.User.model_validate(user)


@router.post("/user", response_model=schemas.User)
async def create_user(user: schemas.UserCreate, db: AsyncDB) -> schemas.User:
    user = await crud.create_user(db=db, user=user)

    return schemas.User.model_validate(user)
