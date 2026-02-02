"""
自定义异常定义
"""

class MCPBaseException(Exception):
    """MCP基础异常类"""
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class ConfigValidationError(MCPBaseException):
    """配置验证异常"""
    def __init__(self, message: str):
        super().__init__(message, "CONFIG_VALIDATION_ERROR")


class AMAPAPIError(MCPBaseException):
    """高德地图API异常"""
    def __init__(self, message: str, status_code: int = None):
        self.status_code = status_code
        super().__init__(message, "AMAP_API_ERROR")


class DingTalkAPIError(MCPBaseException):
    """钉钉API异常"""
    def __init__(self, message: str, status_code: int = None):
        self.status_code = status_code
        super().__init__(message, "DINGTALK_API_ERROR")


class RouteCalculationError(MCPBaseException):
    """路线计算异常"""
    def __init__(self, message: str):
        super().__init__(message, "ROUTE_CALCULATION_ERROR")


class MessageSendError(MCPBaseException):
    """消息发送异常"""
    def __init__(self, message: str):
        super().__init__(message, "MESSAGE_SEND_ERROR")


class TaskExecutionError(MCPBaseException):
    """任务执行异常"""
    def __init__(self, message: str):
        super().__init__(message, "TASK_EXECUTION_ERROR")