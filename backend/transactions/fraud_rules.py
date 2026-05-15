import logging
from datetime import timedelta
from typing import List, Dict, Any
from decimal import Decimal
from django.utils import timezone
from django.db.models import Avg, Count, Sum
from transactions.models import Transaction, RiskLevel, TransactionStatus

logger = logging.getLogger(__name__)


class FraudRule:
    def __init__(self, name: str, weight: float, severity: str):
        self.name = name
        self.weight = weight
        self.severity = severity

    def check(
        self, transaction: Transaction, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        raise NotImplementedError


class AmountSpikeRule(FraudRule):
    def __init__(self):
        super().__init__("AMOUNT_SPIKE", 25, "HIGH")

    def check(
        self, transaction: Transaction, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        user_avg = context.get("user_avg_amount", 0)
        if user_avg > 0 and float(transaction.amount) > user_avg * 3:
            return {
                "triggered": True,
                "rule": self.name,
                "severity": self.severity,
                "weight": self.weight,
                "message": f"Amount ${transaction.amount} is 3x above user average ${user_avg:.2f}",
            }
        return {"triggered": False}


class RapidTransactionsRule(FraudRule):
    def __init__(self):
        super().__init__("RAPID_TRANSACTIONS", 30, "CRITICAL")

    def check(
        self, transaction: Transaction, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        recent_count = context.get("transactions_last_5min", 0)
        if recent_count >= 5:
            return {
                "triggered": True,
                "rule": self.name,
                "severity": self.severity,
                "weight": self.weight,
                "message": f"{recent_count} transactions in the last 5 minutes",
            }
        return {"triggered": False}


class LocationAnomalyRule(FraudRule):
    def __init__(self):
        super().__init__("LOCATION_ANOMALY", 25, "HIGH")

    def check(
        self, transaction: Transaction, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        if not (transaction.latitude and transaction.longitude):
            return {"triggered": False}

        last_transaction = context.get("last_transaction")
        if not last_transaction or not (
            last_transaction.latitude and last_transaction.longitude
        ):
            return {"triggered": False}

        from math import radians, sin, cos, sqrt, atan2

        lat1, lon1 = float(transaction.latitude), float(transaction.longitude)
        lat2, lon2 = float(last_transaction.latitude), float(last_transaction.longitude)

        R = 6371
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = (
            sin(dlat / 2) ** 2
            + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
        )
        distance = 2 * R * atan2(sqrt(a), sqrt(1 - a))

        time_diff = (
            transaction.timestamp - last_transaction.timestamp
        ).total_seconds() / 60

        if distance > 500 and time_diff < 30:
            return {
                "triggered": True,
                "rule": self.name,
                "severity": self.severity,
                "weight": self.weight,
                "message": f"Location changed {distance:.0f}km in {time_diff:.0f} minutes",
            }
        return {"triggered": False}


class HighRiskCountryRule(FraudRule):
    HIGH_RISK_COUNTRIES = {"PK", "NG", "CM", "VN", "RU", "BY", "IR", "SY", "KP", "YE"}

    def __init__(self):
        super().__init__("HIGH_RISK_COUNTRY", 20, "MEDIUM")

    def check(
        self, transaction: Transaction, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        if transaction.merchant_country in self.HIGH_RISK_COUNTRIES:
            return {
                "triggered": True,
                "rule": self.name,
                "severity": self.severity,
                "weight": self.weight,
                "message": f"Transaction with high-risk country: {transaction.merchant_country}",
            }
        return {"triggered": False}


class UnusualHourRule(FraudRule):
    def __init__(self):
        super().__init__("UNUSUAL_HOUR", 15, "LOW")

    def check(
        self, transaction: Transaction, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        hour = transaction.timestamp.hour
        user_avg_hour = context.get("user_avg_hour", 12)

        if hour < 6 or hour > 23:
            if user_avg_hour not in range(6, 23):
                return {
                    "triggered": True,
                    "rule": self.name,
                    "severity": self.severity,
                    "weight": self.weight,
                    "message": f"Transaction at unusual hour: {hour}:00",
                }
        return {"triggered": False}


class NewMerchantRule(FraudRule):
    def __init__(self):
        super().__init__("NEW_MERCHANT", 10, "LOW")

    def check(
        self, transaction: Transaction, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        user_merchants = context.get("user_known_merchants", set())
        if transaction.merchant not in user_merchants and len(user_merchants) > 0:
            first_tx = context.get("first_transaction_date")
            if first_tx:
                days_since_first = (timezone.now() - first_tx).days
                if days_since_first > 30:
                    return {
                        "triggered": True,
                        "rule": self.name,
                        "severity": self.severity,
                        "weight": self.weight,
                        "message": f"New merchant: {transaction.merchant}",
                    }
        return {"triggered": False}


class LargeAmountRule(FraudRule):
    def __init__(self):
        super().__init__("LARGE_AMOUNT", 20, "MEDIUM")

    def check(
        self, transaction: Transaction, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        if float(transaction.amount) > 10000:
            return {
                "triggered": True,
                "rule": self.name,
                "severity": self.severity,
                "weight": self.weight,
                "message": f"Large transaction amount: ${transaction.amount}",
            }
        return {"triggered": False}


class RuleEngine:
    def __init__(self):
        self.rules = [
            AmountSpikeRule(),
            RapidTransactionsRule(),
            LocationAnomalyRule(),
            HighRiskCountryRule(),
            UnusualHourRule(),
            NewMerchantRule(),
            LargeAmountRule(),
        ]

    def get_context(self, transaction: Transaction) -> Dict[str, Any]:
        now = timezone.now()
        five_min_ago = now - timedelta(minutes=5)
        thirty_days_ago = now - timedelta(days=30)

        user_transactions = Transaction.objects.filter(
            user=transaction.user, timestamp__gte=thirty_days_ago
        ).exclude(id=transaction.id)

        context = {}

        agg = user_transactions.aggregate(
            avg_amount=Avg("amount"), avg_hour=Avg("timestamp__hour"), count=Count("id")
        )
        context["user_avg_amount"] = float(agg["avg_amount"] or 0)
        context["user_avg_hour"] = agg["avg_hour"] or 12

        recent_count = user_transactions.filter(timestamp__gte=five_min_ago).count()
        context["transactions_last_5min"] = recent_count

        last_tx = user_transactions.order_by("-timestamp").first()
        context["last_transaction"] = last_tx

        first_tx = user_transactions.order_by("timestamp").first()
        context["first_transaction_date"] = first_tx.timestamp if first_tx else None

        merchants = set(user_transactions.values_list("merchant", flat=True))
        context["user_known_merchants"] = merchants

        return context

    def evaluate(self, transaction: Transaction) -> Dict[str, Any]:
        context = self.get_context(transaction)
        triggered_rules = []
        total_weight = 0
        max_severity = "LOW"

        for rule in self.rules:
            result = rule.check(transaction, context)
            if result.get("triggered"):
                triggered_rules.append(result)
                total_weight += result.get("weight", 0)
                severity_rank = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
                if severity_rank.get(result.get("severity"), 0) > severity_rank.get(
                    max_severity, 0
                ):
                    max_severity = result.get("severity")

        return {
            "transaction_id": str(transaction.id),
            "rules_triggered": triggered_rules,
            "rule_score": min(total_weight, 100),
            "max_severity": max_severity,
            "context": {
                "user_avg_amount": context.get("user_avg_amount"),
                "recent_count": context.get("transactions_last_5min"),
            },
        }


def evaluate_transaction(transaction: Transaction) -> Dict[str, Any]:
    engine = RuleEngine()
    return engine.evaluate(transaction)
