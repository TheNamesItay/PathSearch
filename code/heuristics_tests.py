import unittest

from graph_builder import build_small_grid


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)  # add assertion here

    def test_heuristic_values(self):
        name, graph, s, t = build_small_grid()
        print()



if __name__ == '__main__':
    unittest.main()
