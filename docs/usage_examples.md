# 使用示例和最佳实践

## 快速入门示例

### 1. 基础通勤检查工作流

```python
from app.mcp.workflow_dsl import WorkflowBuilder
from app.mcp.workflow_engine import get_dsl_executor

# 创建简单的工作流
builder = WorkflowBuilder("Simple Commute Check")

workflow = (builder
    .add_start_node("Start", "开始通勤检查")
    .add_mcp_tool_node(
        name="Get Route Info",
        server="amap-mcp-server",
        tool="calculate_route",
        inputs={
            "origin": "${variables.home}",
            "destination": "${variables.work}"
        },
        outputs=["route_data"]
    )
    .add_mcp_tool_node(
        name="Send Notification",
        server="dingtalk-mcp-server",
        tool="send_text_message",
        inputs={
            "content": "今日通勤时长: ${Get Route Info.route_data.duration}分钟"
        }
    )
    .add_end_node("Finish", "检查完成"))

# 设置变量
workflow.set_variable("home", "116.481485,39.990464")
workflow.set_variable("work", "116.481485,39.990464")

# 执行工作流
async def run_example():
    executor = await get_dsl_executor()
    result = await executor.execute_workflow(workflow.build())
    print(f"执行结果: {result.status}")

# 运行示例
import asyncio
asyncio.run(run_example())
```

### 2. YAML工作流定义

```yaml
# commute_check.yaml
name: "Daily Commute Assistant"
variables:
  home: "116.481485,39.990464"
  work: "116.481485,39.990464"

nodes:
  - id: "start"
    type: "start"
    name: "开始检查"
    next_nodes: ["get_route"]

  - id: "get_route"
    type: "mcp_tool"
    name: "获取路线"
    config:
      server: "amap-mcp-server"
      tool: "calculate_route"
    inputs:
      origin: "${variables.home}"
      destination: "${variables.work}"
    outputs: ["route_info"]
    next_nodes: ["send_notification"]

  - id: "send_notification"
    type: "mcp_tool"
    name: "发送通知"
    config:
      server: "dingtalk-mcp-server"
      tool: "send_commute_notification"
    inputs:
      departure_time: "${variables.now}"
      duration_minutes: "${get_route.route_info.duration}"
      distance_km: "${get_route.route_info.distance}"
    next_nodes: ["end"]

  - id: "end"
    type: "end"
    name: "完成"
```

执行YAML工作流：
```python
from app.mcp.workflow_dsl import WorkflowDSLParser
from app.mcp.workflow_engine import get_dsl_executor

# 读取YAML文件
with open('commute_check.yaml', 'r', encoding='utf-8') as f:
    yaml_content = f.read()

# 解析工作流
workflow = WorkflowDSLParser.parse_yaml(yaml_content)

# 执行工作流
executor = await get_dsl_executor()
result = await executor.execute_workflow(workflow, {
    "now": "2024-01-01T08:00:00"
})
```

## 高级使用示例

### 1. 条件分支工作流

```python
builder = WorkflowBuilder("Conditional Commute")

workflow = (builder
    .add_start_node("Start")
    .add_mcp_tool_node("Get Route", "amap-mcp-server", "calculate_route")
    .add_condition_node(
        "Check Duration",
        condition={
            "left": "${Get Route.route_info.duration}",
            "operator": ">",
            "right": 3600  # 1小时
        }
    )
    .add_mcp_tool_node(
        "Send Alert",
        "dingtalk-mcp-server",
        "send_text_message",
        inputs={"content": "⚠️ 通勤时间较长，请提前出发"}
    )
    .add_end_node("Alert Sent"))
```

### 2. 并行执行工作流

```python
# 同时获取路线和天气信息
builder = WorkflowBuilder("Parallel Check")

workflow = (builder
    .add_start_node("Start")
    # 并行分支1：路线信息
    .add_mcp_tool_node("Get Route", "amap-mcp-server", "calculate_route")
    # 并行分支2：天气信息
    .add_mcp_tool_node("Get Weather", "weather-mcp-server", "get_current_weather")
    # 汇聚点
    .add_transform_node(
        "Combine Info",
        script="""
        combined = {
            "commute_time": route_info.duration,
            "weather": weather_info.weather_condition,
            "temperature": weather_info.temperature
        }
        """,
        inputs={
            "route_info": "${Get Route.route_info}",
            "weather_info": "${Get Weather.current_weather}"
        }
    )
    .add_mcp_tool_node(
        "Send Combined",
        "dingtalk-mcp-server",
        "send_markdown_message",
        inputs={
            "title": "今日出行建议",
            "text": """
            ## 出行建议
            - 通勤时长: ${Combine Info.combined.commute_time}分钟
            - 天气状况: ${Combine Info.combined.weather}
            - 当前温度: ${Combine Info.combined.temperature}°C
            """
        }
    )
    .add_end_node("Complete"))
```

