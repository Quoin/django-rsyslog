from __future__ import absolute_import

import re
import socket
from datetime import datetime

from django.views.debug import SafeExceptionReporterFilter
from pythonjsonlogger.jsonlogger import JsonFormatter


class Rfc3164JsonFormatter(JsonFormatter):
    def __init__(self, *args, **kwargs):
        self.app_name = kwargs.pop('app_name', 'python')
        if 'fmt' not in kwargs:
            kwargs['fmt'] = ("%(asctime) %(created) %(filename) %(funcName) "
                             "%(lineno) %(module) %(msecs) %(message) %(name) "
                             "%(pathname) %(process) %(processName) %(relativeCreated) "
                             "%(stack_info) %(exc_info) %(thread) %(threadName)")
        super(Rfc3164JsonFormatter, self).__init__(*args, **kwargs)

    converter = datetime.fromtimestamp

    def formatTime(self, record, datefmt=None):
        t = self.converter(record.created)
        return t.isoformat() + "Z"

    def format(self, record):
        return "{datetime} {hostname} {app_name}[{process}]: {message}".format(
            datetime=self.formatTime(record),
            hostname=socket.gethostname(),
            app_name=getattr(record, 'app_name', self.app_name),
            process=record.process,
            message=super(Rfc3164JsonFormatter, self).format(record))


class DjangoSyslogJsonFormatter(Rfc3164JsonFormatter):
    """
    Should be mixed in after JsonFormatter for a log formatter.
    """
    def format_request(self, request):
        safe_filter = SafeExceptionReporterFilter()
        http_headers = {k: v for k, v in request.META.items() if k.startswith('HTTP_')}
        clean_post = safe_filter.get_post_parameters(request)

        return '{method} {path}\nHTTP Headers:\n  {headers}\nPOST:\n  {params}'.format(
            method=request.method,
            path=request.get_full_path(),
            headers='\n  '.join(['%s: %s' % (re.sub('HTTP_', '', k), v)
                                 for k, v in http_headers.items()]),
            params='\n  '.join(['%s: %s' % (k, v) for k, v in clean_post.items()]) or 'None')

    def format_user(self, request):
        if not hasattr(request, 'user') or not request.user:
            return 'No User'

        user = request.user
        if user.is_anonymous():
            return 'Anonymous User'
        else:
            return ('Authenticated User\n'
                    '  id: {id}\n'
                    '  username: {username}\n'.format(id=user.id, username=user.get_username()))

    def add_fields(self, log_record, record, message_dict):
        super(DjangoSyslogJsonFormatter, self).add_fields(log_record, record, message_dict)
        if hasattr(record, 'request'):
            log_record['request'] = self.format_request(record.request)
            log_record['user'] = self.format_user(record.request)
        else:
            log_record['request'] = 'No request'
            log_record['user'] = 'No user'
