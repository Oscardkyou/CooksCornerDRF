from django.urls import path

from users.views import (
    SignupAPIView,
    VerifyEmailAPIView,
    LoginAPIView,
    TokenRefreshView,
    LogoutAPIView,
    DeleteUserAPIView,
    SendVerifyEmailAPIView,
    ChangePasswordAPIView,
    ForgotPasswordAPIView,
    ForgotPasswordChangeAPIView,
)

urlpatterns = [
    path("login/", LoginAPIView.as_view(), name="cookscorner-login"),
    path(
        "login/refresh/", TokenRefreshView.as_view(), name="cookscorner-login-refresh"
    ),
    path("signup/", SignupAPIView.as_view(), name="cookscorner-signup"),
    path("logout/", LogoutAPIView.as_view(), name="cookscorner-logout"),
    path(
        "email-verify/", VerifyEmailAPIView.as_view(), name="cookscorner-email-verify"
    ),
    path(
        "resend-email/",
        SendVerifyEmailAPIView.as_view(),
        name="cookscorner-resend-email",
    ),
    path("delete-user/", DeleteUserAPIView.as_view(), name="cookscorner-delete"),
    path(
        "change-password/",
        ChangePasswordAPIView.as_view(),
        name="cookscorner-change-password",
    ),
    path(
        "forgot-password/",
        ForgotPasswordAPIView.as_view(),
        name="cookscorner-forgot-password",
    ),
    path(
        "forgot-password/change/",
        ForgotPasswordChangeAPIView.as_view(),
        name="cookscorner-forgot-password-change",
    ),
]
