from sqlmodel import Session

from app.main import Peak, engine

print("Load initial data...")

peak_1 = Peak(
    name="Mount Desert", latitude=44.342827, longitude=-68.307138, altitude=55
)
peak_2 = Peak(
    name="Mount Cadillac",
    latitude=44.409286,
    longitude=-68.247501,
    altitude=466,
)
peak_3 = Peak(
    name="Mount Taranaki Maunga",
    latitude=-39.296770,
    longitude=174.063399,
    altitude=2518,
)
peak_4 = Peak(
    name="Mount Tongariro",
    latitude=-39.1333,
    longitude=175.6500,
    altitude=1978,
)
peak_5 = Peak(
    name="Monte Perdido",
    latitude=42.6499974,
    longitude=0.0499998,
    altitude=3355,
)
peak_6 = Peak(
    name="Mont Blanc", latitude=45.833641, longitude=6.864594, altitude=4806
)

with Session(engine) as session:
    session.add(peak_1)
    session.add(peak_2)
    session.add(peak_3)
    session.add(peak_4)
    session.add(peak_5)
    session.add(peak_6)

    session.commit()

print("Initial data loaded")