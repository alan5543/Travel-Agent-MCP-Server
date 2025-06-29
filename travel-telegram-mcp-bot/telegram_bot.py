from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import TelegramError

from config import logger
from gemini_client import GeminiChatClient

# --- Command Handlers ---

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the /start command with a welcome message."""
    welcome_message = (
        "🌟 *Welcome to TravelBuddy\!* 🌍\n\n"
        "I'm your friendly travel agent assistant, here to help with:\n"
        "• ✈️ Flight searches\n"
        "• 🏨 Hotel bookings\n"
        "• 🗺️ Trip planning\n"
        "• 💸 Budget calculations\n"
        "• 🌐 Fetching web content\n\n"
        "Try asking: 'Calculate 1 \+ 3' to see my tools in action\!\n"
        "Type `/new` to start a fresh conversation or `/help` for more info."
    )
    try:
        await update.message.reply_text(welcome_message, parse_mode="Markdown")
    except TelegramError:
        await update.message.reply_text(welcome_message.replace("*", "").replace("`", ""))


async def new_chat_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the /new command to reset the chat session."""
    chat_client: GeminiChatClient = context.bot_data["chat_client"]
    chat_id = update.effective_chat.id
    response = chat_client.start_session(chat_id)
    try:
        await update.message.reply_text(response)
    except TelegramError:
        await update.message.reply_text(response.replace("*", "").replace("`", ""))


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the /help command."""
    help_message = (
        "📚 *TravelBuddy Help Guide* 📚\n\n"
        "Here's how I can assist you:\n"
        "• *Ask anything travel\-related:* 'Find flights to Paris' or 'Suggest a hotel in Tokyo\.'\n"
        "• *Use my tools directly:* 'Calculate 5 \* 120' or 'Fetch travel tips from a website\.'\n\n"
        "*Commands:*\n"
        "  • `/start` \- Begin our conversation\.\n"
        "  • `/new` \- Start a completely new chat session\.\n"
        "  • `/help` \- Show this help message\.\n\n"
        "I'm here to make your travel planning seamless\! 🌴"
    )
    try:
        await update.message.reply_text(help_message, parse_mode="MarkdownV2")
    except TelegramError:
        await update.message.reply_text(help_message.replace("*", "").replace("`", ""))


# --- Message Handler ---

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles all non-command text messages from the user."""
    chat_client: GeminiChatClient = context.bot_data["chat_client"]
    query = update.message.text
    chat_id = update.effective_chat.id
    
    # Process the query and let process_query handle the Telegram response
    response = await chat_client.process_query(
        query, 
        chat_id, 
        context.bot_data["mcp_client"].gemini_tools, 
        context
    )
    
    # No need to reply again; process_query already sends the response
    logger.info(f"Processed query for chat_id {chat_id}: {query}, Response: {response[:50]}...")


# --- Error Handler ---

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Logs errors and sends a user-friendly message."""
    logger.error("An error occurred: %s", context.error)
    
    error_message = (
        "⚠️ *Oops, something went wrong\!* 😔\n"
        "Don't worry, TravelBuddy is still here to help. Please try your request again, or use `/new` to start over."
    )
    
    if isinstance(update, Update) and update.effective_chat:
        try:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=error_message,
                parse_mode="Markdown"
            )
        except TelegramError:
            # Fallback for the error message itself
             await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=error_message.replace("*", "").replace("`", "").replace("\\", "")
            )