import random
import string
from datetime import datetime, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

User = get_user_model()


class DataSeeder:
    MERCHANTS = [
        ("Amazon", "Shopping", "US"),
        ("Walmart", "Shopping", "US"),
        ("Target", "Shopping", "US"),
        ("Apple Store", "Electronics", "US"),
        ("Best Buy", "Electronics", "US"),
        ("Netflix", "Entertainment", "US"),
        ("Spotify", "Entertainment", "SE"),
        ("Uber", "Transport", "US"),
        ("Lyft", "Transport", "US"),
        ("Starbucks", "Food & Drink", "US"),
        ("McDonalds", "Food & Drink", "US"),
        ("Whole Foods", "Grocery", "US"),
        ("Shell", "Fuel", "US"),
        ("Chevron", "Fuel", "US"),
        ("PayPal", "Financial", "US"),
        ("Venmo", "Financial", "US"),
        ("Steam", "Gaming", "US"),
        ("PlayStation", "Gaming", "JP"),
        ("Nike", "Fashion", "US"),
        ("Adidas", "Fashion", "DE"),
    ]

    LOCATIONS = [
        ("New York, NY", 40.7128, -74.0060),
        ("Los Angeles, CA", 34.0522, -118.2437),
        ("Chicago, IL", 41.8781, -87.6298),
        ("Houston, TX", 29.7604, -95.3698),
        ("Phoenix, AZ", 33.4484, -112.0740),
        ("Philadelphia, PA", 39.9526, -75.1652),
        ("San Antonio, TX", 29.4241, -98.4936),
        ("San Diego, CA", 32.7157, -117.1611),
        ("Dallas, TX", 32.7767, -96.7970),
        ("San Jose, CA", 37.3382, -121.8863),
        ("London, UK", 51.5074, -0.1278),
        ("Paris, FR", 48.8566, 2.3522),
        ("Berlin, DE", 52.5200, 13.4050),
    ]

    HIGH_RISK_COUNTRIES = ["PK", "NG", "CM", "VN", "RU"]

    def __init__(self, num_users=50, transactions_per_user=20):
        self.num_users = num_users
        self.transactions_per_user = transactions_per_user

    @transaction.atomic
    def seed(self):
        print(f"Creating {self.num_users} users with transactions...")

        users = self._create_users()
        self._create_transactions(users)
        self._create_segments()

        print("Seeding completed successfully!")
        return len(users)

    def _create_users(self):
        users = []
        roles = ["VIEWER", "ANALYST", "ADMIN"]

        for i in range(self.num_users):
            email = f"user{i}@quantmind.demo"
            username = f"user_{i}"

            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "username": username,
                    "first_name": f"Demo",
                    "last_name": f"User {i}",
                    "role": random.choice(roles),
                    "is_active": True,
                },
            )
            user.set_password("demo123456")
            user.save()
            users.append(user)

        admin, _ = User.objects.get_or_create(
            email="admin@quantmind.demo",
            defaults={
                "username": "admin",
                "first_name": "Admin",
                "last_name": "User",
                "role": "ADMIN",
                "is_active": True,
            },
        )
        admin.set_password("admin123456")
        admin.save()
        users.append(admin)

        return users

    def _create_transactions(self, users):
        from transactions.models import (
            Transaction,
            TransactionType,
            RiskLevel,
            TransactionStatus,
        )

        total_created = 0
        batch_size = 5000
        transactions_to_create = []

        now = timezone.now()

        for user in users:
            # We dramatically increase scaling if user wants 1,000,000. 
            # We will generate up to self.transactions_per_user 
            num_transactions = random.randint(min(500, self.transactions_per_user), self.transactions_per_user)
            base_amount = random.uniform(50, 500)
            base_location = random.choice(self.LOCATIONS)

            for i in range(num_transactions):
                days_ago = random.randint(0, 365) # Expand window to 1 year
                hours_ago = random.randint(0, 23)
                minutes_ago = random.randint(0, 59)

                timestamp = now - timedelta(
                    days=days_ago, hours=hours_ago, minutes=minutes_ago
                )

                is_anomaly = random.random() < 0.1

                if is_anomaly:
                    amount = base_amount * random.uniform(4, 10)
                    merchant = random.choice(self.MERCHANTS)
                    location = random.choice(self.LOCATIONS)
                else:
                    amount = base_amount * random.uniform(0.5, 1.5)
                    merchant = random.choice(self.MERCHANTS[:10])
                    location = base_location

                tx_type = random.choice(
                    [
                        TransactionType.DEBIT,
                        TransactionType.CREDIT,
                        TransactionType.TRANSFER,
                    ]
                )

                status = random.choice(
                    [
                        TransactionStatus.COMPLETED,
                        TransactionStatus.COMPLETED,
                        TransactionStatus.COMPLETED,
                        TransactionStatus.PENDING,
                        TransactionStatus.FLAGGED
                        if random.random() < 0.1
                        else TransactionStatus.COMPLETED,
                        TransactionStatus.BLOCKED
                        if random.random() < 0.02
                        else TransactionStatus.COMPLETED,
                    ]
                )

                fraud_score = (
                    random.uniform(0, 100)
                    if status in [TransactionStatus.FLAGGED, TransactionStatus.BLOCKED]
                    else random.uniform(0, 40)
                )

                if fraud_score >= 80:
                    risk_level = RiskLevel.CRITICAL
                elif fraud_score >= 60:
                    risk_level = RiskLevel.HIGH
                elif fraud_score >= 40:
                    risk_level = RiskLevel.MEDIUM
                else:
                    risk_level = RiskLevel.LOW

                transactions_to_create.append(
                    Transaction(
                        user=user,
                        amount=Decimal(str(round(amount, 2))),
                        currency="USD",
                        transaction_type=tx_type,
                        merchant=merchant[0],
                        merchant_category=merchant[1],
                        merchant_country=merchant[2] if random.random() < 0.2 else "US",
                        location=location[0],
                        latitude=Decimal(str(location[1]))
                        if random.random() > 0.3
                        else None,
                        longitude=Decimal(str(location[2]))
                        if random.random() > 0.3
                        else None,
                        timestamp=timestamp,
                        status=status,
                        fraud_score=fraud_score,
                        risk_level=risk_level,
                        fraud_probability=fraud_score / 100,
                        is_anomaly=is_anomaly,
                    )
                )

                if len(transactions_to_create) >= batch_size:
                    Transaction.objects.bulk_create(transactions_to_create)
                    total_created += len(transactions_to_create)
                    print(f"Bulk inserted {total_created} transactions...")
                    transactions_to_create = []

        if transactions_to_create:
            Transaction.objects.bulk_create(transactions_to_create)
            total_created += len(transactions_to_create)

        print(f"Created {total_created} total transactions")
        return total_created

    def _create_segments(self):
        from users.models import UserSegment, RiskProfile

        segments = [
            {
                "name": "PREMIUM",
                "description": "High-value customers with consistent spending",
                "avg_amount": 500,
                "avg_frequency": 2.5,
            },
            {
                "name": "REGULAR",
                "description": "Standard users with normal spending patterns",
                "avg_amount": 150,
                "avg_frequency": 1.2,
            },
            {
                "name": "SUSPICIOUS",
                "description": "Users with unusual activity patterns",
                "avg_amount": 300,
                "avg_frequency": 5.0,
            },
            {
                "name": "HIGH_RISK",
                "description": "Users flagged for potential fraud",
                "avg_amount": 800,
                "avg_frequency": 8.0,
            },
            {
                "name": "NEW",
                "description": "Recently registered users",
                "avg_amount": 50,
                "avg_frequency": 0.5,
            },
        ]

        for idx, seg in enumerate(segments):
            UserSegment.objects.update_or_create(
                segment_name=seg["name"],
                defaults={
                    "description": seg["description"],
                    "cluster_id": idx,
                    "avg_transaction_amount": Decimal(str(seg["avg_amount"])),
                    "avg_transaction_frequency": seg["avg_frequency"],
                    "total_users": User.objects.filter(
                        risk_profile__segment=seg["name"]
                    ).count()
                    if User.objects.exists()
                    else 0,
                    "characteristics": {"description": seg["description"]},
                },
            )

        RiskProfile.objects.update_or_create(
            user=User.objects.filter(email="admin@quantmind.demo").first(),
            defaults={
                "overall_score": 25.0,
                "segment": "PREMIUM",
            },
        )

        print("Created user segments")


def run_seeder(num_users=50, transactions_per_user=20):
    seeder = DataSeeder(num_users, transactions_per_user)
    count = seeder.seed()
    return count


if __name__ == "__main__":
    import django
    import os
    import sys

    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_project.settings")
    django.setup()

    count = run_seeder(100, 10000)
    print(f"\nSuccessfully seeded {count} users with millions of data parameters!")
