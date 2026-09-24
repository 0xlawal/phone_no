"""
Advanced Phone Verification APIs
Integration with Twilio, Vonage, and other premium services
Free tier and open APIs included
"""

import os
import requests
import asyncio
import aiohttp
from typing import Optional, Dict
from dataclasses import dataclass
from colorama import Fore, Style


@dataclass
class CarrierInfo:
    """Carrier information response"""
    carrier: str
    line_type: str  # MOBILE, FIXED_LINE, etc.
    country: str
    number_valid: bool


class TwilioVerifier:
    """
    Twilio Lookup API Integration
    Requires: TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN environment variables
    Free tier: Limited lookups per month
    """
    
    def __init__(self):
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.base_url = f"https://lookups.twilio.com/v1/PhoneNumbers"
    
    def is_configured(self) -> bool:
        """Check if Twilio credentials are available"""
        return bool(self.account_sid and self.auth_token)
    
    async def lookup_async(self, phone_number: str, country: Optional[str] = None) -> Optional[CarrierInfo]:
        """
        Async lookup using Twilio
        """
        if not self.is_configured():
            print(f"{Fore.YELLOW}Twilio not configured. Set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN{Style.RESET_ALL}")
            return None
        
        try:
            params = {
                'Type': 'carrier',
            }
            if country:
                params['CountryCode'] = country
            
            async with aiohttp.ClientSession(auth=aiohttp.BasicAuth(self.account_sid, self.auth_token)) as session:
                async with session.get(
                    f"{self.base_url}/{phone_number.replace('+', '')}",
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        carrier_data = data.get('carrier', {})
                        
                        return CarrierInfo(
                            carrier=carrier_data.get('name', 'Unknown'),
                            line_type=carrier_data.get('type', 'Unknown'),
                            country=data.get('country_code', 'Unknown'),
                            number_valid=data.get('valid', False)
                        )
        except Exception as e:
            print(f"{Fore.RED}Twilio lookup error: {e}{Style.RESET_ALL}")
        
        return None


class VonageVerifier:
    """
    Vonage (Nexmo) Phone Verification
    Requires: VONAGE_API_KEY and VONAGE_API_SECRET
    Free tier available
    """
    
    def __init__(self):
        self.api_key = os.getenv('VONAGE_API_KEY')
        self.api_secret = os.getenv('VONAGE_API_SECRET')
        self.base_url = "https://api.nexmo.com/ni/advanced/number"
    
    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_secret)
    
    async def lookup_async(self, phone_number: str) -> Optional[Dict]:
        """
        Async lookup using Vonage Number Insight API
        """
        if not self.is_configured():
            print(f"{Fore.YELLOW}Vonage not configured. Set VONAGE_API_KEY and VONAGE_API_SECRET{Style.RESET_ALL}")
            return None
        
        try:
            params = {
                'api_key': self.api_key,
                'api_secret': self.api_secret,
                'number': phone_number.replace('+', ''),
                'country': '',
                'type': 'json'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.base_url,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status == 200:
                        return await resp.json()
        except Exception as e:
            print(f"{Fore.RED}Vonage lookup error: {e}{Style.RESET_ALL}")
        
        return None


class OVH_PhoneValidator:
    """
    OVH Phone Validation API (Free)
    No authentication required
    """
    
    def __init__(self):
        self.base_url = "https://api.ovh.com/v1/sms"
    
    async def validate_async(self, phone_number: str) -> Optional[Dict]:
        """
        Validate phone format using OVH
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/validate/format",
                    params={'number': phone_number},
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as resp:
                    if resp.status == 200:
                        return await resp.json()
        except Exception as e:
            print(f"{Fore.YELLOW}OVH validation error: {e}{Style.RESET_ALL}")
        
        return None


class IPQualityScore:
    """
    IPQualityScore Phone Verification API
    Requires: IPQS_API_KEY
    Free tier available - checks for fraud/abuse
    """
    
    def __init__(self):
        self.api_key = os.getenv('IPQS_API_KEY')
        self.base_url = "https://api.ipqualityscore.com/api/json/phone"
    
    def is_configured(self) -> bool:
        return bool(self.api_key)
    
    async def check_fraud_async(self, phone_number: str) -> Optional[Dict]:
        """
        Check phone number for fraud/abuse patterns
        """
        if not self.is_configured():
            print(f"{Fore.YELLOW}IPQualityScore not configured. Set IPQS_API_KEY{Style.RESET_ALL}")
            return None
        
        try:
            params = {
                'api_key': self.api_key,
                'phone': phone_number,
                'strictness': 0  # 0=lenient, 1=normal, 2=strict
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/validate",
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status == 200:
                        return await resp.json()
        except Exception as e:
            print(f"{Fore.RED}IPQualityScore error: {e}{Style.RESET_ALL}")
        
        return None


class FreePhoneDB:
    """
    Free Open Phone Number Database
    No authentication required
    """
    
    async def check_spam_async(self, phone_number: str) -> Optional[Dict]:
        """
        Check against spam database
        """
        try:
            # Try multiple free databases
            databases = [
                f"https://opendigitalnumbers.com/api/check?number={phone_number}",
                f"https://api.phonespamfilter.com/check?number={phone_number}",
            ]
            
            for db_url in databases:
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(
                            db_url,
                            timeout=aiohttp.ClientTimeout(total=5)
                        ) as resp:
                            if resp.status == 200:
                                return await resp.json()
                except:
                    continue
        
        except Exception as e:
            print(f"{Fore.YELLOW}SpamDB error: {e}{Style.RESET_ALL}")
        
        return None


class HLRLookup:
    """
    HLR (Home Location Register) Lookup
    Real-time carrier validation
    Requires: HLR_API_KEY
    Checks if number is active on carrier network
    """
    
    def __init__(self):
        self.api_key = os.getenv('HLR_API_KEY')
        self.base_url = "https://api.hlrlookup.com"
    
    def is_configured(self) -> bool:
        return bool(self.api_key)
    
    async def check_active_async(self, phone_number: str) -> Optional[Dict]:
        """
        Check if number is active on carrier network
        """
        if not self.is_configured():
            return None
        
        try:
            headers = {'Authorization': f'Bearer {self.api_key}'}
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/network_status",
                    json={'msisdn': phone_number},
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status == 200:
                        return await resp.json()
        except Exception as e:
            print(f"{Fore.YELLOW}HLR error: {e}{Style.RESET_ALL}")
        
        return None


class CompositePhoneVerifier:
    """
    Combine multiple verification sources
    """
    
    def __init__(self):
        self.twilio = TwilioVerifier()
        self.vonage = VonageVerifier()
        self.ipqs = IPQualityScore()
        self.hlr = HLRLookup()
        self.free_db = FreePhoneDB()
    
    async def verify_all_sources(self, phone_number: str) -> Dict:
        """
        Run all available verification services
        """
        results = {
            'phone_number': phone_number,
            'sources': {}
        }
        
        # Run all checks in parallel
        tasks = []
        
        if self.twilio.is_configured():
            tasks.append(('twilio', self.twilio.lookup_async(phone_number)))
        
        if self.vonage.is_configured():
            tasks.append(('vonage', self.vonage.lookup_async(phone_number)))
        
        if self.ipqs.is_configured():
            tasks.append(('ipqs', self.ipqs.check_fraud_async(phone_number)))
        
        if self.hlr.is_configured():
            tasks.append(('hlr', self.hlr.check_active_async(phone_number)))
        
        # Always check free database
        tasks.append(('free_db', self.free_db.check_spam_async(phone_number)))
        
        # Execute all tasks
        for name, task in tasks:
            try:
                result = await task
                if result:
                    results['sources'][name] = result
            except Exception as e:
                results['sources'][name] = {'error': str(e)}
        
        return results


# Setup instructions
SETUP_GUIDE = """
╔════════════════════════════════════════════════════════════════════╗
║              ADVANCED API SETUP INSTRUCTIONS                       ║
╚════════════════════════════════════════════════════════════════════╝

1. TWILIO (Recommended)
   - Sign up: https://www.twilio.com/console
   - Get Account SID and Auth Token
   - Set environment variables:
     export TWILIO_ACCOUNT_SID='your_sid'
     export TWILIO_AUTH_TOKEN='your_token'
   - Cost: ~$0.01 per lookup, 1000 free lookups/month

2. VONAGE (Nexmo)
   - Sign up: https://dashboard.nexmo.com/
   - Get API Key and API Secret
   - Set environment variables:
     export VONAGE_API_KEY='your_key'
     export VONAGE_API_SECRET='your_secret'
   - Cost: Free tier available

3. IPQualityScore
   - Sign up: https://www.ipqualityscore.com/
   - Get API Key
   - Set environment variable:
     export IPQS_API_KEY='your_key'
   - Cost: Free tier available (fraud detection)

4. HLR Lookup
   - Sign up: https://www.hlrlookup.com/
   - Get API Key
   - Set environment variable:
     export HLR_API_KEY='your_key'
   - Cost: Freemium model

5. Free Options (No Setup Required)
   - OpenDigitalNumbers
   - Phone Spam Filter Database
   - Google Phonenumbers Library (included)

Usage:
   from advanced_apis import CompositePhoneVerifier
   
   verifier = CompositePhoneVerifier()
   results = await verifier.verify_all_sources('+2348012345678')
"""

if __name__ == "__main__":
    print(SETUP_GUIDE)
