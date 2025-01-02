from logging import Logger, getLogger


class ModelLogger:
    _logger: Logger = None

    def __init__(self):
        if self._logger is None:
            logger = getLogger('__maskarade__')
            self.set_logger(logger)

    @classmethod
    def set_logger(cls, logger: Logger):
        cls._logger = logger

        cls.log = logger.log
        cls.debug = logger.debug
        cls.info = logger.info
        cls.warning = logger.warning
        cls.error = logger.error
        cls.exception = logger.exception
