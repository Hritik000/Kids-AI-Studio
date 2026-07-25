import uuid
from typing import Dict, List, Optional
from datetime import datetime, timezone, timedelta
from app.models.saas import SubscriptionPlan, UserSubscription

AVAILABLE_PLANS: Dict[str, SubscriptionPlan] = {
    "plan_free": SubscriptionPlan(
        plan_id="plan_free",
        name="Free",
        monthly_price_usd=0.0,
        credits_per_month=100,
        max_team_members=1,
        storage_limit_gb=2.0,
        features=["100 AI Credits / month", "720p Resolution", "Community Support"]
    ),
    "plan_starter": SubscriptionPlan(
        plan_id="plan_starter",
        name="Starter",
        monthly_price_usd=19.0,
        credits_per_month=1000,
        max_team_members=3,
        storage_limit_gb=25.0,
        features=["1,000 AI Credits / month", "1080p Full HD", "Standard Priority Queue"]
    ),
    "plan_creator": SubscriptionPlan(
        plan_id="plan_creator",
        name="Creator",
        monthly_price_usd=49.0,
        credits_per_month=3500,
        max_team_members=5,
        storage_limit_gb=100.0,
        features=["3,500 AI Credits / month", "4K Ultra HD", "Priority Rendering Queue", "SEO & Publishing Tools"]
    ),
    "plan_pro": SubscriptionPlan(
        plan_id="plan_pro",
        name="Pro",
        monthly_price_usd=99.0,
        credits_per_month=10000,
        max_team_members=15,
        storage_limit_gb=500.0,
        features=["10,000 AI Credits / month", "Multi-Platform Scheduler", "Custom Brand Characters", "24/7 Dedicated Support"]
    )
}

user_subscriptions_db: Dict[str, UserSubscription] = {}

class BillingService:
    @staticmethod
    def get_user_subscription(user_id: str) -> UserSubscription:
        if user_id not in user_subscriptions_db:
            sub = UserSubscription(
                subscription_id=f"sub_{uuid.uuid4().hex[:8]}",
                user_id=user_id,
                plan_id="plan_creator",
                credits_remaining=3500,
                current_period_end=(datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
            )
            user_subscriptions_db[user_id] = sub
        return user_subscriptions_db[user_id]

    @staticmethod
    def subscribe_to_plan(user_id: str, plan_id: str) -> UserSubscription:
        if plan_id not in AVAILABLE_PLANS:
            raise ValueError(f"Plan '{plan_id}' does not exist.")

        plan = AVAILABLE_PLANS[plan_id]
        sub = UserSubscription(
            subscription_id=f"sub_{uuid.uuid4().hex[:8]}",
            user_id=user_id,
            plan_id=plan_id,
            credits_remaining=plan.credits_per_month,
            current_period_end=(datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
        )
        user_subscriptions_db[user_id] = sub
        return sub

    @staticmethod
    def deduct_credits(user_id: str, amount: int) -> bool:
        sub = BillingService.get_user_subscription(user_id)
        if sub.credits_remaining < amount:
            return False
        sub.credits_remaining -= amount
        return True
