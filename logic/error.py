# coding: utf-8

from protocol import game_pb2
from protocol.commands import *

state_error_proto = {
    "DiscardState": {},
    "DrawState": {},
    "ReadyState": {},
    "InitState": {
        "exit_room": (EXIT_ROOM, game_pb2.ExitRoomResponse, 1),
        "ready": (READY, game_pb2.ReadyResponse, 2),
    },
    "WaitState": {},
}
