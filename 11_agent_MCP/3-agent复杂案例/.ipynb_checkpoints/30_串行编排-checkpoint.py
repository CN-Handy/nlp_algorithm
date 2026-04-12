import os

# https://bailian.console.aliyun.com/?tab=model#/api-key
os.environ["OPENAI_API_KEY"] = "sk-78cc4e9ac8f44efdb207b7232e1ae6d8"
os.environ["OPENAI_BASE_URL"] = "https://dashscope.aliyuncs.com/compatible-mode/v1"

import asyncio
from pydantic import BaseModel
from agents import Agent, Runner, trace
from agents import set_default_openai_api, set_tracing_disabled
set_default_openai_api("chat_completions")
set_tracing_disabled(True)


story_outline_agent = Agent(
    name="story_outline_agent",
    model="qwen-max",
    instructions="为故事给定的主体生成大纲。",
)

class OutlineCheckerOutput(BaseModel):
    good_quality: bool


outline_checker_agent = Agent(
    name="outline_checker_agent",
    model="qwen-max",
    instructions="结合故事大纲，为判断大纲大是否有好的质量，输出 good_quality ，并为bool格式，最终输出为json",
    output_type=OutlineCheckerOutput,
)

story_agent = Agent(
    name="story_agent",
    model="qwen-max",
    instructions="基于大纲，编写故事详细的内容，",
    output_type=str,
)


async def main():
    input_prompt = input("你想要听什么故事? ")
    
    with trace("Deterministic story flow"):
        # 1. Generate an outline
        outline_result = await Runner.run(
            story_outline_agent,
            input_prompt,
        )
        print("生成大纲....", outline_result)

        # 2. Check the outline
        outline_checker_result = await Runner.run(
            outline_checker_agent,
            outline_result.final_output,
        )
        print("校验结果....", outline_checker_result)

        
        # 3. Add a gate to stop if the outline is not good quality or not a scifi story
        assert isinstance(outline_checker_result.final_output, OutlineCheckerOutput)
        if not outline_checker_result.final_output.good_quality:
            print("故事不吸引人，所以停止输出...")
            exit(0)


        # 4. Write the story
        story_result = await Runner.run(
            story_agent,
            outline_result.final_output,
        )
        print(f"故事: {story_result.final_output}")


if __name__ == "__main__":
    asyncio.run(main())