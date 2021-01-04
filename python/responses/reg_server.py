from domino.core import log
from . import Response as BaseResponse
from . import Server

class Response (BaseResponse):

    def __init__(self, application, request):
        super().__init__(application, request)

    def __call__(self):
        server_id = self.get('id')
        server_name = self.get('name')
        if not server_name:
            server_name = server_id
        if not server_id:
            return f'НЕ ЗАДАН СЕРВЕР (id)', 500
        server = self.postgres.query(Server).get(server_id)
        if server:
            server.name = server_name
        else:
            server = Server(id = server_id, name = server_name)
            self.postgres.add(server)
        
        return self.success()
