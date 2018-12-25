# coding: utf-8
from rules.player_rules.chow import ChowRule
from rules.player_rules.pong import PongRule
from rules.player_rules.draw_concealed_kong import DrawConcealedKongRule
from rules.player_rules.draw_exposed_kong import DrawExposedKongRule
from rules.player_rules.discard_exposed_kong import DiscardExposedKongRule
from rules.player_rules.win import WinRule
from rules.player_rules.discard_win import DiscardWinRule
from rules.player_rules.draw_win import DrawWinRule
from rules.player_rules.qg_win import QGWinRule
from rules.player_rules.draw_concealed_kong_kg import DrawConcealedKongKGRule
from rules.player_rules.draw_exposed_kong_kg import DrawExposedKongKGRule
from rules.player_rules.discard_exposed_kong_kg import DiscardExposedKongKGRule
from rules.player_rules.yao import YaoRule
from rules.player_rules.ting import TingRule
from rules.player_rules.ting_kong import TingKongRule



rules_dict = {
    "ChowRule": ChowRule(),
    "PongRule": PongRule(),
    "DrawConcealedKongRule": DrawConcealedKongRule(),
    "DrawExposedKongRule": DrawExposedKongRule(),
    "DiscardExposedKongRule": DiscardExposedKongRule(),
    "WinRule": WinRule(),
    "DiscardWinRule": DiscardWinRule(),
    "DrawWinRule": DrawWinRule(),
    "QGWinRule": QGWinRule(),
    "DrawConcealedKongKGRule": DrawConcealedKongKGRule(),
    "DrawExposedKongKGRule": DrawExposedKongKGRule(),
    "DiscardExposedKongKGRule": DiscardExposedKongKGRule(),
    "YaoRule": YaoRule(),
    "TingRule": TingRule(),
    "TingKongRule": TingKongRule(),

}
