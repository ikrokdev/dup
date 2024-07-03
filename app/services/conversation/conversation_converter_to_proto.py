from app.services.conversation.proto import conversation_pb2


def convert_conversation_to_proto(conversation):
    # Create an instance of the protobuf Conversation message
    proto_conversation = conversation_pb2.Conversation()

    # Convert each SpeakerTurn in the conversation to a protobuf Turn message
    for turn in conversation.turns:
        proto_turn = convert_turn_to_proto(turn)
        proto_conversation.turns.append(proto_turn)

    proto_conversation.topics.extend([convert_topic_to_proto(topic) for topic in conversation.topics])

    return proto_conversation


def convert_word_to_proto(word):
    return conversation_pb2.Word(
        word=word.word,
        score=word.score,
        start=word.start,
        end=word.end
    )


def convert_sentence_to_proto(sentence):
    proto_words = [convert_word_to_proto(word) for word in sentence.words]
    return conversation_pb2.Sentence(
        sentence_id=sentence.sentence_id,
        speaker_id=sentence.speaker_id,
        text=sentence.text,
        sentiment_score=sentence.sentiment_score if sentence.sentiment_score is not None else 0.0,
        words=proto_words,
        start=sentence.start,
        end=sentence.end
    )


def convert_topic_to_proto(topic):
    return conversation_pb2.Topic(
        topic_id=topic,
        name=topic,
        relevance=0
    )


def convert_to_start_conversation_response(elapsed_time):
    return conversation_pb2.StartConversationResponse(timer=str(elapsed_time))


def convert_turn_to_proto(turn):
    proto_sentences = [convert_sentence_to_proto(sentence) for sentence in turn.sentences]
    proto_words = [convert_word_to_proto(word) for word in turn.words]
    proto_topics = [convert_topic_to_proto(topic) for topic in []]
    return conversation_pb2.Turn(
        turn_id=turn.turn_id,
        speaker_id=turn.speaker_id,
        text=turn.text,
        sentences=proto_sentences,
        words=proto_words,
        topics=proto_topics,
        start=turn.start,
        end=turn.end
    )
