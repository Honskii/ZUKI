import re
from datetime import datetime, timedelta, tzinfo, timezone

from aiogram import F
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, CallbackQuery

from plugins.db_manager import UnitOfWork
from plugins.telegram_info_collect.factories.chat_member import ChatMemberServiceFactory
from plugins.telegram_adapters.adapters.user_link import get_user_link

from .application_helper.rest import get_current_rests
from .domains.rest import ChatMemberRestDomain
from .factories.rest import ChatMemberRestServiceFactory
from .services.keyboards import KeyboardService
from .router import router

class Form(StatesGroup):
    taking_rest = State()
    confirmed = State()

@router.message(F.text.regexp(r"(?i)^!взять рест$"), F.chat.type.in_({"group", "supergroup"}))
async def rest_handler(message: Message, state: FSMContext, uow_factory: UnitOfWork, app_tzinfo: tzinfo):
    rests = await get_current_rests(
        uow_factory=uow_factory,
        tg_user_id=message.from_user.id,
        tg_chat_id=message.chat.id,
        from_date=datetime.now(tz=timezone.utc).date(),
        app_tzinfo=app_tzinfo
    )

    available_rest_starts = await ChatMemberRestDomain.define_possible_rest_starts(rests, app_tzinfo)

    if not any(available_rest_starts):
        await message.answer("❌ У вас пока не имеется возможность взять рест. Попробуйте позже.")
        return

    ikbm = await KeyboardService.first_ikbm(available_options=available_rest_starts)

    await state.set_state(Form.taking_rest)
    await state.update_data(
        new_rest={"user_id": message.from_user.id,"chat_id": message.chat.id})

    await message.answer(
        "🧉*Оформление реста*\n_Выберите начиная с какой недели хотите взять рест_",
        reply_markup=ikbm,
        parse_mode="Markdown"
    )

@router.callback_query(F.data.regexp(r"rest:[sd][012][sf]"), Form.taking_rest)
async def active_making_rest_callback_handler(
    callback: CallbackQuery,
    state: FSMContext,
    uow_factory: UnitOfWork,
    app_tzinfo: tzinfo
):
    """Обработка выбора вариантов оформления реста"""
    variant = callback.data.split(":", 1)[1]
    data = await state.get_data()
    new_rest = data.get("new_rest", {})

    if (new_rest.get("user_id") != callback.from_user.id or
        new_rest.get("chat_id") != callback.message.chat.id):
        await callback.answer("🪰 Кыш", show_alert=False)
        return

    if variant[0] == "s": # Выбор недели начала реста
        if variant[2] == "f": # Недоступный вариант
            ibkm_rest_reject = await KeyboardService.reject_ikbm()
            await callback.message.edit_text(
                    "❌ Вы выбрать данный вариант. Попробуйте вариант с галочкой.",
                    reply_markup=ibkm_rest_reject
                )
            return
        new_rest["start_week"] = int(variant[1]) # Через сколько недель наступит неделя начала реста
        await state.update_data(new_rest=new_rest)

        rests = await get_current_rests(
            uow_factory=uow_factory,
            tg_user_id=new_rest["user_id"],
            tg_chat_id=new_rest["chat_id"],
            from_date=datetime.now(tz=timezone.utc).date(),
            app_tzinfo=app_tzinfo
        )

        available_rests_durations = await ChatMemberRestDomain.define_possible_rest_durations(
            rest_starts_at=datetime.now(tz=app_tzinfo).date() + timedelta(weeks=new_rest["start_week"]),
            other_rests=rests
        )

        ikbm = await KeyboardService.second_ikbm(available_options=available_rests_durations)
        await callback.message.edit_text(
            "🧉*Оформление реста*\nРест будет выдан начиная {0} недели\n_Выберите продолжительность реста_".format(
                'с этой' if new_rest['start_week'] == 0 else 'со следующей'
            ),
            reply_markup=ikbm,
            parse_mode="Markdown"
        )
        return

    elif variant[0] == "d": # Выбор продолжительности
        if variant[2] == "f": # Недоступный вариант
            ibkm_rest_reject = await KeyboardService.reject_ikbm()
            await callback.message.edit_text(
                    "❌ Вы выбрать данный вариант. Попробуйте вариант с галочкой.",
                    reply_markup=ibkm_rest_reject
                )
            return
        new_rest["duration_weeks"] = int(variant[1]) # Продолжительность реста в неделях
        await state.update_data(new_rest=new_rest)
        await callback.message.edit_text(
            "🟢 Вы выбрали рест, начинающийся *{0}* и продолжительностью *{1}*.\n\n"
            "Нажмите Подтвердить, чтобы оформить рест.".format(
                'с этой недели' if new_rest['start_week'] == 0 else 'со следующей недели',
                '1 неделю' if new_rest['duration_weeks'] == 1 else '2 недели'
            ),
            reply_markup=await KeyboardService.confirm_rest_ikbm(starts=new_rest['start_week']),
            parse_mode="Markdown"
        )
        return

    await callback.message.edit_text("Произошла непредвиденная ошибка")
    return

