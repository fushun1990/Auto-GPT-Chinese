"""Set up the AI and its goals"""
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
        "Create an AI-Assistant:",
        Fore.GREEN,
        "input '--manual' to enter manual mode.",
        speak_text=True,
    )

    user_desire = utils.clean_input(
        f"{Fore.LIGHTBLUE_EX}I want Auto-GPT to{Style.RESET_ALL}: "
    )

    if user_desire == "":
        user_desire = "Write a wikipedia style article about the project: https://github.com/significant-gravitas/Auto-GPT"  # Default prompt

    # If user desire contains "--manual"
    if "--manual" in user_desire:
        logger.typewriter_log(
            "Manual Mode Selected",
            Fore.GREEN,
            speak_text=True,
        )
        return generate_aiconfig_manual()

    else:
        try:
            return generate_aiconfig_automatic(user_desire)
        except Exception as e:
            logger.typewriter_log(
                "Unable to automatically generate AI Config based on user desire.",
                Fore.RED,
                "Falling back to manual mode.",
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
        "你的AI名字: ", Fore.GREEN, "默认，'企业家-GPT'"
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
Your task is to devise up to 5 highly effective goals and an appropriate role-based name (_GPT) for an autonomous agent, ensuring that the goals are optimally aligned with the successful completion of its assigned task.

The user will provide the task, you will provide only the output in the exact format specified below with no explanation or conversation.

Example input:
Help me with marketing my business

Example output:
Name: CMOGPT
Description: a professional digital marketer AI that assists Solopreneurs in growing their businesses by providing world-class expertise in solving marketing problems for SaaS, content products, agencies, and more.
Goals:
- Engage in effective problem-solving, prioritization, planning, and supporting execution to address your marketing needs as your virtual Chief Marketing Officer.

- Provide specific, actionable, and concise advice to help you make informed decisions without the use of platitudes or overly wordy explanations.

- Identify and prioritize quick wins and cost-effective campaigns that maximize results with minimal time and budget investment.

- Proactively take the lead in guiding you and offering suggestions when faced with unclear information or uncertainty to ensure your marketing strategy remains on track.
"""

    # Call LLM with the string as user input
    messages = [
        {
            "role": "system",
            "content": system_prompt,
        },
        {
            "role": "user",
            "content": f"Task: '{user_prompt}'\nRespond only with the output in the exact format specified in the system prompt, with no explanation or conversation.\n",
        },
    ]
    output = create_chat_completion(messages, CFG.fast_llm_model)

    # Debug LLM Output
    logger.debug(f"AI Config Generator Raw Output: {output}")

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
