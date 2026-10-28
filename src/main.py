import asyncio
import logging
from contextlib import asynccontextmanager

from aiogram import Bot, Dispatcher
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import router as api_router
from src.bot.handlers import register_commands, router as bot_router
from src.bot.keyboards import setup_bot_menu
from src.config import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    bot_task: asyncio.Task | None = None
    bot: Bot | None = None

    if settings.bot_token:
        bot = Bot(token=settings.bot_token)
        dp = Dispatcher()
        dp.include_router(bot_router)
        app.state.bot = bot
        app.state.dp = dp

        await setup_bot_menu(bot, settings.webapp_url)
        await register_commands(bot)

        async def run_polling() -> None:
            try:
                await dp.start_polling(bot, handle_signals=False)
            except asyncio.CancelledError:
                pass

        bot_task = asyncio.create_task(run_polling())
        logger.info("Telegram bot polling started")
    else:
        logger.warning("BOT_TOKEN not set — bot polling disabled")

    yield

    if bot_task:
        bot_task.cancel()
        try:
            await bot_task
        except asyncio.CancelledError:
            pass
    if bot:
        await bot.session.close()


app = FastAPI(title="О!дин запрос API", lifespan=lifespan)
settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
