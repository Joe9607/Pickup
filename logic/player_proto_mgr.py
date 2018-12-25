# coding: utf-8

import weakref

from protocol import game_pb2
from protocol.commands import *
from protocol.serialize import send


class PlayerProtoMgr(object):
    def __init__(self, owner):
        self.owner = weakref.proxy(owner)
        self.lock = None
        # 协议
        self.p = None
        # 命令
        self.c = None

    def require(self):
        self.lock = True
        self.p = None
        self.c = None

    def release(self):
        self.lock = False

    def send(self):
        if not self.lock:
            return
        self.release()

        if self.p:
            cmd = self.c
        else:
            cmd = PROMPT
            self.p = game_pb2.PromptResponse()

        for k, v in self.owner.action_dict.items():
            prompt = self.p.prompt.add()
            prompt.action_id = k
            prompt.prompt = v["prompt"]
            prompt.op_card.card = v["op_card"]
            for c in v["ref_cards"]:
                ref_card = prompt.ref_card.add()
                ref_card.card = c

        send(cmd, self.p, self.owner.session)
        self.owner.table.logger.info(self.owner.action_dict)

    def dump(self):
        return {"lock": self.lock, "p": unicode(self.p.SerializeToString(), errors='ignore') if self.p else None, "c": self.c}

    def load(self):
        if not self.p or not self.c:
            return
        if self.c == DRAW:
            proto = game_pb2.DrawResponse()
        elif self.c == DISCARD:
            proto = game_pb2.DiscardResponse()
        elif self.c == ACTION:
            proto = game_pb2.ActionResponse()
        elif self.c == DEAL:
            proto = game_pb2.DealResponse()
        elif self.c == HAIDI:
            proto = game_pb2.QH_HaiDiResponse()
        else:
            proto = game_pb2.PromptResponse()
        self.p = proto.ParseFromString(str(self.p))
