# coding: utf-8


from state.table_state.base import TableStateBase


class RestartState(TableStateBase):

    def execute(self, owner, event):
        super(RestartState, self).execute(owner, event)
        if event == "ready":
            owner.is_all_ready()
