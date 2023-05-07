"""Set up the AI and its goals"""
import json
import re

from colorama import Fore, Style

from autogpt import utils
from autogpt.config import Config
from autogpt.config.ai_config import AIConfig
from autogpt.llm import create_chat_completion
from autogpt.logs import logger

CFG = Config()


def prompt_user() -> AIConfig:
    """Prompt the user for input

    Returns:
        AIConfig: The AIConfig object tailored to the user's input
    """
    ai_name = ""
    ai_config = None

    # Construct the prompt
    logger.typewriter_log(
        "欢迎使用Auto-GPT！",
        Fore.GREEN,
        "使用“python3.10 -m autogpt --help”获取更多信息。",
        speak_text=True,
    )

    # Get user desire
    logger.typewriter_log(
        "创建一个 AI 助手:",
        Fore.GREEN,
        "输入 '--manual' 以进入手动模式。",
        speak_text=True,
    )
    logger.typewriter_log(
        "【不输入】回车。则使用【默认】",
        Fore.RED,
    )

    logger.typewriter_log(
        "我想让 Auto-GPT（默认）:",
        Fore.LIGHTBLUE_EX,
        "编写一篇关于项目【https://github.com/significant-gravitas/Auto-GPT】维基百科风格的文章",
        speak_text=True,
    )

    user_desire = utils.clean_input(
        f"{Fore.LIGHTBLUE_EX}我想让 Auto-GPT{Style.RESET_ALL}: "
    )

    if user_desire == "":
        user_desire = "编写一篇关于项目【https://github.com/significant-gravitas/Auto-GPT】维基百科风格的文章"  # Default prompt

    # If user desire contains "--manual"
    if "--manual" in user_desire:
        logger.typewriter_log(
            "手动模式已选定。",
            Fore.GREEN,
            speak_text=True,
        )
        return generate_aiconfig_manual()

    else:
        try:
            return generate_aiconfig_automatic(user_desire)
        except Exception as e:
            logger.typewriter_log(
                "无法根据用户的愿望自动生成AI配置。",
                Fore.RED,
                "回退到手动模式。",
                speak_text=True,
            )

            return generate_aiconfig_manual()


def generate_aiconfig_manual() -> AIConfig:
    """
    Interactively create an AI configuration by prompting the user to provide the name, role, and goals of the AI.

    This function guides the user through a series of prompts to collect the necessary information to create
    an AIConfig object. The user will be asked to provide a name and role for the AI, as well as up to five
    goals. If the user does not provide a value for any of the fields, default values will be used.

    Returns:
        AIConfig: An AIConfig object containing the user-defined or default AI name, role, and goals.
    """

    # Manual Setup Intro
    logger.typewriter_log(
        "创建一个人工智能助手:",
        Fore.GREEN,
        "在下面输入您的人工智能的名称和角色。不输入任何内容将加载默认设置。",
        speak_text=True,
    )

    # Get AI Name from User
    logger.typewriter_log(
        "你的AI名字: ", Fore.GREEN, "默认：【企业家-GPT】"
    )
    ai_name = utils.clean_input("AI名字: ")
    if ai_name == "":
        ai_name = "企业家-GPT"

    logger.typewriter_log(
        f"我是【{ai_name}】!", Fore.LIGHTBLUE_EX, "我随时为您效劳。", speak_text=True
    )

    # Get AI Role from User
    ai_role = ""
    # logger.typewriter_log(
    #     "描述您的AI的角色: ",
    #     Fore.GREEN,
    #     "默认，'一种旨在自主开发和经营企业，唯一目标是增加您的净资产的人工智能。'",
    # )
    # ai_role = utils.clean_input(f"{ai_name} is: ")
    # if ai_role == "":
    #     ai_role = "一种旨在自主开发和经营企业，唯一目标是增加您的净资产的人工智能。"

    # Enter up to 5 goals for the AI
    logger.typewriter_log(
        "输入您希望我完成的工作，最多5个工作目标: ",
        Fore.GREEN,
        "默认：",
    )
    logger.typewriter_log(
        "1、增加净值",
    )
    logger.typewriter_log(
        "2、增长 Twitter 账户",
    )
    logger.typewriter_log(
        "3、自主开发和管理多个业务",
    )
    logger.info("不输入加载默认设置，不要输入任何内容代表目标设置完成。")
    ai_goals = []
    for i in range(5):
        ai_goal = utils.clean_input(f"{Fore.LIGHTBLUE_EX}Goal{Style.RESET_ALL} {i+1}: ")
        if ai_goal == "":
            break
        ai_goals.append(ai_goal)
    if not ai_goals:
        ai_goals = [
            "增加净值",
            "增长 Twitter 账户",
            "自主开发和管理多个业务",
        ]

    # Get API Budget from User
    logger.typewriter_log(
        "Enter your budget for API calls: ",
        Fore.GREEN,
        "For example: $1.50",
    )
    logger.info("Enter nothing to let the AI run without monetary limit")
    api_budget_input = utils.clean_input(
        f"{Fore.LIGHTBLUE_EX}Budget{Style.RESET_ALL}: $"
    )
    if api_budget_input == "":
        api_budget = 0.0
    else:
        try:
            api_budget = float(api_budget_input.replace("$", ""))
        except ValueError:
            logger.typewriter_log(
                "Invalid budget input. Setting budget to unlimited.", Fore.RED
            )
            api_budget = 0.0

    return AIConfig(ai_name, ai_role, ai_goals, api_budget)


