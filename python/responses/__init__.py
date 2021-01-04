from domino.core import log
from domino.responses import Response as BaseResponse

from domino.tables.postgres.server import Server 
from domino.tables.postgres.request_log import RequestLog

class Response(BaseResponse):
    def __init__(self, application, request):
        super().__init__(application, request)
        self.postgres = None
