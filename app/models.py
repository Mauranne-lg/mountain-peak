from typing import Annotated

from sqlmodel import Field, SQLModel


# Models
class PeakBase(SQLModel):
    name: str = Field(index=True)
    latitude: Annotated[float, Field(ge=-90, le=90, index=True)]
    longitude: Annotated[float, Field(ge=-180, le=180, index=True)]
    altitude: Annotated[int, Field(ge=0)]


class Peak(PeakBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


class PeakPublic(PeakBase):
    id: int
