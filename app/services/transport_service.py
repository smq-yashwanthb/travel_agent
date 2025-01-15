import requests
import json
from datetime import datetime
from app.models import Booking
from config import Config

class TransportService:
    def __init__(self):
        self.redbus_api_key = Config.REDBUS_API_KEY
        self.redbus_api_secret = Config.REDBUS_API_SECRET
        self.base_url = "https://api.redbus.in/v2"
        
    def search_transport(self, prompt):
        """
        Search for available transportation options using RedBus API
        """
        try:
            # Extract travel details from prompt
            travel_details = self._extract_travel_details(prompt)
            
            # Search buses using RedBus API
            headers = {
                'apiKey': self.redbus_api_key,
                'Content-Type': 'application/json'
            }
            
            search_params = {
                'source': travel_details['source'],
                'destination': travel_details['destination'],
                'doj': travel_details['date'],  # Date of journey
                'srcId': self._get_city_id(travel_details['source']),
                'destId': self._get_city_id(travel_details['destination'])
            }
            
            response = requests.post(
                f"{self.base_url}/search",
                headers=headers,
                json=search_params
            )
            
            if response.status_code == 200:
                return self._process_bus_response(response.json())
            else:
                raise Exception(f"RedBus API error: {response.status_code}")
                
        except Exception as e:
            print(f"Error searching buses: {str(e)}")
            return []
            
    def _extract_travel_details(self, prompt):
        """
        Extract travel details from user prompt using NLP
        Implement more sophisticated NLP here
        """
        # Basic implementation - enhance with proper NLP
        import spacy
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(prompt)
        
        # Extract locations, dates, and preferences
        # This is a simplified version - implement more robust extraction
        details = {
            'source': '',
            'destination': '',
            'date': '',
            'preferences': []
        }
        
        # Add your NLP logic here
        
        return details
            
    def _process_bus_response(self, response_data):
        """Process and format bus search results"""
        buses = []
        for bus in response_data.get('inventories', []):
            buses.append({
                'bus_id': bus.get('id'),
                'operator_name': bus.get('travelsName'),
                'bus_type': bus.get('busType'),
                'departure_time': bus.get('departureTime'),
                'arrival_time': bus.get('arrivalTime'),
                'available_seats': bus.get('availableSeats'),
                'fare': bus.get('fare'),
                'boarding_points': bus.get('boardingPoints'),
                'dropping_points': bus.get('droppingPoints'),
                'amenities': bus.get('amenities'),
                'rating': bus.get('rating'),
                'booking_url': self._generate_booking_url(bus.get('id')),
                'cancellation_policy': bus.get('cancellationPolicy')
            })
        return buses
        
    def _generate_booking_url(self, bus_id):
        """Generate actual RedBus booking URL"""
        # This will be a deep link to RedBus booking page
        return f"https://www.redbus.in/booking/select-seat/{bus_id}"
        
    def _get_city_id(self, city_name):
        """Get city ID from RedBus API"""
        try:
            headers = {
                'apiKey': self.redbus_api_key,
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                f"{self.base_url}/cities",
                headers=headers,
                params={'search': city_name}
            )
            
            if response.status_code == 200:
                cities = response.json()
                # Return the first matching city ID
                return cities[0]['id'] if cities else None
            return None
            
        except Exception as e:
            print(f"Error getting city ID: {str(e)}")
            return None
            
    def get_seat_layout(self, bus_id):
        """Get bus seat layout for selection"""
        try:
            headers = {
                'apiKey': self.redbus_api_key,
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                f"{self.base_url}/layout/{bus_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                return response.json()
            return None
            
        except Exception as e:
            print(f"Error getting seat layout: {str(e)}")
            return None
            
    def initiate_booking(self, bus_id, seat_numbers, passenger_details):
        """
        Initiate actual booking on RedBus
        Returns booking URL with selected seats
        """
        try:
            # Create booking session on RedBus
            headers = {
                'apiKey': self.redbus_api_key,
                'Content-Type': 'application/json'
            }
            
            booking_data = {
                'inventoryId': bus_id,
                'seatNumbers': seat_numbers,
                'passengers': passenger_details
            }
            
            response = requests.post(
                f"{self.base_url}/booking/initiate",
                headers=headers,
                json=booking_data
            )
            
            if response.status_code == 200:
                booking_response = response.json()
                # Save booking reference
                booking = Booking(
                    user_id=passenger_details['user_id'],
                    booking_type='bus',
                    status='initiated',
                    booking_details={
                        'bus_id': bus_id,
                        'seats': seat_numbers,
                        'booking_reference': booking_response.get('bookingReference'),
                        'amount': booking_response.get('totalAmount')
                    }
                )
                db.session.add(booking)
                db.session.commit()
                
                # Return RedBus payment URL
                return {
                    'booking_id': booking.id,
                    'payment_url': booking_response.get('paymentUrl'),
                    'booking_reference': booking_response.get('bookingReference')
                }
                
            return None
            
        except Exception as e:
            print(f"Error initiating booking: {str(e)}")
            return None
            
    def check_booking_status(self, booking_reference):
        """Check status of a booking"""
        try:
            headers = {
                'apiKey': self.redbus_api_key,
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                f"{self.base_url}/booking/status/{booking_reference}",
                headers=headers
            )
            
            if response.status_code == 200:
                status_data = response.json()
                # Update booking status in database
                booking = Booking.query.filter_by(
                    booking_details__booking_reference=booking_reference
                ).first()
                
                if booking:
                    booking.status = status_data.get('status')
                    booking.booking_details.update({
                        'ticket_number': status_data.get('ticketNumber'),
                        'pnr': status_data.get('pnr')
                    })
                    db.session.commit()
                
                return status_data
                
            return None
            
        except Exception as e:
            print(f"Error checking booking status: {str(e)}")
            return None