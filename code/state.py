state_index = 0


class State:
    def __init__(self, current, path, available_nodes, bccs=[], snake_d=-1):
        global state_index
        self.current = current
        self.path = path
        self.available_nodes = tuple(available_nodes)
        self.index = state_index
        self.bccs = bccs
        self.snake_dimension = snake_d
        state_index += 1

    @classmethod
    def state_from_tuple(cls, state_tuple):
        current = state_tuple[0]
        path = state_tuple[1]
        available_nodes = state_tuple[2]
        bccs = state_tuple[3]
        snake_dimension = state_tuple[4]
        return cls(current, path, available_nodes, bccs, snake_dimension)

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

    def update_dimension(self, d):
        self.snake_dimension = d

    def to_tuple(self):
        return self.current, self.path, self.available_nodes, [bcc.to_tuple() for bcc in
                                                               self.bccs], self.snake_dimension


class BiCompEntry:
    def __init__(self, in_node, out_node, nodes, h):
        self.in_node = in_node
        self.out_node = out_node
        self.nodes = nodes
        self.h = h

    def print(self):
        print('h', self.h, ' || in', self.in_node, ' || out', self.out_node, ' || nodes', self.nodes)

    def to_tuple(self):
        return self.h, self.in_node, self.out_node, list(self.nodes)