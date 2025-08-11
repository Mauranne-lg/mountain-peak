from fastapi.testclient import TestClient
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app

client = TestClient(app)


@pytest.mark.anyio
async def test_read_peaks():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/peaks/")
    assert response.status_code == 200
    assert len(response.json()) == 6


@pytest.mark.anyio
async def test_read_peaks_within_bouding_box():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/peaks/?min_lat=45&max_lat=78&min_lon=5&max_lon=7")
    assert response.status_code == 200
    assert response.json() == [
        {
            "name": "Mont Blanc",
            "latitude": 45.833641,
            "longitude": 6.864594,
            "altitude": 4806,
            "id": 6,
        }
    ]


@pytest.mark.anyio
async def test_read_peaks_within_bouding_box_bad_data():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get(
            "/peaks/?min_lat=-100&max_lat=100&min_lon=-190&max_lon=190"
        )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_read_peak():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/peaks/1")
    assert response.status_code == 200
    assert response.json() == {
        "name": "Mount Desert",
        "latitude": 44.342827,
        "longitude": -68.307138,
        "altitude": 55,
        "id": 1,
    }


@pytest.mark.anyio
async def test_read_nonexistent_peak():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("peaks/7")
    assert response.status_code == 404
    assert response.json() == {"detail": "Peak not found"}


@pytest.mark.anyio
async def test_create_peak():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post(
            "/peaks/",
            json={
                "name": "Mont Petit Vignemale",
                "latitude": 42.774712,
                "longitude": -0.135086,
                "altitude": 3032,
            },
        )
    assert response.status_code == 200
    assert response.json() == {
        "id": 7,
        "name": "Mont Petit Vignemale",
        "latitude": 42.774712,
        "longitude": -0.135086,
        "altitude": 3032,
    }


@pytest.mark.anyio
async def test_update_peak():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.patch(
            "/peaks/7",
            json={
                "name": "Petit Vignemale",
                "latitude": 42.774612,
                "longitude": -0.1349086,
                "altitude": 3032,
            },
        )
    assert response.status_code == 200
    assert response.json() == {
        "id": 7,
        "name": "Petit Vignemale",
        "latitude": 42.774612,
        "longitude": -0.1349086,
        "altitude": 3032,
    }


@pytest.mark.anyio
async def test_update_peak_non_existing_peak():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.patch(
            "/peaks/25",
            json={
                "name": "Petit Vignemale",
                "latitude": 42.774712,
                "longitude": -0.135086,
                "altitude": 3032,
            },
        )
    assert response.status_code == 404


@pytest.mark.anyio
async def test_delete_peak():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.delete(
            "/peaks/7",
        )
    assert response.status_code == 200


@pytest.mark.anyio
async def test_delete_nonexistent_peak():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.delete(
            "/peaks/25",
        )
    assert response.status_code == 404
    assert response.json() == {"detail": "Peak not found"}
