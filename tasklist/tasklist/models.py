# pylint: disable=missing-module-docstring,missing-class-docstring
from typing import Optional

from pydantic import BaseModel, Field  # pylint: disable=no-name-in-module


# pylint: disable=too-few-public-methods
class Task(BaseModel):
    description: Optional[str] = Field(
        'no description',
        title='Task description',
        max_length=1024,
    )
    completed: Optional[bool] = Field(
        False,
        title='Shows whether the task was completed',
    )
    userID: Optional[str] = Field(
        'no user',
        title = 'user ID',
        max_length=36,
    )

    class Config:
        schema_extra = {
            'example': {
                'description': 'Buy baby diapers',
                'completed': False,
                'userID': 'numeroesquisito'
            }
        }

class User(BaseModel):
    name: Optional[str] = Field(
        'unnamed',
        title='User Name',
        max_length=64,
    )

    class Config:
        schema_extra = {
            'example': {
                'name': 'José',
            }
        }
