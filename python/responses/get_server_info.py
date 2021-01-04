import json
from . import Response as BaseResponse
from . import Server

class Response (BaseResponse):

    def __init__(self, application, request):
        super().__init__(application, request)

    def __call__(self):
        server_id = self.get('id')
        server = self.postgres.query(Server).get(server_id)
        if server:
            return json.dumps(server.info, ensure_ascii=False)
        else:
            return json.dumps({})
