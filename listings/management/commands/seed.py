"""
Management command to seed the database with sample listing data.
Run with: python manage.py seed
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from listings.models import Listing, Booking, Review
from datetime import datetime, timedelta
from decimal import Decimal
import random


class Command(BaseCommand):
    help = 'Seeds the database with sample listing, booking, and review data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding database...')

        # Clear existing data
        self.stdout.write('Clearing existing data...')
        Review.objects.all().delete()
        Booking.objects.all().delete()
        Listing.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

        # Create sample users
        self.stdout.write('Creating users...')
        users = []
        for i in range(5):
            user = User.objects.create_user(
                username=f'user{i+1}',
                email=f'user{i+1}@example.com',
                password='password123',
                first_name=f'FirstName{i+1}',
                last_name=f'LastName{i+1}'
            )
            users.append(user)

        # Create sample listings
        self.stdout.write('Creating listings...')
        locations = [
            'New York, USA',
            'Paris, France',
            'Tokyo, Japan',
            'London, UK',
            'Sydney, Australia',
            'Barcelona, Spain',
            'Dubai, UAE',
            'Amsterdam, Netherlands'
        ]

        property_types = [
            'Cozy Studio Apartment',
            'Luxury Penthouse',
            'Beachfront Villa',
            'Mountain Cabin',
            'City Center Loft',
            'Historic Cottage',
            'Modern Condo',
            'Spacious Family Home'
        ]

        listings = []
        for i in range(20):
            listing = Listing.objects.create(
                host=random.choice(users),
                title=f"{random.choice(property_types)} in {random.choice(locations).split(',')[0]}",
                description=f"Beautiful property with amazing amenities. Perfect for your next vacation. Property {i+1} offers comfort and style.",
                location=random.choice(locations),
                price_per_night=Decimal(random.randint(50, 500)),
                max_guests=random.randint(1, 8),
                available_from=datetime.now().date(),
                available_to=datetime.now().date() + timedelta(days=365)
            )
            listings.append(listing)

        self.stdout.write(self.style.SUCCESS(f'Created {len(listings)} listings'))

        # Create sample bookings
        self.stdout.write('Creating bookings...')
        statuses = ['pending', 'confirmed', 'cancelled', 'completed']
        bookings_count = 0

        for _ in range(30):
            listing = random.choice(listings)
            user = random.choice([u for u in users if u != listing.host])

            check_in = datetime.now().date() + timedelta(days=random.randint(1, 90))
            check_out = check_in + timedelta(days=random.randint(1, 14))
            num_guests = random.randint(1, listing.max_guests)
            nights = (check_out - check_in).days
            total = listing.price_per_night * nights

            Booking.objects.create(
                listing=listing,
                user=user,
                check_in_date=check_in,
                check_out_date=check_out,
                number_of_guests=num_guests,
                total_price=total,
                status=random.choice(statuses)
            )
            bookings_count += 1

        self.stdout.write(self.style.SUCCESS(f'Created {bookings_count} bookings'))

        # Create sample reviews
        self.stdout.write('Creating reviews...')
        reviews_count = 0

        completed_bookings = Booking.objects.filter(status='completed')[:15]
        for booking in completed_bookings:
            try:
                Review.objects.create(
                    listing=booking.listing,
                    user=booking.user,
                    rating=random.randint(3, 5),
                    comment=f"Great stay at {booking.listing.title}! Would definitely recommend."
                )
                reviews_count += 1
            except:
                # Skip if review already exists for this user-listing combo
                pass

        self.stdout.write(self.style.SUCCESS(f'Created {reviews_count} reviews'))
        self.stdout.write(self.style.SUCCESS('Database seeding completed successfully!'))