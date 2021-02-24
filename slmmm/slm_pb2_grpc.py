# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from . import slm_pb2 as slm__pb2


class SLMStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.SetImage = channel.unary_unary(
                '/slm.SLM/SetImage',
                request_serializer=slm__pb2.Image.SerializeToString,
                response_deserializer=slm__pb2.Response.FromString,
                )
        self.SetScreen = channel.unary_unary(
                '/slm.SLM/SetScreen',
                request_serializer=slm__pb2.Screen.SerializeToString,
                response_deserializer=slm__pb2.Response.FromString,
                )
        self.GetNumScreens = channel.unary_unary(
                '/slm.SLM/GetNumScreens',
                request_serializer=slm__pb2.EmptyParams.SerializeToString,
                response_deserializer=slm__pb2.ScreenReply.FromString,
                )
        self.SetPosition = channel.unary_unary(
                '/slm.SLM/SetPosition',
                request_serializer=slm__pb2.Position.SerializeToString,
                response_deserializer=slm__pb2.Response.FromString,
                )
        self.GetPosition = channel.unary_unary(
                '/slm.SLM/GetPosition',
                request_serializer=slm__pb2.EmptyParams.SerializeToString,
                response_deserializer=slm__pb2.Position.FromString,
                )


class SLMServicer(object):
    """Missing associated documentation comment in .proto file."""

    def SetImage(self, request, context):
        """Set the image from a uint8 numpy bytes array and a width and height
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SetScreen(self, request, context):
        """Set the screen the slm is appearing on
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetNumScreens(self, request, context):
        """Get the current number of screens
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SetPosition(self, request, context):
        """Functions for setting the position on the screen
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetPosition(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_SLMServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'SetImage': grpc.unary_unary_rpc_method_handler(
                    servicer.SetImage,
                    request_deserializer=slm__pb2.Image.FromString,
                    response_serializer=slm__pb2.Response.SerializeToString,
            ),
            'SetScreen': grpc.unary_unary_rpc_method_handler(
                    servicer.SetScreen,
                    request_deserializer=slm__pb2.Screen.FromString,
                    response_serializer=slm__pb2.Response.SerializeToString,
            ),
            'GetNumScreens': grpc.unary_unary_rpc_method_handler(
                    servicer.GetNumScreens,
                    request_deserializer=slm__pb2.EmptyParams.FromString,
                    response_serializer=slm__pb2.ScreenReply.SerializeToString,
            ),
            'SetPosition': grpc.unary_unary_rpc_method_handler(
                    servicer.SetPosition,
                    request_deserializer=slm__pb2.Position.FromString,
                    response_serializer=slm__pb2.Response.SerializeToString,
            ),
            'GetPosition': grpc.unary_unary_rpc_method_handler(
                    servicer.GetPosition,
                    request_deserializer=slm__pb2.EmptyParams.FromString,
                    response_serializer=slm__pb2.Position.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'slm.SLM', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class SLM(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def SetImage(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/slm.SLM/SetImage',
            slm__pb2.Image.SerializeToString,
            slm__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def SetScreen(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/slm.SLM/SetScreen',
            slm__pb2.Screen.SerializeToString,
            slm__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetNumScreens(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/slm.SLM/GetNumScreens',
            slm__pb2.EmptyParams.SerializeToString,
            slm__pb2.ScreenReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def SetPosition(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/slm.SLM/SetPosition',
            slm__pb2.Position.SerializeToString,
            slm__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetPosition(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/slm.SLM/GetPosition',
            slm__pb2.EmptyParams.SerializeToString,
            slm__pb2.Position.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
