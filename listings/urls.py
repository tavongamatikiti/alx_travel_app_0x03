"""
URL configuration for listings app.
Uses DRF Router to automatically generate RESTful routes for ViewSets.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'listings'

# Create a router and register viewsets
router = DefaultRouter()
router.register(r'listings', views.ListingViewSet, basename='listing')
router.register(r'bookings', views.BookingViewSet, basename='booking')
router.register(r'reviews', views.ReviewViewSet, basename='review')

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),

    # Payment endpoints
    path('payments/initiate/', views.initiate_payment, name='initiate-payment'),
    path('payments/verify/', views.verify_payment, name='verify-payment'),
]
