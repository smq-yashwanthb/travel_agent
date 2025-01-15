from flask import Blueprint, render_template, request, jsonify
# from app.services.hotel_service import HotelService
# from app.services.transport_service import TransportService
# from app.models.models import db, Booking
from flask_login import login_required, current_user
import json

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

# @main.route('/process_prompt', methods=['POST'])
# @login_required
# def process_prompt():
#     data = request.json
#     prompt = data.get('prompt', '')
    
#     # Process the prompt to understand user requirements
#     requirements = analyze_prompt(prompt)
    
#     if requirements.get('type') == 'hotel':
#         return handle_hotel_search(requirements)
#     elif requirements.get('type') == 'transport':
#         return handle_transport_search(requirements)
#     else:
#         return jsonify({
#             'status': 'error',
#             'message': 'Please specify if you need hotel or transport booking'
#         })

# def analyze_prompt(prompt):
#     """
#     Analyze the user's prompt to extract requirements
#     Implement more sophisticated NLP here
#     """
#     prompt_lower = prompt.lower()
#     requirements = {
#         'type': 'transport' if any(word in prompt_lower for word in ['bus', 'train', 'transport']) else 'hotel',
#         'location': None,
#         'date': None,
#         'preferences': []
#     }
    
#     # Add more sophisticated NLP analysis here
    
#     return requirements

# @main.route('/search_hotels', methods=['POST'])
# @login_required
# def handle_hotel_search(requirements=None):
#     if not requirements:
#         requirements = request.json
    
#     hotel_service = HotelService()
#     hotels = hotel_service.search_hotels(requirements)
    
#     return jsonify({
#         'status': 'success',
#         'type': 'hotel',
#         'results': hotels
#     })

# @main.route('/search_transport', methods=['POST'])
# @login_required
# def handle_transport_search(requirements=None):
#     if not requirements:
#         requirements = request.json
    
#     transport_service = TransportService()
#     transport_options = transport_service.search_transport(requirements)
    
#     return jsonify({
#         'status': 'success',
#         'type': 'transport',
#         'results': transport_options
#     })

# @main.route('/initiate_booking', methods=['POST'])
# @login_required
# def initiate_booking():
#     data = request.json
#     booking_type = data.get('type')
    
#     try:
#         if booking_type == 'hotel':
#             hotel_service = HotelService()
#             booking_result = hotel_service.initiate_booking(
#                 source=data.get('source'),
#                 hotel_id=data.get('hotel_id'),
#                 booking_details={
#                     'user_id': current_user.id,
#                     'check_in': data.get('check_in'),
#                     'check_out': data.get('check_out'),
#                     'guests': data.get('guests'),
#                     'rooms': data.get('rooms')
#                 }
#             )
#         else:  # transport
#             transport_service = TransportService()
#             booking_result = transport_service.initiate_booking(
#                 bus_id=data.get('bus_id'),
#                 seat_numbers=data.get('seats'),
#                 passenger_details={
#                     'user_id': current_user.id,
#                     'name': data.get('passenger_name'),
#                     'age': data.get('age'),
#                     'gender': data.get('gender'),
#                     'phone': data.get('phone')
#                 }
#             )
        
#         if booking_result:
#             return jsonify({
#                 'status': 'success',
#                 'booking_id': booking_result['booking_id'],
#                 'payment_url': booking_result['payment_url']
#             })
#         else:
#             raise Exception("Booking initiation failed")
            
#     except Exception as e:
#         return jsonify({
#             'status': 'error',
#             'message': str(e)
#         })

# @main.route('/booking_status/<booking_id>', methods=['GET'])
# @login_required
# def check_booking_status(booking_id):
#     booking = Booking.query.get_or_404(booking_id)
    
#     # Verify user owns this booking
#     if booking.user_id != current_user.id:
#         return jsonify({
#             'status': 'error',
#             'message': 'Unauthorized'
#         }), 403
    
#     try:
#         if booking.booking_type == 'hotel':
#             hotel_service = HotelService()
#             status = hotel_service.check_booking_status(booking.booking_details['booking_reference'])
#         else:  # transport
#             transport_service = TransportService()
#             status = transport_service.check_booking_status(booking.booking_details['booking_reference'])
            
#         return jsonify({
#             'status': 'success',
#             'booking_status': status
#         })
        
#     except Exception as e:
#         return jsonify({
#             'status': 'error',
#             'message': str(e)
#         })

# @main.route('/my_bookings', methods=['GET'])
# @login_required
# def my_bookings():
#     bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.created_at.desc()).all()
#     return render_template('bookings.html', bookings=bookings)

# @main.route('/get_seat_layout', methods=['GET'])
# @login_required
# def get_seat_layout():
#     bus_id = request.args.get('bus_id')
#     if not bus_id:
#         return jsonify({
#             'status': 'error',
#             'message': 'Bus ID is required'
#         })
    
#     transport_service = TransportService()
#     layout = transport_service.get_seat_layout(bus_id)
    
#     return jsonify({
#         'status': 'success',
#         'layout': layout
#     })