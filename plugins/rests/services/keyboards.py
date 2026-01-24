from typing import List
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery


class KeyboardService:
    """Сервис для создания встроенных клавиатур"""

    @staticmethod
    async def first_ikbm(available_options: List[bool]) -> InlineKeyboardMarkup | None:
        """Первая встроенная клавиатура для выбора недели начала реста"""
        ikb_this_week = InlineKeyboardButton(
            text=f"{"✅" if available_options[0] else "❌"} С этой",
            callback_data=f"rest:s0{'s' if available_options[0] else 'f'}")

        ikb_next_week = InlineKeyboardButton(
            text=f"{"✅" if available_options[1] else "❌"} Со следующей",
            callback_data=f"rest:s1{'s' if available_options[1] else 'f'}")

        return InlineKeyboardMarkup(
            inline_keyboard=[
                [ikb_this_week,
                ikb_next_week],
                [InlineKeyboardButton(text="✖️ Отмена", callback_data="rest:cancel")]
        ])

    @staticmethod
    async def second_ikbm(available_options: List[bool]):
        """Вторая встроенная клавиатура для выбора продолжительности реста"""

        ikb_for_1_week = InlineKeyboardButton(
            text=f"{"✅" if available_options[0] else "❌"} 1 неделя",
            callback_data=f"rest:d1{'s' if available_options[0] else 'f'}")

        ikb_for_2_weeks = InlineKeyboardButton(
            text=f"{"✅" if available_options[1] else "❌"} 2 недели",
            callback_data=f"rest:d2{'s' if available_options[1] else 'f'}")

        return InlineKeyboardMarkup(
            inline_keyboard=[
                [ikb_for_1_week,
                ikb_for_2_weeks],
                [InlineKeyboardButton(text="🤔 до 4-х недель", callback_data="rest:longer_rest")],
                [
                    InlineKeyboardButton(text="◀ Назад", callback_data="rest:start"),
                    InlineKeyboardButton(text="✖️ Отмена", callback_data="rest:cancel")
                ]
            ]
        )

    @staticmethod
    async def reject_ikbm() -> InlineKeyboardMarkup:
        """Встроенная клавиатура для случаев, где остаётся только Назад и Отмена"""
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="◀ Назад", callback_data="rest:start"),
                    InlineKeyboardButton(text="✖️ Отмена", callback_data="rest:cancel")]
        ])

    @staticmethod
    async def confirm_rest_ikbm(starts: int) -> InlineKeyboardMarkup:
        """Встроенная клавиатура для подтверждения взятия реста"""
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="✅ Подтвердить", callback_data="rest:confirm")],
                [InlineKeyboardButton(text="◀ Назад", callback_data=f"rest:s{starts}s"),
                    InlineKeyboardButton(text="✖️ Отмена", callback_data="rest:cancel")]
        ])