#!/usr/bin/env python3
"""
Solana Ecosystem Data Collector
Fetches real-time data from public APIs to enrich narrative analysis.

Part of: Solana Narrative Detection Tool
Agent: copilot-superteam-agent
"""

import json
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from typing import Dict, List, Optional


class SolanaDataCollector:
    """Collects real data from public Solana ecosystem APIs"""

    def __init__(self):
        self.collected_data = {}
        self.errors = []

    def _fetch_json(self, url: str, timeout: int = 10) -> Optional[Dict]:
        """Fetch JSON from URL with error handling"""
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'SolanaNarrativeDetector/1.0',
                'Accept': 'application/json'
            })
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode())
        except Exception as e:
            self.errors.append(f"Error fetching {url}: {str(e)}")
            return None

    def fetch_solana_tps(self) -> Optional[Dict]:
        """Fetch Solana network TPS and performance data"""
        print("  → Fetching Solana network stats...")
        data = self._fetch_json("https://api.mainnet-beta.solana.com", timeout=10)
        # Use public RPC for basic stats
        try:
            payload = json.dumps({
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getRecentPerformanceSamples",
                "params": [5]
            }).encode()
            req = urllib.request.Request(
                "https://api.mainnet-beta.solana.com",
                data=payload,
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': 'SolanaNarrativeDetector/1.0'
                }
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                result = json.loads(resp.read().decode())
                if 'result' in result and result['result']:
                    samples = result['result']
                    avg_tps = sum(s['numTransactions'] / s['samplePeriodSecs'] for s in samples) / len(samples)
                    self.collected_data['solana_tps'] = {
                        'average_tps': round(avg_tps, 2),
                        'samples': len(samples),
                        'fetched_at': datetime.now().isoformat()
                    }
                    print(f"    ✓ Average TPS: {round(avg_tps, 2)}")
                    return self.collected_data['solana_tps']
        except Exception as e:
            self.errors.append(f"TPS fetch error: {str(e)}")
            print(f"    ✗ Error: {str(e)[:60]}")
        return None

    def fetch_defi_tvl(self) -> Optional[Dict]:
        """Fetch Solana DeFi TVL from DeFiLlama"""
        print("  → Fetching Solana DeFi TVL...")
        data = self._fetch_json("https://api.llama.fi/v2/chains")
        if data:
            solana = next((c for c in data if c.get('name', '').lower() == 'solana'), None)
            if solana:
                self.collected_data['defi_tvl'] = {
                    'tvl': solana.get('tvl', 0),
                    'tvl_formatted': f"${solana.get('tvl', 0) / 1e9:.2f}B",
                    'fetched_at': datetime.now().isoformat()
                }
                print(f"    ✓ Solana TVL: ${solana.get('tvl', 0) / 1e9:.2f}B")
                return self.collected_data['defi_tvl']
        print("    ✗ Could not fetch TVL data")
        return None

    def fetch_solana_protocols(self) -> Optional[Dict]:
        """Fetch top Solana protocols from DeFiLlama"""
        print("  → Fetching top Solana protocols...")
        data = self._fetch_json("https://api.llama.fi/protocols")
        if data:
            solana_protocols = [
                p for p in data
                if 'Solana' in (p.get('chains') or [])
            ]
            solana_protocols.sort(key=lambda x: x.get('tvl', 0), reverse=True)
            top_10 = [
                {
                    'name': p.get('name'),
                    'tvl': round(p.get('tvl', 0) / 1e6, 2),
                    'category': p.get('category'),
                    'change_1d': p.get('change_1d'),
                    'change_7d': p.get('change_7d')
                }
                for p in solana_protocols[:10]
            ]
            self.collected_data['top_protocols'] = {
                'total_solana_protocols': len(solana_protocols),
                'top_10': top_10,
                'fetched_at': datetime.now().isoformat()
            }
            print(f"    ✓ Found {len(solana_protocols)} Solana protocols")
            return self.collected_data['top_protocols']
        print("    ✗ Could not fetch protocols")
        return None

    def fetch_github_trends(self) -> Optional[Dict]:
        """Fetch trending Solana-related repos from GitHub"""
        print("  → Fetching GitHub Solana trends...")
        # Search for recently created Solana repos
        two_weeks_ago = (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d')
        url = f"https://api.github.com/search/repositories?q=solana+created:>{two_weeks_ago}&sort=stars&order=desc&per_page=10"
        data = self._fetch_json(url, timeout=15)
        if data and 'items' in data:
            repos = [
                {
                    'name': r.get('full_name'),
                    'description': (r.get('description') or '')[:100],
                    'stars': r.get('stargazers_count'),
                    'language': r.get('language'),
                    'created': r.get('created_at', '')[:10],
                    'topics': r.get('topics', [])[:5]
                }
                for r in data['items'][:10]
            ]
            self.collected_data['github_trends'] = {
                'total_new_repos': data.get('total_count', 0),
                'trending_repos': repos,
                'search_period': f"Since {two_weeks_ago}",
                'fetched_at': datetime.now().isoformat()
            }
            print(f"    ✓ {data.get('total_count', 0)} new Solana repos in 2 weeks")
            return self.collected_data['github_trends']
        print("    ✗ Could not fetch GitHub data")
        return None

    def fetch_github_agent_repos(self) -> Optional[Dict]:
        """Fetch AI agent + Solana repos from GitHub"""
        print("  → Fetching AI Agent + Solana repos...")
        url = "https://api.github.com/search/repositories?q=solana+agent+AI&sort=updated&order=desc&per_page=10"
        data = self._fetch_json(url, timeout=15)
        if data and 'items' in data:
            repos = [
                {
                    'name': r.get('full_name'),
                    'description': (r.get('description') or '')[:100],
                    'stars': r.get('stargazers_count'),
                    'updated': r.get('updated_at', '')[:10]
                }
                for r in data['items'][:10]
            ]
            self.collected_data['agent_repos'] = {
                'total_count': data.get('total_count', 0),
                'repos': repos,
                'fetched_at': datetime.now().isoformat()
            }
            print(f"    ✓ {data.get('total_count', 0)} AI agent + Solana repos found")
            return self.collected_data['agent_repos']
        print("    ✗ Could not fetch agent repos")
        return None

    def fetch_solana_price(self) -> Optional[Dict]:
        """Fetch SOL price from CoinGecko"""
        print("  → Fetching SOL price...")
        data = self._fetch_json(
            "https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd&include_24hr_change=true&include_market_cap=true"
        )
        if data and 'solana' in data:
            sol = data['solana']
            self.collected_data['sol_price'] = {
                'price': sol.get('usd'),
                'change_24h': sol.get('usd_24h_change'),
                'market_cap': sol.get('usd_market_cap'),
                'fetched_at': datetime.now().isoformat()
            }
            price = sol.get('usd', 0)
            change = sol.get('usd_24h_change', 0)
            print(f"    ✓ SOL: ${price:.2f} ({change:+.2f}% 24h)")
            return self.collected_data['sol_price']
        print("    ✗ Could not fetch price")
        return None

    def collect_all(self) -> Dict:
        """Run all data collection tasks"""
        print("\n📡 Collecting real-time Solana ecosystem data...\n")
        
        self.fetch_solana_price()
        self.fetch_solana_tps()
        self.fetch_defi_tvl()
        self.fetch_solana_protocols()
        self.fetch_github_trends()
        self.fetch_github_agent_repos()
        
        self.collected_data['metadata'] = {
            'collected_at': datetime.now().isoformat(),
            'sources_queried': 6,
            'successful': len(self.collected_data) - 1,  # exclude metadata
            'errors': len(self.errors)
        }
        
        print(f"\n✅ Data collection complete: {len(self.collected_data)-1} sources, {len(self.errors)} errors")
        return self.collected_data

    def save(self, filepath: str = "live_data.json"):
        """Save collected data to JSON file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.collected_data, f, indent=2, ensure_ascii=False)
        print(f"📦 Saved to {filepath}")
        return filepath


def main():
    collector = SolanaDataCollector()
    data = collector.collect_all()
    collector.save()
    
    if collector.errors:
        print(f"\n⚠️ Errors encountered:")
        for err in collector.errors:
            print(f"  - {err[:80]}")


if __name__ == "__main__":
    main()
