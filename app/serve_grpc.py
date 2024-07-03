from concurrent import futures
from grpc import server as grpc_server
from app.services import (YTProcessorService, ConversationService, CompositionService)

from app.services.composition.proto import composition_pb2, composition_pb2_grpc
from app.services.data_loaders.proto import data_loaders_pb2, data_loaders_pb2_grpc
from app.services.conversation.proto import conversation_pb2_grpc, conversation_pb2


from grpc_reflection.v1alpha import reflection

def include_reflection(server):
    reflection.enable_server_reflection((
        conversation_pb2.DESCRIPTOR.services_by_name['ConversationService'].full_name,
        data_loaders_pb2.DESCRIPTOR.services_by_name['YouTubeProcessor'].full_name,
        composition_pb2.DESCRIPTOR.services_by_name['CompositionService'].full_name,
        reflection.SERVICE_NAME,
    ), server)


def register_services(server):
    conversation_pb2_grpc.add_ConversationServiceServicer_to_server(ConversationService(), server)
    data_loaders_pb2_grpc.add_YouTubeProcessorServicer_to_server(YTProcessorService(), server)
    composition_pb2_grpc.add_CompositionServiceServicer_to_server(CompositionService(), server)


def serve():
    server = grpc_server(futures.ThreadPoolExecutor(max_workers=10))
    server.add_insecure_port('[::]:50051')
    include_reflection(server)
    register_services(server)
    server.start()
    print("Server started on port 50051.")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()