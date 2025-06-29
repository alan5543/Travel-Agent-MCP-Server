import google.generativeai as genai
from typing import Dict, Any, List
from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import TelegramError
from google.generativeai.types import Tool
from datetime import datetime, timedelta
import aiohttp
import asyncio
from io import BytesIO

import os
import tempfile
from pylatex import Document, NoEscape
from google.api_core.exceptions import ResourceExhausted, ServiceUnavailable

from config import GEMINI_API_KEY, GEMINI_MODEL, logger, MAX_TOOL_ITERATIONS
from prompt import SYSTEM_PROMPT
import html
import re
from telegram.error import BadRequest


# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

class GeminiChatClient:
    """Manages chat sessions with the Gemini API, processing user queries and integrating with Telegram and MCP tools."""
    def __init__(self, model_name: str = GEMINI_MODEL, max_tool_iterations: int = MAX_TOOL_ITERATIONS):
        """Initialize the Gemini client with a specified model and tool iteration limit.

        Args:
            model_name: Name of the Gemini model (e.g., 'gemini-pro').
            max_tool_iterations: Maximum number of tool calls per query (default: from config).
        """
        self.model = genai.GenerativeModel(model_name)
        self.chat_sessions: Dict[int, Dict[str, Any]] = {}  # {chat_id: {"session": Any, "last_activity": datetime}}
        self.session_timeout = timedelta(hours=1)
        self.max_tool_iterations = max_tool_iterations

    def start_session(self, chat_id: int) -> str:
        """Starts a new chat session for a given chat_id with a system prompt.

        Args:
            chat_id: Telegram chat ID for the session.

        Returns:
            A confirmation message for the user.
        """
        logger.info("Starting new chat session for chat_id: %s", chat_id)
        session = self.model.start_chat(enable_automatic_function_calling=False)
        session.send_message(SYSTEM_PROMPT)
        self.chat_sessions[chat_id] = {
            "session": session,
            "last_activity": datetime.now()
        }
        return "✨ ** New chat session started! ** Ask me about flights, hotels, or trip plans! 🌍"

    def cleanup_sessions(self) -> None:
        """Removes sessions inactive for longer than session_timeout."""
        current_time = datetime.now()
        expired = [
            chat_id for chat_id, data in self.chat_sessions.items()
            if current_time - data["last_activity"] > self.session_timeout
        ]
        for chat_id in expired:
            logger.info(f"Cleaning up expired session for chat_id: %s", chat_id)
            del self.chat_sessions[chat_id]

    async def generate_html(self, text: str) -> str:
        """Generates styled HTML with CSS framework-like styling from the input text.
        
        Args:
            text: The text to convert to styled HTML.
            
        Returns:
            The generated HTML with self-contained CSS framework styling.
        """
        html_model = genai.GenerativeModel(GEMINI_MODEL)
        html_session = html_model.start_chat(enable_automatic_function_calling=False)
        html_prompt = (
            "Convert the following text into a beautiful, responsive HTML document using self-contained CSS framework styling "
            "(similar to Bootstrap/Tailwind but all inline). Apply these specific requirements:\n\n"
            "1. CSS FRAMEWORK STYLING:\n"
            "- Create a light, modern UI with utility classes similar to Tailwind/Bootstrap\n"
            "- Include responsive grid system (rows/columns)\n"
            "- Add component classes for cards, alerts, buttons\n"
            "- Use CSS variables for theming\n"
            "- Include hover/focus states for interactive elements\n\n"
            "2. STRUCTURE:\n"
            "- Use proper HTML5 doctype and structure\n"
            "- Include a <style> block with comprehensive utility classes\n"
            "- Semantic HTML with aria attributes where needed\n\n"
            "3. COMPONENTS:\n"
            "- Cards for content sections with shadow and rounded corners\n"
            "- Beautiful buttons with hover effects\n"
            "- Responsive tables with zebra striping\n"
            "- Accordions for collapsible content if sections are long\n"
            "- Tooltips for abbreviations or complex terms\n\n"
            "4. CONTENT HANDLING:\n"
            "- Detect and properly format:\n"
            "  - Code blocks with syntax highlighting-like styling\n"
            "  - Math formulas (render as clean HTML)\n"
            "  - Images (responsive with lightbox if possible)\n"
            "  - Videos/iframes (responsive containers)\n"
            "- Remove all emojis\n"
            "- Convert markdown-like formatting to HTML\n\n"
            "5. OUTPUT REQUIREMENTS:\n"
            "- Fully self-contained (no external resources)\n"
            "- Mobile-first responsive design\n"
            "- Accessible (proper contrast, ARIA attributes)\n"
            "- Lightweight (<1MB preferably)\n"
            "- Clean, readable HTML with proper indentation\n\n"
            "- Ensure the HTML image can be displayed in the Telegram app\n\n"
            "- Also add a view image button for the user to direct to the image link, to prevent the image cannot be rendered\n\n"
            "Here's the text to convert:\n\n" + text
        )
        response = await html_session.send_message_async(html_prompt)
        return response.text


    async def send_telegram_response(self, chat_id: int, text: str, context: ContextTypes.DEFAULT_TYPE, filename: str = None) -> None:
        """
        Sends a response to Telegram in MarkdownV2, handling long messages by splitting them.

        Args:
            chat_id: Telegram chat ID.
            text: The response text, pre-formatted and escaped for MarkdownV2.
            context: Telegram context for sending messages.
        """
        max_length = 4096  # Telegram's message length limit
        if len(text) <= max_length:
            try:
                await context.bot.send_message(
                    chat_id=chat_id, 
                    text=text, 
                    parse_mode="Markdown"
                )
            except BadRequest as e:
                # If MarkdownV2 parsing fails, send as plain text.
                # This is a good fallback, especially during development.
                # You might want to log the error `e` and the problematic `text`.
                print(f"MarkdownV2 parsing failed: {e}")
                await context.bot.send_message(
                    chat_id=chat_id, 
                    text=text # The original text without parsing
                )
        else:
            # Split into chunks if the message is too long
            chunk_size = 4000  # Leave buffer for headers
            chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
            
            for i, chunk in enumerate(chunks, 1):
                # Use MarkdownV2-formatted header for each chunk
                chunk_text = f"*Part {i}/{len(chunks)}:*\n{chunk}"
                try:
                    await context.bot.send_message(
                        chat_id=chat_id, 
                        text=chunk_text, 
                        # parse_mode="MarkdownV2"
                    )
                except BadRequest:
                    # Fallback for chunks as well
                    await context.bot.send_message(
                        chat_id=chat_id, 
                        text=chunk_text
                    )


    # async def send_telegram_response(self, chat_id: int, text: str, context: ContextTypes.DEFAULT_TYPE, filename: str = None) -> None:
    #     """Sends a response to Telegram, handling long messages by splitting into chunks.

    #     Args:
    #         chat_id: Telegram chat ID.
    #         text: The response text to send, which may include intentional HTML tags.
    #         context: Telegram context for sending messages.
    #         filename: Optional filename for sending as a document (if text is too long).
    #     """
    #     max_length = 4096
    #     # Define the expected prefix
    #     prefix_pattern = r"^(✨\s*<b>Your Answer:</b>\s*\n)?"
    #     match = re.match(prefix_pattern, text)
    #     prefix = match.group(1) if match else ""
    #     content = text[len(prefix):]

    #     # Check if content contains HTML tags
    #     is_html = any(tag in content for tag in ["<b>", "<a>", "<i>"])
    #     if is_html:
    #         full_text = text  # Preserve intentional HTML
    #     else:
    #         full_text = prefix + html.escape(content)  # Escape plain text content

    #     if len(full_text) <= max_length:
    #         try:
    #             await context.bot.send_message(chat_id=chat_id, text=full_text, parse_mode="Markdown")
    #         except BadRequest as e:
    #             # Fallback if HTML parsing fails
    #             await context.bot.send_message(chat_id=chat_id, text=full_text, parse_mode=None)
    #     else:
    #         # Split into chunks, reserving space for headers
    #         chunk_size = 4000  # Less than max_length to accommodate headers
    #         chunks = [full_text[i:i + chunk_size] for i in range(0, len(full_text), chunk_size)]
    #         for i, chunk in enumerate(chunks, 1):
    #             # Use HTML-formatted header for each chunk
    #             chunk_text = f"<b>Part {i}/{len(chunks)}:</b>\n{chunk}"
    #             try:
    #                 await context.bot.send_message(chat_id=chat_id, text=chunk_text, parse_mode="Markdown")
    #             except BadRequest as e:
    #                 # Fallback if HTML parsing fails
    #                 await context.bot.send_message(chat_id=chat_id, text=chunk_text, parse_mode=None)

    async def process_query(self, query: str, chat_id: int, tools: List[Tool], context: ContextTypes.DEFAULT_TYPE) -> str:
        """Processes a user query, invoking MCP tools as needed and sending responses via Telegram.

        Args:
            query: The user's input query (e.g., "Find an Airbnb in Hong Kong").
            chat_id: Telegram chat ID for the user session.
            tools: List of MCP tools available for function calls.
            context: Telegram context for sending messages.

        Returns:
            A string containing the response to the query or an error message.
        """
        self.cleanup_sessions()
        if chat_id not in self.chat_sessions:
            self.start_session(chat_id)
        
        chat_session = self.chat_sessions[chat_id]["session"]
        self.chat_sessions[chat_id]["last_activity"] = datetime.now()
        max_retries = 3

        for attempt in range(max_retries):
            try:
                response = await chat_session.send_message_async(query, tools=tools)
                iteration = 0

                while iteration < self.max_tool_iterations:
                    iteration += 1
                    function_call_part = None
                    candidate = response.candidates[0]
                    for part in candidate.content.parts:
                        if part.function_call:
                            function_call_part = part
                            break
                    
                    if function_call_part:
                        fc = function_call_part.function_call
                        tool_name, tool_args = fc.name, dict(fc.args)
                        friendly_tool_name = tool_name.replace("_", " ").title()
                        notification_text = f"🛠️ Step {iteration}/{self.max_tool_iterations}: {friendly_tool_name} in progress..."
                        await context.bot.send_message(chat_id=chat_id, text=notification_text, parse_mode="Markdown")

                        logger.info("Calling tool '%s' with args %s (iteration %d)", tool_name, tool_args, iteration)
                        tool_result = await context.bot_data["mcp_client"].call_tool(tool_name, tool_args)
                        logger.info("Tool result: %s", tool_result)

                        result_value = None
                        if tool_result and tool_result.content:
                            content_block = tool_result.content[0]
                            if hasattr(content_block, 'json'):
                                result_value = content_block.json()
                            elif hasattr(content_block, 'text'):
                                result_value = content_block.text
                            else:
                                result_value = str(content_block)
                        else:
                            result_value = "No content was returned from the tool."

                        function_response = {
                            "role": "function",
                            "parts": [{"function_response": {"name": tool_name, "response": {"result": result_value}}}]
                        }
                        response = await chat_session.send_message_async(function_response, tools=tools)
                    else:
                        response_text = response.text
                        await self.send_telegram_response(chat_id, response_text, context, filename=f"response_{chat_id}")
                        return response.text

                return "⚠️ Error: Exceeded maximum tool call limit. Please simplify your request."
            
            except ResourceExhausted:
                logger.warning(f"Rate limit hit on attempt {attempt + 1}/{max_retries}. Retrying after delay.")
                await asyncio.sleep(2 ** attempt)
                continue
            except ServiceUnavailable:
                logger.warning(f"Service unavailable on attempt {attempt + 1}/{max_retries}. Retrying after delay.")
                await asyncio.sleep(2 ** attempt)
                continue
            except Exception as e:
                logger.error("Unexpected error during query processing: %s", e, exc_info=True)
                return f"⚠️ *Error:* An issue occurred: {str(e)}"
        
        return"⚠️ Error: Failed to process query after multiple attempts. Please try again later."



            # elif filename:
        #     try:
        #         # Generate HTML code
        #         html_code = await self.generate_html(text)
        #         # Prepare the HTML document
        #         filename = f"{filename.replace('.txt', '')}.html" if filename else f"response_{chat_id}.html"
                
        #         # Create form data with HTML content
        #         form = aiohttp.FormData()
        #         form.add_field("chat_id", str(chat_id), content_type="text/plain")
        #         form.add_field(
        #             "document",
        #             html_code.encode('utf-8'),
        #             filename=filename,
        #             content_type="text/html"
        #         )
        #         form.add_field(
        #             "caption",
        #             f"HTML response for chat_id {chat_id}",
        #             content_type="text/plain"
        #         )
                
        #         async with aiohttp.ClientSession() as session:
        #             async with session.post(
        #                 f"https://api.telegram.org/bot{context.bot.token}/sendDocument",
        #                 data=form
        #             ) as response:
        #                 if response.status != 200:
        #                     logger.error(f"Failed to send HTML document: {await response.text()}")
        #                     raise Exception("HTML send failed")
                            
        #     except Exception as e:
        #         logger.error(f"HTML generation failed: {e}")
        #         # Fall back to plain text
        #         filename = filename.replace(".txt", ".md") if filename.endswith(".txt") else f"{filename}.md"
        #         form = aiohttp.FormData()
        #         form.add_field("chat_id", str(chat_id), content_type="text/plain")
        #         form.add_field("document", text.encode("utf-8"), filename=filename, content_type="text/plain")
        #         async with aiohttp.ClientSession() as session:
        #             async with session.post(f"https://api.telegram.org/bot{context.bot.token}/sendDocument", data=form) as response:
        #                 if response.status != 200:
        #                     logger.error(f"Failed to send document: {await response.text()}")
        #                     await context.bot.send_message(chat_id=chat_id, text="⚠️ <b>Error:</b> Could not send full details.")