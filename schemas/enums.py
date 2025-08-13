from enum import Enum


class SubscriptionTier(str, Enum):
    free = "FREE"
    pro = "PRO"
    enterprise = "ENTERPRISE"

    @property
    def level(self) -> int:
        hierarchy = {"FREE": 0, "PRO": 1, "ENTERPRISE": 3}
        return hierarchy[self.value]

    def has_access_to(self, required_tier: "SubscriptionTier") -> bool:
        return self.level >= required_tier.level
