import logging, coloredlogs

FIELD_STYLES = dict(
    asctime=dict(color='green'),
    hostname=dict(color='magenta'),
    levelname=dict(color='white'),
    filename=dict(color='magenta'),
    name=dict(color='blue'),
    threadName=dict(color='green')
)

LEVEL_STYLES = dict(
    debug=dict(color='green'),
    info=dict(color='cyan'),
    verbose=dict(color='blue'),
    warning=dict(color='yellow'),
    error=dict(color='red'),
    critical=dict(color='red')
)

INFO = logging.INFO
DEBUG = logging.DEBUG

def newLogger(name: str, level: int) -> logging.Logger:
    coloredlogs.install(
        level=level,
        fmt="%(asctime)s %(filename)s:%(lineno)d %(levelname)s %(message)s",
        level_styles=LEVEL_STYLES,
        field_styles=FIELD_STYLES,
    )
    return logging.getLogger(name)
