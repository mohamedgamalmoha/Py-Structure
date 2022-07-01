import logging
from abc import abstractmethod


from .protocols import Singleton


class BaseMode(metaclass=Singleton):
    """Abstract base class for representing modes for decorators"""

    @abstractmethod
    def case_info(self, *args, **kwargs):
        """Show general information message"""
        raise NotImplementedError

    @abstractmethod
    def case_success(self, *args, **kwargs):
        """Show the successfully execution message"""
        raise NotImplementedError

    @abstractmethod
    def cae_failed(self, *args, **kwargs):
        """Show the successfully execution message"""
        raise NotImplementedError


class LogMode(BaseMode):
    """Log mode to show the flow of execution in a log file"""

    level = logging.DEBUG
    msg_format: str = '%(asctime)s - %(name)s - %(message)s'
    date_format: str = '%d-%b-%Y %H:%M:%S'
    filename: str = 'debug.log'

    def __init__(self, msg_format: str = None, date_format: str = None, filename: str = None, level: int = None):
        self.msg_format = msg_format or self.msg_format
        self.date_format = date_format or self.date_format
        self.filename = filename or self.filename
        self.level = level or self.level

    def __post_init__(self):
        # customizing log configuration
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(self.level)

        self.formatter = logging.Formatter(self.msg_format, datefmt=self.date_format)

        self.file_handler = logging.FileHandler(self.filename)
        self.file_handler.setLevel(self.level)
        self.file_handler.setFormatter(self.formatter)

        self.logger.addHandler(self.file_handler)

    def case_info(self, msg: str, *args, **kwargs):
        self. logger.info(msg)

    def case_success(self, msg, *args, **kwargs):
        self.logger.debug(msg)

    def cae_failed(self, msg, *args, **kwargs):
        self.logger.error(msg)


class PrintMode(BaseMode):
    """Print mode to show the flow of execution in shell"""

    def __init__(self):
        print('Started')

    def case_success(self, msg, *args, **kwargs):
        print(msg)

    def cae_failed(self, msg, *args, **kwargs):
        print(msg)

    def case_info(self, msg: str, *args, **kwargs):
        print(msg)


class NoneMode(BaseMode):
    """None mode to pass any kind of actions during the flow of execution"""

    def case_success(self, msg, *args, **kwargs): pass
    def cae_failed(self, msg, *args, **kwargs): pass
    def case_info(self, msg: str, *args, **kwargs): pass
