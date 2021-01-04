from flask import make_response
from . import Response as BaseResponse
from . import RequestLog

class Response (BaseResponse):

    def __init__(self, application, request):
        super().__init__(application, request)
        self.account_id = self.get('account_id')

    def request_log_response_text(self):
        request_log_id = self.get('request_log_id')
        request_log = self.postgres.query(RequestLog).get(request_log_id)
        response  = make_response(request_log.response_text)
        response.headers['Content-Disposition'] = 'inline'
        if request_log.response_type == 'xml':
            response.headers['Content-Type'] = 'application/xml; charset=utf-8'
        else:
            #response.headers['Content-Type'] = 'application/octet-stream'
            response.headers['Content-Type'] = 'application/json; charset=utf-8'
            #response.headers['Content-Type'] = 'text; charset=utf-8'
        #response.headers['Content-Description'] = 'File Transfer'
        #response.headers['Content-Length'] = os.path.getsize(xml_file)
        return response

    def request_log_xml_file(self):
        request_log_id = self.get('request_log_id')
        request_log = self.postgres.query(RequestLog).get(request_log_id)
        response  = make_response(request_log.xml_file)
        #response.headers['Content-Type'] = 'text/html; charset=utf-8'
        response.headers['Content-Type'] = 'application/xml; charset=utf-8'
        #response.headers['Content-Description'] = 'File Transfer'
        response.headers['Content-Disposition'] = 'inline'
        #response.headers['Content-Length'] = os.path.getsize(xml_file)
        return response
