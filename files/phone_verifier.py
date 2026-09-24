"""
Advanced International Phone Number Verifier
Validates format, detects location, carrier, and potential scams
"""

import phonenumbers
import requests
import asyncio
import aiohttp
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from colorama import Fore, Style, init

init(autoreset=True)

@dataclass
class PhoneVerificationResult:
    """Store complete phone verification results"""
    phone_number: str
    is_valid: bool
    country: str
    country_code: str
    region: str
    carrier: Optional[str] = None
    line_type: Optional[str] = None
    location: Optional[Dict] = None
    is_likely_scam: bool = False
    scam_indicators: List[str] = None
    fraud_risk_score: float = 0.0
    timestamp: str = None

    def __post_init__(self):
        if self.scam_indicators is None:
            self.scam_indicators = []
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

    def to_dict(self):
        return {
            'phone_number': self.phone_number,
            'is_valid': self.is_valid,
            'country': self.country,
            'country_code': self.country_code,
            'region': self.region,
            'carrier': self.carrier,
            'line_type': self.line_type,
            'location': self.location,
            'is_likely_scam': self.is_likely_scam,
            'scam_indicators': self.scam_indicators,
            'fraud_risk_score': self.fraud_risk_score,
            'timestamp': self.timestamp
        }


class PhoneVerifier:
    """Advanced phone number verifier using multiple APIs"""
    
    def __init__(self):
        # Free API endpoints (no key required or with free tier)
        self.numverify_api = "http://apilayer.net/api/validate"  # Has free tier
        self.opendigitalnumbers_api = "https://opendigitalnumbers.com/api"
        self.abuseipdb_api = "https://api.abuseipdb.com/api/v2/check"
        
        # Known spam patterns
        self.spam_keywords = [
            'spam', 'scam', 'fraud', 'suspicious', 'blocked', 'reported'
        ]
        
        self.high_risk_countries = [
            '+212', '+234', '+256', '+257'  # Known for high fraud rates
        ]

    def validate_phone_format(self, phone_number: str, region: Optional[str] = None) -> Tuple[bool, Optional[phonenumbers.PhoneNumber], str]:
        """
        Validate phone number format using Google's libphonenumber
        
        Args:
            phone_number: Phone number string
            region: Optional region code (e.g., 'NG' for Nigeria)
        
        Returns:
            Tuple of (is_valid, parsed_number, country_name)
        """
        try:
            # Parse the phone number
            parsed = phonenumbers.parse(phone_number, region)
            
            # Validate the format
            is_valid = phonenumbers.is_valid_number(parsed)
            
            # Get country name
            country_name = phonenumbers.region_code_for_number(parsed)
            
            return is_valid, parsed, country_name
        except phonenumbers.NumberParseException as e:
            print(f"{Fore.RED}Error parsing phone number: {e}{Style.RESET_ALL}")
            return False, None, None

    def get_carrier_info(self, parsed_number: phonenumbers.PhoneNumber) -> Tuple[Optional[str], Optional[str]]:
        """Get carrier and line type information"""
        try:
            from phonenumbers import carrier
            from phonenumbers import phonenumberutil
            
            carrier_name = carrier.name_for_number(parsed_number, 'en')
            line_type = phonenumberutil.number_type(parsed_number)
            
            # Map line type to readable format
            type_mapping = {
                0: 'FIXED_LINE',
                1: 'MOBILE',
                2: 'FIXED_LINE_OR_MOBILE',
                3: 'TOLL_FREE',
                4: 'PREMIUM_RATE',
                5: 'SHARED_COST',
                6: 'VOIP',
                7: 'PERSONAL_NUMBER',
                8: 'PAGER',
                9: 'UAN',
                10: 'VOICEMAIL',
                11: 'ITS'
            }
            
            line_type_name = type_mapping.get(line_type, 'UNKNOWN')
            
            return carrier_name if carrier_name else None, line_type_name
        except Exception as e:
            print(f"{Fore.YELLOW}Could not get carrier info: {e}{Style.RESET_ALL}")
            return None, None

    def get_location_info(self, parsed_number: phonenumbers.PhoneNumber) -> Optional[Dict]:
        """Get geographic location information"""
        try:
            from phonenumbers import geocoder
            
            location = geocoder.description_for_number(parsed_number, 'en')
            
            return {
                'city': location if location else 'Unknown',
                'timezones': []
            }
        except Exception as e:
            return None

    async def check_scam_database_async(self, phone_number: str, country_code: str) -> Tuple[bool, List[str], float]:
        """
        Check multiple scam/fraud databases asynchronously
        Uses free APIs with rate limiting
        """
        scam_indicators = []
        fraud_risk_score = 0.0
        is_likely_scam = False
        
        # Check 1: High-risk country indicators
        if country_code.startswith(tuple(self.high_risk_countries)):
            scam_indicators.append('HIGH_RISK_COUNTRY')
            fraud_risk_score += 0.15
        
        # Check 2: Toll-free or premium rate numbers (higher risk)
        if phone_number.startswith(('+1555', '+1888', '+1900')):
            scam_indicators.append('PREMIUM_RATE_NUMBER')
            fraud_risk_score += 0.20
        
        # Check 3: Try OpenDigitalNumbers API (free, no auth)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.opendigitalnumbers_api}/validate",
                    params={'number': phone_number},
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data.get('is_spam'):
                            scam_indicators.append('FLAGGED_IN_SPAM_DB')
                            fraud_risk_score += 0.30
                            is_likely_scam = True
        except asyncio.TimeoutError:
            scam_indicators.append('API_TIMEOUT_SCAM_CHECK')
        except Exception as e:
            print(f"{Fore.YELLOW}Scam check API error: {e}{Style.RESET_ALL}")
        
        # Check 4: Pattern analysis
        if self._check_suspicious_patterns(phone_number):
            scam_indicators.append('SUSPICIOUS_PATTERN')
            fraud_risk_score += 0.10
        
        # Normalize score to 0-1
        fraud_risk_score = min(fraud_risk_score, 1.0)
        
        return is_likely_scam, scam_indicators, fraud_risk_score

    def _check_suspicious_patterns(self, phone_number: str) -> bool:
        """Check for suspicious number patterns"""
        # Remove special characters
        clean_number = ''.join(filter(str.isdigit, phone_number))
        
        # Pattern checks
        patterns = [
            len(clean_number) > 15,  # Unusually long
            clean_number.count('0') > 10,  # Too many zeros
            len(set(clean_number)) < 3,  # Too few unique digits (like 111222333)
        ]
        
        return any(patterns)

    def _get_country_name(self, country_code: str) -> str:
        """Get country name from country code"""
        country_names = {
            'NG': 'Nigeria', 'US': 'United States', 'GB': 'United Kingdom',
            'FR': 'France', 'DE': 'Germany', 'JP': 'Japan', 'IN': 'India',
            'BR': 'Brazil', 'MX': 'Mexico', 'CN': 'China', 'RU': 'Russia',
            'KE': 'Kenya', 'ZA': 'South Africa', 'GH': 'Ghana', 'TZ': 'Tanzania',
            'CA': 'Canada', 'AU': 'Australia', 'NZ': 'New Zealand', 'SG': 'Singapore',
            'HK': 'Hong Kong', 'AE': 'United Arab Emirates', 'SA': 'Saudi Arabia',
        }
        return country_names.get(country_code, country_code)

    async def verify_phone_complete(self, phone_number: str, region: Optional[str] = None) -> PhoneVerificationResult:
        """
        Complete phone verification with all checks
        """
        # Step 1: Format validation
        is_valid, parsed_num, country_code = self.validate_phone_format(phone_number, region)
        
        if not is_valid:
            return PhoneVerificationResult(
                phone_number=phone_number,
                is_valid=False,
                country='Unknown',
                country_code='Unknown',
                region='Unknown'
            )
        
        # Step 2: Get carrier info
        carrier, line_type = self.get_carrier_info(parsed_num)
        
        # Step 3: Get location
        location = self.get_location_info(parsed_num)
        
        # Step 4: Check for scams
        is_likely_scam, scam_indicators, fraud_score = await self.check_scam_database_async(
            phone_number, country_code
        )
        
        # Get country name
        country_name = self._get_country_name(country_code)
        
        return PhoneVerificationResult(
            phone_number=phone_number,
            is_valid=True,
            country=country_name,
            country_code=country_code,
            region=country_code,
            carrier=carrier,
            line_type=line_type,
            location=location,
            is_likely_scam=is_likely_scam,
            scam_indicators=scam_indicators,
            fraud_risk_score=fraud_score
        )

    def print_result(self, result: PhoneVerificationResult):
        """Pretty print verification result"""
        print("\n" + "="*60)
        print(f"{Fore.CYAN}📱 PHONE VERIFICATION REPORT{Style.RESET_ALL}")
        print("="*60)
        
        # Validity
        status = f"{Fore.GREEN}✓ VALID{Style.RESET_ALL}" if result.is_valid else f"{Fore.RED}✗ INVALID{Style.RESET_ALL}"
        print(f"Status: {status}")
        print(f"Phone Number: {result.phone_number}")
        
        if result.is_valid:
            print(f"Country: {result.country} ({result.country_code})")
            print(f"Region: {result.region}")
            
            if result.carrier:
                print(f"Carrier: {result.carrier}")
            if result.line_type:
                print(f"Line Type: {result.line_type}")
            
            if result.location:
                print(f"Location: {result.location.get('city', 'N/A')}")
                if result.location.get('timezones'):
                    print(f"Timezone: {', '.join(result.location['timezones'][:2])}")
            
            # Scam detection
            print("\n" + "-"*60)
            print(f"{Fore.CYAN}🔍 FRAUD DETECTION{Style.RESET_ALL}")
            
            if result.is_likely_scam:
                print(f"Risk Level: {Fore.RED}HIGH RISK ⚠️{Style.RESET_ALL}")
            else:
                risk_level = "LOW" if result.fraud_risk_score < 0.3 else "MEDIUM" if result.fraud_risk_score < 0.6 else "HIGH"
                color = Fore.GREEN if result.fraud_risk_score < 0.3 else Fore.YELLOW if result.fraud_risk_score < 0.6 else Fore.RED
                print(f"Risk Level: {color}{risk_level} ({result.fraud_risk_score:.1%}){Style.RESET_ALL}")
            
            if result.scam_indicators:
                print(f"Indicators: {', '.join(result.scam_indicators)}")
            
            print(f"Verified: {result.timestamp}")
        
        print("="*60 + "\n")


async def main():
    """Demo the phone verifier"""
    verifier = PhoneVerifier()
    
    # Test numbers from different regions
    test_numbers = [
        ('+2348012345678', 'NG'),  # Nigeria
        ('+1202-555-0173', 'US'),  # US (DC)
        ('+44 20 7946 0958', 'GB'),  # UK
        ('+254712345678', 'KE'),   # Kenya
        ('+33123456789', 'FR'),    # France
        ('+8613800000000', 'CN'),  # China
    ]
    
    print(f"{Fore.CYAN}{'='*60}")
    print(f"INTERNATIONAL PHONE NUMBER VERIFIER")
    print(f"{'='*60}{Style.RESET_ALL}\n")
    
    for phone, region in test_numbers:
        print(f"{Fore.YELLOW}Verifying: {phone}{Style.RESET_ALL}")
        result = await verifier.verify_phone_complete(phone, region)
        verifier.print_result(result)
        await asyncio.sleep(0.5)  # Rate limiting


if __name__ == "__main__":
    asyncio.run(main())
