"""
Test script for the receipt splitter API.
Run the server first with: python main.py
Then run this script in another terminal: python test_api.py
"""

import httpx
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"


def print_response(title, response):
    """Pretty print API response"""
    print(f"\n{'=' * 60}")
    print(f"{title}")
    print(f"{'=' * 60}")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Error: {response.text}")
    print()


def create_mock_receipt():
    """Create a mock receipt for testing"""
    return {
        "establishment": "Joe's Diner",
        "date": datetime.now().isoformat(),
        "subtotal": 62.44,
        "tax": 5.62,
        "tip": 10.00,
        "total": 78.06,
        "line_items": [
            {
                "id": "item_1",
                "line_number": 1,
                "desc_clean": "Bacon Burger",
                "price": 12.99,
                "line_total": 12.99,
                "qty": 1,
            },
            {
                "id": "item_2",
                "line_number": 2,
                "desc_clean": "Veggie Burger",
                "price": 10.99,
                "line_total": 10.99,
                "qty": 1,
            },
            {
                "id": "item_3",
                "line_number": 3,
                "desc_clean": "Large Pizza",
                "price": 15.99,
                "line_total": 15.99,
                "qty": 1,
            },
            {
                "id": "item_4",
                "line_number": 4,
                "desc_clean": "Fries",
                "price": 2.99,
                "line_total": 5.98,
                "qty": 2,
            },
            {
                "id": "item_5",
                "line_number": 5,
                "desc_clean": "Caesar Salad",
                "price": 8.99,
                "line_total": 8.99,
                "qty": 1,
            },
            {
                "id": "item_6",
                "line_number": 6,
                "desc_clean": "Nachos",
                "price": 7.50,
                "line_total": 7.50,
                "qty": 1,
            },
        ],
    }


def test_conversation_flow():
    """Test the complete conversation flow"""
    client = httpx.Client(timeout=30.0)

    try:
        # Step 1: Start a conversation
        print("\n🚀 Starting conversation...")
        receipt = create_mock_receipt()
        people = ["You", "Sarah", "Mike"]

        response = client.post(
            f"{BASE_URL}/api/conversation/start",
            json={"receipt": receipt, "people": people},
        )
        print_response("1. START CONVERSATION", response)

        if response.status_code != 200:
            print("❌ Failed to start conversation")
            return

        conversation_id = response.json()["conversation_id"]
        print(f"✅ Conversation started: {conversation_id}")

        # Step 2: Send first message - assign some items
        print("\n💬 Sending message: 'I had the bacon burger and fries'")
        response = client.post(
            f"{BASE_URL}/api/conversation/{conversation_id}/message",
            json={"message": "I had the bacon burger and fries"},
        )
        print_response("2. FIRST MESSAGE - Assign items to You", response)

        # Step 3: Send second message - split something
        print("\n💬 Sending message: 'Sarah and Mike are splitting the pizza'")
        response = client.post(
            f"{BASE_URL}/api/conversation/{conversation_id}/message",
            json={"message": "Sarah and Mike are splitting the pizza"},
        )
        print_response("3. SECOND MESSAGE - Split pizza", response)

        # Step 4: Send third message - assign more items
        print("\n💬 Sending message: 'Sarah had the veggie burger and salad'")
        response = client.post(
            f"{BASE_URL}/api/conversation/{conversation_id}/message",
            json={"message": "Sarah had the veggie burger and salad"},
        )
        print_response("4. THIRD MESSAGE - Assign to Sarah", response)

        # Step 5: Check current state
        print("\n📊 Checking current state...")
        response = client.get(f"{BASE_URL}/api/conversation/{conversation_id}/state")
        print_response("5. CURRENT STATE", response)

        # Step 6: Ask about unassigned items
        print("\n💬 Sending message: 'What's left to assign?'")
        response = client.post(
            f"{BASE_URL}/api/conversation/{conversation_id}/message",
            json={"message": "What's left to assign?"},
        )
        print_response("6. CHECK UNASSIGNED", response)

        # Step 7: Assign remaining items
        print("\n💬 Sending message: 'Mike gets the nachos'")
        response = client.post(
            f"{BASE_URL}/api/conversation/{conversation_id}/message",
            json={"message": "Mike gets the nachos"},
        )
        print_response("7. ASSIGN NACHOS", response)

        # Step 8: Handle tax and tip
        print("\n💬 Sending message: 'Split tax and tip equally between everyone'")
        response = client.post(
            f"{BASE_URL}/api/conversation/{conversation_id}/message",
            json={"message": "Split tax and tip equally between everyone"},
        )
        print_response("8. ASSIGN TAX & TIP", response)

        # Step 9: Get final state
        print("\n📊 Getting final state...")
        response = client.get(f"{BASE_URL}/api/conversation/{conversation_id}/state")
        print_response("9. FINAL STATE", response)

        if response.status_code == 200:
            state = response.json()
            print("\n" + "=" * 60)
            print("💰 FINAL TOTALS")
            print("=" * 60)
            for person, amount in state["totals"].items():
                print(f"{person}: ${amount:.2f}")
            print()

        # Step 10: Get message history
        print("\n📜 Getting message history...")
        response = client.get(f"{BASE_URL}/api/conversation/{conversation_id}/messages")
        print_response("10. MESSAGE HISTORY", response)

        print("\n" + "=" * 60)
        print("✅ Test completed successfully!")
        print("=" * 60)

    except httpx.ConnectError:
        print("\n❌ ERROR: Could not connect to server.")
        print("Make sure the server is running with: python main.py")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
    finally:
        client.close()


if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║        Receipt Splitter API Test Script                 ║
    ╚══════════════════════════════════════════════════════════╝

    This script will test the complete conversation flow:
    1. Start a conversation with a mock receipt
    2. Send messages to assign items
    3. Check state and totals
    4. Verify the agent is working correctly

    Make sure the server is running first!
    """)

    test_conversation_flow()
