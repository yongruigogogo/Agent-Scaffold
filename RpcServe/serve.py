from concurrent import futures
import grpc
from Common.utils import initLogger
from RpcServe import agentService_pb2_grpc, agentService_pb2


class UserServiceServicer(agentService_pb2_grpc.UserServiceServicer):
    #实现 GetUserInfo 接口方法
    def GetUserInfo(self, request, context):
        # request：客户端传递的 UserRequest 实例
        # context：gRPC 上下文对象（用于设置状态码、错误信息等）
        user_id = request.user_id

        # 模拟数据库查询
        user_data = {
            1: {"username": "zhangsan", "age": 25, "email": "zhangsan@example.com"},
            2: {"username": "lisi", "age": 30, "email": "lisi@example.com"}
        }
        if user_id in user_data:
            data = user_data[user_id]
            return agentService_pb2.UserResponse(
                user_id=user_id,
                username=data["username"],
                age=data["age"],
                email=data["email"]
            )
        else:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"User with ID {user_id} not found")
            return agentService_pb2.UserResponse()

def serve():
    logger = initLogger()
    # 创建 gRPC 服务器（使用多线程处理请求）
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=50))
    # 注册自定义的服务实现到服务器
    agentService_pb2_grpc.add_UserServiceServicer_to_server(UserServiceServicer(), server)
    # 绑定端口（格式：[::]:端口号，支持 IPv4/IPv6）
    server.add_insecure_port("[::]:50051")
    # 启动服务器
    logger.info("gRPC server started on port 50051...")
    server.start()
    # 保持服务器运行（阻塞主线程）
    server.wait_for_termination()

if __name__ == "__main__":
    serve()