### 3. 循环处理工作流

```python
# 批量检查多个路线
builder = WorkflowBuilder("Batch Route Check")

workflow = (builder
    .add_start_node("Start")
    .add_transform_node(
        "Prepare Routes",
        script="""
        routes = [
            {"from": "home", "to": "work"},
            {"from": "home", "to": "gym"},
            {"from": "home", "to": "school"}
        ]
        """,
        outputs=["route_list"]
    )
    .add_mcp_tool_node(
        "Process Routes",
        "amap-mcp-server",
        "batch_calculate_routes",
        inputs={"routes": "${Prepare Routes.route_list}"},
        outputs=["batch_results"]
    )
    .add_transform_node(
        "Analyze Results",
        script="""
        best_route = min(batch_results.results, key=lambda x: x.duration)
        worst_route = max(batch_results.results, key=lambda x: x.duration)
        """,
        inputs={"batch_results": "${Process Routes.batch_results}"},
        outputs=["analysis"]
    )
    .add_mcp_tool_node(
        "Send Analysis",
        "dingtalk-mcp-server",
        "send_markdown_message",
        inputs={
            "title": "路线分析报告",
            "text": """
            ## 路线分析结果
            🏆 最佳路线: ${Analyze Results.analysis.best_route}
            😰 最差路线: ${Analyze Results.analysis.worst_route}
            """
        }
    )
    .add_end_node("Analysis Complete"))
```

## 实际应用场景

### 1. 智能闹钟系统

```yaml
name: "Smart Alarm System"
description: "根据通勤和天气情况智能调整闹钟时间"

variables:
  wake_up_base_time: "07:00"
  work_start_time: "09:00"
  location_home: "116.481485,39.990464"
  location_work: "116.481485,39.990464"

nodes:
  - id: "trigger"
    type: "start"
    name: "闹钟触发"
    next_nodes: ["check_schedule", "get_weather"]

  - id: "check_schedule"
    type: "mcp_tool"
    name: "检查日程"
    config:
      server: "calendar-mcp-server"
      tool: "get_events"
    inputs:
      start_date: "${today}"
      end_date: "${today}"
    outputs: ["todays_events"]

  - id: "get_weather"
    type: "mcp_tool"
    name: "获取天气"
    config:
      server: "weather-mcp-server"
      tool: "get_current_weather"
    inputs:
      city: "北京"
    outputs: ["weather_data"]

  - id: "calculate_commute"
    type: "mcp_tool"
    name: "计算通勤"
    config:
      server: "amap-mcp-server"
      tool: "calculate_route"
    inputs:
      origin: "${variables.location_home}"
      destination: "${variables.location_work}"
    outputs: ["commute_info"]

  - id: "analyze_factors"
    type: "transform"
    name: "综合分析"
    config:
      script: |
        # 分析各因素对起床时间的影响
        adjustment = 0
        
        # 日程因素
        if todays_events.total_count > 3:
            adjustment += 15  # 会议多，早点起
        
        # 天气因素
        if "雨" in weather_data.weather_condition:
            adjustment += 10  # 雨天路滑，预留时间
        
        # 通勤因素
        commute_minutes = commute_info.duration / 60
        if commute_minutes > 45:
            adjustment += 20  # 路程远，早点出门
        
        final_wake_time = parse_time(variables.wake_up_base_time) - timedelta(minutes=adjustment)
    inputs:
      todays_events: "${check_schedule.todays_events}"
      weather_data: "${get_weather.weather_data}"
      commute_info: "${calculate_commute.commute_info}"
    outputs: ["wake_time_adjustment"]

  - id: "set_alarm"
    type: "mcp_tool"
    name: "设置闹钟"
    config:
      server: "calendar-mcp-server"
      tool: "add_event"
    inputs:
      title: "智能闹钟"
      start_time: "${analyze_factors.wake_time_adjustment.final_wake_time}"
      end_time: "${analyze_factors.wake_time_adjustment.final_wake_time}"
      event_type: "reminder"
      description: "根据今日情况智能调整的起床时间"
    outputs: ["alarm_set"]

  - id: "notify_user"
    type: "mcp_tool"
    name: "通知用户"
    config:
      server: "dingtalk-mcp-server"
      tool: "send_text_message"
    inputs:
      content: |
        🎯 智能闹钟已设置
        起床时间: ${set_alarm.alarm_set.event.start_time}
        调整原因: ${analyze_factors.wake_time_adjustment.reasons}
    next_nodes: ["complete"]

  - id: "complete"
    type: "end"
    name: "设置完成"
```

### 2. 出差准备助手

