from ticket_generator import TicketGenerator
from ticket_verifier import TicketVerifier
import time
from datetime import datetime, timedelta

def test_offline_verification():
    # Create generator and verifier with same key
    generator = TicketGenerator()
    verifier = TicketVerifier(generator.secret_key)
    
    # Current time
    current_time = int(time.time())
    
    # Generate tickets with different scenarios
    test_cases = [
        {
            "name": "Valid ticket",
            "ticket_id": "VALID123",
            "draw_date": current_time + 7*24*60*60,  # 7 days from now
            "ticket_price": 100,
            "draw_number": 1
        },
        {
            "name": "Expired ticket",
            "ticket_id": "EXPIRED123",
            "draw_date": current_time - 24*60*60,  # 1 day ago
            "ticket_price": 100,
            "draw_number": 2
        },
        {
            "name": "Premium ticket",
            "ticket_id": "PREMIUM123",
            "draw_date": current_time + 14*24*60*60,  # 14 days from now
            "ticket_price": 500,
            "draw_number": 3
        }
    ]
    
    print("Testing Offline Ticket Verification\n")
    
    for test in test_cases:
        print(f"\nTesting: {test['name']}")
        print("-" * 50)
        
        # Generate ticket data
        encoded_data = generator.generate_ticket_data(
            test['ticket_id'],
            test['draw_date'],
            test['ticket_price'],
            test['draw_number']
        )
        
        # Verify ticket
        is_valid, result = verifier.verify_ticket(encoded_data)
        
        print(f"Ticket ID: {test['ticket_id']}")
        print(f"Is Valid: {is_valid}")
        if isinstance(result, dict):
            print("Ticket Details:")
            for key, value in result.items():
                print(f"  {key}: {value}")
        else:
            print(f"Result: {result}")
        
        # Try to verify the same ticket again (should fail)
        if is_valid:
            print("\nTrying to verify same ticket again:")
            is_valid2, result2 = verifier.verify_ticket(encoded_data)
            print(f"Is Valid: {is_valid2}")
            print(f"Result: {result2}")

if __name__ == "__main__":
    test_offline_verification()
