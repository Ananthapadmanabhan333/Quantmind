# QuantMind – AI-Powered Financial Intelligence & Risk Engine

## Project Overview
- **Project Name**: QuantMind
- **Type**: Production-Ready Fintech Platform
- **Core Functionality**: Real-time fraud detection, risk scoring, user behavior analysis, and transaction monitoring
- **Target Users**: Financial institutions, fraud analysts, risk managers, system administrators

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           FRONTEND (React + Tailwind)                    │
│                   Dashboard | Charts | Alerts | Real-time Feed          │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         DJANGO API GATEWAY                              │
│                Auth | Transactions | Users | Analytics                  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        ▼                           ▼                           ▼
┌───────────────┐         ┌─────────────────┐         ┌─────────────────┐
│  TRANSACTION  │         │  RISK ENGINE    │         │ DECISION ENGINE │
│    SERVICE    │         │  (FastAPI)      │         │  (FastAPI)      │
└───────────────┘         └─────────────────┘         └─────────────────┘
        │                           │                           │
        ▼                           ▼                           ▼
┌───────────────┐         ┌─────────────────┐         ┌─────────────────┐
│ ML SERVICE    │         │ ML SERVICE      │         │ ML SERVICE      │
│ (FastAPI)     │         │ (FastAPI)       │         │ (FastAPI)       │
└───────────────┘         └─────────────────┘         └─────────────────┘
        │                           │                           │
        └───────────────────────────┼───────────────────────────┘
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    PostgreSQL + Redis                                   │
│              Transactions | Users | Cache | Sessions                    │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

| Component | Technology |
|-----------|------------|
| API Gateway | Django 4.2 + Django REST Framework |
| ML Microservices | FastAPI + Uvicorn |
| Frontend | React 18 + Tailwind CSS + Recharts |
| Database | PostgreSQL 15 |
| Cache | Redis 7 |
| ML Models | scikit-learn, XGBoost, pandas, numpy |
| Auth | JWT (djangorestframework-simplejwt) |
| Container | Docker + Docker Compose |

---

## Data Models

### 1. User
```python
- id: UUID (primary key)
- email: string (unique)
- username: string (unique)
- password: hashed string
- role: enum (ADMIN, ANALYST)
- is_active: boolean
- created_at: datetime
- updated_at: datetime
```

### 2. Transaction
```python
- id: UUID (primary key)
- user_id: FK to User
- amount: decimal
- currency: string (default: USD)
- transaction_type: enum (DEBIT, CREDIT, TRANSFER)
- merchant: string
- merchant_category: string
- location: string
- latitude: float (optional)
- longitude: float (optional)
- timestamp: datetime
- status: enum (PENDING, COMPLETED, FLAGGED, BLOCKED)
- fraud_score: float (0-100)
- risk_level: enum (LOW, MEDIUM, HIGH, CRITICAL)
- metadata: JSON
- created_at: datetime
```

### 3. RiskProfile
```python
- id: UUID (primary key)
- user_id: FK to User (unique)
- overall_score: float (0-100)
- fraud_probability: float (0-1)
- last_transaction_count: integer
- last_24h_volume: decimal
- last_7d_volume: decimal
- segment: string (PREMIUM, REGULAR, SUSPICIOUS, HIGH_RISK)
- flags: JSON
- updated_at: datetime
```

### 4. Alert
```python
- id: UUID (primary key)
- transaction_id: FK to Transaction
- alert_type: enum (FRAUD_DETECTED, ANOMALY, HIGH_RISK, LOCATION_ANOMALY)
- severity: enum (LOW, MEDIUM, HIGH, CRITICAL)
- message: text
- is_resolved: boolean
- resolved_by: FK to User (optional)
- created_at: datetime
```

### 5. UserSegment
```python
- id: UUID (primary key)
- segment_name: string
- description: text
- cluster_id: integer
- avg_transaction_amount: decimal
- avg_transaction_frequency: float
- total_users: integer
- characteristics: JSON
- created_at: datetime
```

---

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/auth/login/ | User login, returns JWT |
| POST | /api/auth/register/ | User registration |
| POST | /api/auth/refresh/ | Refresh JWT token |
| GET | /api/auth/me/ | Get current user |

### Transactions
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/transactions/ | List transactions (paginated) |
| POST | /api/transactions/ | Create transaction |
| GET | /api/transactions/{id}/ | Get transaction detail |
| GET | /api/transactions/stats/ | Transaction statistics |
| GET | /api/transactions/feed/ | Real-time transaction feed |

### Users & Risk
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/users/ | List users |
| GET | /api/users/{id}/ | User detail |
| GET | /api/users/{id}/risk-profile/ | User risk profile |
| GET | /api/users/{id}/behavior/ | User behavior analysis |
| GET | /api/users/segments/ | User segments |

