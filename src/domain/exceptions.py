"""Domain exceptions"""


class DomainException(Exception):
    """Domain exception base class"""

    pass


class CrawlerException(DomainException):
    """Crawler exception"""

    pass


class AnalyzerException(DomainException):
    """Analyzer exception"""

    pass


class NotifierException(DomainException):
    """Notifier exception"""

    pass


class ConfigurationException(DomainException):
    """Configuration exception"""

    pass
