# coding: utf-8

from protocol import game_pb2
from protocol.commands import *
from protocol.serialize import send
from state.player_state.base import PlayerStateBase


class PromptState(PlayerStateBase):

    def enter(self, owner):
        super(PromptState, self).enter(owner)
        owner.table.player_prompts.append(owner.uuid)
        owner.send_prompts()

    def next_state(self, owner):
        if owner.machine.last_state.name == "WaitState":
            owner.machine.to_last_state()
        else:
            owner.machine.last_state.next_state(owner)

    def execute(self, owner, event, proto=None):
        super(PromptState, self).execute(owner, event, proto)
        from logic.player_action import action, discard
        if event == "action":
            action(owner, proto)
        elif event == "discard":
            discard(owner, proto)
        else:
            owner.table.logger.warn("player {0} event {1} not register".format(owner.seat, event))

