"""
MCP Commute Assistant - 智能通勤助手
基于MCP协议的自动化通勤路线检查和通知系统
"""

__version__ = "1.0.0"
__author__ = "Standup Coder"
__email__ = "standup.coder@example.com"

from .main import create_app

__all__ = ['create_app']