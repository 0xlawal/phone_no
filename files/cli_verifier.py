"""
Interactive CLI for Phone Number Verification
Batch processing, CSV export, and real-time validation
"""

import asyncio
import json
import csv
from pathlib import Path
from typing import List
from datetime import datetime
from colorama import Fore, Style, init
from phone_verifier import PhoneVerifier, PhoneVerificationResult

init(autoreset=True)


class PhoneVerifierCLI:
    """Interactive CLI wrapper for phone verification"""
    
    def __init__(self):
        self.verifier = PhoneVerifier()
        self.results: List[PhoneVerificationResult] = []

    def print_banner(self):
        """Print welcome banner"""
        banner = f"""
{Fore.CYAN}
╔═══════════════════════════════════════════════════════════╗
║    🌍 INTERNATIONAL PHONE NUMBER VERIFIER v1.0            ║
║    Validate • Locate • Detect Scams • Multi-Region        ║
╚═══════════════════════════════════════════════════════════╝
{Style.RESET_ALL}
Features:
  ✓ Format validation (250+ regions)
  ✓ Carrier & line type detection
  ✓ Geographic location mapping
  ✓ Scam/fraud detection
  ✓ Batch processing (CSV)
  ✓ Export results (JSON/CSV)

Commands:
  1 - Verify single number
  2 - Batch verify from CSV
  3 - View results
  4 - Export results
  5 - Clear results
  6 - Exit
        """
        print(banner)

    async def verify_single(self):
        """Verify a single phone number"""
        print(f"\n{Fore.CYAN}Single Phone Verification{Style.RESET_ALL}")
        print("-" * 60)
        
        phone = input(f"{Fore.YELLOW}Enter phone number (e.g., +2348012345678): {Style.RESET_ALL}").strip()
        region = input(f"{Fore.YELLOW}Enter region code (optional, e.g., NG): {Style.RESET_ALL}").strip() or None
        
        print(f"\n{Fore.CYAN}Verifying...{Style.RESET_ALL}")
        result = await self.verifier.verify_phone_complete(phone, region)
        
        self.results.append(result)
        self.verifier.print_result(result)

    async def batch_verify(self):
        """Verify numbers from CSV file"""
        print(f"\n{Fore.CYAN}Batch Phone Verification{Style.RESET_ALL}")
        print("-" * 60)
        
        csv_path = input(f"{Fore.YELLOW}Enter CSV file path: {Style.RESET_ALL}").strip()
        
        if not Path(csv_path).exists():
            print(f"{Fore.RED}File not found: {csv_path}{Style.RESET_ALL}")
            return
        
        try:
            with open(csv_path, 'r') as f:
                reader = csv.DictReader(f)
                phones = list(reader)
            
            if not phones:
                print(f"{Fore.RED}No data in CSV file{Style.RESET_ALL}")
                return
            
            print(f"\n{Fore.CYAN}Processing {len(phones)} numbers...{Style.RESET_ALL}\n")
            
            for idx, row in enumerate(phones, 1):
                phone = row.get('phone') or row.get('phone_number') or list(row.values())[0]
                region = row.get('region')
                
                print(f"{Fore.YELLOW}[{idx}/{len(phones)}] {phone}{Style.RESET_ALL}")
                
                result = await self.verifier.verify_phone_complete(phone, region)
                self.results.append(result)
                
                status = f"{Fore.GREEN}✓ Valid{Style.RESET_ALL}" if result.is_valid else f"{Fore.RED}✗ Invalid{Style.RESET_ALL}"
                risk = f"{Fore.RED}⚠️ Scam Risk{Style.RESET_ALL}" if result.is_likely_scam else f"{Fore.GREEN}Safe{Style.RESET_ALL}"
                
                print(f"  Status: {status} | Risk: {risk}\n")
                
                await asyncio.sleep(0.3)  # Rate limiting
            
            print(f"{Fore.GREEN}✓ Batch processing complete!{Style.RESET_ALL}")
            print(f"Total verified: {len(self.results)}")
        
        except Exception as e:
            print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")

    def view_results(self):
        """Display all results"""
        if not self.results:
            print(f"{Fore.YELLOW}No results to display{Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.CYAN}VERIFICATION RESULTS ({len(self.results)} total){Style.RESET_ALL}")
        print("=" * 80)
        
        for idx, result in enumerate(self.results, 1):
            status = "✓" if result.is_valid else "✗"
            risk = "🔴" if result.is_likely_scam else "🟢"
            country = result.country_code if result.is_valid else "N/A"
            
            print(f"{idx}. {status} {result.phone_number:20} | {country:6} | {risk} {result.fraud_risk_score:.0%}")
        
        print("=" * 80 + "\n")

    def export_results(self):
        """Export results to JSON or CSV"""
        if not self.results:
            print(f"{Fore.YELLOW}No results to export{Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.CYAN}Export Results{Style.RESET_ALL}")
        print("-" * 60)
        
        export_format = input(f"{Fore.YELLOW}Format (json/csv): {Style.RESET_ALL}").strip().lower()
        filename = input(f"{Fore.YELLOW}Filename (without extension): {Style.RESET_ALL}").strip()
        
        if not filename:
            filename = f"phone_verification_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            if export_format == 'json':
                filepath = f"{filename}.json"
                data = [r.to_dict() for r in self.results]
                with open(filepath, 'w') as f:
                    json.dump(data, f, indent=2)
                print(f"{Fore.GREEN}✓ Exported to {filepath}{Style.RESET_ALL}")
            
            elif export_format == 'csv':
                filepath = f"{filename}.csv"
                with open(filepath, 'w', newline='') as f:
                    fieldnames = [
                        'phone_number', 'is_valid', 'country', 'country_code',
                        'carrier', 'line_type', 'is_likely_scam', 'fraud_risk_score',
                        'scam_indicators', 'timestamp'
                    ]
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    for result in self.results:
                        row = result.to_dict()
                        row['scam_indicators'] = '|'.join(row['scam_indicators'])
                        writer.writerow({k: row.get(k) for k in fieldnames})
                
                print(f"{Fore.GREEN}✓ Exported to {filepath}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}Invalid format. Use 'json' or 'csv'{Style.RESET_ALL}")
        
        except Exception as e:
            print(f"{Fore.RED}Export error: {e}{Style.RESET_ALL}")

    def clear_results(self):
        """Clear all results"""
        if self.results:
            confirm = input(f"{Fore.YELLOW}Clear all {len(self.results)} results? (y/n): {Style.RESET_ALL}").strip().lower()
            if confirm == 'y':
                self.results.clear()
                print(f"{Fore.GREEN}✓ Results cleared{Style.RESET_ALL}")

    async def run(self):
        """Main CLI loop"""
        self.print_banner()
        
        while True:
            try:
                choice = input(f"\n{Fore.CYAN}Select option (1-6): {Style.RESET_ALL}").strip()
                
                if choice == '1':
                    await self.verify_single()
                elif choice == '2':
                    await self.batch_verify()
                elif choice == '3':
                    self.view_results()
                elif choice == '4':
                    self.export_results()
                elif choice == '5':
                    self.clear_results()
                elif choice == '6':
                    print(f"\n{Fore.GREEN}Thank you for using Phone Verifier!{Style.RESET_ALL}\n")
                    break
                else:
                    print(f"{Fore.RED}Invalid option. Try again.{Style.RESET_ALL}")
            
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}Exiting...{Style.RESET_ALL}\n")
                break
            except Exception as e:
                print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")


async def main():
    cli = PhoneVerifierCLI()
    await cli.run()


if __name__ == "__main__":
    asyncio.run(main())