def generate_aiconfig_automatic(user_prompt) -> AIConfig:
    """Generates an AIConfig object from the given string.

    Returns:
    AIConfig: The AIConfig object tailored to the user's input
    """

    system_prompt = """
您的任务是制定最多5个高效的目标和一个适当的基于角色的名称（_GPT）用于自主代理，确保这些目标与成功完成其分配任务的最佳对齐。

用户提供任务，您将仅按照下面指定的确切格式提供输出，不得进行任何解释或交谈。

输入示例:
帮助我推广我的业务

输出示例:
Name: CMOGPT
Description: 一款专业的数字营销AI，为自由职业者提供世界一流的专业知识，解决SaaS、内容产品、代理商等各种营销问题，帮助他们发展业务。
Goals:
- 作为您的虚拟首席营销官，参与有效的问题解决、优先级确定、规划和支持执行，以解决您的营销需求。

- 提供具体、可行和简洁的建议，帮助您做出明智的决策，而不使用陈词滥调或过于冗长的解释。

- 确定并优先考虑快速获胜和成本效益高的营销活动，最大化结果，同时最小化时间和预算投入。

- 主动引领您并在面对不明确的信息或不确定性时提供建议，确保您的营销策略保持在正确的轨道上。
"""

    # Call LLM with the string as user input
    messages = [
        {
            "role": "system",
            "content": system_prompt,
        },
        {
            "role": "user",
            "content": f"任务: '{user_prompt}'\n只用系统提示中指定的精确格式回复输出，不要进行解释或对话。\n",
        },
    ]
    logger.debug(f"发送给chatGPT的内容:{json.dumps(messages, ensure_ascii=False)}")
    output = create_chat_completion(messages, CFG.fast_llm_model)

    # Debug LLM Output
    logger.debug(f"\nAI配置生成器原始输出:\n {output}\n\n")

    # Parse the output
    ai_name = re.search(r"Name(?:\s*):(?:\s*)(.*)", output, re.IGNORECASE).group(1)
    ai_role = (
        re.search(
            r"Description(?:\s*):(?:\s*)(.*?)(?:(?:\n)|Goals)",
            output,
            re.IGNORECASE | re.DOTALL,
        )
        .group(1)
        .strip()
    )
    ai_goals = re.findall(r"(?<=\n)-\s*(.*)", output)
    api_budget = 0.0  # TODO: parse api budget using a regular expression

    return AIConfig(ai_name, ai_role, ai_goals, api_budget)
