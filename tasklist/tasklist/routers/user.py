import uuid

from typing import Dict

from fastapi import APIRouter, HTTPException, Depends

from ..database import DBSession, get_db
from ..models import  User, Task

router = APIRouter()

@router.post(
    '',
    summary='Creates a new user',
    description='Creates a new user and returns the user with ID and name.',
    response_model=uuid.UUID,
)
async def create_user(user: User, db: DBSession = Depends(get_db)):
    return db.create_user(user)


@router.delete(
    '/{uuid_}',
    summary='Deletes user',
    description='Deletes a user identified by its UUID',
)
async def remove_user(uuid_: uuid.UUID, db: DBSession = Depends(get_db)):
    try:
        db.remove_user(uuid_)
    except KeyError as exception:
        raise HTTPException(
            status_code=404,
            detail='User not found',
        ) from exception

@router.patch(
    '/{uuid_}',
    summary='Alters user',
    description='Alters a user identified by its UUID',
)
async def update_user(
        uuid_: uuid.UUID,
        name: str,
        db: DBSession = Depends(get_db),
):
    try:
        db.update_user(uuid_, name)
    except KeyError as exception:
        raise HTTPException(
            status_code=404,
            detail='Task not found',
        ) from exception


@router.get(
    '/{uuid_}',
    summary='Reads user',
    description='Reads user from UUID.',
    response_model=User,
)
async def read_user(uuid_: uuid.UUID, db: DBSession = Depends(get_db)):
    try:
        return db.read_user(uuid_)
    except KeyError as exception:
        raise HTTPException(
            status_code=404,
            detail='Task not found',
        ) from exception