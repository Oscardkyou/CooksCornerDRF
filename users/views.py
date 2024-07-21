import jwt
from decouple import config
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import Response, APIView
from rest_framework_simplejwt.views import TokenRefreshView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .serializers import SignupSerializer, ChangePasswordSerializer
from .models import User, ConfirmationCode
from .users_services import (
    create_token_and_send_to_email,
    get_user_by_token,
    get_tokens_for_user,
    destroy_token,
)
from .swagger import (
    signup_swagger,
    login_swagger,
    resend_swagger,
    logout_swagger,
    forgot_password_swagger,
    forgot_password_change_swagger,
)

from userprofile.models import UserProfile


def handle_user_verification(user, token):
    if user.is_verified:
        raise ValidationError("User is already verified.")
    user_code = ConfirmationCode.objects.get(user=user)
    if token != user_code.code:
        raise ValidationError("Invalid or expired activation token.")
    user.is_verified = True
    user.save()


def create_user_profile(user, username):
    try:
        UserProfile.objects.create(user=user, username=username)
    except Exception as e:
        user.delete()
        raise ValidationError("Invalid username or profile could not be created.")


class SignupAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = SignupSerializer

    @swagger_auto_schema(
        tags=["Registration"],
        operation_description="Register a new user and send a verification email.",
        request_body=signup_swagger["request_body"],
        responses={
            201: signup_swagger["response"],
            400: "Invalid data.",
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        try:
            create_user_profile(user, request.data.get("username"))
        except ValidationError as e:
            return Response({"Message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        create_token_and_send_to_email(
            user=user, query="verify-account", url=config("EMAIL_LINK")
        )
        tokens = get_tokens_for_user(user)
        return Response(tokens, status=status.HTTP_201_CREATED)


class VerifyEmailAPIView(APIView):
    @swagger_auto_schema(
        tags=["Registration"],
        operation_description="Verify user's email using the token sent to their email.",
        manual_parameters=[
            openapi.Parameter(
                "Token",
                in_=openapi.IN_QUERY,
                description="Unique token for email verification.",
                type=openapi.TYPE_STRING,
            )
        ],
        responses={
            200: "Successfully verified.",
            400: "Invalid token.",
        },
    )
    def get(self, request):
        token = request.GET.get("token")
        try:
            user = get_user_by_token(token)
            handle_user_verification(user, token)
        except jwt.exceptions.DecodeError:
            return Response(
                {"Error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST
            )
        except ValidationError as e:
            return Response({"Error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {"Message": "User successfully verified"}, status=status.HTTP_200_OK
        )


class SendVerifyEmailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=["Registration"],
        operation_description="Resend the verification token to the user's email.",
        request_body=resend_swagger["request_body"],
        responses={
            200: "The verification email has been sent.",
            400: "User is already verified.",
        },
    )
    def post(self, request):
        user = request.user
        if user.is_verified:
            return Response(
                {"Message": "User is already verified."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        create_token_and_send_to_email(
            user=user, query="verify-account", url=config("EMAIL_LINK")
        )
        return Response(
            {"Message": "The verification email has been sent."},
            status=status.HTTP_200_OK,
        )


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        tags=["Authorization"],
        operation_description="Authenticate user and provide them with access and refresh tokens.",
        request_body=login_swagger["request_body"],
        responses={
            200: login_swagger["response"],
            404: "User not found.",
            400: "Incorrect password.",
        },
    )
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        password = request.data.get("password")
        user = User.objects.filter(email=email).first()
        if not user:
            return Response(
                {"Error": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )
        if not user.check_password(password):
            return Response(
                {"Error": "Incorrect password."}, status=status.HTTP_400_BAD_REQUEST
            )
        tokens = get_tokens_for_user(user)
        return Response(tokens, status=status.HTTP_200_OK)


class TokenRefreshView(TokenRefreshView):
    @swagger_auto_schema(
        tags=["Authorization"],
        operation_description="Refresh the access token using the refresh token.",
    )
    def post(self, *args, **kwargs):
        return super().post(*args, **kwargs)


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=["Authorization"],
        operation_description="Log out user by invalidating their refresh token.",
        request_body=logout_swagger["request_body"],
        responses={
            200: "Successfully logged out.",
            400: "Invalid token.",
        },
    )
    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get("refresh")
        try:
            destroy_token(refresh_token)
            return Response(
                {"Message": "Successfully logged out."}, status=status.HTTP_200_OK
            )
        except Exception:
            return Response(
                {"Error": "Unable to log out."}, status=status.HTTP_400_BAD_REQUEST
            )


class DeleteUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=["Authorization"],
        operation_description="Delete the user's account.",
        request_body=logout_swagger["request_body"],
        responses={
            200: "User successfully deleted.",
            400: "Invalid token.",
        },
    )
    def delete(self, request, *args, **kwargs):
        user = request.user
        try:
            destroy_token(request.data.get("refresh"))
        except Exception:
            return Response(
                {"Error": "Can't delete the user."}, status=status.HTTP_400_BAD_REQUEST
            )
        user.delete()
        return Response(
            {"Message": "User has been successfully deleted."},
            status=status.HTTP_200_OK,
        )


class ForgotPasswordAPIView(APIView):
    @swagger_auto_schema(
        tags=["Authorization"],
        operation_description="Send a token to user's email to allow them to reset their password.",
        request_body=forgot_password_swagger["request_body"],
        responses={
            200: "Verification email sent.",
            400: "Invalid data.",
        },
    )
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        try:
            user = User.objects.get(email=email)
            create_token_and_send_to_email(
                user=user, query="change-password", url=config("EMAIL_LINK_PASSWORD")
            )
            return Response(
                {"Message": "Verification email sent."}, status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {"Error": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )


class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=["Authorization"],
        operation_description="Allow authenticated user to change their password.",
        request_body=ChangePasswordSerializer,
        responses={
            200: "Password successfully changed.",
            400: "Invalid data.",
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(
            data=request.data, context={"user": request.user}
        )
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.set_password(serializer.validated_data["new_password"])
        user.save()
        return Response(
            {"Message": "Password successfully changed."}, status=status.HTTP_200_OK
        )


class ForgotPasswordChangeAPIView(APIView):
    @swagger_auto_schema(
        tags=["Authorization"],
        operation_description="Allow user to change their password using the reset token.",
        manual_parameters=forgot_password_change_swagger["parameters"],
        request_body=forgot_password_change_swagger["request_body"],
        responses={
            200: "Password successfully changed.",
            400: "Invalid data.",
        },
    )
    def post(self, request, *args, **kwargs):
        token = request.GET.get("token")
        try:
            user = get_user_by_token(token)
            new_password = request.data.get("password")
            confirm_password = request.data.get("password_confirm")
            if new_password != confirm_password:
                raise ValidationError("Passwords do not match.")
            validate_password(new_password, user=user)
            user.set_password(new_password)
            user.save()
            return Response(
                {"Message": "Password successfully changed."}, status=status.HTTP_200_OK
            )
        except jwt.DecodeError:
            return Response(
                {"Error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST
            )
        except ValidationError as e:
            return Response({"Error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
