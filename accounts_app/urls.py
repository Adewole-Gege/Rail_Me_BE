from django.urls import path
from .views import PassengerRegistrationView, VerifyOTPView, PassengerLoginView, ForgotPasswordView, ResetPasswordView, SendOtpView

urlpatterns = [
    path('register/', PassengerRegistrationView.as_view(), name='passenger-register'),
    path('send-otp/', SendOtpView.as_view(), name='send-otp'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('login/', PassengerLoginView.as_view(), name='passenger-login'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/<str:uidb64>/<str:token>/', ResetPasswordView.as_view(), name='reset-password'), #uidb64 are for user id encoded in base64, token is the JWT token
]