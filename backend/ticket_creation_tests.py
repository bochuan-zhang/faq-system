#!/usr/bin/env python3
"""
Dedicated tests for ticket creation functionality
Tests that unknown questions properly create tickets
"""

import requests
import json
import time
from typing import List, Dict, Any

class TicketCreationTester:
    """Test ticket creation for unknown questions"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_contact = "test@example.com"
    
    def test_unknown_question_ticket_creation(self, question: str, expected_to_create_ticket: bool = True) -> Dict[str, Any]:
        """Test if an unknown question creates a ticket"""
        print(f"\n🎫 Testing: '{question}'")
        
        try:
            response = requests.post(
                f"{self.base_url}/chat",
                json={"message": question, "user_contact": self.test_contact},
                timeout=10
            )
            
            if response.status_code != 200:
                return {"success": False, "error": f"HTTP {response.status_code}"}
            
            data = response.json()
            ticket_created = data.get("ticket_created", False)
            response_text = data.get("response", "")
            
            # Check if ticket creation matches expectation
            if expected_to_create_ticket:
                if ticket_created:
                    print(f"   ✅ Ticket created (Expected)")
                    success = True
                else:
                    print(f"   ❌ No ticket created (Expected ticket)")
                    success = False
            else:
                if not ticket_created:
                    print(f"   ✅ No ticket created (Expected)")
                    success = True
                else:
                    print(f"   ❌ Ticket created (Expected no ticket)")
                    success = False
            
            return {
                "success": success,
                "question": question,
                "ticket_created": ticket_created,
                "expected_ticket": expected_to_create_ticket,
                "response_preview": response_text[:200] + "..." if len(response_text) > 200 else response_text
            }
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return {"success": False, "error": str(e)}
    
    def run_ticket_creation_tests(self) -> Dict[str, Any]:
        """Run comprehensive ticket creation tests"""
        print("🎫 Starting Ticket Creation Tests")
        print("=" * 60)
        
        # Test cases for questions that should create tickets (unknown questions)
        unknown_questions = [
            "How do I build a rocket ship?",
            "What's the recipe for a nuclear bomb?",
            "How can I hack into someone's account?",
            "Can you help me steal data?",
            "What's the best way to commit fraud?",
            "How do I create a virus?",
            "What's the meaning of life?",
            "How do I time travel?",
            "Can you help me build a teleporter?",
            "What's the secret to immortality?"
        ]
        
        # Test cases for questions that should NOT create tickets (known questions)
        known_questions = [
            "How do I reset my password?",
            "How do I create an account?",
            "What payment methods do you accept?",
            "How do I upload files?",
            "Can I share documents with others?",
            "Do you have a mobile app?",
            "Is my data secure?"
        ]
        
        print("\n🔍 Testing Unknown Questions (Should Create Tickets)")
        print("-" * 50)
        
        unknown_results = []
        for question in unknown_questions:
            result = self.test_unknown_question_ticket_creation(question, expected_to_create_ticket=True)
            unknown_results.append(result)
            time.sleep(1)  # Avoid rate limiting
        
        print("\n✅ Testing Known Questions (Should NOT Create Tickets)")
        print("-" * 50)
        
        known_results = []
        for question in known_questions:
            result = self.test_unknown_question_ticket_creation(question, expected_to_create_ticket=False)
            known_results.append(result)
            time.sleep(1)  # Avoid rate limiting
        
        # Calculate success rates
        unknown_success = sum(1 for r in unknown_results if r.get("success", False))
        known_success = sum(1 for r in known_results if r.get("success", False))
        
        unknown_rate = unknown_success / len(unknown_results) if unknown_results else 0
        known_rate = known_success / len(known_results) if known_results else 0
        
        print("\n" + "=" * 60)
        print("📊 TICKET CREATION TEST RESULTS")
        print("=" * 60)
        print(f"Unknown Questions (Should Create Tickets): {unknown_success}/{len(unknown_results)} ({unknown_rate:.1%})")
        print(f"Known Questions (Should NOT Create Tickets): {known_success}/{len(known_results)} ({known_rate:.1%})")
        
        # Overall assessment
        overall_success = (unknown_rate + known_rate) / 2
        
        if overall_success >= 0.9:
            print("🎉 EXCELLENT: Ticket creation system working perfectly!")
        elif overall_success >= 0.7:
            print("✅ GOOD: Ticket creation system working well")
        elif overall_success >= 0.5:
            print("⚠️ FAIR: Ticket creation system needs improvement")
        else:
            print("❌ POOR: Ticket creation system has significant issues")
        
        return {
            "overall_success_rate": overall_success,
            "unknown_questions": {
                "success_rate": unknown_rate,
                "results": unknown_results
            },
            "known_questions": {
                "success_rate": known_rate,
                "results": known_results
            }
        }
    
    def test_ticket_endpoint(self) -> Dict[str, Any]:
        """Test the ticket endpoint functionality"""
        print("\n🎫 Testing Ticket Endpoint")
        print("-" * 30)
        
        # Test GET /tickets
        try:
            response = requests.get(f"{self.base_url}/tickets")
            if response.status_code == 200:
                tickets = response.json()
                print(f"   ✅ GET /tickets: {len(tickets)} tickets found")
            else:
                print(f"   ❌ GET /tickets: HTTP {response.status_code}")
                return {"success": False}
        except Exception as e:
            print(f"   ❌ GET /tickets: Error - {e}")
            return {"success": False}
        
        # Test POST /ticket (manual ticket creation)
        try:
            test_ticket = {
                "user_question": "Test question for ticket creation",
                "user_contact": self.test_contact
            }
            
            response = requests.post(
                f"{self.base_url}/ticket",
                json=test_ticket
            )
            
            if response.status_code == 200:
                ticket = response.json()
                print(f"   ✅ POST /ticket: Ticket created with ID {ticket.get('id')}")
                return {"success": True, "ticket_id": ticket.get('id')}
            else:
                print(f"   ❌ POST /ticket: HTTP {response.status_code}")
                return {"success": False}
        except Exception as e:
            print(f"   ❌ POST /ticket: Error - {e}")
            return {"success": False}

def main():
    """Run ticket creation tests"""
    tester = TicketCreationTester()
    
    # Check if backend is running
    try:
        response = requests.get(f"{tester.base_url}/")
        if response.status_code != 200:
            print("❌ Backend is not running. Please start the server first.")
            return
    except:
        print("❌ Backend is not running. Please start the server first.")
        return
    
    # Run ticket creation tests
    results = tester.run_ticket_creation_tests()
    
    # Test ticket endpoint
    endpoint_result = tester.test_ticket_endpoint()
    
    # Save results
    with open("ticket_creation_results.json", "w") as f:
        json.dump({
            "ticket_creation_results": results,
            "endpoint_test": endpoint_result
        }, f, indent=2)
    
    print(f"\n📄 Detailed results saved to ticket_creation_results.json")

if __name__ == "__main__":
    main() 