import pytest
import redis
from testcontainers.redis import RedisContainer

from authx_extra.addons.keys import HTTPKeys
from authx_extra.cache import HTTPCache


class TestHTTPKeys:
    @pytest.fixture(scope="class")
    def redis_container(self):
        with RedisContainer() as redis:
            yield redis

    @pytest.fixture(scope="function")
    def redis_client(self, redis_container):
        redis_url = redis_container.get_connection_url()
        client = redis.Redis.from_url(redis_url)
        yield client
        client.flushdb()

    @pytest.mark.asyncio
    async def test_generate_keys(self, redis_client):
        namespace = "test_namespace"
        redis_url = redis_client.connection_pool.connection_kwargs["url"]
        HTTPCache.init(redis_url=redis_url, namespace=namespace)
        namespaced_key = await HTTPKeys.generate_key(key="hello", config=HTTPCache)
        assert namespaced_key == f"{namespace}:hello"

    @pytest.mark.asyncio
    async def test_generate_key_with_attr(self, redis_client):
        class User:
            id: str = "112358"

        user = User()

        namespace = "test_namespace"
        redis_url = redis_client.connection_pool.connection_kwargs["url"]
        HTTPCache.init(redis_url=redis_url, namespace=namespace)
        namespaced_key = await HTTPKeys.generate_key(
            key="hello.{}", config=HTTPCache, obj=user, obj_attr="id"
        )
        assert namespaced_key == f"{namespace}:hello.112358"

    @pytest.mark.asyncio
    async def test_generate_keys_with_attr(self, redis_client):
        class User:
            id: str = "112358"

        user = User()

        namespace = "test_namespace"
        redis_url = redis_client.connection_pool.connection_kwargs["url"]
        HTTPCache.init(redis_url=redis_url, namespace=namespace)
        namespaced_keys = await HTTPKeys.generate_keys(
            keys=["hello.{}", "foo.{}"], config=HTTPCache, obj=user, obj_attr="id"
        )
        namespaced_keys = sorted(namespaced_keys)
        assert namespaced_keys[1] == f"{namespace}:hello.112358"
        assert namespaced_keys[0] == f"{namespace}:foo.112358"
