from datetime import datetime, timezone, tzinfo

from datetime import date, timedelta
from ..models.rest import ChatMemberRest

class ChatMemberRestDomain:
    @staticmethod
    async def rests_interceps(
        rest_1: ChatMemberRest,
        rest_2: ChatMemberRest,
    ) -> bool:
        """Проверяет, пересекаются ли два периода реста"""
        if (not rest_1.starts_at or not rest_1.ends_at or
            not rest_2.starts_at or not rest_2.ends_at):
            raise ValueError("Rest start and end dates must be set")
        return not (
            rest_1.ends_at < rest_2.starts_at or
            rest_2.ends_at < rest_1.starts_at
        )

    @staticmethod
    async def check_all_rests_interceps(
        rest: ChatMemberRest,
        other_rests: list[ChatMemberRest]
    ) -> bool:
        """Проверяет, пересекаются ли периоды реста из списка с текущим периодом реста"""
        for other_rest in other_rests:
            if await ChatMemberRestDomain.rests_interceps(rest, other_rest):
                return True
        return False

    @staticmethod
    async def can_take_rest_starts_from_date(rest_starts_at: date) -> bool:
        """Проверяет, можно ли взять рест на указанную дату"""
        return rest_starts_at.weekday() not in (5, 6)  # Суббота и Воскресенье

    @staticmethod
    async def filter_and_format_rests(
        rests_from_db: list[ChatMemberRest],
        app_tzinfo: tzinfo = timezone.utc
    ) -> list[ChatMemberRest]:
        """Фильтрует и форматирует периоды реста из базы данных"""
        rests = []
        for rest in rests_from_db:
            if rest.state == "revoked":
                continue
            rest.starts_at = rest.starts_at.astimezone(app_tzinfo).date()
            rest.ends_at = rest.ends_at.astimezone(app_tzinfo).date()
            rests.append(rest)
        return rests

    @staticmethod
    async def define_possible_rest_starts(
        rests: list[ChatMemberRest],
        app_tzinfo: tzinfo
    ) -> list[bool]:
        """Определяет возможные даты начала реста"""
        rest_start_week_available = [False, False]

        today = datetime.now(tz=app_tzinfo).date()
        this_monday = today - timedelta(days=today.weekday())

        for i in range(2):
            if i == 0 and not await ChatMemberRestDomain.can_take_rest_starts_from_date(
                rest_starts_at=today
            ):
                continue # На этой неделе уже нельзя взять рест
            rest_start_date = this_monday + timedelta(weeks=i)
            rest = await ChatMemberRestDomain.calculate_rest_dates(
                rest_starts_at=rest_start_date,
                duration_weeks=1
            )
            rest_start_week_available[i] = not await ChatMemberRestDomain.check_all_rests_interceps(
                rest=rest, other_rests=rests
            )
        return rest_start_week_available

    @staticmethod
    async def define_possible_rest_durations(
        rest_starts_at: date,
        other_rests: list[ChatMemberRest]
    ) -> list[bool]:
        """Определяет возможные продолжительности реста"""
        rest_duration_available = [False, False]

        for i in range(2):
            duration_weeks = i + 1
            rest = await ChatMemberRestDomain.calculate_rest_dates(
                rest_starts_at=rest_starts_at,
                duration_weeks=duration_weeks
            )

            rest_duration_available[i] = not await ChatMemberRestDomain.check_all_rests_interceps(
                rest=rest, other_rests=other_rests
            )
        return rest_duration_available

    @staticmethod
    async def calculate_rest_dates(
        rest_starts_at: date,
        duration_weeks: int
    ) -> ChatMemberRest:
        """Вычисляет даты начала и окончания реста на основе даты взятия реста"""
        new_rest = ChatMemberRest()
        new_rest.starts_at = rest_starts_at - timedelta(days=rest_starts_at.weekday())
        new_rest.ends_at = new_rest.starts_at + timedelta(weeks=duration_weeks) - timedelta(days=1)
        return new_rest