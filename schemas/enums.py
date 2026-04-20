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


class SubscriptionStatus(str, Enum):
    incomplete = "incomplete"
    trialing = "trialing"
    past_due = "past_due"
    unpaid = "unpaid"
    paid = "paid"

    @property
    def is_active(self) -> bool:
        return self in (self.trialing,)

    @property
    def is_past_due(self) -> bool:
        return self == self.past_due

    @property
    def requires_payment(self) -> bool:
        return self in (self.past_due, self.unpaid)

    @classmethod
    def from_stripe(cls, stripe_status: str) -> "SubscriptionStatus":
        """Convierte el status de Stripe al enum."""
        mapping = {
            "incomplete": cls.incomplete,
            "trialing": cls.trialing,
            "active": cls.trialing,  # active se considera trialing a efectos de acceso
            "past_due": cls.past_due,
            "unpaid": cls.unpaid,
            "incomplete_expired": cls.incomplete,
            "paid": cls.paid,  # paid -> subscription activa
        }
        return mapping.get(stripe_status, cls.incomplete)
