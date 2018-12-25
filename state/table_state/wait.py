# coding: utf-8

from state.table_state.base import TableStateBase
from logic.table_action import step,end


class WaitState(TableStateBase):

    def execute(self, owner, event):
        super(WaitState, self).execute(owner, event)
        if event == "step":
            step(owner)
        elif event == "end":
            end(owner)
