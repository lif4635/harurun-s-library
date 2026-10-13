import contextlib
import io
import json
import os
import tempfile
import unittest
import random
from unittest.mock import patch

from library_codex.debug.DebugView import dump_array, dump_flow, dump_graph
from library_codex.graph_flow.MaxFlow import MaxFlowGraph
from library_codex.graph_flow.MinCostFlow import MinCostFlowGraph
from library_codex.graph_flow.MinCostBFlow import MinCostBFlow
from library_codex.graph_flow.PushRelabel import PushRelabel
from library_codex.fenwick_tree.BIT import BIT
from library_codex.segment_tree.SegTree import SegTree


class TestDebugView(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)

    def read(self, path):
        with open(path, encoding="utf-8") as stream:
            return json.load(stream)

    def test_flow_snapshots_do_not_mutate(self):
        g = MaxFlowGraph(4)
        for edge in [(0, 1, 3), (0, 2, 2), (1, 2, 1), (1, 3, 2), (2, 3, 3), (2, 2, 8), (0, 1, 0)]:
            g.add_edge(*edge)
        g.flow(0, 3, 1)
        before = g.edges()
        path = dump_flow(g, 0, 3, directory=self.directory.name)
        partial = self.read(path)
        self.assertFalse(partial["minimumCut"])
        self.assertEqual(before, g.edges())
        g.flow(0, 3)
        self.assertEqual(path, dump_flow(g, 0, 3, directory=self.directory.name))
        result = self.read(path)
        self.assertTrue(result["minimumCut"])
        self.assertEqual(result["edges"][0]["flow"], "3")
        self.assertEqual(result["edges"][0]["reverse"], "3")
        g.change_edge(0, 3, 0)
        self.assertFalse(self.read(dump_flow(g, 0, 3, directory=self.directory.name))["minimumCut"])

    def test_cost_flow_and_large_integer(self):
        g = MinCostFlowGraph(2)
        g.add_edge(0, 1, 10 ** 30, 7)
        g.flow(0, 1, 10 ** 20)
        edge = self.read(dump_flow(g, 0, 1, directory=self.directory.name))["edges"][0]
        self.assertEqual(edge["capacity"], str(10 ** 30))
        self.assertEqual(edge["flow"], str(10 ** 20))
        self.assertEqual(edge["cost"], "7")

    def test_graph_and_array_protocol(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            path = dump_graph(2, [(0, 1, 10 ** 30), (1, 1)], directed=True,
                              labels=["<script>", "終点"], positions=[(0, 0), (2, 4)], directory=self.directory.name)
        result = self.read(path)
        self.assertEqual(output.getvalue(), "")
        self.assertEqual(result["nodes"][1]["position"], [2.0, 4.0])
        self.assertEqual(result["edges"][0]["weight"], str(10 ** 30))
        class Values:
            def tolist(self):
                return [0, 10 ** 30, "</script>"]
        array = self.read(dump_array(Values(), directory=self.directory.name))
        self.assertEqual(array["values"], ["0", str(10 ** 30), "</script>"])
        self.assertEqual(self.read(dump_graph(0, [], directory=self.directory.name))["nodes"], [])

    def test_atomic_failure_and_bounds(self):
        path = dump_array([1], directory=self.directory.name)
        with patch("os.replace", side_effect=OSError("failure")):
            with self.assertRaises(OSError):
                dump_array([2], directory=self.directory.name)
        self.assertEqual(self.read(path)["values"], ["1"])
        self.assertFalse(any(name.endswith(".tmp") for name in os.listdir(self.directory.name)))
        for n, edges in [(501, []), (1, [(0, 1)]), (1, [(0, 0)] * 3001), (1, [(0, 0, float("inf"))])]:
            with self.assertRaises(ValueError):
                dump_graph(n, edges, directory=self.directory.name)
        with self.assertRaises(ValueError):
            dump_array(range(10001), directory=self.directory.name)
        with self.assertRaises(ValueError):
            dump_array(["x" * 2100000], directory=self.directory.name)
        self.assertEqual(self.read(path)["values"], ["1"])

    def test_environment_and_name_is_not_a_path(self):
        with patch.dict(os.environ, {"HARU_DUMP_DIR": self.directory.name}):
            path = dump_array([3], name="../../unsafe")
        self.assertEqual(os.path.dirname(path), self.directory.name)
        self.assertEqual(self.read(path)["name"], "../../unsafe")

    def test_random_maxflow_backends(self):
        rng = random.Random(20261014)
        for backend in (MaxFlowGraph, PushRelabel):
            for _ in range(20):
                g = backend(6)
                for _ in range(20):
                    g.add_edge(rng.randrange(6), rng.randrange(6), rng.randrange(9))
                g.flow(0, 5)
                before = g.edges()
                result = self.read(dump_flow(g, 0, 5, directory=self.directory.name))
                self.assertEqual(result["reachable"], g.min_cut(0))
                self.assertTrue(result["minimumCut"])
                self.assertEqual(g.edges(), before)

    def test_bflow_and_real_array_structures(self):
        g = MinCostBFlow(2)
        g.add_edge(0, 1, -2, 5, 3)
        g.add_supply(0, 2)
        g.add_demand(1, 2)
        self.assertTrue(g.run()[0])
        edge = self.read(dump_flow(g, directory=self.directory.name))["edges"][0]
        self.assertEqual((edge["lower"], edge["flow"], edge["reverse"]), ("-2", "2", "4"))
        for values in (BIT([2, 5, 7]), SegTree(min, 10 ** 9, [2, 5, 7])):
            self.assertEqual(self.read(dump_array(values, directory=self.directory.name))["values"], ["2", "5", "7"])
            self.assertEqual(values.tolist(), [2, 5, 7])


if __name__ == "__main__":
    unittest.main()
