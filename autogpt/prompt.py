from colorama import Fore

from autogpt.config import Config
from autogpt.config.ai_config import AIConfig
from autogpt.config.config import Config
from autogpt.logs import logger
from autogpt.promptgenerator import PromptGenerator
from autogpt.setup import prompt_user
from autogpt.utils import clean_input

CFG = Config()


def get_prompt() -> str:
    """
    This function generates a prompt string that includes various constraints,
        commands, resources, and performance evaluations.

    Returns:
        str: The generated prompt string.
    """

    # Initialize the Config object
    cfg = Config()

    # Initialize the PromptGenerator object
    prompt_generator = PromptGenerator()

    # Add constraints to the PromptGenerator object
    prompt_generator.add_constraint(
        "短期记忆的限制是4000个字符串。你的短期记忆很短暂，因此应该立即将重要信息保存到文件中。"
    )
    prompt_generator.add_constraint(
        "如果你不确定之前是如何做某件事或者想要回忆起过去的事件，想到类似的事件会有助于你记忆。"
    )
    prompt_generator.add_constraint("没有用户帮助")
    prompt_generator.add_constraint(
        '不要回复除json以外的任何字符串'
    )
    prompt_generator.add_constraint(
        '只使用双引号中列出的命令，例如："命令名称"'
    )
    prompt_generator.add_constraint(
        "Use subprocesses for commands that will not terminate within a few minutes"
    )

    # Define the command list
    commands = [
        ("谷歌搜索", "google", {"input": "<search>"}),
        (
            "浏览网站",
            "browse_website",
            {"url": "<url>", "question": "<what_you_want_to_find_on_website>"},
        ),
        (
            "启动 GPT 代理",
            "start_agent",
            {"name": "<name>", "task": "<short_task_desc>", "prompt": "<prompt>"},
        ),
        (
            "向 GPT 代理发送消息",
            "message_agent",
            {"key": "<key>", "message": "<message>"},
        ),
        ("列出 GPT 代理列表", "list_agents", {}),
        ("删除 GPT 代理", "delete_agent", {"key": "<key>"}),
        (
            "克隆代码库",
            "clone_repository",
            {"repository_url": "<url>", "clone_path": "<directory>"},
        ),
        ("写入文件", "write_to_file", {"file": "<file>", "text": "<text>"}),
        ("读取文件", "read_file", {"file": "<file>"}),
        ("追加到文件", "append_to_file", {"file": "<file>", "text": "<text>"}),
        ("删除文件", "delete_file", {"file": "<file>"}),
        ("搜索文件", "search_files", {"directory": "<directory>"}),
        ("分析代码", "analyze_code", {"code": "<full_code_string>"}),
        (
            "获取改进后的代码。",
            "improve_code",
            {"suggestions": "<list_of_suggestions>", "code": "<full_code_string>"},
        ),
        (
            "编写测试",
            "write_tests",
            {"code": "<full_code_string>", "focus": "<list_of_focus_areas>"},
        ),
        ("执行 Python 文件", "execute_python_file", {"file": "<file>"}),
        ("生成图像", "generate_image", {"prompt": "<prompt>"}),
        ("发送推文", "send_tweet", {"text": "<text>"}),
    ]

    # Only add the audio to text command if the model is specified
    if cfg.huggingface_audio_to_text_model:
        commands.append(
            ("将音频转换为文本", "read_audio_from_file", {"file": "<file>"}),
        )

    # Only add shell command to the prompt if the AI is allowed to execute it
    if cfg.execute_local_commands:
        commands.append(
            (
                "执行 Shell 命令，仅限非交互式命令。",
                "execute_shell",
                {"command_line": "<command_line>"},
            ),
        )
        commands.append(
            (
                "Execute Shell Command Popen, non-interactive commands only",
                "execute_shell_popen",
                {"command_line": "<command_line>"},
            ),
        )

    # Only add the download file command if the AI is allowed to execute it
    if cfg.allow_downloads:
        commands.append(
            (
                "Downloads a file from the internet, and stores it locally",
                "download_file",
                {"url": "<file_url>", "file": "<saved_filename>"},
            ),
        )

    # Add these command last.
    commands.append(
        ("什么都不做", "do_nothing", {}),
    )
    commands.append(
        ("任务完成（关闭）", "task_complete", {"reason": "<reason>"}),
    )

    # Add commands to the PromptGenerator object
    for command_label, command_name, args in commands:
        prompt_generator.add_command(command_label, command_name, args)

    # Add resources to the PromptGenerator object
    prompt_generator.add_resource(
        "用于搜索和信息收集的互联网访问。"
    )
    prompt_generator.add_resource("长期内存管理。")
    prompt_generator.add_resource(
        "由 GPT-3.5 驱动的代理，用于委派简单任务。"
    )
    prompt_generator.add_resource("文件输出。")

    # Add performance evaluations to the PromptGenerator object
    prompt_generator.add_performance_evaluation(
        "持续审查和分析你的行动，以确保你发挥出最佳水平。"
    )
    prompt_generator.add_performance_evaluation(
        "不断地对自己的宏观行为进行建设性自我批评。"
    )
    prompt_generator.add_performance_evaluation(
        "反思过去的决策和策略，以完善你的方法。"
    )
    prompt_generator.add_performance_evaluation(
        "每个命令都有代价，所以要聪明高效。旨在以最少的步骤完成任务。"
    )

    # Generate the prompt string
    return prompt_generator.generate_prompt_string()


def construct_prompt() -> str:
    """Construct the prompt for the AI to respond to

    Returns:
        str: The prompt string
    """
    config = AIConfig.load(CFG.ai_settings_file)
    if CFG.skip_reprompt and config.ai_name:
        logger.typewriter_log("名字 :", Fore.GREEN, config.ai_name)
        logger.typewriter_log("角色 :", Fore.GREEN, config.ai_role)
        logger.typewriter_log("目标:", Fore.GREEN, f"{config.ai_goals}")
    elif config.ai_name:
        logger.typewriter_log(
            "欢迎回来！",
            Fore.GREEN,
            f"您希望继续使用【 {config.ai_name}】?",
            speak_text=True,
        )
        should_continue = clean_input(
            f"""继续使用上次的设置吗?
名字:  {config.ai_name}
角色:  {config.ai_role}
目标: {config.ai_goals}
继续 (y/n): """
        )
        if should_continue.lower() == "n":
            config = AIConfig()

    if not config.ai_name:
        config = prompt_user()
        config.save(CFG.ai_settings_file)

    # Get rid of this global:
    global ai_name
    ai_name = config.ai_name

    return config.construct_full_prompt()
