from rest_framework import serializers
from .models import Booking
from admin_app.models import Train
from django.utils import timezone
from datetime import timedelta


class BookTrainSerializer(serializers.ModelSerializer):
    train_name = serializers.ChoiceField(choices=[], write_only=True)
    departure_time = serializers.DateTimeField()
    seats_booked = serializers.IntegerField()

    class Meta:
        model = Booking
        fields = ['train_name', 'seats_booked', 'price', 'departure_time', 'arrival_time', 'booked_at']
        read_only_fields = ['price', 'arrival_time', 'booked_at']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Load train choices dynamically (after DB is ready)
        self.fields['train_name'].choices = [
            (t.name, t.name) for t in Train.objects.all()
        ]

    def validate(self, attrs):
        seats_booked = attrs.get('seats_booked', 0)
        if seats_booked <= 0:
            raise serializers.ValidationError("You must book at least one seat.")

        train_name = attrs.get('train_name')
        try:
            train = Train.objects.get(name=train_name)
        except Train.DoesNotExist:
            raise serializers.ValidationError({"train_name": f"Train '{train_name}' does not exist."})

        if train.seats_remaining <= 0:
            raise serializers.ValidationError("No seats available on this train.")

        if seats_booked > train.seats_remaining:
            raise serializers.ValidationError(
                f"Only {train.seats_remaining} seats are available on this train."
            )

        # Validate time
        departure_time = attrs.get('departure_time')
        if departure_time < timezone.now():
            raise serializers.ValidationError("Departure time cannot be in the past.")

        attrs['train'] = train
        return attrs
    

    def create(self, validated_data):
        user = self.context['request'].user
        train = validated_data['train']
        seats_booked = validated_data['seats_booked']
        departure_time = validated_data['departure_time']

        # Deduct booked seats
        train.seats_remaining -= seats_booked
        train.save()

        # Determine arrival time automatically based on train route
        route_durations = {
            'Rail-Me Express 001': 11,
            'Rail-Me Express 002': 9,
            'Rail-Me Express 003': 10,
            'Rail-Me Express 004': 11,
            'Rail-Me Express 005': 8,
            'Rail-Me Express 006': 11,
            'Rail-Me Express 007': 12,
            'Rail-Me Express 008': 11,
            'Rail-Me Express 009': 14,
            'Rail-Me Express 010': 11,
            'Rail-Me Express 020': 15,
            'Rail-Me Express 030': 12,
            'Rail-Me Express 040': 13,
            'Rail-Me Express 050': 15,
            'Rail-Me Express 060': 7,
            'Rail-Me Express 070': 8,
            'Rail-Me Express 080': 3,
            'Rail-Me Express 090': 8,
            'Rail-Me Express 101': 6,
            'Rail-Me Express 202': 9,
        }

        duration = route_durations.get(train.name, 10)  # default 10 hours
        arrival_time = departure_time + timedelta(hours=duration)

        # Save booking
        booking = Booking.objects.create(
            user=user,
            train=train,
            seats_booked=seats_booked,
            departure_time=departure_time,
            arrival_time=arrival_time,
            price=train.price
        )

        return booking


class AvailableTrainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Train
        fields = ['name','image',  'departure_station', 'destination', 'arrival_station', 'price', 'seats_remaining']

