import requests
from datetime import datetime
# from app.models.models import Booking, db
from config import Config

class HotelService:
    def __init__(self):
        self.booking_api_key = Config.BOOKING_COM_API_KEY
        self.booking_secret = Config.BOOKING_COM_SECRET
        self.mmt_api_key = Config.MAKEMYTRIP_API_KEY
        self.mmt_secret = Config.MAKEMYTRIP_SECRET
        
    def search_hotels(self, prompt):
        """
        Search hotels using multiple APIs (Booking.com and MakeMyTrip)
        Returns combined and deduplicated results
        """
        hotels = []
        
        # Extract search parameters from prompt
        search_params = self._extract_hotel_requirements(prompt)
        
        # Search using Booking.com API
        booking_results = self._search_booking_com(search_params)
        hotels.extend(booking_results)
        
        # Search using MakeMyTrip API
        mmt_results = self._search_makemytrip(search_params)
        hotels.extend(mmt_results)
        
        # Deduplicate and sort results
        return self._process_and_sort_results(hotels)
        
    def _extract_hotel_requirements(self, prompt):
        """
        Extract hotel search requirements from prompt using NLP
        """
        import spacy
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(prompt)
        
        # Extract location, dates, preferences
        # Implement more sophisticated NLP here
        params = {
            'location': '',
            'check_in': '',
            'check_out': '',
            'guests': 1,
            'rooms': 1,
            'min_rating': 0,
            'preferences': []
        }
        
        # Add your NLP logic here
        
        return params
        
    def _search_booking_com(self, params):
        """
        Search hotels using Booking.com API
        """
        try:
            headers = {
                'Authorization': f'Bearer {self.booking_api_key}',
                'Content-Type': 'application/json'
            }
            
            search_params = {
                'city_id': self._get_booking_city_id(params['location']),
                'checkin': params['check_in'],
                'checkout': params['check_out'],
                'adults_number': params['guests'],
                'room_number': params['rooms'],
                'filter': {
                    'min_review_score': params['min_rating'] * 2  # Booking.com uses 1-10 scale
                }
            }
            
            response = requests.post(
                'https://distribution-xml.booking.com/json/bookings',
                headers=headers,
                json=search_params
            )
            
            if response.status_code == 200:
                return self._process_booking_response(response.json())
            return []
            
        except Exception as e:
            print(f"Booking.com API error: {str(e)}")
            return []
            
    def _search_makemytrip(self, params):
        """
        Search hotels using MakeMyTrip API
        """
        try:
            headers = {
                'api-key': self.mmt_api_key,
                'Content-Type': 'application/json'
            }
            
            search_params = {
                'city': params['location'],
                'checkin': params['check_in'],
                'checkout': params['check_out'],
                'rooms': [{
                    'adults': params['guests']
                }],
                'filters': {
                    'rating': params['min_rating']
                }
            }
            
            response = requests.post(
                'https://api.makemytrip.com/hotels/search',
                headers=headers,
                json=search_params
            )
            
            if response.status_code == 200:
                return self._process_mmt_response(response.json())
            return []
            
        except Exception as e:
            print(f"MakeMyTrip API error: {str(e)}")
            return []
            
    def _process_booking_response(self, response_data):
        """Process Booking.com API response"""
        hotels = []
        for hotel in response_data.get('result', []):
            hotels.append({
                'source': 'booking.com',
                'hotel_id': hotel.get('hotel_id'),
                'name': hotel.get('hotel_name'),
                'rating': hotel.get('review_score') / 2,  # Convert to 5-star scale
                'price': {
                    'amount': hotel.get('min_total_price'),
                    'currency': hotel.get('currency')
                },
                'location': {
                    'address': hotel.get('address'),
                    'latitude': hotel.get('latitude'),
                    'longitude': hotel.get('longitude')
                },
                'amenities': hotel.get('facilities', []),
                'images': hotel.get('photos', []),
                'booking_url': self._generate_booking_url('booking', hotel.get('hotel_id')),
                'cancellation_policy': hotel.get('cancellation_policy')
            })
        return hotels
        
    def _process_mmt_response(self, response_data):
        """Process MakeMyTrip API response"""
        hotels = []
        for hotel in response_data.get('hotels', []):
            hotels.append({
                'source': 'makemytrip',
                'hotel_id': hotel.get('id'),
                'name': hotel.get('name'),
                'rating': hotel.get('rating'),
                'price': {
                    'amount': hotel.get('price', {}).get('amount'),
                    'currency': hotel.get('price', {}).get('currency')
                },
                'location': {
                    'address': hotel.get('address'),
                    'latitude': hotel.get('latitude'),
                    'longitude': hotel.get('longitude')
                },
                'amenities': hotel.get('amenities', []),
                'images': hotel.get('images', []),
                'booking_url': self._generate_booking_url('mmt', hotel.get('id')),
                'cancellation_policy': hotel.get('cancellationPolicy')
            })
        return hotels
        
    def _generate_booking_url(self, source, hotel_id):
        """Generate actual booking URL based on source"""
        if source == 'booking':
            return f"https://www.booking.com/hotel/detail.html?hotel_id={hotel_id}"
        elif source == 'mmt':
            return f"https://www.makemytrip.com/hotels/hotel-details/?hotelId={hotel_id}"
        return None
        
    def _process_and_sort_results(self, hotels):
        """
        Process and sort hotel results
        - Remove duplicates
        - Sort by price or rating
        - Apply any additional filters
        """
        # Remove duplicates based on hotel name and location
        seen = set()
        unique_hotels = []
        for hotel in hotels:
            key = f"{hotel['name']}_{hotel['location']['latitude']}_{hotel['location']['longitude']}"
            if key not in seen:
                seen.add(key)
                unique_hotels.append(hotel)
        
        # Sort by price (you can modify sorting criteria)
        return sorted(unique_hotels, key=lambda x: x['price']['amount'])
        
    def initiate_booking(self, source, hotel_id, booking_details):
        """
        Initiate actual hotel booking
        Returns booking URL with selected options
        """
        try:
            if source == 'booking':
                return self._initiate_booking_com_booking(hotel_id, booking_details)
            elif source == 'mmt':
                return self._initiate_mmt_booking(hotel_id, booking_details)
            return None
            
        except Exception as e:
            print(f"Error initiating booking: {str(e)}")
            return None
            
    def _initiate_booking_com_booking(self, hotel_id, booking_details):
        """Initiate booking on Booking.com"""
        headers = {
            'Authorization': f'Bearer {self.booking_api_key}',
            'Content-Type': 'application/json'
        }
        
        booking_data = {
            'hotel_id': hotel_id,
            'checkin': booking_details['check_in'],
            'checkout': booking_details['check_out'],
            'guests': booking_details['guests'],
            'rooms': booking_details['rooms']
        }
        
        response = requests.post(
            'https://distribution-xml.booking.com/json/bookings',
            headers=headers,
            json=booking_data
        )
        
        if response.status_code == 200:
            booking_response = response.json()
            # Save booking reference
            # booking = Booking(
            #     user_id=booking_details['user_id'],
            #     booking_type='hotel',
            #     status='initiated',
            #     booking_details={
            #         'hotel_id': hotel_id,
            #         'source': 'booking.com',
            #         'booking_reference': booking_response.get('booking_reference'),
            #         'amount': booking_response.get('total_amount')
            #     }
            # )
            # db.session.add(booking)
            # db.session.commit()
            
            return {
                'booking_id': 'booking.id',
                'payment_url': booking_response.get('payment_url'),
                'booking_reference': booking_response.get('booking_reference')
            }
            
        return None
        
    def _initiate_mmt_booking(self, hotel_id, booking_details):
        """Initiate booking on MakeMyTrip"""
        # Similar implementation as Booking.com
        # Implement MakeMyTrip specific booking logic
        pass