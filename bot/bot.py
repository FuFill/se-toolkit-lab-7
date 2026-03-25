#!/usr/bin/env python3
"""LMS Telegram Bot entry point.

Supports two modes:
1. Test mode (--test): Runs handlers directly without Telegram connection
2. Telegram mode: Runs the bot with aiogram for Telegram integration

Task 3: Adds LLM-based intent routing for natural language queries.
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
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import get_settings
from handlers import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
    route_intent,
)
from services import LMSAPIClient, LLMClient

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
    # Natural language query - no command
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
        case "":
            # Natural language query - use LLM intent routing
            # This is handled separately in run_test_mode
            return ""
        case _:
            # Unknown command - use LLM to try to understand
            return f"❓ Неизвестная команда: /{command}\n\nПопробуйте /help для списка доступных команд."


def run_test_mode(query: str) -> None:
    """Run bot in test mode - execute handler or LLM routing.

    Args:
        query: Command string or natural language query
    """
    settings = get_settings()

    # Check if it's a slash command
    command, args = parse_command(query)
    if command:
        response = handle_command(command, args)
        print(response)
        sys.exit(0)

    # Natural language query - use LLM routing
    if not settings.lms_api_base_url or not settings.lms_api_key:
        print("Error: LMS_API_BASE_URL and LMS_API_KEY required in .env.bot.secret", file=sys.stderr)
        sys.exit(1)

    if not settings.llm_api_base_url or not settings.llm_api_key:
        print("Error: LLM_API_BASE_URL and LLM_API_KEY required in .env.bot.secret", file=sys.stderr)
        sys.exit(1)

    # Initialize clients
    api_client = LMSAPIClient(settings.lms_api_base_url, settings.lms_api_key)
    llm_client = LLMClient(settings.llm_api_base_url, settings.llm_api_key, settings.llm_api_model)

    # Route the query through LLM
    response = route_intent(query, api_client, llm_client, debug=True)
    print(response)
    sys.exit(0)


def get_start_keyboard() -> InlineKeyboardMarkup:
    """Create inline keyboard for /start command.

    Returns:
        InlineKeyboardMarkup with common action buttons
    """
    keyboard = [
        [
            InlineKeyboardButton(text="📋 Доступные лабы", callback_data="labs"),
            InlineKeyboardButton(text="🏥 Статус системы", callback_data="health"),
        ],
        [
            InlineKeyboardButton(text="📊 Топ студентов", callback_data="top_learners"),
            InlineKeyboardButton(text="❓ Помощь", callback_data="help"),
        ],
        [
            InlineKeyboardButton(text="🔍 Найти худшую лабораторию", callback_data="worst_lab"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


async def run_telegram_mode() -> None:
    """Run bot in Telegram mode with aiogram."""
    settings = get_settings()

    if not settings.bot_token:
        logger.error("BOT_TOKEN not found in environment. Cannot start Telegram bot.")
        sys.exit(1)

    # Initialize clients
    lms_client = LMSClient(
        base_url=settings.lms_api_base_url or "http://localhost:42002",
        api_key=settings.lms_api_key or "",
    )
    llm_client = LLMClient(
        api_key=settings.llm_api_key or "",
        base_url=settings.llm_api_base_url or "http://localhost:42005/v1",
        model=settings.llm_api_model,
    )

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()

    # Initialize API and LLM clients
    api_client = None
    llm_client = None
    if settings.lms_api_base_url and settings.lms_api_key:
        api_client = LMSAPIClient(settings.lms_api_base_url, settings.lms_api_key)
    if settings.llm_api_base_url and settings.llm_api_key:
        llm_client = LLMClient(settings.llm_api_base_url, settings.llm_api_key, settings.llm_api_model)

    # Register command handlers
    @dp.message(Command("start"))
    async def cmd_start(message: types.Message, command: CommandObject) -> None:
        response = handle_start()
        await message.answer(response, reply_markup=get_start_keyboard())

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

    # Handle callback queries from inline buttons
    @dp.callback_query()
    async def handle_callback(callback: types.CallbackQuery) -> None:
        action = callback.data

        if action == "labs":
            response = handle_labs()
        elif action == "health":
            response = handle_health()
        elif action == "help":
            response = handle_help()
        elif action == "top_learners":
            if api_client and llm_client:
                response = route_intent("кто топ 5 студентов?", api_client, llm_client)
            else:
                response = "LLM не настроен"
        elif action == "worst_lab":
            if api_client and llm_client:
                response = route_intent("какая лаборатория имеет наименьший процент сдачи?", api_client, llm_client)
            else:
                response = "LLM не настроен"
        else:
            response = "Неизвестное действие"

        await callback.message.answer(response)
        await callback.answer()

    # Handle all other messages (natural language queries)
    @dp.message()
    async def handle_message(message: types.Message) -> None:
        user_text = message.text

        if not user_text:
            return

        # Check if it's a slash command (shouldn't reach here, but just in case)
        if user_text.startswith("/"):
            await message.answer("Неизвестная команда. Попробуйте /help")
            return

        # Use LLM intent routing for natural language queries
        if api_client and llm_client:
            # Send "thinking" message
            thinking = await message.answer("🤔 Думаю...")

            try:
                response = route_intent(user_text, api_client, llm_client)
                await thinking.edit_text(response)
            except Exception as e:
                logger.error(f"Error in intent routing: {e}")
                await thinking.edit_text(f"Ошибка: {e}")
        else:
            await message.answer(
                "Я пока не умею отвечать на вопросы. Попробуйте использовать команды:\n"
                "/help — показать команды\n"
                "/labs — показать лабораторные\n"
                "/scores <lab> — показать оценки"
            )

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
