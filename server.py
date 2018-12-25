# coding: utf-8
import time
from uuid import uuid4
# import platform
from tornado.ioloop import IOLoop, PeriodicCallback
# from tornado.httpserver import HTTPServer
from tornado.websocket import WebSocketHandler
from tornado.web import Application
from tornado.options import define, options


# noinspection PyAbstractClass
class WSServer(WebSocketHandler):
    uuid = None
    last_time = 0

    def check_origin(self, origin):
        return True

    def open(self, *args, **kwargs):
        from logic.session_manager import SessionMgr
        self.uuid = str(uuid4())
        SessionMgr().add(self)

    def on_close(self):
        from logic.session_manager import SessionMgr
        try:
            player = SessionMgr().player(self)
            if player:
                player.online_status(False)
                player.session = None
        except ReferenceError:
            pass
        SessionMgr().cancel(self)

    def on_message(self, buf):
        self.last_time = time.time()
        from protocol.deserialize import receive
        receive(buf, self)


def main():
    define("host", "0.0.0.0", type=str)
    define("server_port", 8051, type=int)
    # define("server_port", 8045, type=int)
    define("logger_port", 8047, type=int)
   # define("redis_host", "192.168.36.77", type=str)
    define("redis_host", "192.168.1.3", type=str)
    define("redis_port", 6379, type=int)
    define("redis_password", None, type=str)
    define("redis_db", 6, type=int)
    options.parse_command_line()

    from logic.table_manager import TableMgr
    TableMgr().reload()
    from web.handler import CreateRoomHandler, MaintenanceHandler, DismissRoomHandler, LoadBalanceHandler, \
        ExistRoomHandler, RunningHandler, BroadcastHandler
    app = Application(
        handlers=[
            (r"/ws", WSServer),
            (r"/web/create_room", CreateRoomHandler),
            (r"/web/maintenance", MaintenanceHandler),
            (r"/web/dismiss", DismissRoomHandler),
            (r"/web/load_balance", LoadBalanceHandler),
            (r"/web/exist_room", ExistRoomHandler),
            (r"/web/running", RunningHandler),
            (r"/web/broadcast", BroadcastHandler),
        ],
    )

    # app.settings["debug"] = True
    app.listen(options.server_port)
    # if platform.system() == "Windows":
    #     app.settings["debug"] = True
    #     app.listen(options.port)
    # else:
    #     http_server = HTTPServer(app)
    #     http_server.bind(options.port, options.host)
    #     http_server.start(num_processes=0)  # tornado将按照cpu核数来fork进程

    # if platform.system() == "Windows":
    #     from logger import LogRotate
    #     log_rotate = LogRotate()
    #     PeriodicCallback(log_rotate.consumer, 1000).start()

    from logic.session_manager import SessionMgr, heartbeat
    PeriodicCallback(SessionMgr().heartbeat, 1000*heartbeat).start()
    IOLoop.instance().start()


if __name__ == '__main__':
    main()
