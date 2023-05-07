"""Configurator module."""
import click
from colorama import Back, Fore, Style

from autogpt import utils
from autogpt.config import Config
from autogpt.logs import logger
from autogpt.memory import get_supported_memory_backends

CFG = Config()


def create_config(
    continuous: bool,
    continuous_limit: int,
    ai_settings_file: str,
    skip_reprompt: bool,
    speak: bool,
    debug: bool,
    gpt3only: bool,
    gpt4only: bool,
    memory_type: str,
    browser_name: str,
    allow_downloads: bool,
    skip_news: bool,
) -> None:
    """Updates the config object with the given arguments.

    Args:
        continuous (bool): Whether to run in continuous mode
        continuous_limit (int): The number of times to run in continuous mode
        ai_settings_file (str): The path to the ai_settings.yaml file
        skip_reprompt (bool): Whether to skip the re-prompting messages at the beginning of the script
        speak (bool): Whether to enable speak mode
        debug (bool): Whether to enable debug mode
        gpt3only (bool): Whether to enable GPT3.5 only mode
        gpt4only (bool): Whether to enable GPT4 only mode
        memory_type (str): The type of memory backend to use
        browser_name (str): The name of the browser to use when using selenium to scrape the web
        allow_downloads (bool): Whether to allow Auto-GPT to download files natively
        skips_news (bool): Whether to suppress the output of latest news on startup
    """
    CFG.set_debug_mode(False)
    CFG.set_continuous_mode(False)
    CFG.set_speak_mode(False)

    if debug:
        logger.typewriter_log("调试模式: ", Fore.GREEN, "ENABLED")
        CFG.set_debug_mode(True)

    if continuous:
        logger.typewriter_log("连续模式: ", Fore.RED, "ENABLED")
        logger.typewriter_log(
            "警告: ",
            Fore.RED,
            "不建议使用连续模式。它具有潜在的危险性，可能会导致您的AI永远运行或执行您通常不授权的操作。请自行承担风险",
        )
        CFG.set_continuous_mode(True)

        if continuous_limit:
            logger.typewriter_log(
                "连续模式限制: ", Fore.GREEN, f"{continuous_limit}"
            )
            CFG.set_continuous_limit(continuous_limit)

    # Check if continuous limit is used without continuous mode
    if continuous_limit and not continuous:
        raise click.UsageError("--continuous-limit 只能与【--continuous】一起使用 ")

    if speak:
        logger.typewriter_log("朗读模式: ", Fore.GREEN, "ENABLED")
        CFG.set_speak_mode(True)

    if gpt3only:
        logger.typewriter_log("仅限GPT3.5模式: ", Fore.GREEN, "ENABLED")
        CFG.set_smart_llm_model(CFG.fast_llm_model)

    if gpt4only:
        logger.typewriter_log("仅限GPT4模式: ", Fore.GREEN, "ENABLED")
        CFG.set_fast_llm_model(CFG.smart_llm_model)

    if memory_type:
        supported_memory = get_supported_memory_backends()
        chosen = memory_type
        if chosen not in supported_memory:
            logger.typewriter_log(
                "仅支持以下内存后端: ",
                Fore.RED,
                f"{supported_memory}",
            )
            logger.typewriter_log("默认为: ", Fore.YELLOW, CFG.memory_backend)
        else:
            CFG.memory_backend = chosen

    if skip_reprompt:
        logger.typewriter_log("跳过重新提示: ", Fore.GREEN, "ENABLED")
        CFG.skip_reprompt = True

    if ai_settings_file:
        file = ai_settings_file

        # Validate file
        (validated, message) = utils.validate_yaml_file(file)
        if not validated:
            logger.typewriter_log("文件验证失败", Fore.RED, message)
            logger.double_check()
            exit(1)

        logger.typewriter_log("使用 AI 配置文件:", Fore.GREEN, file)
        CFG.ai_settings_file = file
        CFG.skip_reprompt = True

    if browser_name:
        CFG.selenium_web_browser = browser_name

    if allow_downloads:
        logger.typewriter_log("本地下载:", Fore.GREEN, "ENABLED")
        logger.typewriter_log(
            "警告: ",
            Fore.YELLOW,
            f"{Back.LIGHTYELLOW_EX}Auto-GPT现在可以下载并保存文件到您的计算机。{Back.RESET} "
            + "建议您仔细监控其下载的任何文件。",
        )
        logger.typewriter_log(
            "警告: ",
            Fore.YELLOW,
            f"{Back.RED + Style.BRIGHT}请永远记住，不要打开你不确定的文件！{Style.RESET_ALL}",
        )
        CFG.allow_downloads = True

    if skip_news:
        CFG.skip_news = True
