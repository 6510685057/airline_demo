from django.test import TestCase, Client
from django.urls import reverse
from django.db.models import Max
from .models import Airport, Flight, Passenger


class FlightViewTestCase(TestCase):

    def setUp(self):
        # create airports
        airport1 = Airport.objects.create(code="AAA", city="City A")
        airport2 = Airport.objects.create(code="BBB", city="City B")

        flight = Flight.objects.create(
            origin=airport1, destination=airport2, duration=400)
        passenger = Passenger.objects.create(
            first="harry", last="potter")
        flight.passengers.add(passenger)

    def test_index_view_status_code(self):
        """ index view's status code is ok """

        c = Client()
        response = c.get(reverse('flights:index'))
        self.assertEqual(response.status_code, 200)

    def test_index_view_context(self):
        """ context is correctly set """

        c = Client()
        response = c.get(reverse('flights:index'))
        self.assertEqual(
            response.context['flights'].count(), 1)

    def test_valid_flight_page(self):
        """ valid flight page should return status code 200 """

        c = Client()
        f = Flight.objects.first()
        response = c.get(reverse('flights:flight', args=(f.id,)))
        self.assertEqual(response.status_code, 200)

    def test_invalid_flight_page(self):
        """ invalid flight page should return status code 404 """

        max_id = Flight.objects.all().aggregate(Max("id"))['id__max']

        c = Client()
        response = c.get(reverse('flights:flight', args=(max_id+1,)))
        self.assertEqual(response.status_code, 404)

    def test_cannot_book_nonavailable_seat_flight(self):
        """ cannot book full capacity flight"""

        passenger = Passenger.objects.create(
            first="hemione", last="granger")
        f = Flight.objects.first()
        #f.capacity = 1
        f.save()

        c = Client()
        c.post(reverse('flights:book', args=(f.id,)),
               {'passenger': passenger.id})
        self.assertEqual(f.passengers.count(), 1)
