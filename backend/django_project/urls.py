from django.urls import path, include

urlpatterns = [
    path("api/auth/", include("auth_system.urls")),
    path("api/transactions/", include("transactions.urls")),
    path("api/users/", include("users.urls")),
    path("api/dashboard/", include("dashboard.urls")),
    path("api/", include("notifications.urls")),
    path("api/", include("api.urls")),
]
