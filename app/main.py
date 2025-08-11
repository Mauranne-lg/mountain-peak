from typing import Annotated, Optional
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select


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


class PeakCreate(PeakBase):
    pass


class PeakUpdate(PeakBase):
    pass


# Database initialisation and connection
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


# app initialisation
@asynccontextmanager
async def lifespan(app: FastAPI):  # pragma: no cover
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(lifespan=lifespan)


# Routes - CRUD peaks
@app.post("/peaks/", response_model=PeakPublic)
async def create_peak(peak: PeakCreate, session: SessionDep):
    db_peak = Peak.model_validate(peak)
    session.add(db_peak)
    session.commit()
    session.refresh(db_peak)
    return db_peak


@app.get("/peaks/", response_model=list[PeakPublic])
async def read_peaks(
    session: SessionDep,
    min_lat: Optional[float] = Query(
        None, ge=-90, le=90, description="Minimum latitude of the bounding box"
    ),
    max_lat: Optional[float] = Query(
        None, ge=-90, le=90, description="Maximum latitude of the bounding box"
    ),
    min_lon: Optional[float] = Query(
        None, ge=-180, le=180, description="Minimum longitude of the bounding box"
    ),
    max_lon: Optional[float] = Query(
        None, ge=-180, le=180, description="Maximum longitude of the bounding box"
    ),
) -> list[Peak]:
    statement = select(Peak)

    # Apply each provided box filters if provided
    if min_lat is not None:
        statement = statement.where(Peak.latitude >= min_lat)
    if max_lat is not None:
        statement = statement.where(Peak.latitude <= max_lat)
    if min_lon is not None:
        statement = statement.where(Peak.longitude >= min_lon)
    if max_lon is not None:
        statement = statement.where(Peak.longitude <= max_lon)

    peaks = session.exec(statement)

    return peaks


@app.get("/peaks/{peak_id}", response_model=PeakPublic)
async def read_peak(peak_id: int, session: SessionDep) -> Peak:
    peak = session.get(Peak, peak_id)
    if not peak:
        raise HTTPException(status_code=404, detail="Peak not found")
    return peak


@app.patch("/peaks/{peak_id}", response_model=PeakPublic)
async def update_peak(peak_id: int, peak: PeakUpdate, session: SessionDep):
    peak_db = session.get(Peak, peak_id)
    if not peak_db:
        raise HTTPException(status_code=404, detail="Peak not found")
    peak_data = peak.model_dump(exclude_unset=True)
    peak_db.sqlmodel_update(peak_data)
    session.add(peak_db)
    session.commit()
    session.refresh(peak_db)
    return peak_db


@app.delete("/peaks/{peak_id}")
async def delete_peak(peak_id: int, session: SessionDep):
    peak = session.get(Peak, peak_id)
    if not peak:
        raise HTTPException(status_code=404, detail="Peak not found")
    session.delete(peak)
    session.commit()
    return {"ok": True}
