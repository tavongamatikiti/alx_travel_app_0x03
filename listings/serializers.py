"""
Serializers for the travel booking application.
Handles serialization of Listing and Booking models for API responses.
"""

from rest_framework import serializers
from .models import Listing, Booking, Review
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class ListingSerializer(serializers.ModelSerializer):
    """
    Serializer for the Listing model.
    Includes host information and validation for dates.
    """
    host = UserSerializer(read_only=True)
    host_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='host',
        write_only=True
    )

    class Meta:
        model = Listing
        fields = [
            'listing_id',
            'host',
            'host_id',
            'title',
            'description',
            'location',
            'price_per_night',
            'max_guests',
            'available_from',
            'available_to',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['listing_id', 'created_at', 'updated_at']

    def validate(self, data):
        """
        Validate that available_to is after available_from.
        """
        if 'available_from' in data and 'available_to' in data:
            if data['available_to'] <= data['available_from']:
                raise serializers.ValidationError(
                    "available_to must be after available_from"
                )
        return data


class BookingSerializer(serializers.ModelSerializer):
    """
    Serializer for the Booking model.
    Includes nested listing and user information with validation.
    """
    listing = ListingSerializer(read_only=True)
    listing_id = serializers.PrimaryKeyRelatedField(
        queryset=Listing.objects.all(),
        source='listing',
        write_only=True
    )
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='user',
        write_only=True
    )

    class Meta:
        model = Booking
        fields = [
            'booking_id',
            'listing',
            'listing_id',
            'user',
            'user_id',
            'check_in_date',
            'check_out_date',
            'number_of_guests',
            'total_price',
            'status',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['booking_id', 'created_at', 'updated_at']

    def validate(self, data):
        """
        Validate booking dates and guest count.
        """
        # Validate check_out is after check_in
        if 'check_in_date' in data and 'check_out_date' in data:
            if data['check_out_date'] <= data['check_in_date']:
                raise serializers.ValidationError(
                    "check_out_date must be after check_in_date"
                )

        # Validate number of guests doesn't exceed listing capacity
        if 'number_of_guests' in data and 'listing' in data:
            listing = data['listing']
            if data['number_of_guests'] > listing.max_guests:
                raise serializers.ValidationError(
                    f"Number of guests cannot exceed {listing.max_guests}"
                )

        return data


class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for the Review model.
    """
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='user',
        write_only=True
    )
    listing_id = serializers.PrimaryKeyRelatedField(
        queryset=Listing.objects.all(),
        source='listing',
        write_only=True
    )

    class Meta:
        model = Review
        fields = [
            'review_id',
            'listing_id',
            'user',
            'user_id',
            'rating',
            'comment',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['review_id', 'created_at', 'updated_at']