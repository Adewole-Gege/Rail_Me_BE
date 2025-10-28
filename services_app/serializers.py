from rest_framework import serializers
from .models import Service
from decimal import Decimal

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['train', 'service_type', 'price', 'created_by', 'created_at']
        read_only_fields = ['price', 'created_by', 'created_at']
        
    def validate(self, data):
        train = data.get('train')
        service_type = data.get('service_type')

        # Check if that service already exists for this train
        if Service.objects.filter(train=train, service_type=service_type).exists():
            raise serializers.ValidationError({
                "detail": f"A {service_type} service already exists for this train."
            })

        return data
    
    def create(self, validated_data):
        train = validated_data['train']
        service_type = validated_data['service_type']
        admin = self.context['request'].user
        base_price = train.price

        # Assign price dynamically based on service type
        if service_type == 'reservation':
            price = base_price
        elif service_type == 'economy':
            price = base_price * Decimal('1.3')
        elif service_type == 'business':
            price = base_price * Decimal('1.8')
        else:
            raise serializers.ValidationError({
                "detail": "Invalid service type selected."
            })

        # Create just one service
        service = Service.objects.create(
            train=train,
            service_type=service_type,
            price=price,
            created_by=admin
        )
        return service
    
    
