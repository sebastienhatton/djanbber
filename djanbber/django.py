# -*- coding: utf-8 -*-
'''
Created on 15.10.2012

@author: unax
'''
from logging import Handler
from django.views.debug import (
    get_exception_reporter_filter,
    ExceptionReporter,
)
import traceback
from sender import JabberSender
from django.conf import settings

class Logger(Handler):
    sender = None
    def __init__(self, **kwargs):
        Handler.__init__(self, **kwargs)
        self.sender = JabberSender.create(**settings.DJANBBER)

    def emit(self, record):
        try:
            request = record.request
            subject = '%s (%s IP): %s' % (
                record.levelname,
                (request.META.get('REMOTE_ADDR') in settings.INTERNAL_IPS
                 and 'internal' or 'EXTERNAL'),
                record.getMessage()
            )
            f = get_exception_reporter_filter(request)
            request_repr = f.get_request_repr(request)
        except Exception:
            subject = '%s: %s' % (
                record.levelname,
                record.getMessage()
            )
            request = None
            request_repr = "Request repr() unavailable."
        subject = self.format_subject(subject)

        if record.exc_info:
            exc_info = record.exc_info
            stack_trace = '\n'.join(traceback.format_exception(*record.exc_info))
        else:
            exc_info = (None, record.getMessage(), None)
            stack_trace = 'No stack trace available'

        message = "%s\n\n%s" % (stack_trace, request_repr)
        reporter = ExceptionReporter(request, is_email=True, *exc_info)
        #html_message = self.include_html and reporter.get_traceback_html() or None
        self.sender.send(message)
