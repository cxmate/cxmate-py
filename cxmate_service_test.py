import unittest
import random

import networkx
from cxmate_service import Stream, NetworkElementBuilder

class TestFromNetworkX(unittest.TestCase):
    def test_from_networkx(self):
        num_nodes = 100
        num_edges = 50
        net = create_random_networkx_mock(num_nodes, num_edges)
        net.graph['desc'] = 'example'
        nodeCount = 0
        edgeCount = 0

        for aspect in Stream.from_networkx(net):
            which = aspect.WhichOneof('element')
            if which == 'node':
                nodeCount += 1
                node = aspect.node
                self.assertEqual(net.node[node.id]['name'], node.name)
            elif which == 'edge':
                edgeCount += 1
                edge = aspect.edge
                self.assertEqual(edge.id, net[edge.sourceId][edge.targetId]['id'])
            elif which == 'nodeAttribute':
                attr = aspect.nodeAttribute
                self.assertEqual(net[attr.nodeId][attr.name], attr.value)
            elif which == 'edgeAttribute':
                attr = aspect.edgeAttribute
                a, b = edges[attr.edgeId]
                self.assertEqual(str(net[a][b]['value']), attr.value)
            elif which == 'networkAttribute':
                attr = aspect.networkAttribute
                self.assertEqual(net.graph[attr.name], attr.value)
            else:
                print("UNTESTED %s" % aspect)
        self.assertEqual(nodeCount, len(net))
        self.assertEqual(edgeCount, net.size())

    def testFromValue(self):
        typ, value = NetworkElementBuilder.from_value(1)
        self.assertEqual(typ, 'int')
        self.assertEqual(value, '1')

        typ, value = NetworkElementBuilder.from_value(False)
        self.assertEqual(typ, 'boolean')
        self.assertEqual(value, 'False')

        typ, value = NetworkElementBuilder.from_value(1.5)
        self.assertEqual(typ, 'float')
        self.assertEqual(value, '1.5')

        typ, value = NetworkElementBuilder.from_value('H')
        self.assertEqual(typ, 'string')
        self.assertEqual(value, 'H')

        typ, value = NetworkElementBuilder.from_value({1: 2})
        self.assertEqual(typ, 'string')
        self.assertEqual(value, '{1: 2}')

    def testToNetworkX(self):
        num_nodes = 100
        num_edges = 50
        net = create_random_networkx_mock(num_nodes, num_edges)
        stream = Stream.from_networkx(net)
        net_res = Stream.to_networkx(stream)

edges = {}
def create_random_networkx_mock(num_nodes=100, num_edges=100):
    n = networkx.Graph()
    for n_id in range(num_nodes):
        n.add_node(n_id, name=hex(n_id))
    ID = num_nodes
    for e_id in range(num_edges):
        n1 = random.randint(0, num_nodes-1)
        n2 = random.randint(0, num_nodes-2)
        val = random.choice([1, 1.5, 'a', True, {1:2}])
        edges[ID] = (n1, n2)
        n.add_edge(n1, n2, id=ID, value=val)
        ID += 1
    return n

if __name__ == '__main__':
    unittest.main()