```yaml
name: "Business Trip Assistant"
description: "出差前的智能准备助手"

variables:
  trip_destination: "上海"
  trip_dates: ["2024-02-01", "2024-02-03"]
  home_location: "116.481485,39.990464"

nodes:
  - id: "start_planning"
    type: "start"
    name: "开始出差规划"
    next_nodes: ["check_weather", "check_calendar"]

  - id: "check_weather"
    type: "mcp_tool"
    name: "查询目的地天气"
    config:
      server: "weather-mcp-server"
      tool: "get_weather_forecast"
    inputs:
      city: "${variables.trip_destination}"
      days: 3
    outputs: ["destination_weather"]

  - id: "check_calendar"
    type: "mcp_tool"
    name: "检查工作安排"
    config:
      server: "calendar-mcp-server"
      tool: "get_events"
    inputs:
      start_date: "${variables.trip_dates[0]}"
      end_date: "${variables.trip_dates[1]}"
    outputs: ["work_schedule"]

  - id: "plan_transport"
    type: "mcp_tool"
    name: "规划交通路线"
    config:
      server: "amap-mcp-server"
      tool: "calculate_route"
    inputs:
      origin: "${variables.home_location}"
      destination: "${variables.trip_destination}"
    outputs: ["travel_route"]

  - id: "generate_checklist"
    type: "transform"
    name: "生成准备清单"
    config:
      script: |
        checklist = []
        
        # 根据天气添加物品
        weather = destination_weather.forecasts[0]
        if weather.precipitation_probability > 50:
            checklist.append("雨伞")
        if weather.low_temperature < 10:
            checklist.append("厚外套")
        
        # 根据工作安排添加物品
        if work_schedule.total_count > 0:
            checklist.append("笔记本电脑")
            checklist.append("充电器")
        
        # 根据路程时间添加提醒
        travel_time = travel_route.duration / 3600
        if travel_time > 3:
            checklist.append("颈枕")
            checklist.append("眼罩")
        
        result = {"items": checklist}
    inputs:
      destination_weather: "${check_weather.destination_weather}"
      work_schedule: "${check_calendar.work_schedule}"
      travel_route: "${plan_transport.travel_route}"
    outputs: ["packing_list"]

  - id: "send_preparation"
    type: "mcp_tool"
    name: "发送准备提醒"
    config:
      server: "dingtalk-mcp-server"
      tool: "send_markdown_message"
    inputs:
      title: "✈️ 出差准备提醒"
      text: |
        ## 出差准备清单
        📅 目的地: ${variables.trip_destination}
        📆 时间: ${variables.trip_dates[0]} 至 ${variables.trip_dates[1]}
        
        ### 🎒 必备物品
        ${"\n".join(["- " + item for item in generate_checklist.packing_list.items])}
        
        ### 🚗 交通信息
        - 预计行程时间: ${plan_transport.travel_route.duration}分钟
        - 建议提前2小时出发
        
        ### 📋 工作安排
        - 期间有${check_calendar.work_schedule.total_count}个工作事项需要注意
        
        祝您旅途愉快！
    next_nodes: ["complete_planning"]

  - id: "complete_planning"
    type: "end"
    name: "规划完成"
```

## 最佳实践

### 1. 错误处理

```python
# 在工作流中添加错误处理节点
workflow = (builder
    .add_start_node("Start")
    .add_mcp_tool_node("Critical Task", "server", "tool")
    .add_condition_node(
        "Check Success",
        condition={
            "left": "${Critical Task.status}",
            "operator": "==",
            "right": "success"
        }
    )
    .add_mcp_tool_node(
        "Success Path",
        "dingtalk-mcp-server",
        "send_text_message",
        inputs={"content": "✅ 任务执行成功"}
    )
    .add_mcp_tool_node(
        "Error Handler",
        "dingtalk-mcp-server",
        "send_error_notification",
        inputs={
            "error_title": "任务执行失败",
            "error_message": "${Critical Task.error}"
        }
    ))
```

### 2. 变量管理

```python
# 使用环境变量
import os
from dotenv import load_dotenv

load_dotenv()

workflow.set_variable("api_key", os.getenv("AMAP_API_KEY"))
workflow.set_variable("webhook_url", os.getenv("DINGTALK_WEBHOOK"))
```

### 3. 性能优化

```python
# 批量处理提高效率
workflow = (builder
    .add_transform_node(
        "Batch Prepare",
        script="""
        # 将多个小任务合并为批处理
        batch_requests = []
        for item in input_items:
            batch_requests.append({
                "origin": item.origin,
                "destination": item.destination
            })
        """,
        outputs=["batch_data"]
    )
    .add_mcp_tool_node(
        "Batch Process",
        "amap-mcp-server",
        "batch_calculate_routes",
        inputs={"routes": "${Batch Prepare.batch_data}"}
    ))
```

这些示例展示了MCP编排系统的强大功能和灵活性，可以根据具体需求组合不同的MCP服务器和服务来创建复杂的工作流。