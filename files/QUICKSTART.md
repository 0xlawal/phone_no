# 🚀 Quick Start Guide - Phone Number Verifier

Get up and running in 5 minutes!

---

## Step 1️⃣: Install Dependencies (2 minutes)

```bash
# Install all required packages
pip install -r requirements.txt

# Wait for installation to complete...
# You should see ✓ Successfully installed messages
```

**What gets installed?**
- ✅ `phonenumbers` (8.13.40) - Google's phone validation library
- ✅ `requests` (2.31.0) - HTTP requests
- ✅ `aiohttp` (3.9.1) - Async HTTP
- ✅ `pydantic` (2.5.3) - Data validation
- ✅ `pandas` (2.1.4) - Data processing
- ✅ `colorama` (0.4.6) - Colored terminal output

---

## Step 2️⃣: Verify Installation (30 seconds)

```bash
# Test if everything installed correctly
python -c "
import phonenumbers
from colorama import Fore, Style
import requests
print(f'{Fore.GREEN}✓ Phone Verifier is ready!{Style.RESET_ALL}')
print('All dependencies installed successfully')
"
```

Expected output:
```
✓ Phone Verifier is ready!
All dependencies installed successfully
```

---

## Step 3️⃣: Run Demo (1 minute)

### Option A: Auto Demo
```bash
# Run pre-configured test with 6 phone numbers
python phone_verifier.py
```

This will verify numbers from:
- 🇳🇬 Nigeria
- 🇺🇸 United States
- 🇬🇧 United Kingdom
- 🇰🇪 Kenya
- 🇫🇷 France
- 🇨🇳 China

### Option B: Interactive CLI
```bash
# Start the interactive menu
python cli_verifier.py
```

Menu options:
```
1 - Verify single number
2 - Batch verify from CSV
3 - View results
4 - Export results (JSON/CSV)
5 - Clear results
6 - Exit
```

---

## Step 4️⃣: Test Your First Number (1 minute)

### In CLI Mode (Recommended for beginners)
```bash
python cli_verifier.py
```
- Select: `1` (Verify single number)
- Enter: `+2348012345678` (or any valid phone)
- Region: `NG` (optional)
- See results instantly!

### In Python Code
```python
import asyncio
from phone_verifier import PhoneVerifier

async def test():
    verifier = PhoneVerifier()
    result = await verifier.verify_phone_complete('+2348012345678', 'NG')
    
    print(f"✓ Valid: {result.is_valid}")
    print(f"🌍 Country: {result.country}")
    print(f"📱 Carrier: {result.carrier}")
    print(f"⚠️ Fraud Risk: {result.fraud_risk_score:.0%}")

asyncio.run(test())
```

---

## Step 5️⃣: Batch Process CSV (if needed)

### 1. Prepare your CSV
Create `my_numbers.csv`:
```csv
phone,region
+2348012345678,NG
+1202-555-0173,US
+447911123456,GB
```

### 2. Run batch verification
```bash
python cli_verifier.py
# Select: 2 (Batch verify)
# Enter: my_numbers.csv
# Wait for processing...
```

### 3. Export results
```
Select: 4 (Export results)
Format: csv (or json)
Filename: my_results
```

Gets saved as: `my_results.csv`

---

## 📱 Test Phone Numbers (Try These!)

| Number | Country | Expected Result |
|--------|---------|-----------------|
| `+2348012345678` | Nigeria 🇳🇬 | ✓ Valid Mobile (MTN) |
| `+1202-555-0173` | USA 🇺🇸 | ✓ Valid Fixed (DC) |
| `+447911123456` | UK 🇬🇧 | ✓ Valid Mobile |
| `+33123456789` | France 🇫🇷 | ✓ Valid |
| `+254712345678` | Kenya 🇰🇪 | ✓ Valid Mobile |
| `+1555-123-4567` | USA 🇺🇸 | ⚠️ Toll-free (high fraud risk) |

---

## 🎯 Common Tasks

### Check if number is valid
```bash
python cli_verifier.py → Option 1
```

### Batch verify hundreds of numbers
```bash
python cli_verifier.py → Option 2 → Your CSV file
```

### Get location of a number
```python
from phone_verifier import PhoneVerifier
import asyncio

async def get_location(phone):
    v = PhoneVerifier()
    r = await v.verify_phone_complete(phone)
    print(f"{phone} → {r.location}")

asyncio.run(get_location('+2348012345678'))
```

