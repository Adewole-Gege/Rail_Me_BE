from django.urls import path
from .views import (AdminRegistrationView, SendOtpView, VerifyOTPView, AdminLoginView, 
                    ForgotPasswordView, ResetPasswordView, TrainCreateView, TrainListView, TrainDeleteView,
                    CommuterListView)

urlpatterns = [
    path('register/', AdminRegistrationView.as_view(), name='admin-register'),
    path('send-otp/', SendOtpView.as_view(), name='send-otp'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('login/', AdminLoginView.as_view(), name='admin-login'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/<str:uidb64>/<str:token>/', ResetPasswordView.as_view(), name='reset-password'),
    path('create-train/', TrainCreateView.as_view(), name='create-train'),
    path('trains/', TrainListView.as_view(), name='train-list'),
    path('delete-train/<int:pk>/', TrainDeleteView.as_view(), name='delete-train'),
    path('commuters-list/', CommuterListView.as_view(), name='commuter-list'),
]
