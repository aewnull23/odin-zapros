from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import BotCommand, Message

from src.ai.intent import analyze_travel_query
from src.bot.keyboards import search_keyboard
from src.search.engine import search_hotels
from src.search.tours import search_tours
from src.store.sessions import create_session
from src.util.query_helpers import needs_clarification

router = Router()

CLARIFY_MESSAGES = {
    "location": "Укажите, пожалуйста, город или направление (например: Сочи, Питер, Махачкала).",
    "dates": "Когда планируете поездку? Можно так: «на выходные», «15–17 ноября» или «на 2 дня».",
    "budget": "Какой у вас ориентир по бюджету за всё проживание? Например: «до 10 тысяч».",
}


@router.message(CommandStart())
async def cmd_start(message: Message):
    text = (
        "Привет! Я «О!дин запрос» — AI-ассистент для поиска отелей и туров.\n\n"
        "Опишите поездку одним сообщением. Я могу искать в интернете контекст и сам выставлю фильтры.\n"
        "Пример:\n"
        "«Хочу в Махачкалу на 3 дня в ноябре, до 15 тысяч, у моря или тур по Дагестану»\n\n"
        "Или откройте Mini App для карточек и бронирования."
    )
    await message.answer(text, reply_markup=search_keyboard())


@router.message(F.text & ~F.text.startswith("/"))
async def handle_text(message: Message):
    query = (message.text or "").strip()
    if len(query) < 5:
        await message.answer(
            "Расскажите чуть подробнее: куда, когда, бюджет и что важнее — отель или тур?"
        )
        return

    parsed, filters, web_insight = await analyze_travel_query(query)
    if needs_clarification(parsed):
        hints = [CLARIFY_MESSAGES.get(f, f"Уточните: {f}") for f in parsed.missing_fields]
        await message.answer(
            "Почти понял запрос, но не хватает деталей:\n\n" + "\n".join(f"• {h}" for h in hints)
        )
        return

    hotels = search_hotels(parsed, filters) if filters.product_type in ("hotel", "both") else []
    tours = search_tours(parsed, filters) if filters.product_type in ("tour", "both") else []

    if not hotels and not tours:
        await message.answer(
            "Не нашёл подходящих вариантов. Попробуйте изменить бюджет, город или ослабить пожелания."
        )
        return

    session = create_session(
        query,
        parsed,
        filters,
        hotels,
        tours,
        user_id=message.from_user.id if message.from_user else None,
        web_insight=web_insight,
    )

    lines = [
        f"Готово. Фильтры AI: {filters.product_type}, звёзды от {filters.min_stars}, "
        f"до {filters.max_distance_km} км от центра."
    ]
    if web_insight:
        lines.append(web_insight[:400] + ("…" if len(web_insight or "") > 400 else ""))
    if hotels:
        lines.append(f"\nОтели ({len(hotels)}):")
        for i, h in enumerate(hotels[:2], 1):
            lines.append(f"{i}. {h.name} — {h.price_per_night:,} ₽/ночь".replace(",", " "))
    if tours:
        lines.append(f"\nТуры ({len(tours)}):")
        for i, t in enumerate(tours[:2], 1):
            lines.append(f"{i}. {t.name} — {t.price_total:,} ₽".replace(",", " "))
    lines.append("\nОткройте Mini App для всех результатов и бронирования.")
    await message.answer("\n".join(lines), reply_markup=search_keyboard(session.id))


async def register_commands(bot):
    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Начать и открыть поиск"),
        ]
    )
