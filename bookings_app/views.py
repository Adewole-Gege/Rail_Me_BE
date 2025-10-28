from rest_framework import generics, permissions, status, serializers
from .models import Booking, TRAIN_DURATIONS
from .serializers import BookTrainSerializer, AvailableTrainSerializer
from admin_app.models import Train
from rest_framework.response import Response
from datetime import timedelta
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from django.utils.dateparse import parse_datetime

class BookTrainView(generics.CreateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookTrainSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response({"message": "Train booked successfully."}, status=status.HTTP_201_CREATED)

        except serializers.ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AvailableTrainsView(generics.ListAPIView):
    queryset = Train.objects.filter(seats_remaining__gt=0)
    serializer_class = AvailableTrainSerializer
    permission_classes = [permissions.IsAuthenticated]


class EditBookingTimeView(generics.UpdateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookTrainSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        booking = get_object_or_404(Booking, pk=kwargs['pk'], user=request.user)
        new_departure = request.data.get('departure_time')

        if not new_departure:
            return Response(
                {"error": "Please provide a new departure_time."},
                status=status.HTTP_400_BAD_REQUEST
            )

        new_departure_time = parse_datetime(new_departure)

        if not new_departure_time:
            return Response(
                {"error": "Invalid departure_time format. Use ISO format (e.g. 2025-10-25T09:00:00Z)."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if timezone.is_naive(new_departure_time):
            new_departure_time = timezone.make_aware(new_departure_time)

        if new_departure_time < timezone.now():
            return Response(
                {"error": "Departure time cannot be in the past."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Recalculate arrival time based on train route duration
        duration_hours = TRAIN_DURATIONS.get(booking.train.name, 6)
        booking.departure_time = new_departure_time
        booking.arrival_time = new_departure_time + timedelta(hours=duration_hours)
        booking.save()

        serializer = self.get_serializer(booking)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class CancelBookingView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, booking_id):
        try:
            booking = Booking.objects.get(id=booking_id, user=request.user)
        except Booking.DoesNotExist:
            return Response(
                {"error": "Booking not found or does not belong to you."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Restore the seats to the train
        train = booking.train
        train.seats_remaining += booking.seats_booked
        train.save()

        booking.delete()

        return Response(
            {"message": "Your booking has been successfully canceled."},
            status=status.HTTP_200_OK
        )
        

