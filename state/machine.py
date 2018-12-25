# coding: utf-8

import weakref


class Machine(object):
    def __init__(self, owner):
        self.owner = weakref.proxy(owner)
        self.last_state = None
        self.cur_state = None
        self.owner.machine = self

    def trigger(self, new_state):
        if self.cur_state:
            self.cur_state.exit(self.owner)
            self.last_state = self.cur_state
        self.cur_state = new_state
        self.owner.state = new_state.name
        self.cur_state.before(self.owner)
        self.cur_state.enter(self.owner)
        self.cur_state.after(self.owner)
        # self.owner.dumps()

    def to_last_state(self):
        self.trigger(self.last_state)

    def execute(self, callback, proto):
        self.cur_state.execute(self.owner, callback, proto)

    def next_state(self):
        self.cur_state.next_state(self.owner)
