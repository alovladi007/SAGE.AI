"""
Load Testing Script for SAGE.AI Academic Integrity Platform
backend/load_test.py

Tests API performance under concurrent load.
"""

import asyncio
import aiohttp
import time
import json
from typing import List, Dict, Any
from dataclasses import dataclass, field
from statistics import mean, median, stdev
import sys


@dataclass
class LoadTestResult:
    """Results from a load test"""
    endpoint: str
    total_requests: int
    successful: int = 0
    failed: int = 0
    response_times: List[float] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    
    @property
    def success_rate(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return (self.successful / self.total_requests) * 100
    
    @property
    def avg_response_time(self) -> float:
        return mean(self.response_times) if self.response_times else 0.0
    
    @property
    def median_response_time(self) -> float:
        return median(self.response_times) if self.response_times else 0.0
    
    @property
    def p95_response_time(self) -> float:
        if not self.response_times:
            return 0.0
        sorted_times = sorted(self.response_times)
        index = int(len(sorted_times) * 0.95)
        return sorted_times[index]
    
    @property
    def p99_response_time(self) -> float:
        if not self.response_times:
            return 0.0
        sorted_times = sorted(self.response_times)
        index = int(len(sorted_times) * 0.99)
        return sorted_times[index]


class LoadTester:
    """Handles load testing for the platform"""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.results: Dict[str, LoadTestResult] = {}
    
    async def test_signup(self, session: aiohttp.ClientSession, user_num: int) -> tuple[bool, float]:
        """Test user signup endpoint"""
        start = time.time()
        try:
            async with session.post(
                f"{self.base_url}/api/auth/signup",
                json={
                    "email": f"loadtest{user_num}@example.com",
                    "password": "LoadTest123",
                    "full_name": f"Load Test User {user_num}",
                    "institution": "Load Test University"
                }
            ) as response:
                duration = time.time() - start
                success = response.status == 200
                return success, duration
        except Exception as e:
            duration = time.time() - start
            return False, duration
    
    async def test_login(self, session: aiohttp.ClientSession, user_num: int) -> tuple[bool, float, str]:
        """Test user login endpoint"""
        start = time.time()
        try:
            async with session.post(
                f"{self.base_url}/api/auth/login",
                json={
                    "email": f"loadtest{user_num}@example.com",
                    "password": "LoadTest123"
                }
            ) as response:
                duration = time.time() - start
                if response.status == 200:
                    data = await response.json()
                    token = data.get("access_token", "")
                    return True, duration, token
                return False, duration, ""
        except Exception as e:
            duration = time.time() - start
            return False, duration, ""
    
    async def test_me_endpoint(self, session: aiohttp.ClientSession, token: str) -> tuple[bool, float]:
        """Test protected /me endpoint"""
        start = time.time()
        try:
            async with session.get(
                f"{self.base_url}/api/auth/me",
                headers={"Authorization": f"Bearer {token}"}
            ) as response:
                duration = time.time() - start
                success = response.status == 200
                return success, duration
        except Exception as e:
            duration = time.time() - start
            return False, duration
    
    async def test_search(self, session: aiohttp.ClientSession) -> tuple[bool, float]:
        """Test paper search endpoint"""
        start = time.time()
        try:
            async with session.get(
                f"{self.base_url}/api/papers/search?limit=10"
            ) as response:
                duration = time.time() - start
                success = response.status == 200
                return success, duration
        except Exception as e:
            duration = time.time() - start
            return False, duration
    
    async def run_concurrent_signups(self, num_users: int, concurrent: int):
        """Run concurrent signup tests"""
        print(f"\n🔄 Testing {num_users} signups with {concurrent} concurrent requests...")
        
        result = LoadTestResult(
            endpoint="/api/auth/signup",
            total_requests=num_users
        )
        
        async with aiohttp.ClientSession() as session:
            for batch_start in range(0, num_users, concurrent):
                batch_end = min(batch_start + concurrent, num_users)
                tasks = [
                    self.test_signup(session, i)
                    for i in range(batch_start, batch_end)
                ]
                
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for success, duration in batch_results:
                    if success:
                        result.successful += 1
                    else:
                        result.failed += 1
                    result.response_times.append(duration)
        
        self.results["signup"] = result
        return result
    
    async def run_concurrent_logins(self, num_logins: int, concurrent: int):
        """Run concurrent login tests"""
        print(f"\n🔄 Testing {num_logins} logins with {concurrent} concurrent requests...")
        
        result = LoadTestResult(
            endpoint="/api/auth/login",
            total_requests=num_logins
        )
        
        async with aiohttp.ClientSession() as session:
            for batch_start in range(0, num_logins, concurrent):
                batch_end = min(batch_start + concurrent, num_logins)
                tasks = [
                    self.test_login(session, i % 100)  # Reuse first 100 users
                    for i in range(batch_start, batch_end)
                ]
                
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for success, duration, token in batch_results:
                    if success:
                        result.successful += 1
                    else:
                        result.failed += 1
                    result.response_times.append(duration)
        
        self.results["login"] = result
        return result
    
    async def run_concurrent_me_requests(self, num_requests: int, concurrent: int):
        """Run concurrent /me endpoint tests"""
        print(f"\n🔄 Testing {num_requests} /me requests with {concurrent} concurrent requests...")
        
        # First, create a user and get token
        async with aiohttp.ClientSession() as session:
            success, _, token = await self.test_login(session, 0)
            if not success or not token:
                print("❌ Failed to get auth token for /me test")
                return None
        
        result = LoadTestResult(
            endpoint="/api/auth/me",
            total_requests=num_requests
        )
        
        async with aiohttp.ClientSession() as session:
            for batch_start in range(0, num_requests, concurrent):
                batch_end = min(batch_start + concurrent, num_requests)
                tasks = [
                    self.test_me_endpoint(session, token)
                    for _ in range(batch_start, batch_end)
                ]
                
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for success, duration in batch_results:
                    if success:
                        result.successful += 1
                    else:
                        result.failed += 1
                    result.response_times.append(duration)
        
        self.results["me"] = result
        return result
    
    async def run_concurrent_searches(self, num_searches: int, concurrent: int):
        """Run concurrent search tests"""
        print(f"\n🔄 Testing {num_searches} searches with {concurrent} concurrent requests...")
        
        result = LoadTestResult(
            endpoint="/api/papers/search",
            total_requests=num_searches
        )
        
        async with aiohttp.ClientSession() as session:
            for batch_start in range(0, num_searches, concurrent):
                batch_end = min(batch_start + concurrent, num_searches)
                tasks = [
                    self.test_search(session)
                    for _ in range(batch_start, batch_end)
                ]
                
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for success, duration in batch_results:
                    if success:
                        result.successful += 1
                    else:
                        result.failed += 1
                    result.response_times.append(duration)
        
        self.results["search"] = result
        return result
    
    def print_results(self):
        """Print formatted test results"""
        print("\n" + "=" * 80)
        print("LOAD TEST RESULTS")
        print("=" * 80)
        
        for name, result in self.results.items():
            print(f"\n📊 {result.endpoint}")
            print(f"   Total Requests:     {result.total_requests}")
            print(f"   Successful:         {result.successful} ({result.success_rate:.1f}%)")
            print(f"   Failed:             {result.failed}")
            print(f"   Avg Response Time:  {result.avg_response_time*1000:.2f}ms")
            print(f"   Median:             {result.median_response_time*1000:.2f}ms")
            print(f"   P95:                {result.p95_response_time*1000:.2f}ms")
            print(f"   P99:                {result.p99_response_time*1000:.2f}ms")
        
        print("\n" + "=" * 80)
        
        # Overall summary
        total_requests = sum(r.total_requests for r in self.results.values())
        total_successful = sum(r.successful for r in self.results.values())
        overall_success_rate = (total_successful / total_requests * 100) if total_requests > 0 else 0
        
        print(f"\n✅ OVERALL SUCCESS RATE: {overall_success_rate:.1f}% ({total_successful}/{total_requests})")
        
        if overall_success_rate >= 99:
            print("🎉 EXCELLENT - System handles load very well!")
        elif overall_success_rate >= 95:
            print("✅ GOOD - System performs well under load")
        elif overall_success_rate >= 90:
            print("⚠️  ACCEPTABLE - Some issues under load")
        else:
            print("❌ POOR - System struggles under load")


async def main():
    """Run load tests"""
    print("🚀 SAGE.AI Load Testing")
    print("=" * 80)
    
    tester = LoadTester()
    
    # Test 1: User Signup (100 users, 10 concurrent)
    await tester.run_concurrent_signups(num_users=100, concurrent=10)
    
    # Test 2: User Login (200 logins, 20 concurrent)
    await tester.run_concurrent_logins(num_logins=200, concurrent=20)
    
    # Test 3: Protected endpoint (500 requests, 50 concurrent)
    await tester.run_concurrent_me_requests(num_requests=500, concurrent=50)
    
    # Test 4: Search endpoint (1000 requests, 100 concurrent)
    await tester.run_concurrent_searches(num_searches=1000, concurrent=100)
    
    # Print results
    tester.print_results()


if __name__ == "__main__":
    asyncio.run(main())
