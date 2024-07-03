cd ..\app\proto

python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. conversation.proto

python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. data_loaders.proto

python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. composition.proto
