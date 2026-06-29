#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MJA OpenResolver Scanner - Runner
"""

import asyncio
import sys
import os
from mja_scanner import MJAScanner

async def main():
    """Main entry point"""
    if not os.path.exists('config.json'):
        print("⚠️  Config file not found! Using defaults...")
    
    scanner = MJAScanner('config.json')
    
    print("=" * 70)
    print("  🚀 MJA OpenResolver Scanner v1.0")
    print("=" * 70)
    print(f"  Platform: {scanner.detect_platform()}")
    print(f"  Profile: {scanner.config.get('profile', 'balanced').title()}")
    print(f"  Targets: {len(scanner.config.get('targets', []))} networks")
    print(f"  Total IPs: {scanner.total_ips_to_scan:,}")
    print("=" * 70)
    print("  Press Ctrl+C to stop safely at any time")
    print("=" * 70)
    
    try:
        # اجرای اسکن برای هر target
        for target in scanner.config.get('targets', []):
            if not scanner.is_running:
                break
            await scanner.scan_network(target)
            
    except KeyboardInterrupt:
        scanner.safe_stop(None, None)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        scanner.save_state()
    
    finally:
        print("\n\n📊 Generating final report...")
        scanner.save_state()
        scanner.generate_report()
        print("✅ Done! Results saved to:")
        print("   - client_resolvers.txt")
        print("   - scan_report.csv")
        print("   - scan.log")
        print("   - state.json")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
