# coding: utf-8


from behavior_tree.base import NodeBase


class IteratorNode(NodeBase):
    def __init__(self, weight, condition_nodes):
        super(IteratorNode, self).__init__(weight)
        self.condition_nodes = condition_nodes

    def condition(self, player):
        # super(SequenceNode, self).condition(player)
        flag = False
        for node in self.condition_nodes:
            if node.condition(player):
                flag = True
        return flag
