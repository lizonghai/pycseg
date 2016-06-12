# -*- coding: utf-8 -*-


import unittest

from pycseg.utils import shortest_path


class ShortestPathTestCase(unittest.TestCase):
    def setUp(self):
        self.graph = {'a': {'b': 1},
                      'b': {'c': 2, 'd': 5},
                      'c': {'d': 1},
                      'd': {}}

        self.graph2 = {'c': {'d': 3, 'e': 2},
                       'd': {'f': 4},
                       'e': {'d': 1, 'f': 2, 'g': 3},
                       'f': {'g': 2, 'h': 1},
                       'g': {'h': 2},
                       'h': {}, }

    def test_dijkstra(self):
        dist, pred = shortest_path.dijkstra(self.graph, 'a', 'd')
        self.assertDictEqual(dist, {'a': 0, 'c': 3, 'b': 1, 'd': 4})
        self.assertDictEqual(pred, {'b': 'a', 'c': 'b', 'd': 'c'})

    def test_dijkstra_shortest_path(self):
        path, distance = shortest_path.dijkstra_shortest_path(self.graph, 'a', 'c')
        self.assertListEqual(path, ['a', 'b', 'c'])
        self.assertEqual(distance, 3)

    def test_yen_ksp(self):
        source, target = 'c', 'h'
        paths = shortest_path.yen_ksp(self.graph2, source, target, 3)
        self.assertListEqual([path[0] for path in paths],
                             [['c', 'e', 'f', 'h'],
                              ['c', 'e', 'g', 'h'],
                              ['c', 'd', 'f', 'h']])

        paths = shortest_path.yen_ksp(self.graph2, source, target)
        self.assertListEqual([path[0] for path in paths],
                             [['c', 'e', 'f', 'h']])

        paths = shortest_path.yen_ksp(self.graph2, source, target, 10)
        print("TOP-10 shortest paths")
        for path in paths:
            print("cost:{}\tpath:{}".format(path[1][target], path[0]))


if __name__ == '__main__':
    unittest.main()
