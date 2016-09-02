# Django-Rsyslog

This is a log handler and formatter for Django projects to use to send logs to
Rsyslog.

## Handler
The handler uses the octet-counted encoding which allows for new lines within
messages (although you generally shouldn't need new lines if you use the
associated formatter).  It is a subclass of the base `logging.SysLogHandler` so
all options used there are also applicable and required.  You can probably use
the standard SysLogHandler with the JSON formatter although I haven't tried this.

## Formatter
The formatter is very opinionated and will output a Syslog line with the log
message as a JSON string with most of the typical fields included in Django
error log records included by default (see `django_rsyslog/formatters.py` for
full list), as well as request information (method, path, headers, POST data)
and username/id from `request.user` (if logged in).  It uses Django's
`SafeExceptionReporterFilter` to mask sensitive data, but this requires manual
config in your Django views.

## Usage
Here is an example logging config in the Django settings file:

```python
LOGGING = {
    ...
    'formatters': {
        'rfc3164_json': {
            "()": 'django_rsyslog.DjangoSyslogJsonFormatter',
            "app_name": "django",
        },
        ...
    },
    'handlers': {                                                                                                                                                                                    
        'rsyslog': {
            'level': 'WARNING',
            'class': 'django_rsyslog.OctetCountedSysLogHandler',
            'address': ('rsyslog', 1514),
            'socktype': socket.SOCK_DGRAM,
            'formatter': 'rfc3164_json',
        },
        ...
    }
    'loggers': {
        ...
        'django': {
            'handlers': ['rsyslog'],
            'level': 'WARNING',
            'propagate': False,
        },
        ...
    }
}
```

You can make `app_name` anything you want in the formatter config, although I
have found it easier to just leave it as 'django' so I can easily reuse generic
filters in logstash (which rsyslog can forward to if you want).

No need to put stuff in INSTALLED_APPS, just make sure this lib is installed in
your python env.
