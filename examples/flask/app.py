from io import BytesIO

from flask import Flask, send_file, request, jsonify
from redis import Redis
import qrcode

from bixin_api import Client
from bixin_api.event import make, LoginEvent
from bixin_api.storage.redis import RedisStore
from bixin_api.utils import login


BIXIN_CONF = dict(
    name="your_vendor_name",
    secret="secret",
    aes_key="aes_key",
)
redis_client = Redis()

store = RedisStore(redis_client)

bixin_client = Client(
    vendor_name=BIXIN_CONF['name'],
    secret=BIXIN_CONF['secret'],
    access_token=None,
)

session_id = "1"

app = Flask(__name__)


def mk_qrcode(url):
    with BytesIO() as f:
        qrcode.make(url).save(f)
    return f


@app.route('/api/v1/u/events/', methods=['POST'])
def callback():
    event = make(request.data, aes_key=BIXIN_CONF['aes_key'])
    if not isinstance(event, LoginEvent):
        return {}
    session = login.get_unexpired_session(
        storage_backend=store,
        session_id=event.qr_code_id,
    )
    if session is None:
        return {}
    session = login.mark_session_as_bind(session=session)
    login.save_session(store, session)
    return ""

@app.route('/qr_code/')
def qr_code():
    session = login.get_or_create_session(
        storage_backend=store,
        bixin_client=bixin_client,
        session_id=session_id,
    )
    session.save()
    fp = mk_qrcode(session.url)
    return send_file(
        fp,
        mimetype='image/png',
    )


@app.route('/qr_code/status/')
def qr_code_status():
    session = login.get_unexpired_session(
        storage_backend=store,
        session_id=session_id,
    )
    if session.is_bind:
        # login the user here and delete the qrcode record, anyway
        data = {
            "session_id": session_id,
            'status': "already bind",
        }
    else:
        data = {
            "session_id": session_id,
            'status': 'not bind yet',
        }
    return jsonify(data)


app.run(debug=False, host='0.0.0.0', port=2333)
