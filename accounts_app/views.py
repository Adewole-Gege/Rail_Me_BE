from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import PassengerRegistrationSerializer, OTPRequestSerializer ,PassengerLoginSerializer, ForgotPasswordSerializer, ResetPasswordSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from .models import Passenger, OTP


# Create your views here.
class PassengerRegistrationView(APIView):
    def post(self, request): # handles POST requests to register a new passenger
        serializer = PassengerRegistrationSerializer(data=request.data) # passes the user's data into the registration serializer to check it
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Passenger registered successfully! OTP sent to email."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class SendOtpView(APIView):
    def post(self, request):
        serializer = OTPRequestSerializer(data=request.data)
        if serializer.is_valid():
            result = serializer.save()
            return Response(result, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
   
   
class VerifyOTPView(APIView):
    def post(self, request):
        target = request.data.get("target")
        code = request.data.get("otp")

        if not target or not code:
            return Response({"error": "Target and OTP code are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Find the OTP record
        otp_instance = OTP.objects.filter(target=target, code=code, is_used=False).last()

        if not otp_instance:
            return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)

        if timezone.now() > otp_instance.expires_at:
            return Response({"error": "OTP has expired."}, status=status.HTTP_400_BAD_REQUEST)

        # Get the user related to this target
        user = Passenger.objects.filter(email=target).first()
        if not user:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        
        if user.is_verified:
            return Response({"message": "User is already verified."}, status=status.HTTP_200_OK)

        # Mark the user as verified
        user.is_verified = True
        user.save()

        # Mark OTP as used
        otp_instance.is_used = True
        otp_instance.save()

        return Response({"message": "Account verified successfully."}, status=status.HTTP_200_OK)
    
    
class PassengerLoginView(APIView):
    def post(self, request):
        serializer = PassengerLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
 
class ForgotPasswordView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Password reset link sent to your email"}, status=status.HTTP_200_OK)
    
    
class ResetPasswordView(APIView):
    def post(self, request, uidb64, token, *args, **kwargs):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(uidb64=uidb64, token=token)
        return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)

