import time

from app import ConversationQueries
from app.services.conversation.proto import conversation_pb2_grpc
from .conversation_converter_to_proto import convert_to_start_conversation_response, convert_turn_to_proto, \
    convert_conversation_to_proto


def print_descriptor(descriptor, indent=0):
    indent_str = ' ' * indent
    print(indent_str + "Descriptor Name:", descriptor.name)

    for field in descriptor.fields:
        print(indent_str + "  Field:", field.name, "Type:", field.type)

    for nested_type in descriptor.nested_types:
        print(indent_str + "  Nested Type:")
        print_descriptor(nested_type, indent + 4)

    for enum_type in descriptor.enum_types:
        print(indent_str + "  Enum Type:", enum_type.name)
        for enum_value in enum_type.values:
            print(indent_str + "    Value:", enum_value.name)


class ConversationService(conversation_pb2_grpc.ConversationServiceServicer):
    def __init__(self):
        self.queries = ConversationQueries('../data/---')

    def StartConversation(self, request, context):
        start_time = time.time()
        # while True: # Send updates till the client termination
        for update in range(10):  # Send 10 updates only
            elapsed_time = time.time() - start_time
            yield convert_to_start_conversation_response(str(elapsed_time))
            time.sleep(3)

    def GetTurn(self, request, context):
        turn = self.queries.get_turn(request.turn_id, request.include_words)
        proto_turn = convert_turn_to_proto(turn)
        return proto_turn

    def GetConversation(self, request, context):
        print_descriptor(request.DESCRIPTOR)
        conversation = self.queries.get_conversation(request.include_words)
        proto_conversation = convert_conversation_to_proto(conversation)
        return proto_conversation
