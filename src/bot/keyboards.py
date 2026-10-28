from aiogram import Bot
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    MenuButtonWebApp,
    WebAppInfo,
)

from src.config import get_settings


def webapp_url_with_session(base_url: str, session_id: str | None = None) -> str:
    base = base_url.rstrip("/")
    if session_id:
        return f"{base}/?session={session_id}"
    return f"{base}/"


def search_keyboard(session_id: str | None = None) -> InlineKeyboardMarkup:
    settings = get_settings()
    url = webapp_url_with_session(settings.webapp_url, session_id)
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Открыть подбор в Mini App",
                    web_app=WebAppInfo(url=url),
                )
            ]
        ]
    )


async def setup_bot_menu(bot: Bot, webapp_url: str) -> None:
    await bot.set_chat_menu_button(
        menu_button=MenuButtonWebApp(text="Поиск отелей", web_app=WebAppInfo(url=webapp_url.rstrip("/") + "/"))
    )
