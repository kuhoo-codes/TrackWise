from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from tests.test_helpers import AuthHelper


@patch("src.services.auth_service.redis_client")
def test_create_timeline_success(mock_redis: MagicMock, client: TestClient, auth_helper: AuthHelper) -> None:
    headers = auth_helper.get_auth_headers("appa")
    mock_redis.exists.return_value = 0
    payload = {
        "title": "My Career Timeline",
        "description": "Professional journey",
        "is_public": False,
        "default_zoom_level": 1,
    }

    response = client.post("/timelines", json=payload, headers=headers)
    data = response.json()

    assert response.status_code == 201
    assert data["title"] == payload["title"]
    assert data["description"] == payload["description"]
    assert "id" in data
    assert "created_at" in data


@patch("src.services.auth_service.redis_client")
def test_get_timelines_success(mock_redis: MagicMock, client: TestClient, auth_helper: AuthHelper) -> None:
    headers = auth_helper.get_auth_headers("appa")
    mock_redis.exists.return_value = 0
    client.post(
        "/timelines",
        json={"title": "Timeline A", "description": "Desc A", "is_public": False},
        headers=headers,
    )

    response = client.get("/timelines", headers=headers)
    data = response.json()

    assert response.status_code == 200
    assert isinstance(data, list)
    assert len(data) >= 1
    assert "id" in data[0]
    assert "title" in data[0]


@patch("src.services.auth_service.redis_client")
def test_get_single_timeline_success(mock_redis: MagicMock, client: TestClient, auth_helper: AuthHelper) -> None:
    headers = auth_helper.get_auth_headers("appa")
    mock_redis.exists.return_value = 0

    create_res = client.post(
        "/timelines",
        json={"title": "Single Timeline", "description": "", "is_public": False},
        headers=headers,
    )
    timeline_id = create_res.json()["id"]

    response = client.get(f"/timelines/{timeline_id}", headers=headers)
    data = response.json()

    assert response.status_code == 200
    assert data["id"] == timeline_id
    assert data["title"] == "Single Timeline"
    assert "nodes" in data


@patch("src.services.auth_service.redis_client")
def test_delete_timeline_success(mock_redis: MagicMock, client: TestClient, auth_helper: AuthHelper) -> None:
    headers = auth_helper.get_auth_headers("appa")
    mock_redis.exists.return_value = 0

    create_res = client.post(
        "/timelines",
        json={"title": "Delete Me", "description": "", "is_public": False},
        headers=headers,
    )
    timeline_id = create_res.json()["id"]

    delete_res = client.delete(f"/timelines/{timeline_id}", headers=headers)
    assert delete_res.status_code == 204

    get_res = client.get(f"/timelines/{timeline_id}", headers=headers)
    assert get_res.status_code == 404


@patch("src.services.auth_service.redis_client")
def test_create_timeline_node_success(mock_redis: MagicMock, client: TestClient, auth_helper: AuthHelper) -> None:
    headers = auth_helper.get_auth_headers("appa")
    mock_redis.exists.return_value = 0

    timeline_res = client.post(
        "/timelines",
        json={"title": "Node Timeline", "description": "", "is_public": False},
        headers=headers,
    )
    timeline_id = timeline_res.json()["id"]

    payload = {
        "timeline_id": timeline_id,
        "title": "Started Job",
        "type": "work",
        "start_date": "2022-01-01",
        "end_date": "2023-01-01",
        "is_current": False,
    }

    response = client.post("/timelines/node", json=payload, headers=headers)
    data = response.json()

    assert response.status_code == 201
    assert data["title"] == payload["title"]
    assert data["type"] == "work"
    assert "id" in data


@patch("src.services.auth_service.redis_client")
def test_get_timeline_node_with_children(mock_redis: MagicMock, client: TestClient, auth_helper: AuthHelper) -> None:
    headers = auth_helper.get_auth_headers("appa")
    mock_redis.exists.return_value = 0

    timeline_res = client.post(
        "/timelines",
        json={"title": "Parent Child Timeline", "description": "", "is_public": False},
        headers=headers,
    )
    timeline_id = timeline_res.json()["id"]

    parent_res = client.post(
        "/timelines/node",
        json={
            "timeline_id": timeline_id,
            "title": "Parent Node",
            "type": "work",
            "start_date": "2020-01-01",
            "is_current": True,
        },
        headers=headers,
    )
    parent_id = parent_res.json()["id"]

    client.post(
        "/timelines/node",
        json={
            "timeline_id": timeline_id,
            "parent_id": parent_id,
            "title": "Child Node",
            "type": "project",
            "start_date": "2021-01-01",
            "end_date": "2021-06-01",
            "is_current": False,
        },
        headers=headers,
    )

    response = client.get(f"/timelines/node/{parent_id}", headers=headers)
    data = response.json()

    assert response.status_code == 200
    assert data["id"] == parent_id
    assert len(data["children"]) == 1
    assert data["children"][0]["title"] == "Child Node"


@patch("src.services.auth_service.redis_client")
def test_update_timeline_node_success(mock_redis: MagicMock, client: TestClient, auth_helper: AuthHelper) -> None:
    headers = auth_helper.get_auth_headers("appa")
    mock_redis.exists.return_value = 0

    timeline_id = client.post(
        "/timelines",
        json={"title": "Update Node Timeline", "description": "", "is_public": False},
        headers=headers,
    ).json()["id"]

    node_id = client.post(
        "/timelines/node",
        json={
            "timeline_id": timeline_id,
            "title": "Old Title",
            "type": "work",
            "start_date": "2022-01-01",
            "is_current": True,
        },
        headers=headers,
    ).json()["id"]

    response = client.patch(
        f"/timelines/node/{node_id}",
        json={
            "title": "Updated Title",
            "type": "work",
            "start_date": "2022-01-01",
            "is_current": True,
        },
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"


@patch("src.services.auth_service.redis_client")
def test_delete_timeline_node_success(mock_redis: MagicMock, client: TestClient, auth_helper: AuthHelper) -> None:
    headers = auth_helper.get_auth_headers("appa")
    mock_redis.exists.return_value = 0

    timeline_id = client.post(
        "/timelines",
        json={"title": "Delete Node Timeline", "description": "", "is_public": False},
        headers=headers,
    ).json()["id"]

    node_id = client.post(
        "/timelines/node",
        json={
            "timeline_id": timeline_id,
            "title": "Temp Node",
            "type": "work",
            "start_date": "2022-01-01",
            "is_current": True,
        },
        headers=headers,
    ).json()["id"]

    response = client.delete(f"/timelines/node/{node_id}", headers=headers)
    assert response.status_code == 204


def test_timelines_unauthorized(client: TestClient) -> None:
    response = client.get("/timelines")
    assert response.status_code == 403
