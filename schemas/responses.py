from pydantic import BaseModel, Field


class DatabaseErrorResponse(BaseModel):
    detail: str = Field(example=["database error en {funcion}: connection timeout"])


class NotFound(BaseModel):
    detail: str = Field(
        examples=[
            [
                "Group whit group_id 1 not found",
                "Project whit project_id 1 not found",
                "Chat whit project_id 1 not found",
                "User whit user_id 1 not found",
            ]
        ]
    )
