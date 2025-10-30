"""Domain exceptions"""


class DomainException(Exception):
    """领域异常基类"""

    pass


class CrawlerException(DomainException):
    """爬虫异常"""

    pass


class AnalyzerException(DomainException):
    """分析器异常"""

    pass


class NotifierException(DomainException):
    """通知器异常"""

    pass


class ConfigurationException(DomainException):
    """配置异常"""

    pass
