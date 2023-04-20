"""Set up the AI and its goals"""
from colorama import Fore, Style

from autogpt import utils
from autogpt.config.ai_config import AIConfig
from autogpt.logs import logger


def prompt_user() -> AIConfig:
    """Prompt the user for input

    Returns:
        AIConfig: The AIConfig object containing the user's input
    """
    ai_name = ""
    # Construct the prompt
    logger.typewriter_log(
        "欢迎使用Auto-GPT！",
        Fore.GREEN,
        "run with '--help' for more information.",
        speak_text=True,
    )

    logger.typewriter_log(
        "Create an AI-Assistant:",
        Fore.GREEN,
        "Enter the name of your AI and its role below. Entering nothing will load"
        " defaults.",
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
    logger.typewriter_log(
        "描述您的AI的角色: ",
        Fore.GREEN,
        "默认，'一种旨在自主开发和经营企业，唯一目标是增加您的净资产的人工智能。'",
    )
    ai_role = utils.clean_input(f"{ai_name} is: ")
    if ai_role == "":
        ai_role = "一种旨在自主开发和经营企业，唯一目标是增加您的净资产的人工智能。"

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
    print("不输入加载默认设置，不要输入任何内容代表目标设置完成。", flush=True)
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

    return AIConfig(ai_name, ai_role, ai_goals)
