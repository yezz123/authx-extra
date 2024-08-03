from datetime import datetime

import pytest
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from testcontainers.redis import RedisContainer

from authx_extra.cache import HTTPCache, cache, invalidate_cache


class User:
    id: str = "112358"


user = User()
app = FastAPI()


@pytest.fixture(scope="module")
def redis_container():
    with RedisContainer() as redis:
        yield redis


@pytest.fixture(scope="function")
def app_client(redis_container):
    redis_url = redis_container.get_connection_url()
    HTTPCache.init(redis_url=redis_url, namespace="test_namespace")
    yield TestClient(app)


@app.get("/b/home")
@cache(key="b.home", ttl_in_seconds=180)
async def home(request: Request, response: Response):
    return JSONResponse({"page": "home", "datetime": str(datetime.utcnow())})


@app.get("/b/logged-in")
@cache(key="b.logged_in.{}", obj="user", obj_attr="id")
async def logged_in(request: Request, response: Response, user=user):
    return JSONResponse(
        {"page": "home", "user": user.id, "datetime": str(datetime.utcnow())}
    )


async def my_ttl_callable():
    return 3600


@app.get("/b/ttl_callable")
@cache(key="b.ttl_callable_expiry", ttl_func=my_ttl_callable)
async def path_with_ttl_callable(request: Request, response: Response):
    return JSONResponse(
        {"page": "path_with_ttl_callable", "datetime": str(datetime.utcnow())}
    )


@app.post("/b/logged-in")
@invalidate_cache(
    key="b.logged_in.{}", obj="user", obj_attr="id", namespace="test_namespace"
)
async def post_logged_in(request: Request, response: Response, user=user):
    return JSONResponse(
        {"page": "home", "user": user.id, "datetime": str(datetime.utcnow())}
    )


@app.get("/b/profile")
@cache(key="b.profile.{}", obj="user", obj_attr="id")
async def logged_in(request: Request, response: Response, user=user):
    return JSONResponse(
        {"page": "profile", "user": user.id, "datetime": str(datetime.utcnow())}
    )


@app.post("/b/invalidate_multiple")
@invalidate_cache(
    keys=["b.logged_in.{}", "b.profile.{}"],
    obj="user",
    obj_attr="id",
    namespace="test_namespace",
)
async def invalidate_multiple(request: Request, response: Response, user=user):
    return JSONResponse(
        {"page": "invalidate_multiple", "datetime": str(datetime.utcnow())}
    )


def test_invalidate_multiple(app_client, redis_container):
    redis_client = redis_container.get_client()
    redis_client.flushdb()
    response = extracted_result(app_client, "/b/logged-in")
    response2 = extracted_result(app_client, "/b/profile")
    assert response2.headers["Cache-hit"] == "true"
    response3 = app_client.post(
        "/b/invalidate_multiple",
        headers={
            "Content-Type": "application/json",
            "X-Product-Id": "0fb6a4d4-ae65-4f18-be44-edb9ace6b5bb",
        },
    )
    assert response3.status_code == 200
    assert redis_client.get("test_namespace:b.logged_in.112358") is None
    assert redis_client.get("test_namespace:b.profile.112358") is None


def extracted_result(client, arg):
    result = client.get(
        arg,
        headers={
            "Content-Type": "application/json",
            "X-Product-Id": "0fb6a4d4-ae65-4f18-be44-edb9ace6b5bb",
        },
    )
    assert result.status_code == 200
    result = client.get(
        arg,
        headers={
            "Content-Type": "application/json",
            "X-Product-Id": "0fb6a4d4-ae65-4f18-be44-edb9ace6b5bb",
        },
    )
    return result


def test_home_cached_response(app_client, redis_container):
    redis_client = redis_container.get_client()
    redis_client.flushdb()
    response = app_client.get(
        "/b/home",
        headers={
            "Content-Type": "application/json",
            "X-Product-Id": "0fb6a4d4-ae65-4f18-be44-edb9ace6b5bb",
        },
    )
    assert response.status_code == 200
    response = app_client.get(
        "/b/home",
        headers={
            "Content-Type": "application/json",
            "X-Product-Id": "0fb6a4d4-ae65-4f18-be44-edb9ace6b5bb",
        },
    )
    assert response.headers["Cache-hit"] == "true"


def test_with_ttl_callable(app_client, redis_container):
    redis_client = redis_container.get_client()
    redis_client.flushdb()
    response = app_client.get(
        "/b/ttl_callable",
        headers={
            "Content-Type": "application/json",
            "X-Product-Id": "0fb6a4d4-ae65-4f18-be44-edb9ace6b5bb",
        },
    )
    assert response.status_code == 200
    response = app_client.get(
        "/b/ttl_callable",
        headers={
            "Content-Type": "application/json",
            "X-Product-Id": "0fb6a4d4-ae65-4f18-be44-edb9ace6b5bb",
        },
    )
    assert response.headers["Cache-hit"] == "true"
    assert (
        pytest.approx(
            redis_client.ttl("test_namespace:b.ttl_callable_expiry"), rel=1e-3
        )
        == 3600
    )


def test_home_cached_with_current_user(app_client, redis_container):
    redis_client = redis_container.get_client()
    redis_client.flushdb()

    response = app_client.get(
        "/b/logged-in",
        headers={
            "Content-Type": "application/json",
            "X-Product-Id": "0fb6a4d4-ae65-4f18-be44-edb9ace6b5bb",
        },
    )
    assert response.status_code == 200

    response = app_client.get(
        "/b/logged-in",
        headers={
            "Content-Type": "application/json",
            "X-Product-Id": "0fb6a4d4-ae65-4f18-be44-edb9ace6b5bb",
        },
    )
    assert response.headers["Cache-hit"] == "true"
    assert response.status_code == 200
    value = redis_client.get("test_namespace:b.logged_in.112358")
    assert value is not None


def test_cache_invalidation(app_client, redis_container):
    redis_client = redis_container.get_client()
    redis_client.flushdb()

    response = app_client.get(
        "/b/logged-in",
        headers={
            "Content-Type": "application/json",
            "X-Product-Id": "0fb6a4d4-ae65-4f18-be44-edb9ace6b5bb",
        },
    )
    assert response.status_code == 200

    response = app_client.get(
        "/b/logged-in",
        headers={
            "Content-Type": "application/json",
            "X-Product-Id": "0fb6a4d4-ae65-4f18-be44-edb9ace6b5bb",
        },
    )
    assert response.headers["Cache-hit"] == "true"
    assert response.status_code == 200
    value = redis_client.get("test_namespace:b.logged_in.112358")
    assert value is not None

    app_client.post(
        "/b/logged-in",
        headers={
            "Content-Type": "application/json",
            "X-Product-Id": "0fb6a4d4-ae65-4f18-be44-edb9ace6b5bb",
        },
    )

    response = app_client.get(
        "/b/logged-in",
        headers={
            "Content-Type": "application/json",
            "X-Product-Id": "0fb6a4d4-ae65-4f18-be44-edb9ace6b5bb",
        },
    )
    assert response.headers.get("Cache-hit", None) is None
