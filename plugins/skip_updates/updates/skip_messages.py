from datetime import datetime, timedelta
from aiogram.types import Update, Message

class MessagesUpdateSkipper:
    def __init__(self, skip_interval_seconds: int = 30):
        self.skip_interval = skip_interval_seconds

    def should_skip(self, update: Update) -> bool:
        if isinstance(update, Message):
            if (datetime.now(tz=update.date.tzinfo) - update.date).seconds > self.skip_interval:
                return True
        return False
