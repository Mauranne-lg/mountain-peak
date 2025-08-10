from typing import Annotated
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select


# Models
class PeakBase(SQLModel):
    name: str = Field(index=True)
    lat: Annotated[float, Field(ge=-90, le=90)]
    lon: Annotated[float, Field(ge=-180, le=180)]
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


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def create_initial_peaks():
    peak_1 = Peak(name="Mount Desert", lat=44.342827, lon=-68.307138, altitude=55)
    peak_2 = Peak(name="Mount Cadillac", lat=44.409286, lon=-68.247501, altitude=466)
    peak_3 = Peak(
        name="Mount Taranaki Maunga", lat=-39.296770, lon=174.063399, altitude=2518
    )
    peak_4 = Peak(name="Mount Tongariro", lat=-39.1333, lon=175.6500, altitude=1978)
    peak_5 = Peak(name="Monte Perdido", lat=42.6499974, lon=0.0499998, altitude=3355)
    peak_6 = Peak(name="Mont Blanc", lat=45.833641, lon=6.864594, altitude=4806)

    with Session(engine) as session:
        session.add(peak_1)
        session.add(peak_2)
        session.add(peak_3)
        session.add(peak_4)
        session.add(peak_5)
        session.add(peak_6)

        session.commit()


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


# app initialisation
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    create_initial_peaks()
    yield


app = FastAPI(lifespan=lifespan)


# Routes - CRUD peaks
@app.post("/peaks/", response_model=PeakPublic)
def create_peak(peak: PeakCreate, session: SessionDep):
    db_peak = Peak.model_validate(peak)
    session.add(db_peak)
    session.commit()
    session.refresh(db_peak)
    return db_peak


@app.get("/peaks/", response_model=list[PeakPublic])
def read_peaks(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[Peak]:
    peaks = session.exec(select(Peak).offset(offset).limit(limit)).all()
    return peaks


@app.get("/peaks/{peak_id}", response_model=PeakPublic)
def read_peak(peak_id: int, session: SessionDep) -> Peak:
    peak = session.get(Peak, peak_id)
    if not peak:
        raise HTTPException(status_code=404, detail="Peak not found")
    return peak


@app.patch("/peaks/{peak_id}", response_model=PeakPublic)
def update_peak(peak_id: int, peak: PeakUpdate, session: SessionDep):
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
def delete_peak(peak_id: int, session: SessionDep):
    peak = session.get(Peak, peak_id)
    if not peak:
        raise HTTPException(status_code=404, detail="Peak not found")
    session.delete(peak)
    session.commit()
    return {"ok": True}
