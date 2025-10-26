# API Testing Guide

## Quick Start

### 1. Start the Server
```bash
python main.py
```

The server will start on `http://localhost:8000`

### 2. Run the Test Script (Easiest!)
```bash
python test_api.py
```

This will run a complete test flow with a mock receipt and show you how the agent works.

---

## Manual Testing with curl

### Test 1: Start a Conversation

```bash
curl -X POST http://localhost:8000/api/conversation/start \
  -H "Content-Type: application/json" \
  -d '{
    "receipt": {
      "establishment": "Joes Diner",
      "date": "2024-01-15T19:30:00",
      "subtotal": 45.50,
      "tax": 4.10,
      "tip": 9.00,
      "total": 58.60,
      "line_items": [
        {
          "id": "item_1",
          "line_number": 1,
          "desc_clean": "Bacon Burger",
          "price": 12.99,
          "line_total": 12.99,
          "qty": 1
        },
        {
          "id": "item_2",
          "line_number": 2,
          "desc_clean": "Large Pizza",
          "price": 15.99,
          "line_total": 15.99,
          "qty": 1
        },
        {
          "id": "item_3",
          "line_number": 3,
          "desc_clean": "Fries",
          "price": 2.99,
          "line_total": 5.98,
          "qty": 2
        }
      ]
    },
    "people": ["You", "Sarah", "Mike"]
  }'
```

**Response:** You'll get a `conversation_id` - save this for the next steps!

### Test 2: Send a Message (Replace CONVERSATION_ID)

```bash
curl -X POST http://localhost:8000/api/conversation/CONVERSATION_ID/message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I had the bacon burger and fries"
  }'
```

### Test 3: Check Current State

```bash
curl http://localhost:8000/api/conversation/CONVERSATION_ID/state
```

### Test 4: Get Message History

```bash
curl http://localhost:8000/api/conversation/CONVERSATION_ID/messages
```

---

## Testing with Python (Interactive)

You can also test interactively in a Python REPL:

```python
import httpx

# Start conversation
client = httpx.Client()
response = client.post("http://localhost:8000/api/conversation/start", json={
    "receipt": {
        "establishment": "Test Restaurant",
        "date": "2024-01-15",
        "subtotal": 30.00,
        "tax": 2.70,
        "tip": 6.00,
        "total": 38.70,
        "line_items": [
            {
                "id": "item_1",
                "line_number": 1,
                "desc_clean": "Burger",
                "price": 15.00,
                "line_total": 15.00,
                "qty": 1
            },
            {
                "id": "item_2",
                "line_number": 2,
                "desc_clean": "Pizza",
                "price": 15.00,
                "line_total": 15.00,
                "qty": 1
            }
        ]
    },
    "people": ["Alice", "Bob"]
})

# Get conversation ID
conv_id = response.json()["conversation_id"]
print(f"Conversation ID: {conv_id}")

# Send a message
response = client.post(
    f"http://localhost:8000/api/conversation/{conv_id}/message",
    json={"message": "Alice had the burger, Bob had the pizza"}
)
print(response.json()["message"])

# Check state
response = client.get(f"http://localhost:8000/api/conversation/{conv_id}/state")
print("Totals:", response.json()["totals"])
```

---

## Example Conversation Flow

1. **Start**: Create conversation with receipt and people
   - Response: Welcome message + conversation_id

2. **Assign items**: "I had the burger"
   - Agent calls `assign_items` function
   - Response: "Got it, marking the burger for you"

3. **Split items**: "Sarah and I are splitting the pizza"
   - Agent calls `assign_items` with both people
   - Response: Confirmation message

4. **Check progress**: "What's left?"
   - Agent calls `get_unassigned_items`
   - Response: Lists remaining items

5. **Handle tax/tip**: "Split tax and tip equally"
   - Agent calls `assign_tax` and `assign_tip`
   - Response: Confirmation

6. **Get final totals**: Check `/state` endpoint
   - Response: Shows how much each person owes

---

## Testing the TabScanner Integration

If you want to test with a real receipt:

### Upload Receipt
```bash
curl -X POST http://localhost:8000/api/receipt/upload \
  -F "file=@/path/to/receipt.jpg"
```

### Poll for Results (use token from upload)
```bash
curl http://localhost:8000/api/receipt/result/YOUR_TOKEN
```

---

## Troubleshooting

### Server won't start?
- Check if port 8000 is available: `lsof -i :8000`
- Make sure dependencies are installed: `pip install -r requirements.txt`
- Check `.env` file has valid API keys

### API returns 404?
- Verify server is running
- Check the conversation_id is correct
- Make sure you're using the right endpoint URL

### Agent not responding correctly?
- Check the `ANTHROPIC_API_KEY` in `.env`
- Look at server logs for error messages
- Verify the receipt has valid `line_items` with `id` fields

---

## API Endpoints Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/receipt/upload` | Upload receipt image |
| GET | `/api/receipt/result/{token}` | Get parsed receipt |
| POST | `/api/conversation/start` | Start new conversation |
| POST | `/api/conversation/{id}/message` | Send message to agent |
| GET | `/api/conversation/{id}/state` | Get current assignments |
| GET | `/api/conversation/{id}/messages` | Get message history |
| POST | `/api/conversation/{id}/confirm` | Finalize split |

---

## Tips for Testing

1. **Start with the test script** (`python test_api.py`) - it shows the complete flow
2. **Use descriptive messages** - the agent understands natural language
3. **Try ambiguous requests** - see how the agent handles clarification
4. **Check state frequently** - watch how assignments update in real-time
5. **Test edge cases** - unassigned items, changing mind, etc.
