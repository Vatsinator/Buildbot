import sys
from datetime import datetime


output = sys.stdout


def info(msg):
    """
    Log message as a standard info.
    :param msg: The message to be logged.
    """
    dt = datetime.utcnow()
    log = '[%s-%s-%s %s:%s:%s] %s\n' % (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, msg)
    output.write(log)
