#!/usr/bin/env python3
"""LMS Telegram Bot entry point.

Supports two modes:
1. Test mode (--test): Runs handlers directly without Telegram connection
2. Telegram mode: Runs the bot with aiogram for Telegram integration
"""

import argparse
import logging
import sys
import io
from typing import Any

# Fix Windows console encoding for Unicode output
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandObject

from config import get_settings
from handlers import handle_start, handle_help, handle_health, handle_labs, handle_scores

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def parse_command(text: str) -> tuple[str, list[str]]:
    """Parse command text into command name and arguments.

    Args:
        text: User input text (e.g., "/scores lab-04" or "/start")

    Returns:
        Tuple of (command_name, arguments_list)
    """
    text = text.strip()
    if text.startswith("/"):
        parts = text[1:].split(maxsplit=1)
        command = parts[0]
        args = parts[1].split() if len(parts) > 1 else []
        return command, args
    # Natural language query - treat as unknown command
    return "", [text]


def handle_command(command: str, args: list[str]) -> str:
    """Route command to appropriate handler.

    Args:
        command: Command name without leading slash
        args: List of command arguments

    Returns:
        Handler response text
    """
    match command:
        case "start":
            return handle_start()
        case "help":
            return handle_help()
        case "health":
            return handle_health()
        case "labs":
            return handle_labs()
        case "scores":
            lab_id = args[0] if args else None
            return handle_scores(lab_id)
        case _:
            # Unknown command or natural language query
            # For now, return help message
            # Task 3: Add LLM-based intent routing here
            return (
                f"❓ Неизвестная команда: /{command}\n\n"
                "Попробуйте /help для списка доступных команд."
            )


def run_test_mode(query: str) -> None:
    """Run bot in test mode - execute handler directly.

    Args:
        query: Command string (e.g., "/start" or "/scores lab-04")
    """
    command, args = parse_command(query)
    response = handle_command(command, args)
    print(response)
    sys.exit(0)


async def run_telegram_mode() -> None:
    """Run bot in Telegram mode with aiogram."""
    settings = get_settings()

    if not settings.bot_token:
        logger.error("BOT_TOKEN not found in environment. Cannot start Telegram bot.")
        sys.exit(1)

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()

    # Register command handlers
    @dp.message(Command("start"))
    async def cmd_start(message: types.Message, command: CommandObject) -> None:
        response = handle_start()
        await message.answer(response)

    @dp.message(Command("help"))
    async def cmd_help(message: types.Message, command: CommandObject) -> None:
        response = handle_help()
        await message.answer(response)

    @dp.message(Command("health"))
    async def cmd_health(message: types.Message, command: CommandObject) -> None:
        response = handle_health()
        await message.answer(response)

    @dp.message(Command("labs"))
    async def cmd_labs(message: types.Message, command: CommandObject) -> None:
        response = handle_labs()
        await message.answer(response)

    @dp.message(Command("scores"))
    async def cmd_scores(message: types.Message, command: CommandObject) -> None:
        lab_id = command.args.split()[0] if command.args else None
        response = handle_scores(lab_id)
        await message.answer(response)

    # Start polling
    logger.info("Starting Telegram bot...")
    await dp.start_polling(bot)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="LMS Telegram Bot")
    parser.add_argument(
        "--test",
        type=str,
        metavar="QUERY",
        help="Run in test mode with the specified command query",
    )

    args = parser.parse_args()

    if args.test:
        run_test_mode(args.test)
    else:
        import asyncio
        asyncio.run(run_telegram_mode())


if __name__ == "__main__":
    main()
