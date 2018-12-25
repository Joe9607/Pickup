# coding: utf-8


from state.table_state.base import TableStateBase
from state.table_state.ready import ReadyState


class InitState(TableStateBase):
    def next_state(self, owner):
        owner.machine.trigger(ReadyState())

    def execute(self, owner, event):
        super(InitState, self).execute(owner, event)
        if event == "ready":
            owner.is_all_ready()
