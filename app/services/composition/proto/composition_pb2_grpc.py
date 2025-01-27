# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import app.services.composition.proto.composition_pb2 as composition__pb2


class CompositionServiceStub(object):
    """The composition service definition.
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.GetComposition = channel.unary_unary(
                '/composition.CompositionService/GetComposition',
                request_serializer=composition__pb2.GetCompositionRequest.SerializeToString,
                response_deserializer=composition__pb2.GetCompositionResponse.FromString,
                )


class CompositionServiceServicer(object):
    """The composition service definition.
    """

    def GetComposition(self, request, context):
        """Request to get a specific composition by user and composition ID
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_CompositionServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'GetComposition': grpc.unary_unary_rpc_method_handler(
                    servicer.GetComposition,
                    request_deserializer=composition__pb2.GetCompositionRequest.FromString,
                    response_serializer=composition__pb2.GetCompositionResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'composition.CompositionService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class CompositionService(object):
    """The composition service definition.
    """

    @staticmethod
    def GetComposition(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/composition.CompositionService/GetComposition',
            composition__pb2.GetCompositionRequest.SerializeToString,
            composition__pb2.GetCompositionResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
