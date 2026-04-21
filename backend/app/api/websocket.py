import socketio
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins="*")
sio_app = socketio.ASGIApp(sio)

@sio.event
async def connect(sid, environ): pass
@sio.event
async def subscribe_pair(sid, data):
    p = data.get('pair')
    if p: sio.enter_room(sid, p)
