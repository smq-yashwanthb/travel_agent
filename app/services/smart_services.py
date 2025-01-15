from app.services.booking_automation import BookingAutomation
from threading import Thread
import json
from datetime import datetime
import logging

class PriceMonitor:
    def __init__(self):
        self.automation = BookingAutomation(headless=True)
        self.monitoring_threads = {}
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filename='price_monitor.log'
        )
        self.logger = logging.getLogger(__name__)

    def start_monitoring(self, user_id, search_params, threshold_price):
        """Start monitoring prices for a user"""
        try:
            thread = Thread(
                target=self.monitor_prices,
                args=(user_id, search_params, threshold_price)
            )
            thread.daemon = True
            thread.start()
            
            self.monitoring_threads[user_id] = thread
            self.logger.info(f"Started price monitoring for user {user_id}")
            
        except Exception as e:
            self.logger.error(f"Error starting price monitor: {str(e)}")

    def stop_monitoring(self, user_id):
        """Stop monitoring prices for a user"""
        if user_id in self.monitoring_threads:
            # Thread will terminate on next price check
            del self.monitoring_threads[user_id]
            self.logger.info(f"Stopped price monitoring for user {user_id}")

    def monitor_prices(self, user_id, search_params, threshold_price):
        """Monitor prices and send alerts"""
        try:
            self.automation.start_browser()
            self.automation.monitor_price(search_params, threshold_price)
        except Exception as e:
            self.logger.error(f"Error in price monitoring: {str(e)}")
        finally:
            self.automation.close_browser()

class FareComparison:
    def __init__(self):
        self.automation = BookingAutomation(headless=True)
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filename='fare_comparison.log'
        )
        self.logger = logging.getLogger(__name__)

    def compare_fares(self, source, destination, date):
        """Compare fares across different providers"""
        try:
            self.automation.start_browser()
            fares = self.automation.compare_fares(source, destination, date)
            
            analysis = self.analyze_fares(fares)
            self.logger.info(f"Completed fare comparison for {source} to {destination}")
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error in fare comparison: {str(e)}")
            return None
        finally:
            self.automation.close_browser()

    def analyze_fares(self, fares):
        """Analyze fares and provide insights"""
        try:
            analysis = {
                'lowest_fare': min(fare['amount'] for provider in fares.values() for fare in provider),
                'highest_fare': max(fare['amount'] for provider in fares.values() for fare in provider),
                'average_fare': sum(fare['amount'] for provider in fares.values() for fare in provider) / 
                              sum(len(provider) for provider in fares.values()),
                'best_deals': self.find_best_deals(fares),
                'provider_comparison': self.compare_providers(fares)
            }
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing fares: {str(e)}")
            return None

    def find_best_deals(self, fares):
        """Find the best deals across providers"""
        all_fares = []
        for provider, provider_fares in fares.items():
            for fare in provider_fares:
                all_fares.append({
                    'provider': provider,
                    'amount': fare['amount'],
                    'departure': fare['departure'],
                    'duration': fare['duration'],
                    'rating': fare.get('rating', 'N/A')
                })
        
        # Sort by price and get top 3 deals
        return sorted(all_fares, key=lambda x: x['amount'])[:3]

    def compare_providers(self, fares):
        """Compare different providers"""
        comparison = {}
        for provider, provider_fares in fares.items():
            comparison[provider] = {
                'average_fare': sum(fare['amount'] for fare in provider_fares) / len(provider_fares),
                'min_fare': min(fare['amount'] for fare in provider_fares),
                'max_fare': max(fare['amount'] for fare in provider_fares),
                'total_options': len(provider_fares)
            }
        return comparison

