from colorama import Fore

from autogpt.config.ai_config import AIConfig
from autogpt.config.config import Config
from autogpt.llm import ApiManager
from autogpt.logs import logger
from autogpt.prompts.generator import PromptGenerator
from autogpt.setup import prompt_user
from autogpt.utils import clean_input

CFG = Config()

DEFAULT_TRIGGERING_PROMPT = (
    "确定使用哪个下一个命令，并使用上述指定的格式进行响应："
)


def build_default_prompt_generator() -> PromptGenerator:
    """
    This function generates a prompt string that includes various constraints,
        commands, resources, and performance evaluations.

    Returns:
        str: The generated prompt string.
    """

    # Initialize the PromptGenerator object
    prompt_generator = PromptGenerator()

    # Add constraints to the PromptGenerator object
    prompt_generator.add_constraint(
        "短期记忆限制为约4000个单词。由于您的短期记忆是短暂的，因此请立即将重要信息保存到文件中。"
    )
    prompt_generator.add_constraint(
        "如果您不确定之前如何完成某件事，或想要回忆过去的事件，思考类似的事件会帮助您记忆。"
    )
    prompt_generator.add_constraint("无用户协助")
    prompt_generator.add_constraint(
        '只使用下面列出的命令，例如：task_complete'
    )

    # Define the command list
    commands = [
        ("task_complete", "任务完成（关闭）", {"reason": "<reason>"}),
    ]

    # Add commands to the PromptGenerator object
    for command_label, command_name, args in commands:
        prompt_generator.add_command(command_label, command_name, args)

    # Add resources to the PromptGenerator object
    prompt_generator.add_resource(
        "可用于搜索和信息收集的互联网访问。"
    )
    prompt_generator.add_resource("长期记忆管理。")
    prompt_generator.add_resource(
        "使用GPT-3.5的代理来委派简单任务。"
    )
    prompt_generator.add_resource("文件输出。")

    # Add performance evaluations to the PromptGenerator object
    prompt_generator.add_performance_evaluation(
        "持续审查和分析您的行动，确保您发挥出最佳的能力。"
    )
    prompt_generator.add_performance_evaluation(
        "不断地进行建设性自我批评，关注您的总体行为。"
    )
    prompt_generator.add_performance_evaluation(
        "回顾过去的决策和策略，以优化您的方法。"
    )
    prompt_generator.add_performance_evaluation(
        "每个指令都有一个成本，因此要聪明高效。目标是用最少的步骤完成任务。"
    )
    prompt_generator.add_performance_evaluation("将所有代码写入文件中。")
    return prompt_generator


def construct_main_ai_config() -> AIConfig:
    """Construct the prompt for the AI to respond to

    Returns:
        str: The prompt string
    """
    config = AIConfig.load(CFG.ai_settings_file)
    if CFG.skip_reprompt and config.ai_name:
        logger.typewriter_log("名字 :", Fore.GREEN, config.ai_name)
        logger.typewriter_log("角色 :", Fore.GREEN, config.ai_role)
        logger.typewriter_log("目标:", Fore.GREEN, f"{config.ai_goals}")
        logger.typewriter_log(
            "API预算:",
            Fore.GREEN,
            "无限制的" if config.api_budget <= 0 else f"${config.api_budget}",
        )
    elif config.ai_name:
        logger.typewriter_log(
            "欢迎回来！",
            Fore.GREEN,
            f"你希望我继续成为 {config.ai_name}?",
            speak_text=True,
        )
        should_continue = clean_input(
            f"""继续使用上次的设置?
名字:  {config.ai_name}
角色:  {config.ai_role}
目标: {config.ai_goals}
API 预算: {"无限" if config.api_budget <= 0 else f"${config.api_budget}"}
继续 ({CFG.authorise_key}/{CFG.exit_key}): """
        )
        if should_continue.lower() == CFG.exit_key:
            config = AIConfig()

    if not config.ai_name:
        config = prompt_user()
        config.save(CFG.ai_settings_file)

    # set the total api budget
    api_manager = ApiManager()
    api_manager.set_total_budget(config.api_budget)

    # Agent Created, print message
    logger.typewriter_log(
        config.ai_name,
        Fore.LIGHTBLUE_EX,
        "已创建，具有以下细节:",
        speak_text=True,
    )

    # Print the ai config details
    # Name
    logger.typewriter_log("名字:", Fore.GREEN, config.ai_name, speak_text=False)
    # Role
    logger.typewriter_log("角色:", Fore.GREEN, config.ai_role, speak_text=False)
    # Goals
    logger.typewriter_log("目标:", Fore.GREEN, "", speak_text=False)
    for goal in config.ai_goals:
        logger.typewriter_log("-", Fore.GREEN, goal, speak_text=False)

    logger.typewriter_log("\n\n", speak_text=False)
    return config
