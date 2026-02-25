"""
Google Sheets MCP服务器
提供Google Sheets API操作功能
"""

import os
from typing import Any, Dict, List, Optional

from .base_server import BaseMCPServer, MCPTool, MCPResource, ServerCapability


class GoogleSheetsMCPServer(BaseMCPServer):
    """Google Sheets MCP服务器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.credentials_path = config.get("credentials_path", os.environ.get("GOOGLE_CREDENTIALS_PATH", ""))
        self.service_account_json = config.get("service_account_json", os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", ""))
        super().__init__(config)
    
    def register_tools(self):
        """注册Google Sheets操作工具"""
        self._register_tool(MCPTool(
            name="create_spreadsheet",
            description="创建新表格",
            input_schema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "表格标题"},
                    "sheet_title": {"type": "string", "description": "工作表标题"}
                },
                "required": ["title"]
            },
            capability=ServerCapability.WRITE
        ))
        
        self._register_tool(MCPTool(
            name="read_range",
            description="读取表格范围",
            input_schema={
                "type": "object",
                "properties": {
                    "spreadsheet_id": {"type": "string", "description": "表格ID"},
                    "range": {"type": "string", "description": "范围如 Sheet1!A1:B10"}
                },
                "required": ["spreadsheet_id", "range"]
            },
            capability=ServerCapability.READ
        ))
        
        self._register_tool(MCPTool(
            name="write_range",
            description="写入表格范围",
            input_schema={
                "type": "object",
                "properties": {
                    "spreadsheet_id": {"type": "string", "description": "表格ID"},
                    "range": {"type": "string", "description": "范围"},
                    "values": {"type": "array", "description": "要写入的数据"}
                },
                "required": ["spreadsheet_id", "range", "values"]
            },
            capability=ServerCapability.WRITE
        ))
        
        self._register_tool(MCPTool(
            name="append_row",
            description="追加行数据",
            input_schema={
                "type": "object",
                "properties": {
                    "spreadsheet_id": {"type": "string", "description": "表格ID"},
                    "sheet_name": {"type": "string", "description": "工作表名称"},
                    "values": {"type": "array", "description": "行数据"}
                },
                "required": ["spreadsheet_id", "values"]
            },
            capability=ServerCapability.WRITE
        ))
        
        self._register_tool(MCPTool(
            name="list_spreadsheets",
            description="列出所有表格",
            input_schema={
                "type": "object",
                "properties": {},
                "required": []
            },
            capability=ServerCapability.READ
        ))
        
        self._register_tool(MCPTool(
            name="get_spreadsheet_info",
            description="获取表格信息",
            input_schema={
                "type": "object",
                "properties": {
                    "spreadsheet_id": {"type": "string", "description": "表格ID"}
                },
                "required": ["spreadsheet_id"]
            },
            capability=ServerCapability.READ
        ))
    
    def register_resources(self):
        """注册资源"""
        self._register_resource(MCPResource(
            uri="sheets://spreadsheets",
            name="spreadsheet_list",
            description="表格列表"
        ))
    
    async def _get_sheets_service(self):
        """获取Google Sheets服务"""
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        
        if self.service_account_json:
            import json
            info = json.loads(self.service_account_json)
            credentials = service_account.Credentials.from_service_account_info(
                info, scopes=["https://www.googleapis.com/auth/spreadsheets"]
            )
        elif self.credentials_path:
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path, scopes=["https://www.googleapis.com/auth/spreadsheets"]
            )
        else:
            raise ValueError("No credentials provided")
        
        return build("sheets", "v4", credentials=credentials)
    
    async def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """执行Google Sheets操作"""
        spreadsheet_id = params.get("spreadsheet_id", "")
        range_str = params.get("range", "")
        
        service = await self._get_sheets_service()
        sheets = service.spreadsheets()
        
        if tool_name == "create_spreadsheet":
            spreadsheet = {
                "properties": {"title": params.get("title", "New Spreadsheet")},
                "sheets": [{
                    "properties": {"title": params.get("sheet_title", "Sheet1")},
                    "data": [{"startRow": 0, "startColumn": 0}]
                }]
            }
            result = sheets.create(body=spreadsheet).execute()
            return {"spreadsheet_id": result.get("spreadsheetId"), "url": result.get("spreadsheetUrl")}
        
        elif tool_name == "read_range":
            result = sheets.values().get(
                spreadsheetId=spreadsheet_id,
                range=range_str
            ).execute()
            return {"values": result.get("values", [])}
        
        elif tool_name == "write_range":
            body = {"values": params.get("values", [])}
            result = sheets.values().update(
                spreadsheetId=spreadsheet_id,
                range=range_str,
                valueInputOption="USER_ENTERED",
                body=body
            ).execute()
            return {"updated_cells": result.get("updatedCells")}
        
        elif tool_name == "append_row":
            sheet_name = params.get("sheet_name", "Sheet1")
            range_str = f"{sheet_name}!A:A"
            body = {"values": [params.get("values", [])]}
            result = sheets.values().append(
                spreadsheetId=spreadsheet_id,
                range=range_str,
                valueInputOption="USER_ENTERED",
                body=body
            ).execute()
            return {"updated_rows": result.get("updates", {}).get("updatedRows")}
        
        elif tool_name == "list_spreadsheets":
            from googleapiclient.discovery import build
            from google.oauth2 import service_account
            
            if self.service_account_json:
                import json
                info = json.loads(self.service_account_json)
                credentials = service_account.Credentials.from_service_account_info(
                    info, scopes=["https://www.googleapis.com/auth/drive.readonly"]
                )
            else:
                credentials = service_account.Credentials.from_service_account_file(
                    self.credentials_path, scopes=["https://www.googleapis.com/auth/drive.readonly"]
                )
            
            drive = build("drive", "v3", credentials=credentials)
            results = drive.files().list(
                q="mimeType='application/vnd.google-apps.spreadsheet'",
                pageSize=50
            ).execute()
            return {"files": results.get("files", [])}
        
        elif tool_name == "get_spreadsheet_info":
            result = sheets.get(spreadsheetId=spreadsheet_id).execute()
            return result
        
        raise ValueError(f"Unknown tool: {tool_name}")
    
    async def _read_resource_content(self, resource: MCPResource) -> Any:
        """读取资源内容"""
        if resource.uri == "sheets://spreadsheets":
            return await self.execute_tool("list_spreadsheets", {})
        raise ValueError(f"Unknown resource: {resource.uri}")
