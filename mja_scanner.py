#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MJA OpenResolver Scanner v1.0 - Socket Version (No external dependencies)
"""

import asyncio
import ipaddress
import json
import random
import time
import os
import sys
import signal
import csv
import socket
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass, asdict
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
    latency: float = 0.0
    loss: float = 0.0
    score: float = 0.0
    alive: bool = False
    timestamp: str = ""

class MJAScanner:
    def __init__(self, config_path: str = "config.json"):
        self.config = self.load_config(config_path)
        self.state = self.load_state()
        self.results: List[ResolverResult] = []
        self.scanned_ips: Set[str] = set()
        self.is_running = True
        self.current_batch = 0
        self.total_ips_to_scan = 0
        
        self.current_workers = self.config.get('initial_workers', 100)
        self.current_timeout = self.config.get('initial_timeout', 3.0)
        
        self.stats = {
            'scanned': 0,
            'healthy': 0,
            'dead': 0,
            'speed': 0,
            'start_time': datetime.now(),
            'last_save': datetime.now()
        }
        
        signal.signal(signal.SIGINT, self.safe_stop)
        signal.signal(signal.SIGTERM, self.safe_stop)
        self.calculate_total_ips()
        
        # DNS query for testing
        self.dns_query = self.config.get('dns_query', 'google.com')
        self.dns_port = self.config.get('ports', [53])[0]
        
        # Build DNS query packet
        self.dns_query_packet = self.build_dns_query(self.dns_query)

    def build_dns_query(self, domain: str) -> bytes:
        """ساخت پکت DNS query برای تست"""
        parts = domain.split('.')
        query = b''
        for part in parts:
            query += bytes([len(part)]) + part.encode()
        query += b'\x00'
        
        header = b'\xAA\xAA\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00'
        return header + query + b'\x00\x01\x00\x01'

    def calculate_total_ips(self):
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
        default_config = {
            'profile': 'balanced',
            'initial_workers': 100,
            'min_workers': 20,
            'max_workers': 500,
            'initial_timeout': 3.0,
            'min_timeout': 1.0,
            'max_timeout': 10.0,
            'batch_size': 1000,
            'save_interval': 60,
            'smart_sampling': True,
            'random_scan': True,
            'targets': ['8.8.8.8', '1.1.1.0/24'],
            'ports': [53],
            'dns_query': 'google.com',
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
        except:
            pass
            
        return default_config

    async def scan_target(self, ip: str, port: int = 53) -> Optional[ResolverResult]:
        """اسکن با socket (بدون کتابخانه خارجی)"""
        try:
            start_time = time.time()
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(self.current_timeout)
            
            try:
                sock.sendto(self.dns_query_packet, (ip, port))
                data, _ = sock.recvfrom(512)
                
                latency = (time.time() - start_time) * 1000  # ms
                
                if len(data) >= 12:
                    response_code = data[3] & 0x0F
                    if response_code == 0:
                        score = self.calculate_score(latency, 0)
                        return ResolverResult(
                            ip=ip,
                            latency=latency,
                            loss=0,
                            score=score,
                            alive=True,
                            timestamp=datetime.now().isoformat()
                        )
                        
            except socket.timeout:
                pass
            except Exception:
                pass
            finally:
                sock.close()
                
            return None
            
        except Exception as e:
            logging.debug(f"Error scanning {ip}: {e}")
            return None

    def calculate_score(self, latency: float, loss: float) -> float:
        weights = self.config.get('scoring_weights', {
            'latency': 0.5,
            'loss': 0.3,
            'alive': 0.2
        })
        
        latency_score = max(0, min(100, 100 - (latency / 10)))
        loss_score = 100 * (1 - loss)
        alive_score = 100
        
        total_score = (
            latency_score * weights.get('latency', 0.5) +
            loss_score * weights.get('loss', 0.3) +
            alive_score * weights.get('alive', 0.2)
        )
        
        return round(total_score, 1)

    async def smart_sampling(self, network: str) -> bool:
        try:
            net = ipaddress.ip_network(network, strict=False)
            all_ips = list(net.hosts())
            
            if len(all_ips) < 10:
                return True
            
            samples = random.sample(all_ips, min(10, len(all_ips)))
            
            old_timeout = self.current_timeout
            self.current_timeout = min(self.current_timeout * 2, self.config.get('max_timeout', 10.0))
            
            tasks = [self.scan_target(str(ip)) for ip in samples]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            self.current_timeout = old_timeout
            
            alive_count = sum(1 for r in results if r and isinstance(r, ResolverResult) and r.alive)
            return alive_count >= len(samples) * 0.2
            
        except Exception as e:
            logging.error(f"Smart sampling error: {e}")
            return True

    async def scan_network(self, network: str):
        try:
            logging.info(f"Starting scan: {network}")
            
            if ':' in network:
                ip, port = network.split(':')
                result = await self.scan_target(ip, int(port))
                if result and result.alive:
                    self.add_result(result)
                return
            
            net = ipaddress.ip_network(network, strict=False)
            
            if self.config.get('smart_sampling', True):
                if not await self.smart_sampling(network):
                    logging.info(f"Skipping {network} (sampling failed)")
                    return
            
            ips = [str(ip) for ip in net.hosts()]
            
            if self.config.get('random_scan', True):
                random.shuffle(ips)
            
            for i in range(0, len(ips), self.config.get('batch_size', 1000)):
                if not self.is_running:
                    break
                    
                batch = ips[i:i + self.config.get('batch_size', 1000)]
                batch = [ip for ip in batch if ip not in self.scanned_ips]
                
                if not batch:
                    continue
                
                semaphore = asyncio.Semaphore(self.current_workers)
                tasks = []
                
                for ip in batch:
                    if not self.is_running:
                        break
                    tasks.append(self.scan_with_semaphore(semaphore, ip))
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for ip, result in zip(batch, results):
                    if isinstance(result, Exception):
                        self.stats['dead'] += 1
                    elif result and result.alive:
                        self.add_result(result)
                    else:
                        self.stats['dead'] += 1
                    
                    self.stats['scanned'] += 1
                    self.scanned_ips.add(ip)
                
                self.current_batch += 1
                self.update_stats()
                
                if time.time() - self.stats['last_save'] > self.config.get('save_interval', 60):
                    self.save_state()
                    self.stats['last_save'] = time.time()
                
                self.display_progress()
                        
        except KeyboardInterrupt:
            self.safe_stop(None, None)
        except Exception as e:
            logging.error(f"Error scanning {network}: {e}")

    def add_result(self, result: ResolverResult):
        """Add result and save to file (بدون پورت)"""
        self.results.append(result)
        self.stats['healthy'] += 1
        
        # Save to client_resolvers.txt immediately (فقط IP)
        with open('client_resolvers.txt', 'a') as f:
            f.write(f"{result.ip}\n")

    async def scan_with_semaphore(self, semaphore: asyncio.Semaphore, ip: str):
        async with semaphore:
            return await self.scan_target(ip)

    def adjust_workers(self) -> int:
        return self.current_workers

    def update_stats(self):
        elapsed = (datetime.now() - self.stats['start_time']).total_seconds()
        if elapsed > 0:
            self.stats['speed'] = self.stats['scanned'] / elapsed

    def load_state(self) -> Dict:
        try:
            with open('state.json', 'r') as f:
                state = json.load(f)
                self.scanned_ips = set(state.get('scanned_ips', []))
                return state
        except:
            return {'scanned_ips': [], 'results': [], 'dead_ranges': {}}

    def save_state(self):
        try:
            state = {
                'scanned_ips': list(self.scanned_ips),
                'results': [asdict(r) for r in self.results],
                'current_batch': self.current_batch,
                'dead_ranges': self.state.get('dead_ranges', {})
            }
            with open('state.json', 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving state: {e}")

    def safe_stop(self, signum, frame):
        print("\n\n🛑 Safely stopping... Saving state...")
        self.is_running = False
        self.save_state()
        print("✅ State saved successfully")
        sys.exit(0)

    def generate_report(self):
        """Generate CSV report (بدون پورت)"""
        try:
            with open('scan_report.csv', 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['IP', 'Latency', 'Loss', 'Score', 'Alive', 'Timestamp'])
                for result in self.results:
                    writer.writerow([
                        result.ip,
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
        os.system('cls' if os.name == 'nt' else 'clear')
        elapsed = (datetime.now() - self.stats['start_time']).total_seconds()
        remaining = self.calculate_remaining()
        
        print("=" * 70)
        print("  🚀 MJA OpenResolver Scanner v1.0 (Socket Edition)")
        print("=" * 70)
        print(f"  Platform: {self.detect_platform()}")
        print(f"  Profile: {self.config.get('profile', 'balanced').title()}")
        print(f"  Workers: {self.current_workers}")
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
        progress = (self.stats['scanned'] / self.total_ips_to_scan * 100) if self.total_ips_to_scan > 0 else 0
        print(f"\r  Progress: {progress:.1f}% | Scanned: {self.stats['scanned']:,} | "
              f"Healthy: {self.stats['healthy']:,} | Speed: {self.stats['speed']:.1f} ips/sec", end='')

    def detect_platform(self) -> str:
        if sys.platform.startswith('win'):
            return 'Windows'
        elif sys.platform.startswith('linux'):
            if 'android' in sys.platform.lower():
                return 'Android (Termux)'
            return 'Linux'
        elif sys.platform.startswith('darwin'):
            return 'macOS'
        return 'Unknown'

    def format_time(self, seconds: float) -> str:
        if seconds < 0:
            seconds = 0
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def calculate_remaining(self) -> float:
        if self.stats['speed'] > 0:
            remaining_ips = self.total_ips_to_scan - self.stats['scanned']
            return remaining_ips / self.stats['speed']
        return 0
