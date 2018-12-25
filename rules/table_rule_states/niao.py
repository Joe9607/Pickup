# coding: utf-8

from state.table_state.base import TableStateBase
from state.table_state.settle_for_round import SettleForRoundState


class NiaoState(TableStateBase):
    def enter(self, owner):
        super(NiaoState, self).enter(owner)
        """抓鸟完成切换到小结算状态"""

        if owner.conf.is_normal_niao():
            from logic.table_action import draw_niao_hard
            draw_niao_hard(owner)

        owner.logger.info({"winners": owner.winner_list, "losers": owner.loser_list, "cards": owner.draw_niao_list})
        owner.machine.trigger(SettleForRoundState())
