"""
Browser MCP服务器
提供浏览器自动化功能
"""

from typing import Any, Dict, List, Optional

from .base_server import BaseMCPServer, MCPTool, MCPResource, ServerCapability


class BrowserMCPServer(BaseMCPServer):
    """Browser MCP服务器 (使用Playwright)"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.headless = config.get("headless", True) if config else True
        self._browser = None
        self._context = None
        super().__init__(config)
    
    def register_tools(self):
        """注册浏览器操作工具"""
        self._register_tool(MCPTool(
            name="navigate",
            description="导航到URL",
            input_schema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "目标URL"},
                    "wait_until": {"type": "string", "default": "load"}
                },
                "required": ["url"]
            },
            capability=ServerCapability.EXECUTE
        ))
        
        self._register_tool(MCPTool(
            name="screenshot",
            description="截图",
            input_schema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "保存路径"},
                    "full_page": {"type": "boolean", "default": False}
                },
                "required": []
            },
            capability=ServerCapability.READ
        ))
        
        self._register_tool(MCPTool(
            name="click",
            description="点击元素",
            input_schema={
                "type": "object",
                "properties": {
                    "selector": {"type": "string", "description": "CSS选择器"}
                },
                "required": ["selector"]
            },
            capability=ServerCapability.EXECUTE
        ))
        
        self._register_tool(MCPTool(
            name="fill",
            description="填写表单",
            input_schema={
                "type": "object",
                "properties": {
                    "selector": {"type": "string", "description": "CSS选择器"},
                    "value": {"type": "string", "description": "填写内容"}
                },
                "required": ["selector", "value"]
            },
            capability=ServerCapability.WRITE
        ))
        
        self._register_tool(MCPTool(
            name="get_text",
            description="获取元素文本",
            input_schema={
                "type": "object",
                "properties": {
                    "selector": {"type": "string", "description": "CSS选择器"}
                },
                "required": ["selector"]
            },
            capability=ServerCapability.READ
        ))
        
        self._register_tool(MCPTool(
            name="get_html",
            description="获取页面HTML",
            input_schema={
                "type": "object",
                "properties": {},
                "required": []
            },
            capability=ServerCapability.READ
        ))
        
        self._register_tool(MCPTool(
            name="evaluate",
            description="执行JavaScript",
            input_schema={
                "type": "object",
                "properties": {
                    "script": {"type": "string", "description": "JavaScript代码"}
                },
                "required": ["script"]
            },
            capability=ServerCapability.EXECUTE
        ))
        
        self._register_tool(MCPTool(
            name="wait_for_selector",
            description="等待元素出现",
            input_schema={
                "type": "object",
                "properties": {
                    "selector": {"type": "string", "description": "CSS选择器"},
                    "timeout": {"type": "integer", "default": 30000}
                },
                "required": ["selector"]
            },
            capability=ServerCapability.EXECUTE
        ))
        
        self._register_tool(MCPTool(
            name="close",
            description="关闭浏览器",
            input_schema={
                "type": "object",
                "properties": {},
                "required": []
            },
            capability=ServerCapability.EXECUTE
        ))
    
    def register_resources(self):
        """注册资源"""
        self._register_resource(MCPResource(
            uri="browser://page",
            name="current_page",
            description="当前页面内容"
        ))
    
    async def _get_page(self):
        """获取Playwright页面"""
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            raise ImportError("Please install playwright: pip install playwright")
        
        if self._browser is None:
            playwright = await async_playwright().start()
            self._browser = await playwright.chromium.launch(headless=self.headless)
            self._context = await self._browser.new_context()
        
        return await self._context.new_page()
    
    async def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """执行浏览器操作"""
        page = await self._get_page()
        
        if tool_name == "navigate":
            url = params.get("url", "")
            wait_until = params.get("wait_until", "load")
            await page.goto(url, wait_until=wait_until)
            return {"url": page.url, "title": await page.title()}
        
        elif tool_name == "screenshot":
            path = params.get("path", "screenshot.png")
            full_page = params.get("full_page", False)
            await page.screenshot(path=path, full_page=full_page)
            return {"saved_to": path}
        
        elif tool_name == "click":
            selector = params.get("selector", "")
            await page.click(selector)
            return {"clicked": selector}
        
        elif tool_name == "fill":
            selector = params.get("selector", "")
            value = params.get("value", "")
            await page.fill(selector, value)
            return {"filled": selector}
        
        elif tool_name == "get_text":
            selector = params.get("selector", "")
            text = await page.locator(selector).text_content()
            return {"text": text}
        
        elif tool_name == "get_html":
            html = await page.content()
            return {"html": html}
        
        elif tool_name == "evaluate":
            script = params.get("script", "")
            result = await page.evaluate(script)
            return {"result": result}
        
        elif tool_name == "wait_for_selector":
            selector = params.get("selector", "")
            timeout = params.get("timeout", 30000)
            await page.wait_for_selector(selector, timeout=timeout)
            return {"found": selector}
        
        elif tool_name == "close":
            if self._browser:
                await self._browser.close()
                self._browser = None
            return {"closed": True}
        
        raise ValueError(f"Unknown tool: {tool_name}")
    
    async def _read_resource_content(self, resource: MCPResource) -> Any:
        """读取资源内容"""
        if resource.uri == "browser://page":
            page = await self._get_page()
            return {"url": page.url, "title": await page.title()}
        raise ValueError(f"Unknown resource: {resource.uri}")
