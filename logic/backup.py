# coding: utf-8

import json
from settings import redis
from logic.player import Player
from logic.table import Table
from logic.table_conf import TableConf
from state.player_state.prompt_discard import PromptDiscardState
from state.player_state.prompt_draw import PromptDrawState
from web.request import WebRequest

from state.player_state.deal import DealState
from state.player_state.discard import DiscardState
from state.player_state.draw import DrawState
from state.player_state.draw_after_kong import DrawAfterKongState
from state.player_state.init import InitState
from state.player_state.pause import PauseState

from state.player_state.prompt_ting_kong import PromptTingKongState
from state.player_state.prompt import PromptState
from state.player_state.ready import ReadyState
from state.player_state.settle import SettleState
from state.player_state.wait import WaitState

from rules.player_rule_states.chow import ChowState
from rules.player_rule_states.pong import PongState
from rules.player_rule_states.yao import YaoState
from rules.player_rule_states.win import WinState
from rules.player_rule_states.discard_win import DiscardWinState
from rules.player_rule_states.draw_win import DrawWinState
from rules.player_rule_states.qg_win import QGWinState
from rules.player_rule_states.discard_exposed_kong import DiscardExposedKongState
from rules.player_rule_states.draw_exposed_kong import DrawExposedKongState
from rules.player_rule_states.draw_concealed_kong import DrawConcealedKongState
from rules.player_rule_states.ting import TingState

from state.table_state.deal import DealState as TableDealState
from state.table_state.end import EndState as TableEndState
from state.table_state.init import InitState as TableInitState
from state.table_state.ready import ReadyState as TableReadyState
from state.table_state.restart import RestartState as TableRestartState
from state.table_state.settle_for_room import SettleForRoomState as TableSettleForRoomState
from state.table_state.settle_for_round import SettleForRoundState as TableSettleForRoundState
from state.table_state.step import StepState as TableStepState
from state.table_state.wait import WaitState as TableWaitState
from state.table_state.haidi import HaiDiState as TableHaiDiState
from rules.table_rule_states.niao import NiaoState as TableNiaoState

from rules.player_rule_states.discard_exposed_kong_kg import DiscardExposedKongKGState
from rules.player_rule_states.draw_exposed_kong_kg import DrawExposedKongKGState
from rules.player_rule_states.draw_concealed_kong_kg import DrawConcealedKongKGState

player_state = {
    "DealState": DealState(),
    "DiscardState": DiscardState(),
    "DrawState": DrawState(),
    "InitState": InitState(),
    "PauseState": PauseState(),
    "PromptState": PromptState(),
    "PromptDrawState": PromptDrawState(),
    "PromptDiscardState": PromptDiscardState(),
    "PromptTingKongState": PromptTingKongState(),
    "ReadyState": ReadyState(),
    "SettleState": SettleState(),
    "WaitState": WaitState(),
    "ChowState": ChowState(),
    "PongState": PongState(),
    "WinState": WinState(),
    "DiscardWinState": DiscardWinState(),
    "DrawWinState": DrawWinState(),
    "QGWinState": QGWinState(),
    "DiscardExposedKongState": DiscardExposedKongState(),
    "DrawExposedKongState": DrawExposedKongState(),
    "DrawConcealedKongState": DrawConcealedKongState(),
    "DiscardExposedKongKGState": DiscardExposedKongKGState(),
    "DrawExposedKongKGState": DrawExposedKongKGState(),
    "DrawConcealedKongKGState": DrawConcealedKongKGState(),
    "YaoState": YaoState(),
    "DrawAfterKongState":DrawAfterKongState(),
    "TingState": TingState(),

}

table_state = {
    "DealState": TableDealState(),
    "EndState": TableEndState(),
    "InitState": TableInitState(),
    "ReadyState": TableReadyState(),
    "RestartState": TableRestartState(),
    "SettleForRoomState": TableSettleForRoomState(),
    "SettleForRoundState": TableSettleForRoundState(),
    "StepState": TableStepState(),
    "WaitState": TableWaitState(),
    "NiaoState": TableNiaoState(),
    "HaiDiState": TableHaiDiState(),
}


def loads_player(uuid, table):
    raw = redis.get("player:{0}".format(uuid))
    # print "player", uuid, raw
    if not raw:
        return
    data = json.loads(raw)
    player = Player(uuid, None, None, table)
    for k, v in data.items():
        if k in ("table", "session", "machine", "proto"):
            continue
        else:
            player.__dict__[k] = v
    proto = data.get("proto")
    if proto:
        player.proto.__dict__.update(proto)
        player.proto.load()
    state = data["machine"]
    for k, v in player.action_dict.items():
        player.action_dict[int(k)] = v
        del player.action_dict[k]
    player.machine.last_state = player_state[state[0]] if state[0] else None
    player.machine.cur_state = player_state[state[1]] if state[1] else None
    return player


def loads_table(room_id):
    raw = redis.get("table:{0}".format(room_id))
    # print "table", room_id, raw
    if not raw:
        return
    data = json.loads(raw)

    table = Table(room_id, None, None, None)
    for k, v in data.items():
        if k in ("logger", "conf", "player_dict", "seat_dict", "machine"):
            continue
        else:
            table.__dict__[k] = v

    table.conf = TableConf(table.kwargs)
    table.request = WebRequest(room_id, table.room_uuid, table.conf.game_type, table.conf.app_id, table.owner)

    for i in data["player_dict"]:
        table.player_dict[i] = loads_player(i, table)

    for i, j in data["seat_dict"].items():
        table.seat_dict[int(i)] = table.player_dict[j]

    state = data["machine"]
    table.machine.last_state = table_state[state[0]] if state[0] else None
    table.machine.cur_state = table_state[state[1]] if state[1] else None
    return table

