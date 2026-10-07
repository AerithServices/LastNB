class UserType:
    OWNER = "owner"
    PREMIUM = "premium"
    BLACKLISTED = "blacklisted"


class UserManager:
    def __init__(self):
        self.owners: set[int] = set()
        self.premium: set[int] = set()
        self.blacklisted: set[int] = set()

    def is_owner(self, user_id: int) -> bool:
        return user_id in self.owners

    def is_premium(self, user_id: int) -> bool:
        return user_id in self.premium

    def is_blacklisted(self, user_id: int) -> bool:
        return user_id in self.blacklisted

    def get_user_type(self, user_id: int) -> str | None:
        if self.is_owner(user_id):
            return UserType.OWNER
        if self.is_premium(user_id):
            return UserType.PREMIUM
        if self.is_blacklisted(user_id):
            return UserType.BLACKLISTED
        return None

    def add_owner(self, user_id: int) -> None:
        self.owners.add(user_id)

    def remove_owner(self, user_id: int) -> None:
        self.owners.discard(user_id)

    def add_premium(self, user_id: int) -> None:
        self.premium.add(user_id)

    def remove_premium(self, user_id: int) -> None:
        self.premium.discard(user_id)

    def add_blacklisted(self, user_id: int) -> None:
        self.blacklisted.add(user_id)

    def remove_blacklisted(self, user_id: int) -> None:
        self.blacklisted.discard(user_id)


user_manager = UserManager()