### Analytics & Dashboard
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/dashboard/stats/ | Dashboard statistics |
| GET | /api/dashboard/fraud-alerts/ | Active fraud alerts |
| GET | /api/dashboard/risks/ | Risk distribution |
| GET | /api/dashboard/charts/ | Chart data |

### ML Services (FastAPI)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /ml/fraud/predict | Predict fraud probability |
| POST | /ml/anomaly/detect | Detect anomalies |
| POST | /ml/segment/users | Segment users |
| POST | /ml/risk/score | Calculate risk score |
| POST | /ml/models/train | Train ML model |
| GET | /ml/models/status | Model status |

---

## Feature Specifications

### 1. Authentication System
- JWT-based authentication with access/refresh tokens
- Role-based access control (ADMIN, ANALYST)
- Token expiry: 15 minutes access, 7 days refresh
- Password hashing: bcrypt

### 2. Transaction Module
- CRUD operations on transactions
- Filtering by date range, status, user, amount
- Pagination with cursor-based navigation
- Real-time transaction feed via WebSocket

### 3. Fraud Detection Engine

#### Rule-Based Detection
- **Amount Spike**: Transaction > 3x user's average
- **Rapid Transactions**: > 5 transactions in 5 minutes
- **Location Anomaly**: > 500km from previous transaction in < 30 min
- **Unusual Merchant**: Transaction with new merchant category
- **High-Risk Country**: Cross-border to high-risk countries
- **Time Anomaly**: Transaction at unusual hour for user

#### ML-Based Detection
- **Isolation Forest**: Anomaly detection on transaction features
- **XGBoost Classifier**: Binary fraud classification
- **Features**: amount, time_of_day, day_of_week, velocity, location_delta, merchant_risk

### 4. Risk Scoring System (0-100)
```
Risk Score = (
  fraud_probability * 40 +
  rule_violations * 20 +
  behavioral_anomaly * 20 +
  historical_fraud * 20
)
```

### 5. User Analytics
- Spending behavior patterns
- Transaction frequency analysis
- Category distribution
- K-Means clustering for segmentation

### 6. Decision Engine
- Auto-flag transactions with risk score > 70
- Auto-block transactions with risk score > 90
- Mark high-risk users (score > 80)
- Trigger alerts for critical events

### 7. Dashboard (React)
- Dark theme with modern fintech aesthetic
- Real-time transaction feed (WebSocket)
- Fraud alerts panel with severity indicators
- Risk score distribution charts (bar, pie)
- User segmentation visualization
- Transaction volume heatmap
- Key metrics: total volume, fraud rate, alert count

---

## UI Components

### Layout
- Fixed sidebar navigation (280px)
- Top header with user menu
- Main content area with responsive grid

### Pages
1. **Dashboard**: Stats cards, charts, recent transactions
2. **Transactions**: Filterable table with details modal
3. **Users**: User list with risk scores
4. **Alerts**: Alert list with resolution actions
5. **Analytics**: Charts and segmentation
6. **Settings**: System configuration

### Color Palette
- Background: #0F172A (slate-900)
- Surface: #1E293B (slate-800)
- Primary: #3B82F6 (blue-500)
- Success: #10B981 (emerald-500)
- Warning: #F59E0B (amber-500)
- Danger: #EF4444 (red-500)
- Text: #F8FAFC (slate-50)
- Muted: #94A3B8 (slate-400)

---

## Security Requirements
- CORS configured for frontend origin
- Rate limiting on auth endpoints
- Input validation and sanitization
- SQL injection prevention (Django ORM)
- XSS prevention (React escaping)
- HTTPS in production

---

## Acceptance Criteria
1. ✅ User can register and login with JWT
2. ✅ Admin can create/view transactions
3. ✅ System detects fraud using rules + ML
4. ✅ Risk scores calculated and displayed
5. ✅ Users segmented via clustering
6. ✅ Dashboard shows real-time data
7. ✅ Alerts triggered for high-risk events
8. ✅ All endpoints return proper errors
9. ✅ Docker containers run successfully
10. ✅ Frontend builds without errors

---

## Folder Structure
```
quantmind/
├── backend/
│   ├── django_project/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   ├── api/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   ├── auth/
│   ├── transactions/
│   ├── users/
│   ├── dashboard/
│   └── manage.py
├── ml_service/
│   ├── main.py
│   ├── models/
│   ├── routers/
│   └── utils/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── services/
│   │   └── App.tsx
│   └── package.json
├── docker-compose.yml
├── Dockerfile.backend
├── Dockerfile.ml
├── Dockerfile.frontend
└── README.md
```