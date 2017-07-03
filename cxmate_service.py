import sys
import time
import logging
from  concurrent.futures import ThreadPoolExecutor

import networkx
import grpc

import cxmate_pb2
import cxmate_pb2_grpc

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

class ServiceServicer(cxmate_pb2_grpc.cxMateServiceServicer):
    """
    CyServiceServicer is an implementation of a grpc service definiton to process CX streams
    """
    def __init__(self, process):
        """
        Construct a new 'CyServiceServicer' grpc service object

        :param process: A function that handles processing a call to the service
        """
        self.process = process

    def StreamNetworks(self, input_stream, context):
        """
        A generator function called by grpc. Will catch all exceptions to protect
        the service

        :param element_iter: An iterator yielding CX protobuf objects
        :param context: A grpc context object with request metadata
        :returns: Must generate CX protobuf objects
        """
        #try:
        output_stream = self.process(input_stream)
        for element in output_stream:
            yield element

        #except Exception as e:
        """
            message = 'Unexpected error in the heat diffusion service: '  + str(e)
            error = self.create_internal_crash_error(message, 500)
            print error
            yield error
            """

    def create_internal_crash_error(self, message, status):
        element = cxmate_pb2.NetworkElement()
        error = element.error
        error.status = status
        error.code = 'cy://heat-diffusion/' + str(status)
        error.message = message
        error.link = 'http://logs.cytoscape.io/heat-diffusion'
        return element

class Stream:
    """
    Static methods to convert popular network formats to and from CX stream iterators
    """

    @staticmethod
    def to_networkx(ele_iter):
        """
        Creates a networkx object from a stream iterator

        :param ele_iter: A stream iterator iterating CX elements
        :returns: A networkx object
        """
        parameters = {}
        attrs = []
        edges = {}
        network = networkx.Graph()
        for ele in ele_iter:
            #print 'Processing element'
            #print ele
            ele_type = ele.WhichOneof('element')
            if ele_type == 'parameter':
                param = ele.parameter
                parameters[param.name] = param.value
            elif ele_type == 'node':
                node = ele.node
                network.add_node(int(node.id), name=node.name)
            elif ele_type == 'edge':
                edge = ele.edge
                src, tgt = int(edge.sourceId), int(edge.targetId)
                edges[int(edge.id)] = (src, tgt)
                network.add_edge(src, tgt, id=int(edge.id), interaction=edge.interaction)
            elif ele_type == 'nodeAttribute':
                attr = ele.nodeAttribute
                network.add_node(attr.nodeId, **{attr.name: Stream.parse_value(attr)})
            elif ele_type == 'edgeAttribute':
                attr = ele.edgeAttribute
                attrs.append(attr)
            elif ele_type == 'networkAttribute':
                attr = ele.networkAttribute
                network[attr.name] = Stream.parse_value(attr)

        for attr in attrs:
            source, target = edges[int(attr.edgeId)]
            network[source][target][attr.name] = Stream.parse_value(attr)
        #print network.nodes(data=True)
        #print network.edges(data=True)
        #print parameters
        return network, parameters

    @staticmethod
    def from_networkx(networkx):
        """
        Creates a stream iterator from a networkx object

        :param networkx: A networkx object
        :returns: A stream iterator iterating CX elements
        """

        for nodeId, attrs in networkx.nodes(data=True):
            yield NetworkElementBuilder.Node(nodeId, attrs.get('name', ''))

            for k, v in attrs.items():
                if k not in ('name'):
                    yield NetworkElementBuilder.NodeAttribute(nodeId, k, v)

        for sourceId, targetId, attrs in networkx.edges(data=True):
            yield NetworkElementBuilder.Edge(attrs['id'], sourceId, targetId, attrs.get('interaction', ''))

            for k, v in attrs.items():
                if k not in ('interaction', 'id'):
                    yield NetworkElementBuilder.EdgeAttribute(attrs['id'], k, v)

        for key, value in networkx.graph.items():
            yield NetworkElementBuilder.NetworkAttribute(key, value)

    @staticmethod
    def parse_value(attr):
        value = attr.value
        if attr.type:
            if attr.type in ('boolean'):
                value = value.lower() in ('true')
            elif attr.type in ('double', 'float'):
                value = float(value)
            elif attr.type in ('integer', 'short', 'long'):
                value = int(value)
        return value

class NetworkElementBuilder():
    """
    Factory class for declaring the network element from networkx attributes
    """
    @staticmethod
    def from_value(value):
        if isinstance(value, bool):
            return 'boolean', str(value)
        elif isinstance(value, float):
            return 'float', str(value)
        elif isinstance(value, int):
            return 'integer', str(value)
        return 'string', str(value)

    @staticmethod
    def Node(nodeId, name):
        ele = cxmate_pb2.NetworkElement()
        node = ele.node
        node.id = nodeId
        node.name = name
        return ele

    @staticmethod
    def Edge(edgeId, sourceId, targetId, interaction):
        ele = cxmate_pb2.NetworkElement()
        edge = ele.edge
        edge.id = edgeId
        edge.sourceId = sourceId
        edge.targetId = targetId
        edge.interaction = interaction
        return ele

    @staticmethod
    def NodeAttribute(nodeId, key, value):
        ele = cxmate_pb2.NetworkElement()
        nodeAttr = ele.nodeAttribute
        nodeAttr.nodeId = nodeId
        typ, value = NetworkElementBuilder.from_value(value)
        nodeAttr.type = typ
        nodeAttr.name = key
        nodeAttr.value = value
        return ele

    @staticmethod
    def EdgeAttribute(edgeId, key, value):
        ele = cxmate_pb2.NetworkElement()
        edgeAttr = ele.edgeAttribute
        edgeAttr.edgeId = edgeId
        typ, value = NetworkElementBuilder.from_value(value)
        edgeAttr.type = typ
        edgeAttr.name = key
        edgeAttr.value = value
        return ele

    @staticmethod
    def NetworkAttribute(key, value):
        ele = cxmate_pb2.NetworkElement()
        networkAttr = ele.networkAttribute
        networkAttr.name = key
        typ, value = NetworkElementBuilder.from_value(value)
        networkAttr.type = typ
        networkAttr.value = value
        return ele

class Service:
    """
    A cxMate service
    """

    def process(self, input_stream):
        """
        Process handles a single cxMate request.

        :param input_stream: A stream iterator yielding CX protobuf objects
        :returns: A stream iterator yielding CX protobuf objects
        """
        pass

    def run(self, listen_on = '0.0.0.0:8080', max_workers=10):
        """
        Run starts the service and then waits for a keyboard interupt

        :param str listen_on: The tcp address the service should listen on, 0.0.0.0:8080 by default
        :param int max_workers: The number of worker threads serving the service, 10 by default
        :returns: none
        """
        server = grpc.server(ThreadPoolExecutor(max_workers=max_workers))
        servicer = ServiceServicer(self.process)
        cxmate_pb2_grpc.add_cxMateServiceServicer_to_server(servicer, server)
        server.add_insecure_port(listen_on)
        server.start()
        try:
            while True:
                time.sleep(_ONE_DAY_IN_SECONDS)
        except KeyboardInterrupt:
            server.stop(0)

