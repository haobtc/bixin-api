import json

import time

from ..storage.abstract import NaiveStorageBackend


def mk_login_session_cls(storage_backend):

    assert isinstance(storage_backend, NaiveStorageBackend)


    class LoginSession:
        """
        :type _store: bixin_api.storage.abstract.NaiveStorageBackend
        """

        _key_prefix = 'login.'
        _store = None

        def __init__(
                self, session_id,
                url, is_bind, expire_at=None,
                bixin_user_id=None,
        ):
            if self._store is None:
                raise RuntimeError("Store should be set before LoginSession instantiation.")
            # 如果登录了，则is_bind应该被标记为True
            self.session_id = session_id
            self.url = url
            self.bixin_user_id = bixin_user_id
            self.is_bind = is_bind
            self.expire_at = expire_at or time.time() + 360

            self._save_key = self._get_save_key(session_id)

        @classmethod
        def _get_save_key(cls, session_id):
            return "%s%s" % (cls._key_prefix, session_id)

        def as_dict(self):
            return {
                'session_id': self.session_id,
                'url': self.url,
                'bixin_user_id': self.bixin_user_id,
                'is_bind': self.is_bind,
                'expire_at': self.expire_at,
            }

        @classmethod
        def new(cls, bixin_client, session_id, is_app=True):
            """
            :type bixin_client: bixin_api.client.Client
            """
            url = bixin_client.get_login_qr_code(
                qr_code_id=session_id,
                is_app=is_app,
            )
            return cls(
                session_id=session_id,
                url=url,
                is_bind=False,
            )

        @classmethod
        def get_or_create(cls, bixin_client, session_id, is_app=True):
            qrcode = cls.get_unexpired(session_id)
            if qrcode is None:
                qrcode = cls.new(bixin_client, session_id, is_app=is_app)
            return qrcode

        @classmethod
        def get_unexpired(cls, session_id):
            """
            Return None if no result.
            """
            key = cls._get_save_key(session_id)
            data = cls._store.get(key)
            if data is not None:
                return cls(**json.loads(data))
            return None

        def mark_as_bind(self):
            self.is_bind = True
            self.save()

        def save(self):
            self._store.set(
                self._save_key,
                value=json.dumps(self.as_dict()),
                expire_at=self.expire_at,
            )

        def delete(self):
            self._store.delete(self._save_key)

    LoginSession._store = storage_backend

    return LoginSession
