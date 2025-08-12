from contextlib import asynccontextmanager
from functools import lru_cache
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Session, SQLModel, create_engine, select

from . import config
from .models import Peak, PeakBase, PeakPublic


@lru_cache
def get_settings():
    return config.Settings()


# Database initialisation and connection
db_name = get_settings().database_name
sqlite_url = f"sqlite:///{db_name}"

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


@app.get("/")
async def root():
    return {
        "message": "Welcome to Mountain Peak API! "
        "Explore documentation available to get peaks!"
    }


# Routes - CRUD peaks
@app.get("/peaks/", response_model=list[PeakPublic])
async def read_peaks(
    session: SessionDep,
    min_lat: float | None = Query(
        None, ge=-90, le=90, description="Minimum latitude of the bounding box"
    ),
    max_lat: float | None = Query(
        None, ge=-90, le=90, description="Maximum latitude of the bounding box"
    ),
    min_lon: float | None = Query(
        None,
        ge=-180,
        le=180,
        description="Minimum longitude of the bounding box",
    ),
    max_lon: float | None = Query(
        None,
        ge=-180,
        le=180,
        description="Maximum longitude of the bounding box",
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


@app.post("/peaks/", response_model=PeakPublic)
async def create_peak(peak: PeakBase, session: SessionDep):
    db_peak = Peak.model_validate(peak)
    session.add(db_peak)
    session.commit()
    session.refresh(db_peak)
    return db_peak


@app.get("/peaks/{peak_id}", response_model=PeakPublic)
async def read_peak(peak_id: int, session: SessionDep) -> Peak:
    peak = session.get(Peak, peak_id)
    if not peak:
        raise HTTPException(status_code=404, detail="Peak not found")
    return peak


@app.patch("/peaks/{peak_id}", response_model=PeakPublic)
async def update_peak(peak_id: int, peak: PeakBase, session: SessionDep):
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
