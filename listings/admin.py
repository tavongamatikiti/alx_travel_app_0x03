"""
Admin configuration for the listings app models.
"""
from django.contrib import admin
from .models import Listing, Booking, Review


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    """Admin interface for Listing model."""
    list_display = [
        'listing_id',
        'title',
        'host',
        'location',
        'price_per_night',
        'max_guests',
        'available_from',
        'available_to',
        'created_at'
    ]
    list_filter = ['location', 'created_at', 'price_per_night']
    search_fields = ['title', 'description', 'location', 'host__username']
    readonly_fields = ['listing_id', 'created_at', 'updated_at']
    ordering = ['-created_at']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """Admin interface for Booking model."""
    list_display = [
        'booking_id',
        'listing',
        'user',
        'check_in_date',
        'check_out_date',
        'number_of_guests',
        'total_price',
        'status',
        'created_at'
    ]
    list_filter = ['status', 'created_at', 'check_in_date']
    search_fields = ['listing__title', 'user__username']
    readonly_fields = ['booking_id', 'created_at', 'updated_at']
    ordering = ['-created_at']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Admin interface for Review model."""
    list_display = [
        'review_id',
        'listing',
        'user',
        'rating',
        'created_at'
    ]
    list_filter = ['rating', 'created_at']
    search_fields = ['listing__title', 'user__username', 'comment']
    readonly_fields = ['review_id', 'created_at', 'updated_at']
    ordering = ['-created_at']
