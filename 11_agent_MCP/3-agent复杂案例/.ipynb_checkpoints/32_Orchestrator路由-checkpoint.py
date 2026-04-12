import os

# https://bailian.console.aliyun.com/?tab=model#/api-key
os.environ["OPENAI_API_KEY"] = "sk-78cc4e9ac8f44efdb207b7232e1ae6d8"
os.environ["OPENAI_BASE_URL"] = "https://dashscope.aliyuncs.com/compatible-mode/v1"

import asyncio
import uuid

from openai.types.responses import ResponseContentPartDoneEvent, ResponseTextDeltaEvent
from agents import Agent, RawResponsesStreamEvent, Runner, TResponseInputItem, trace
from agents import Agent, ItemHelpers, MessageOutputItem, Runner, trace
from agents.extensions.visualization import draw_graph
from agents import set_default_openai_api, set_tracing_disabled
set_default_openai_api("chat_completions")
set_tracing_disabled(True)


math_agent = Agent(
    name="math_agent",
    model="qwen-max",
    instructions="你是小王，擅长数学计算，回答问题的时候先告诉我你是谁。",
)

language_agent = Agent(
    name="language_agent",
    model="qwen-max",
    instructions="你是小李，擅长将翻译，回答问题的时候先告诉我你是谁。",
)

sport_agent = Agent(
    name="sport_agent",
    model="qwen-max",
    instructions="你是小张，擅长介绍各种体育运动，回答问题的时候先告诉我你是谁。",
)

orchestrator_agent = Agent(
    name="orchestrator_agent",
    model="qwen-max",
    instructions=(
        "You are math / language and sport agent. You use the tools given to you to response."
        "If asked for multiple task, you call the relevant tools in order."
        "You never translate on your own, you always use the provided tools."
    ),
    tools=[
        math_agent.as_tool(
            tool_name="slove_math",
            tool_description="解决数学题",
        ),
        language_agent.as_tool(
            tool_name="translate_language",
            tool_description="进行文本翻译",
        ),
        sport_agent.as_tool(
            tool_name="sport_introduction",
            tool_description="介绍运动行为",
        ),
    ],
)

async def main():
    # We'll create an ID for this conversation, so we can link each trace
    conversation_id = str(uuid.uuid4().hex[:16])

    try:
        draw_graph(orchestrator_agent, filename="Orchestrator路由")
    except:
        print("绘制agent失败，默认跳过。。。")

    msg = input("你好，我可以帮你回答数学、翻译和体育运动介绍，你还有什么问题？")
    
    with trace("Orchestrator"):
        orchestrator_result = await Runner.run(orchestrator_agent, msg)

        for item in orchestrator_result.new_items:
            try:
                print(item.output)
            except:
                pass

if __name__ == "__main__":
    asyncio.run(main())