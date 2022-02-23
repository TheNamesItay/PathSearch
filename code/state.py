state_index = 0


class State:
    def __init__(self, current, path, available_nodes):
        global state_index
        self.current = current
        self.path = path
        self.available_nodes = tuple(available_nodes)
        self.index = state_index
        self.bccs = []
        state_index += 1

    def __hash__(self):
        return self.index

    def print(self):
        print('-----------------------')
        print('current', self.current)
        print('path', self.path)
        print('available', self.available_nodes)
        print('comps', [c.h for c in self.bccs])
        print('-----------------------')

    def print_bccs(self):
        print('++++++ bccs:')
        for c in self.bccs:
            c.print()
        print('++++++')


class BiCompEntry:
    def __init__(self, in_node, out_node, nodes, h):
        self.in_node = in_node
        self.out_node = out_node
        self.nodes = nodes
        self.h = h

    def print(self):
        print('h', self.h, ' || in', self.in_node, ' || out', self.out_node, ' || nodes', self.nodes)