#!/usr/bin/env python3
"""
Comprehensive test suite for the FAQ chat system
Handles AI response variability and fallback scenarios
"""

import requests
import json
import time
import re
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class TestCase:
    """Test case structure"""
    name: str
    question: str
    expected_keywords: List[str]
    expected_topics: List[str]
    should_create_ticket: bool = False
    max_response_length: int = 500

class ChatSystemTester:
    """Test suite for the chat system"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results = []
    
    def test_endpoint_health(self) -> bool:
        """Test if the backend is running"""
        try:
            response = requests.get(f"{self.base_url}/")
            if response.status_code == 200:
                print("✅ Backend health check passed")
                return True
            else:
                print(f"❌ Backend health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Backend health check failed: {e}")
            return False
    
    def test_chat_response(self, test_case: TestCase) -> Dict[str, Any]:
        """Test a single chat response"""
        print(f"\n🧪 Testing: {test_case.name}")
        print(f"   Question: {test_case.question}")
        
        try:
            response = requests.post(
                f"{self.base_url}/chat",
                json={
                    "message": test_case.question,
                    "user_contact": "test@example.com"
                },
                timeout=10
            )
            
            if response.status_code != 200:
                print(f"   ❌ HTTP Error: {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
            
            data = response.json()
            response_text = data.get("response", "").lower()
            ticket_created = data.get("ticket_created", False)
            
            # Test 1: Check if response contains expected keywords
            keyword_matches = []
            for keyword in test_case.expected_keywords:
                if keyword.lower() in response_text:
                    keyword_matches.append(keyword)
            
            # Test 2: Check if response contains expected topics
            topic_matches = []
            for topic in test_case.expected_topics:
                if topic.lower() in response_text:
                    topic_matches.append(topic)
            
            # Test 3: Check response length
            response_length = len(data.get("response", ""))
            length_ok = response_length <= test_case.max_response_length
            
            # Test 4: Check ticket creation
            ticket_ok = ticket_created == test_case.should_create_ticket
            
            # Calculate score
            keyword_score = len(keyword_matches) / len(test_case.expected_keywords) if test_case.expected_keywords else 1
            topic_score = len(topic_matches) / len(test_case.expected_topics) if test_case.expected_topics else 1
            overall_score = (keyword_score + topic_score + (1 if length_ok else 0) + (1 if ticket_ok else 0)) / 4
            
            success = overall_score >= 0.75  # 75% threshold
            
            result = {
                "success": success,
                "score": overall_score,
                "keyword_matches": keyword_matches,
                "topic_matches": topic_matches,
                "response_length": response_length,
                "ticket_created": ticket_created,
                "response_preview": data.get("response", "")[:100] + "..." if len(data.get("response", "")) > 100 else data.get("response", "")
            }
            
            if success:
                print(f"   ✅ Passed (Score: {overall_score:.2f})")
            else:
                print(f"   ❌ Failed (Score: {overall_score:.2f})")
                print(f"      Keywords found: {keyword_matches}")
                print(f"      Topics found: {topic_matches}")
                print(f"      Length: {response_length}/{test_case.max_response_length}")
                print(f"      Ticket: {ticket_created} (expected: {test_case.should_create_ticket})")
            
            return result
            
        except Exception as e:
            print(f"   ❌ Test failed: {e}")
            return {"success": False, "error": str(e)}
    
    def test_variations(self, base_question: str, variations: List[str], expected_keywords: List[str]) -> Dict[str, Any]:
        """Test multiple variations of the same question"""
        print(f"\n🔄 Testing variations of: {base_question}")
        
        results = []
        for i, variation in enumerate(variations, 1):
            test_case = TestCase(
                name=f"Variation {i}",
                question=variation,
                expected_keywords=expected_keywords,
                expected_topics=[],
                should_create_ticket=False
            )
            
            result = self.test_chat_response(test_case)
            results.append(result)
            
            # Add delay to avoid rate limiting
            time.sleep(1)
        
        # Calculate consistency score
        successful_tests = sum(1 for r in results if r.get("success", False))
        consistency_score = successful_tests / len(results)
        
        print(f"   📊 Consistency Score: {consistency_score:.2f} ({successful_tests}/{len(results)} passed)")
        
        return {
            "consistency_score": consistency_score,
            "results": results
        }
    
    def run_comprehensive_tests(self) -> Dict[str, Any]:
        """Run all comprehensive tests"""
        print("🚀 Starting Comprehensive Chat System Tests")
        print("=" * 60)
        
        # Test cases covering different scenarios
        test_cases = [
            TestCase(
                name="Password Reset",
                question="How do I reset my password?",
                expected_keywords=["password", "reset", "forgot", "email", "link"],
                expected_topics=["account management"],
                should_create_ticket=False
            ),
            TestCase(
                name="Account Creation",
                question="How do I create an account?",
                expected_keywords=["account", "create", "sign up", "email", "verify"],
                expected_topics=["account management"],
                should_create_ticket=False
            ),
            TestCase(
                name="Billing Information",
                question="What payment methods do you accept?",
                expected_keywords=["payment", "credit card", "paypal", "billing"],
                expected_topics=["billing"],
                should_create_ticket=False
            ),
            TestCase(
                name="File Upload",
                question="How do I upload files?",
                expected_keywords=["upload", "file", "drag", "drop", "browse"],
                expected_topics=["product features"],
                should_create_ticket=False
            ),
            TestCase(
                name="Document Sharing",
                question="Can I share documents with others?",
                expected_keywords=["share", "document", "permission", "email"],
                expected_topics=["product features"],
                should_create_ticket=False
            ),
            TestCase(
                name="Mobile App",
                question="Do you have a mobile app?",
                expected_keywords=["mobile", "app", "ios", "android", "download"],
                expected_topics=["mobile access"],
                should_create_ticket=False
            ),
            TestCase(
                name="Security",
                question="Is my data secure?",
                expected_keywords=["security", "encryption", "data", "secure"],
                expected_topics=["data and privacy"],
                should_create_ticket=False
            ),
            TestCase(
                name="Unknown Question",
                question="How do I build a rocket ship?",
                expected_keywords=[],  # No specific keywords expected
                expected_topics=[],
                should_create_ticket=True  # Should create ticket for unknown topics
            )
        ]
        
        # Run individual tests
        individual_results = []
        for test_case in test_cases:
            result = self.test_chat_response(test_case)
            individual_results.append(result)
            time.sleep(1)  # Avoid rate limiting
        
        # Test variations
        password_variations = [
            "How do I reset my password?",
            "I forgot my password, what should I do?",
            "Can you help me reset my password?",
            "What's the process for password reset?",
            "I need to change my password"
        ]
        
        variation_results = self.test_variations(
            "password reset",
            password_variations,
            ["password", "reset", "email", "link"]
        )
        
        # Calculate overall statistics
        successful_individual = sum(1 for r in individual_results if r.get("success", False))
        total_individual = len(individual_results)
        overall_score = successful_individual / total_individual if total_individual > 0 else 0
        
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        print(f"✅ Individual Tests: {successful_individual}/{total_individual} passed ({overall_score:.2%})")
        print(f"🔄 Variation Consistency: {variation_results['consistency_score']:.2%}")
        
        # Overall assessment
        if overall_score >= 0.8 and variation_results['consistency_score'] >= 0.8:
            print("🎉 EXCELLENT: System is working very well!")
        elif overall_score >= 0.6 and variation_results['consistency_score'] >= 0.6:
            print("✅ GOOD: System is working well with minor issues")
        else:
            print("⚠️ NEEDS IMPROVEMENT: System has significant issues")
        
        return {
            "overall_score": overall_score,
            "consistency_score": variation_results['consistency_score'],
            "individual_results": individual_results,
            "variation_results": variation_results
        }

def main():
    """Run the test suite"""
    tester = ChatSystemTester()
    
    # Check if backend is running
    if not tester.test_endpoint_health():
        print("❌ Backend is not running. Please start the server first.")
        return
    
    # Run comprehensive tests
    results = tester.run_comprehensive_tests()
    
    # Save results to file
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Detailed results saved to test_results.json")

if __name__ == "__main__":
    main() 