@router.callback_query(F.data == "rest:confirm", Form.taking_rest)
async def confirm_rest(callback: CallbackQuery, state: FSMContext, uow_factory: UnitOfWork, app_tzinfo):
    """Подтверждение оформления реста"""
    data = await state.get_data()
    new_rest = data.get("new_rest", {})

    if (new_rest.get("user_id") != callback.from_user.id or
        new_rest.get("chat_id") != callback.message.chat.id):
        await callback.answer("🪰 Кыш", show_alert=False)
        return

    rest_start_date = datetime.now(tz=app_tzinfo).date() + timedelta(weeks=new_rest["start_week"])
    rest = await ChatMemberRestDomain.calculate_rest_dates(
        rest_starts_at=rest_start_date,
        duration_weeks=new_rest["duration_weeks"]
    )

    async with uow_factory() as uow:
        rest_service = ChatMemberRestServiceFactory(uow.session).create()

        await rest_service.put(
            tg_user_id=new_rest["user_id"],
            tg_chat_id=new_rest["chat_id"],
            state="active",
            starts_at=datetime.now(tz=app_tzinfo).date() + timedelta(weeks=new_rest["start_week"]),
            ends_at=datetime.now(tz=app_tzinfo).date() + timedelta(weeks=new_rest["start_week"] + new_rest["duration_weeks"]),
            revoked=False
        )

    await callback.message.edit_text(
        "✅ Рест успешно оформлен с *{0}* по *{1}*.".format(
            rest.starts_at.strftime("%d.%m.%Y"),
            rest.ends_at.strftime("%d.%m.%Y")
        ),
        parse_mode="Markdown"
    )
    await state.clear()

@router.callback_query(F.data == "rest:start", Form.taking_rest)
async def restart_keyboard(callback: CallbackQuery, state: FSMContext, uow_factory: UnitOfWork, app_tzinfo: tzinfo):
    """Возврат к первой клавиатуре оформления реста"""
    data = await state.get_data()
    rest = dict(data.get("new_rest", {}))
    if rest.get("user_id") != callback.from_user.id or rest.get("chat_id") != callback.message.chat.id:
        await callback.answer("🪰 Кыш", show_alert=False)
        return

    rests = await get_current_rests(
        uow_factory=uow_factory,
        tg_user_id=rest["user_id"],
        tg_chat_id=rest["chat_id"],
        from_date=datetime.now(tz=timezone.utc).date(),
        app_tzinfo=app_tzinfo
    )

    available_rest_starts = await ChatMemberRestDomain.define_possible_rest_starts(rests, app_tzinfo)

    ikbm = await KeyboardService.first_ikbm(available_options=available_rest_starts)

    await callback.message.edit_text(
        "🧉*Оформление реста*\n_Выберите начиная с какой недели хотите взять рест_",
        reply_markup=ikbm,
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "rest:cancel", Form.taking_rest)
async def remove_keyboard(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    rest = dict(data.get("new_rest", {}))
    if rest.get("user_id") != callback.from_user.id or rest.get("chat_id") != callback.message.chat.id:
        await callback.answer("🪰 Кыш", show_alert=False)
        return
    await callback.message.edit_text("❌ Оформление реста отменено.")
    await state.clear()

@router.callback_query(F.data == "rest:longer_rest", Form.taking_rest)
async def remove_keyboard(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    rest = dict(data.get("new_rest", {}))
    if rest.get("user_id") != callback.from_user.id and rest.get("chat_id") != callback.message.chat.id:
        await callback.answer("🪰 Кыш", show_alert=False)
        return
    await callback.message.edit_text("🟡 Получить более продолжительный рест можно по уважительной причине, уточнив у администрации напрямую.")

@router.message(F.text.regexp(r"(?i)^!выдать рест (\d+) (\d+)$"), F.chat.type.in_({"group", "supergroup"}))
async def admin_give_rest_handler(message: Message, state: FSMContext, app_tz: tzinfo):
    if message.reply_to_message is None:
        await message.answer("❌ Команду необходимо использовать в ответ на сообщение пользователя, которому вы хотите выдать рест.")
        return
    rest_chat_member_id = message.reply_to_message.from_user.id

    async with UnitOfWork() as uow:
        chat_member_service = ChatMemberServiceFactory(uow.session).create()
        chat_member = await chat_member_service.get_by_user_and_chat_tg_ids(
            tg_user_id=rest_chat_member_id,
            tg_chat_id=message.chat.id
        )
        if chat_member is None:
            await message.answer("❌ Пользователь не является участником этого чата.")
            return
        chat_member_role = await chat_member_service.get_role(chat_member.id)
        if chat_member_role.level < 6: # TODO: Создать разрешение на выдачу рестов и проверять через сервис
            await message.answer("❌ У вас недостаточно прав для выдачи рестов.")
            return

    match = re.match(r"(?i)^!выдать рест (\d+) (\d+)$", message.text)
    if not match:
        return

    starts_from_week = int(match.group(1))
    duration_weeks = int(match.group(2))

    if duration_weeks == 0:
        await message.answer("❌ Продолжительность реста должна быть не менее 1 недели.")
        return

    rest_start_date = datetime.now(tz=app_tz).date()
    rest = await ChatMemberRestDomain.calculate_rest_dates(
        rest_starts_at=rest_start_date + timedelta(weeks=starts_from_week),
        duration_weeks=duration_weeks
    )

    async with UnitOfWork() as uow:
        rest_service = ChatMemberRestServiceFactory(uow.session).create()

        await rest_service.put(
            tg_user_id=message.from_user.id,
            tg_chat_id=message.chat.id,
            state="active",
            starts_at=rest.starts_at,
            ends_at=rest.ends_at,
            revoked=False
        )
        await rest_service.put(
            tg_user_id=message.from_user.id,
            tg_chat_id=message.chat.id,
            state="blocked",
            starts_at=rest.starts_at + timedelta(weeks=duration_weeks),
            ends_at=rest.ends_at + timedelta(weeks=duration_weeks),
            revoked=False
        )

    await message.answer(
        "✅ Рест успешно выдан пользователю с ID *{0}* с *{1}* по *{2}*.".format(
            rest_chat_member_id,
            rest.starts_at.strftime("%d.%m.%Y"),
            rest.ends_at.strftime("%d.%m.%Y")
        ),
        parse_mode="Markdown"
    )