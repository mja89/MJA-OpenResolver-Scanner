#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MJA OpenResolver Scanner v1.0
Core Scanner Engine
"""

import asyncio
import aiodns
import ipaddress
import json
import random
import time
import os
import sys
import signal
import csv
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from collections import deque
import logging

# تنظیمات لاگ
logging.basicConfig(
    filename='scan.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

@dataclass
class ResolverResult:
    """Data class for resolver scan results"""
    ip: str
    port: int = 53
    latency: float = 0.0
    loss: float = 0.0
    score: float = 0.0
    alive: bool = False
    timestamp: str = ""

class MJAScanner:
    """Main scanner class with all features"""
    
    def __init__(self, config_path: str = "config.json"):
        self.config = self.load_config(config_path)
        self.state = self.load_state()
        self.results: List[ResolverResult] = []
        self.scanned_ips: Set[str] = set()
        self.batch_results: List[ResolverResult] = []
        self.is_running = True
        self.current_batch = 0
        self.total_ips_to_scan = 0
        self.targets_processed = 0
        
        # Adaptive variables (simplified)
        self.current_workers = self.config.get('initial_workers', 100)
        self.current_timeout = self.config.get('initial_timeout', 3.0)
        self.cpu_threshold = self.config.get('cpu_threshold', 70)
        self.ram_limit = self.config.get('ram_limit', 80)
        
        # Statistics
        self.stats = {
            'scanned': 0,
            'healthy': 0,
            'dead': 0,
            'speed': 0,
            'start_time': datetime.now(),
            'last_save': datetime.now(),
            'last_update': datetime.now()
        }
        
        # Performance profile
        self.set_performance_profile(self.config.get('profile', 'balanced'))
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.safe_stop)
        signal.signal(signal.SIGTERM, self.safe_stop)
        
        # Calculate total IPs
        self.calculate_total_ips()

    def calculate_total_ips(self):
        """Calculate total IPs to scan"""
        self.total_ips_to_scan = 0
        for target in self.config.get('targets', []):
            try:
                if '/' in target:
                    net = ipaddress.ip_network(target, strict=False)
                    self.total_ips_to_scan += net.num_addresses
                else:
                    self.total_ips_to_scan += 1
            except:
                self.total_ips_to_scan += 1

    def load_config(self, path: str) -> Dict:
        """Load configuration with defaults"""
        default_config = {
            'profile': 'balanced',
            'initial_workers': 100,
            'min_workers': 20,
            'max_workers': 500,
            'initial_timeout': 3.0,
            'min_timeout': 1.0,
            'max_timeout': 10.0,
            'cpu_threshold': 70,
            'ram_limit': 80,
            'batch_size': 1000,
            'batch_time': 120,
            'save_interval': 60,
            'smart_sampling': True,
            'random_scan': True,
            'auto_continue': False,
            'targets': ['8.8.8.8', '1.1.1.0/24'],
            'ports': [53],
            'dns_query': 'google.com',
            'dns_type': 'A',
            'scoring_weights': {
                'latency': 0.5,
                'loss': 0.3,
                'alive': 0.2
            }
        }
        
        try:
            with open(path, 'r') as f:
                config = json.load(f)
                default_config.update(config)
        except FileNotFoundError:
            logging.warning(f"Config file {path} not found, using defaults")
        except Exception as e:
            logging.error(f"Error loading config: {e}")
            
        return default_config

    def set_performance_profile(self, profile: str):
        """Set performance parameters based on profile"""
        profiles = {
            'battery': {
                'workers': 50,
                'timeout': 3.0,
                'batch_size': 500
            },
            'balanced': {
                'workers': 100,
                'timeout': 2.0,
                'batch_size': 1000
            },
            'turbo': {
                'workers': 300,
                'timeout': 1.0,
                'batch_size': 2000
            }
        }
        
        if profile in profiles:
            p = profiles[profile]
            self.current_workers = p['workers']
            self.current_timeout = p['timeout']
            self.config['batch_size'] = p['batch_size']
            logging.info(f"Set performance profile: {profile}")

    async def scan_target(self, ip: str, port: int = 53) -> Optional[ResolverResult]:
        """Scan a single IP with DNS resolution"""
        try:
            start_time = time.time()
            resolver = aiodns.DNSResolver(nameservers=[ip])
            resolver.timeout = self.current_timeout
            
            # Test DNS resolution
            result = await resolver.query(
                self.config.get('dns_query', 'google.com'), 
                self.config.get('dns_type', 'A')
            )
            
            latency = (time.time() - start_time) * 1000  # ms
            
            # Calculate score
            score = self.calculate_score(latency, 0)
            
            return ResolverResult(
                ip=ip,
                port=port,
                latency=latency,
                loss=0,
                score=score,
                alive=True,
                timestamp=datetime.now().isoformat()
            )
            
        except asyncio.TimeoutError:
            logging.debug(f"Timeout scanning {ip}")
            return None
        except Exception as e:
            logging.debug(f"Error scanning {ip}: {e}")
            return None

    def calculate_score(self, latency: float, loss: float) -> float:
        """Calculate resolver score based on latency and loss"""
        weights = self.config.get('scoring_weights', {
            'latency': 0.5,
            'loss': 0.3,
            'alive': 0.2
        })
        
        # Normalize latency (lower is better, max 1000ms)
        latency_score = max(0, min(100, 100 - (latency / 10)))
        
        # Loss score (0% loss = 100, 100% loss = 0)
        loss_score = 100 * (1 - loss)
        
        # Alive score
        alive_score = 100
        
        total_score = (
            latency_score * weights.get('latency', 0.5) +
            loss_score * weights.get('loss', 0.3) +
            alive_score * weights.get('alive', 0.2)
        )
        
        return round(total_score, 1)

    async def smart_sampling(self, network: str) -> bool:
        """Sample network before full scan"""
        try:
            net = ipaddress.ip_network(network, strict=False)
            all_ips = list(net.hosts())
            
            if len(all_ips) < 10:
                return True  # Small network, scan all
            
            samples = random.sample(all_ips, min(10, len(all_ips)))
            
            # Scan samples with higher timeout
            old_timeout = self.current_timeout
            self.current_timeout = min(self.current_timeout * 2, self.config.get('max_timeout', 10.0))
            
            tasks = [self.scan_target(str(ip)) for ip in samples]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            self.current_timeout = old_timeout
            
            # If at least 20% of samples are alive, full scan
            alive_count = sum(1 for r in results if r and isinstance(r, ResolverResult) and r.alive)
            return alive_count >= len(samples) * 0.2
            
        except Exception as e:
            logging.error(f"Smart sampling error for {network}: {e}")
            return True  # Default to full scan on error

    def should_skip_network(self, network: str) -> bool:
        """Check if network should be skipped (dead range)"""
        if 'dead_ranges' not in self.state:
            return False
        
        dead_info = self.state['dead_ranges'].get(network, {})
        return dead_info.get('count', 0) >= 3

    def mark_dead_network(self, network: str):
        """Mark network as dead"""
        if 'dead_ranges' not in self.state:
            self.state['dead_ranges'] = {}
        
        if network not in self.state['dead_ranges']:
            self.state['dead_ranges'][network] = {'count': 0, 'last_checked': datetime.now().isoformat()}
        
        self.state['dead_ranges'][network]['count'] += 1
        self.state['dead_ranges'][network]['last_checked'] = datetime.now().isoformat()
        self.save_state()

    async def scan_network(self, network: str):
        """Scan a network with smart sampling"""
        try:
            logging.info(f"Starting scan for network: {network}")
            
            # Handle single IP
            if ':' in network:
                ip, port = network.split(':')
                result = await self.scan_target(ip, int(port))
                if result and result.alive:
                    self.add_result(result)
                return
            
            net = ipaddress.ip_network(network, strict=False)
            
            # Check if network should be skipped
            if self.should_skip_network(network):
                logging.info(f"Skipping {network} (dead range)")
                return
            
            # Smart sampling
            if self.config.get('smart_sampling', True):
                if not await self.smart_sampling(network):
                    logging.info(f"Skipping {network} (sampling failed)")
                    self.mark_dead_network(network)
                    return
            
            # Full scan
            ips = [str(ip) for ip in net.hosts()]
            
            # Shuffle for random scanning
            if self.config.get('random_scan', True):
                random.shuffle(ips)
            
            # Process in batches
            for i in range(0, len(ips), self.config.get('batch_size', 1000)):
                if not self.is_running:
                    break
                    
                batch = ips[i:i + self.config.get('batch_size', 1000)]
                
                # Remove already scanned
                batch = [ip for ip in batch if ip not in self.scanned_ips]
                
                if not batch:
                    continue
                
                # Adaptive workers
                workers = self.adjust_workers()
                
                # Scan batch
                semaphore = asyncio.Semaphore(workers)
                tasks = []
                
                for ip in batch:
                    if not self.is_running:
                        break
                    tasks.append(self.scan_with_semaphore(semaphore, ip))
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results
                for ip, result in zip(batch, results):
                    if isinstance(result, Exception):
                        logging.debug(f"Error scanning {ip}: {result}")
                        self.stats['dead'] += 1
                    elif result and result.alive:
                        self.add_result(result)
                    else:
                        self.stats['dead'] += 1
                    
                    self.stats['scanned'] += 1
                    self.scanned_ips.add(ip)
                
                self.current_batch += 1
                
                # Update stats
                self.update_stats()
                
                # Save state periodically
                if time.time() - self.stats['last_save'] > self.config.get('save_interval', 60):
                    self.save_state()
                    self.stats['last_save'] = time.time()
                
                # Check for batch stop
                if self.config.get('batch_stop', False):
                    if not await self.ask_continue():
                        break
                
                # Display progress
                self.display_progress()
                        
        except KeyboardInterrupt:
            self.safe_stop(None, None)
        except Exception as e:
            logging.error(f"Error scanning {network}: {e}")

    def add_result(self, result: ResolverResult):
        """Add result and save to file"""
        self.results.append(result)
        self.stats['healthy'] += 1
        
        # Save to client_resolvers.txt immediately
        with open('client_resolvers.txt', 'a') as f:
            f.write(f"{result.ip}:{result.port}\n")

    async def scan_with_semaphore(self, semaphore: asyncio.Semaphore, ip: str):
        """Scan with semaphore for rate limiting"""
        async with semaphore:
            return await self.scan_target(ip)

    def adjust_workers(self) -> int:
        """Adaptive worker adjustment (simplified for Android compatibility)"""
        # غیرفعال برای سازگاری با اندروید
        return self.current_workers

    def update_stats(self):
        """Update scanning statistics"""
        elapsed = (datetime.now() - self.stats['start_time']).total_seconds()
        if elapsed > 0:
            self.stats['speed'] = self.stats['scanned'] / elapsed

    def load_state(self) -> Dict:
        """Load saved state"""
        try:
            with open('state.json', 'r') as f:
                state = json.load(f)
                # Restore scanned IPs
                self.scanned_ips = set(state.get('scanned_ips', []))
                return state
        except FileNotFoundError:
            return {
                'scanned_ips': [],
                'results': [],
                'current_batch': 0,
                'dead_ranges': {},
                'last_scan': None
            }
        except Exception as e:
            logging.error(f"Error loading state: {e}")
            return {
                'scanned_ips': [],
                'results': [],
                'current_batch': 0,
                'dead_ranges': {},
                'last_scan': None
            }

    def save_state(self):
        """Save current state"""
        try:
            state = {
                'scanned_ips': list(self.scanned_ips),
                'results': [asdict(r) for r in self.results],
                'current_batch': self.current_batch,
                'dead_ranges': self.state.get('dead_ranges', {}),
                'last_scan': datetime.now().isoformat()
            }
            
            with open('state.json', 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving state: {e}")

    def safe_stop(self, signum, frame):
        """Handle Ctrl+C gracefully"""
        print("\n\n🛑 Safely stopping... Saving state...")
        logging.info("Safe stop initiated")
        self.is_running = False
        self.save_state()
        print("✅ State saved successfully")
        sys.exit(0)

    async def ask_continue(self) -> bool:
        """Ask user to continue (mobile mode)"""
        if self.config.get('auto_continue', False):
            return True
        
        response = input("\nContinue scanning? (y/n): ").lower()
        return response == 'y'

    def generate_report(self):
        """Generate CSV report"""
        try:
            with open('scan_report.csv', 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['IP', 'Port', 'Latency', 'Loss', 'Score', 'Alive', 'Timestamp'])
                
                for result in self.results:
                    writer.writerow([
                        result.ip,
                        result.port,
                        result.latency,
                        result.loss,
                        result.score,
                        result.alive,
                        result.timestamp
                    ])
            logging.info("Report generated: scan_report.csv")
        except Exception as e:
            logging.error(f"Error generating report: {e}")

    def display_dashboard(self):
        """Display real-time dashboard"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
        elapsed = (datetime.now() - self.stats['start_time']).total_seconds()
        remaining = self.calculate_remaining()
        
        print("=" * 70)
        print("  🚀 MJA OpenResolver Scanner v1.0")
        print("=" * 70)
        print(f"  Platform: {self.detect_platform()}")
        print(f"  Profile: {self.config.get('profile', 'balanced').title()}")
        print(f"  Workers: {self.current_workers}")
        print(f"  CPU: {self.get_cpu_usage()}%")
        print(f"  RAM: {self.get_ram_usage()}%")
        print("─" * 70)
        print(f"  Batch: {self.current_batch}")
        print(f"  Current Range: {self.config.get('targets', [''])[0]}")
        print("─" * 70)
        print(f"  Scanned: {self.stats['scanned']:,}")
        print(f"  Healthy: {self.stats['healthy']:,} 🟢")
        print(f"  Dead: {self.stats['dead']:,} 🔴")
        print("─" * 70)
        print(f"  Speed: {self.stats['speed']:.2f} IPs/sec")
        print(f"  Elapsed: {self.format_time(elapsed)}")
        print(f"  Remaining: {self.format_time(remaining)}")
        print("=" * 70)
        print("  Press Ctrl+C to stop safely")

    def display_progress(self):
        """Display progress line"""
        elapsed = (datetime.now() - self.stats['start_time']).total_seconds()
        progress = (self.stats['scanned'] / self.total_ips_to_scan * 100) if self.total_ips_to_scan > 0 else 0
        
        print(f"\r  Progress: {progress:.1f}% | Scanned: {self.stats['scanned']:,} | "
              f"Healthy: {self.stats['healthy']:,} | Speed: {self.stats['speed']:.1f} ips/sec", end='')

    def detect_platform(self) -> str:
        """Auto-detect platform"""
        if sys.platform.startswith('win'):
            return 'Windows'
        elif sys.platform.startswith('linux'):
            if 'android' in sys.platform.lower():
                return 'Android (Termux)'
            return 'Linux'
        elif sys.platform.startswith('darwin'):
            return 'macOS'
        return 'Unknown'

    def get_cpu_usage(self) -> str:
        """Get CPU usage"""
        return "N/A"

    def get_ram_usage(self) -> str:
        """Get RAM usage"""
        return "N/A"

    def format_time(self, seconds: float) -> str:
        """Format time in HH:MM:SS"""
        if seconds < 0:
            seconds = 0
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def calculate_remaining(self) -> float:
        """Estimate remaining time"""
        if self.stats['speed'] > 0:
            remaining_ips = self.total_ips_to_scan - self.stats['scanned']
            return remaining_ips / self.stats['speed']
        return 0