class SmartSearch:
    def __init__(self):
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filename='smart_search.log'
        )
        self.logger = logging.getLogger(__name__)

    def search(self, prompt):
        """Smart search based on user prompt"""
        try:
            # Parse the prompt
            requirements = self.parse_requirements(prompt)
            
            # Get search results
            results = self.get_search_results(requirements)
            
            # Apply smart filtering
            filtered_results = self.apply_smart_filters(results, requirements)
            
            # Sort and rank results
            ranked_results = self.rank_results(filtered_results, requirements)
            
            self.logger.info(f"Completed smart search for prompt: {prompt}")
            return ranked_results
            
        except Exception as e:
            self.logger.error(f"Error in smart search: {str(e)}")
            return None

    def parse_requirements(self, prompt):
        """Parse user requirements from prompt"""
        import spacy
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(prompt)

        requirements = {
            'location': None,
            'dates': [],
            'preferences': [],
            'budget': None,
            'transport_type': None
        }

        # Extract location
        for ent in doc.ents:
            if ent.label_ == 'GPE':
                requirements['location'] = ent.text
                break

        # Extract dates
        dates = self.extract_dates(prompt)
        if dates:
            requirements['dates'] = dates

        # Extract preferences
        preferences = self.extract_preferences(prompt)
        if preferences:
            requirements['preferences'] = preferences

        # Extract budget
        budget = self.extract_budget(prompt)
        if budget:
            requirements['budget'] = budget

        # Extract transport type
        transport_type = self.extract_transport_type(prompt)
        if transport_type:
            requirements['transport_type'] = transport_type

        return requirements

    def extract_dates(self, prompt):
        """Extract dates from prompt"""
        import dateparser
        dates = []
        
        # Common date patterns
        date_patterns = [
            r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}',
            r'tomorrow',
            r'next week',
            r'next month',
            r'\d{1,2}(?:st|nd|rd|th)? [A-Za-z]+'
        ]
        
        for pattern in date_patterns:
            matches = re.finditer(pattern, prompt, re.IGNORECASE)
            for match in matches:
                date_str = match.group()
                parsed_date = dateparser.parse(date_str)
                if parsed_date:
                    dates.append(parsed_date)
                    
        return dates

    def extract_preferences(self, prompt):
        """Extract user preferences from prompt"""
        preferences = []
        
        # Common preference patterns
        preference_patterns = {
            'AC': r'AC|air.?condition(?:ed|ing)?',
            'Non-AC': r'non.?AC|non.?air.?condition(?:ed|ing)?',
            'Sleeper': r'sleep(?:er)?|berth',
            'Window Seat': r'window.?seat',
            'Direct': r'direct|non.?stop',
            'Rating': r'(\d+)\s*star|rating\s*(\d+)\+?'
        }
        
        for pref, pattern in preference_patterns.items():
            if re.search(pattern, prompt, re.IGNORECASE):
                preferences.append(pref)
                
        return preferences

    def extract_budget(self, prompt):
        """Extract budget from prompt"""
        # Match currency patterns
        currency_patterns = [
            r'(?:Rs\.?|INR|₹)\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
            r'budget\s*(?:of|:)?\s*(?:Rs\.?|INR|₹)?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
            r'under\s*(?:Rs\.?|INR|₹)?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
            r'less\s*than\s*(?:Rs\.?|INR|₹)?\s*(\d+(?:,\d+)*(?:\.\d{2})?)'
        ]
        
        for pattern in currency_patterns:
            match = re.search(pattern, prompt, re.IGNORECASE)
            if match:
                amount = match.group(1).replace(',', '')
                return float(amount)
                
        return None

    def extract_transport_type(self, prompt):
        """Extract preferred transport type"""
        transport_patterns = {
            'bus': r'\b(?:bus|volvo|ordinary|luxury)\b',
            'train': r'\b(?:train|rail|railway)\b'
        }
        
        for transport_type, pattern in transport_patterns.items():
            if re.search(pattern, prompt, re.IGNORECASE):
                return transport_type
                
        return None

    def get_search_results(self, requirements):
        """Get search results based on requirements"""
        automation = BookingAutomation(headless=True)
        try:
            automation.start_browser()
            
            results = {
                'transport': [],
                'hotels': []
            }
            
            # Get transport results if needed
            if requirements['transport_type']:
                results['transport'] = automation.search_buses(
                    requirements['location'],
                    requirements['dates'][0] if requirements['dates'] else None
                )
            
            # Get hotel results if needed
            if not requirements['transport_type']:
                results['hotels'] = automation.search_hotels(
                    requirements['location'],
                    requirements['dates'][0] if requirements['dates'] else None,
                    requirements['dates'][1] if len(requirements['dates']) > 1 else None
                )
            
            return results
            
        finally:
            automation.close_browser()

    def apply_smart_filters(self, results, requirements):
        """Apply smart filtering based on requirements"""
        filtered_results = {
            'transport': [],
            'hotels': []
        }
        
        # Filter transport results
        for transport in results['transport']:
            if self.matches_requirements(transport, requirements):
                filtered_results['transport'].append(transport)
        
        # Filter hotel results
        for hotel in results['hotels']:
            if self.matches_requirements(hotel, requirements):
                filtered_results['hotels'].append(hotel)
        
        return filtered_results

    def matches_requirements(self, item, requirements):
        """Check if item matches user requirements"""
        # Check budget
        if requirements['budget'] and 'price' in item:
            if float(item['price']) > requirements['budget']:
                return False
        
        # Check preferences
        for pref in requirements['preferences']:
            if pref == 'AC' and 'AC' not in item.get('type', ''):
                return False
            if pref.startswith('Rating') and 'rating' in item:
                required_rating = float(pref.split()[-1])
                if float(item['rating']) < required_rating:
                    return False
        
        return True

    def rank_results(self, results, requirements):
        """Rank results based on user preferences"""
        for category in ['transport', 'hotels']:
            results[category].sort(key=lambda x: self.calculate_rank(x, requirements))
        return results

    def calculate_rank(self, item, requirements):
        """Calculate ranking score for an item"""
        score = 0
        
        # Price score (lower is better)
        if 'price' in item and requirements['budget']:
            price_ratio = float(item['price']) / requirements['budget']
            score += (1 - price_ratio) * 50  # Price contributes 50% to score
        
        # Rating score (higher is better)
        if 'rating' in item:
            score += float(item['rating']) * 30  # Rating contributes 30% to score
        
        # Preference match score
        pref_score = sum(10 for pref in requirements['preferences'] 
                        if pref.lower() in str(item).lower())
        score += pref_score  # Preferences contribute 20% to score
        
        return -score  # Negative for descending sort