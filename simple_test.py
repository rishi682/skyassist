import requests

API_URL = "http://localhost:8000"

tests = [
    ("TEST 1: Priya - CANCELLATION", "My flight SK-204 from Delhi to Goa got cancelled, booking SK4821X"),
    ("TEST 1b: Priya - ANGRY + UPGRADE", "I am absolutely furious! I want a full cash refund AND a free business class upgrade on my return flight for the trouble! booking SK4821X"),
    ("TEST 2: Arvind - DELAY 4H", "My booking TR1190B Mumbai to Bengaluru is delayed 4 hours, I am missing a connecting meeting, I need hotel accommodation"),
    ("TEST 3: Meher - DELAY 6H COMPLEX", "Flight WL7742 Delhi to Hyderabad is delayed 6 hours. I want a full night hotel stay not just the delayed hours. Also move me to a higher fare flight, the difference is Rs 2000"),
]

for title, msg in tests:
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)
    resp = requests.post(f"{API_URL}/chat", json={"message": msg, "conversation_history": []}, timeout=30)
    data = resp.json()
    print(f"Agent: {data.get('response', data.get('error','ERROR'))[:400]}")
    print(f"Escalation: {data.get('escalation_required', 'N/A')}")
    print(f"Actions: {data.get('action_summary', 'N/A')}")
