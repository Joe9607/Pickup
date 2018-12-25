# coding: utf-8
from protocol import game_pb2
from protocol.commands import PROMPT, NOTIFY_MSG
from protocol.serialize import send
from rules.define import PLAYER_MSG_RECONNECT
from state.player_state.base import PlayerStateBase


class PromptDrawState(PlayerStateBase):

    def enter(self, owner):
        super(PromptDrawState, self).enter(owner)
        # owner.table.reset_proto(PROMPT)
        owner.table.player_prompts.append(owner.uuid)
        # owner.send_prompts()
        owner.proto.send()
        owner.table.clear_actions()

    def next_state(self, owner):
        owner.machine.last_state.next_state(owner)

    def execute(self, owner, event, proto=None):
        super(PromptDrawState, self).execute(owner, event, proto)
        from logic.player_action import action, discard
        if event == "action":
            action(owner, proto)
        elif event == "discard" and owner.table.state != 'HaiDiState':
            discard(owner, proto)
        else:
            owner.table.logger.warn("player {0} event {1} not register".format(owner.seat, event))
            proto_re = game_pb2.CommonNotify()
            proto_re.messageId = PLAYER_MSG_RECONNECT
            send(NOTIFY_MSG, proto_re, owner.session)