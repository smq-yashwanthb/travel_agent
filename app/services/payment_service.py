import razorpay
from app.models import db
from config import Config

class PaymentService:
    def __init__(self):
        self.client = razorpay.Client(
            auth=(Config.RAZORPAY_KEY_ID, Config.RAZORPAY_KEY_SECRET)
        )
        
    def create_payment_link(self, booking):
        """Create a payment link for the booking"""
        try:
            payment_data = {
                'amount': int(booking.total_amount * 100),  # Amount in paise
                'currency': 'INR',
                'accept_partial': False,
                'description': f'Booking ID: {booking.id}',
                'customer': {
                    'name': booking.user.username,
                    'email': booking.user.email
                },
                'notify': {
                    'email': True,
                    'sms': True
                },
                'reminder_enable': True,
            }
            
            payment_link = self.client.payment_link.create(payment_data)
            
            # Update booking with payment details
            booking.payment_id = payment_link['id']
            db.session.commit()
            
            return payment_link['short_url']
            
        except Exception as e:
            print(f"Error creating payment link: {str(e)}")
            return None
            
    def verify_payment(self, payment_id):
        """Verify payment status"""
        try:
            payment = self.client.payment_link.fetch(payment_id)
            return payment['status'] == 'paid'
        except Exception as e:
            print(f"Error verifying payment: {str(e)}")
            return False