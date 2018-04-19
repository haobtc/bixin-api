import time

from .abstract import NaiveStorageBackend


class RedisStore(NaiveStorageBackend):

    _prefix = "bixin_api."

    def __init__(self, redis_client):
        """
        :type redis_client: redis.Redis
        """
        self.client = redis_client

    def _get_key(self, the_key):
        return "%s%s" % (self._prefix, the_key)

    @classmethod
    def get_ttl(cls, expire_at):
        now = time.time()
        ttl_seconds = expire_at - now
        if ttl_seconds < 0:
            ttl_seconds = 0
        return int(ttl_seconds)

    def set(self, key, value, expire_at):
        key = self._get_key(key)
        ttl = self.get_ttl(expire_at=expire_at)
        return self.client.setex(name=key, value=value, time=ttl)

    def get(self, key, require_unexpired=True):
        key = self._get_key(key)
        return self.client.get(key)

    def delete(self, key):
        key = self._get_key(key)
        return self.client.delete(key)