### Detect if number is scam
```python
if result.is_likely_scam:
    print("⚠️ This looks like a scam number!")
    print(f"Indicators: {result.scam_indicators}")
else:
    print("✓ This number appears safe")
```

### Export results to Excel-readable CSV
```bash
# CLI: Select 4 → csv → results
# Then open results.csv in Excel/Google Sheets
```

---

## ⚡ Advanced: Add Premium APIs (Optional)

### Add Twilio (Better Carrier Detection)
```bash
# 1. Sign up: https://www.twilio.com/console
# 2. Get credentials from dashboard
# 3. Set environment variables:

export TWILIO_ACCOUNT_SID="ACxxxxxxxxxxxxxxxxxxxxxxxxxx"
export TWILIO_AUTH_TOKEN="your_token_here"

# 4. Restart Python, it will use Twilio automatically
```

### Add Vonage (More Accurate)
```bash
export VONAGE_API_KEY="your_key"
export VONAGE_API_SECRET="your_secret"
```

### Add IPQualityScore (Better Fraud Detection)
```bash
export IPQS_API_KEY="your_key"
```

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'phonenumbers'"
```bash
# Solution: Install dependencies again
pip install -r requirements.txt

# Or individual package
pip install phonenumbers
```

### "Invalid phone number"
```python
# Make sure to include country code
✗ 08012345678      # WRONG (missing country code)
✓ +2348012345678   # CORRECT
```

### "API connection failed"
```
- This is normal if offline
- Verifier still works with local validation
- APIs are optional, not required
```

### "CSV file not found"
```bash
# Make sure CSV is in current directory
# Or provide full path:
/home/user/documents/numbers.csv

# Check file encoding is UTF-8
file my_numbers.csv
```

---

## 📊 Understanding Results

### Output Fields Explained
```python
result.phone_number      # The number checked
result.is_valid         # ✓ Format is correct
result.country          # Country name
result.country_code     # Country code (e.g., 'NG')
result.carrier          # Telecom provider
result.line_type        # MOBILE, FIXED_LINE, VOIP, etc.
result.location         # City and timezone
result.fraud_risk_score # 0.0-1.0 (0% to 100%)
result.is_likely_scam   # True if flagged as fraud
result.scam_indicators  # List of fraud patterns found
```

### Fraud Risk Score
```
🟢 0-30%   : Safe to call
🟡 30-60%  : Caution - verify first
🔴 60-100% : High risk - may be scam
```

---

## 🎬 Full Example Walkthrough

```bash
# 1. Start interactive CLI
python cli_verifier.py

# 2. See menu:
#    Select option (1-6): 

# 3. Pick option 1 (single verification)
#    Select option (1-6): 1

# 4. Enter a number
#    Enter phone number: +2348012345678
#    Enter region (optional): NG

# 5. See results:
#    ✓ VALID
#    Country: Nigeria (NG)
#    Carrier: MTN Nigeria
#    Line Type: MOBILE
#    Risk Level: LOW (15%)
#    ✓ Safe to call

# 6. Continue with more numbers or export
```

---

## 📈 Next Steps After Setup

1. ✅ Installed all packages
2. ✅ Verified installation works
3. ✅ Tested with demo numbers
4. ⏭️ **Use with your own numbers**
5. ⏭️ (Optional) Add premium APIs
6. ⏭️ (Optional) Automate with batch CSV

---

## 💡 Pro Tips

- **Rate limiting**: Add `await asyncio.sleep(0.5)` between calls to be nice to APIs
- **Batch processing**: 100+ numbers? Use CSV batch mode, not one-by-one
- **Export format**: JSON for programmatic access, CSV for Excel/Sheets
- **High-risk check**: Use `is_likely_scam` to flag immediately
- **Keep updated**: Spam databases change daily

---

## 🆘 Need Help?

1. Check README.md for detailed docs
2. Review examples in QUICKSTART.md (this file)
3. Check error messages carefully
4. Verify all dependencies installed
5. Try with a known valid number first

---

## ✨ You're Ready!

```bash
# Your next command:
python cli_verifier.py

# Or start coding:
python

# Then paste:
import asyncio
from phone_verifier import PhoneVerifier

async def test():
    v = PhoneVerifier()
    r = await v.verify_phone_complete('+2348012345678')
    print(f"✓ {r.country} - {r.carrier}")

asyncio.run(test())
```

**Happy verifying! 📱✨**
