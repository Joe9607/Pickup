# coding: utf-8


from state.base import StateBase


class TableStateBase(StateBase):
    def __init__(self):
        super(TableStateBase, self).__init__()
        self.register = {}

    def enter(self, owner):
        owner.dumps()
        owner.logger.info("table enter {0}".format(self.name))

    def execute(self, owner, event):
        owner.logger.info("table execute event {0}".format(event))
        owner.event = event
