from collections import namedtuple
import json

import time

from ..storage.abstract import NaiveStorageBackend


__KEY_PREFIX = "login."

LoginSession = namedtuple(
    "LoginSession",
    (
        'session_id',
        'url',
        'is_bind',
        'expire_at',
        'bixin_user_id',
    ),
)


def _get_save_key(key):
    return "%s%s" % (__KEY_PREFIX, key)


def save_session(storage_backend, session: LoginSession):
    save_key = _get_save_key(session.session_id)
    storage_backend.set(
        save_key,
        value=json.dumps(session._asdict()),
        expire_at=session.expire_at,
    )


def delete_session(storage_backend, session_id):
    """
    :type storage_backend: bixin_api.storage.abstract.NaiveStorageBackend
    """
    key = _get_save_key(session_id)
    return storage_backend.delete(key)


def mark_session_as_bind(session: LoginSession):
    session_dict = session._asdict()
    session_dict.pop('is_bind')
    return LoginSession(
        session.is_bind,
        **session_dict
    )


def create_session(
        session_id,
        url,
        expire_at=None,
        bixin_user_id=None,
):
    return LoginSession(
        session_id=session_id,
        url=url,
        is_bind=False,
        expire_at=expire_at or time.time() + 360,
        bixin_user_id=bixin_user_id,
    )


def get_or_create_session(
        storage_backend,
        bixin_client,
        session_id,
        expire_at=None,
):
    """
    :type storage_backend: bixin_api.storage.abstract.NaiveStorageBackend
    :type bixin_client: bixin_api.client.Client
    """
    assert isinstance(storage_backend, NaiveStorageBackend)
    session = get_unexpired_session(storage_backend, session_id)
    if session_id is not None:
        return session
    login_url = bixin_client.get_login_qr_code(
        qr_code_id=session_id,
        is_app=True,
    )
    session = create_session(
        session_id=session_id,
        url=login_url,
        expire_at=expire_at,
    )
    save_session(storage_backend, session)
    return session


def get_unexpired_session(storage_backend, session_id):
    """
    Return None if no result.
    """
    key = _get_save_key(session_id)
    data = storage_backend.get(key)
    if data is not None:
        return LoginSession(**json.loads(data))
    return None
