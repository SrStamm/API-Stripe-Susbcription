from enum import Enum


class SubscriptionTier(str, Enum):
    free = "FREE"
    pro = "PRO"
    enterprise = "ENTERPRISE"
