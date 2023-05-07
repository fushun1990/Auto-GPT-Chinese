import argparse
import logging

from autogpt.commands.file_operations import ingest_file, list_files
from autogpt.config import Config
from autogpt.memory import get_memory

cfg = Config()


def configure_logging():
    logging.basicConfig(
        format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
        level=logging.DEBUG,
        handlers=[
            logging.FileHandler(filename="log-ingestion.txt", mode="a"),
            logging.StreamHandler(),
        ],
    )
    return logging.getLogger("AutoGPT-读取")


def ingest_directory(directory, memory, args):
    """
    Ingest all files in a directory by calling the ingest_file function for each file.

    :param directory: The directory containing the files to ingest
    :param memory: An object with an add() method to store the chunks in memory
    """
    global logger
    try:
        files = list_files(directory)
        for file in files:
            ingest_file(file, memory, args.max_length, args.overlap)
    except Exception as e:
        logger.error(f"读取目录时出错 '{directory}': {str(e)}")


def main() -> None:
    logger = configure_logging()

    parser = argparse.ArgumentParser(
        description="将一个文件或一个包含多个文件的目录摄入到内存中。在运行此脚本之前，请确保设置了您的 .env 文件。"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--file", type=str, help="要读取的文件。")
    group.add_argument(
        "--dir", type=str, help="包含要读取的文件的目录。"
    )
    parser.add_argument(
        "--init",
        action="store_true",
        help="初始化内存并清除其内容（默认值：False）",
        default=False,
    )
    parser.add_argument(
        "--overlap",
        type=int,
        help="读取文件时块之间的重叠大小（默认值：200）",
        default=200,
    )
    parser.add_argument(
        "--max_length",
        type=int,
        help="读取文件时每个块的最大长度（默认值：4000）",
        default=4000,
    )
    args = parser.parse_args()

    # Initialize memory
    memory = get_memory(cfg, init=args.init)
    logger.debug("使用类型的内存: " + memory.__class__.__name__)

    if args.file:
        try:
            ingest_file(args.file, memory, args.max_length, args.overlap)
            logger.info(f"'{args.file}' 文件成功读取。")
        except Exception as e:
            logger.error(f"读取文件时出错 '{args.file}': {str(e)}")
    elif args.dir:
        try:
            ingest_directory(args.dir, memory, args)
            logger.info(f"'{args.dir}' 目录成功读取。")
        except Exception as e:
            logger.error(f"读取目录时出错 '{args.dir}': {str(e)}")
    else:
        logger.warn(
            "请提供一个文件路径（--file）或一个目录名称（--dir）作为输入，位于 auto_gpt_workspace 目录中。"
        )


if __name__ == "__main__":
    main()
