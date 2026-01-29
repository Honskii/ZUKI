from typing import List

class CallDomain:
    @staticmethod
    def get_user_emoji(user_full_name: str, call_signs: List[str]):
        return call_signs[sum([ord(c) for c in user_full_name]) % len(call_signs)]