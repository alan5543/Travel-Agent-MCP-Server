# main.py
import asyncio
import sys

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from config import TELEGRAM_BOT_TOKEN, logger
from mcp_server_config import mcp_server_configs
from mcp_client import MCPClient
from gemini_client import GeminiChatClient
from telegram_bot import (
    start_command,
    new_chat_command,
    help_command,
    handle_message,
    error_handler,
)

async def main() -> None:
    """Main application entry point."""

    mcp_client = MCPClient()
    chat_client = GeminiChatClient()
    application = None
    try:
        # Connect to MCP servers first
        await mcp_client.connect(mcp_server_configs)

        # Build the Telegram application
        application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

        # Store clients in bot_data for access in handlers
        application.bot_data["mcp_client"] = mcp_client
        application.bot_data["chat_client"] = chat_client

        # Register handlers
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("new", new_chat_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        application.add_error_handler(error_handler)

        # Start the bot
        logger.info("Telegram MCP Bot Started!")
        await application.initialize()
        await application.start()
        await application.updater.start_polling(allowed_updates=Update.ALL_TYPES)

        # Keep the application running
        await asyncio.Event().wait()

    except Exception as e:
        logger.critical("A critical error occurred on startup: %s", e, exc_info=True)
        # You might want to notify an admin via a different channel here
        raise
    finally:
        # Graceful shutdown
        if application:
            logger.info("Stopping Telegram MCP Bot...")
            await application.updater.stop()
            await application.stop()
            await application.shutdown()
        await mcp_client.cleanup()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Application shut down by user.")
    except Exception as e:
        logger.error("Application failed to run: %s", e, exc_info=True)

