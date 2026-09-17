"""
Data sources for the airline agent.
This is the single source of truth for all customer, booking, and policy data.
"""

# Customer Profiles
CUSTOMERS = {
    "SK4821X": {
        "name": "Priya Nair",
        "loyalty_tier": "Gold",
        "booking_reference": "SK4821X",
        "contact_email": "priya.nair@example.com",
        "contact_phone": "+91-98xxxxxxx1",
        "travel_history": {
            "flights_last_12_months": 6,
            "prior_complaints": 1,
            "prior_complaint_details": "Delayed baggage, resolved with voucher"
        }
    },
    "TR1190B": {
        "name": "Arvind Kulkarni",
        "loyalty_tier": "Silver",
        "booking_reference": "TR1190B",
        "contact_email": "arvind.kulkarni@example.com",
        "contact_phone": "+91-98xxxxxxx2",
        "travel_history": {
            "flights_last_12_months": 3,
            "prior_complaints": 0,
            "prior_complaint_details": None
        }
    },
    "WL7742": {
        "name": "Meher Kaur",
        "loyalty_tier": "Platinum",
        "booking_reference": "WL7742",
        "contact_email": "meher.kaur@example.com",
        "contact_phone": "+91-98xxxxxxx3",
        "travel_history": {
            "flights_last_12_months": 10,
            "prior_complaints": 1,
            "prior_complaint_details": "Overbooking, resolved with tier-status upgrade"
        }
    }
}

# Booking and Flight Data
BOOKINGS = {
    "SK4821X": [
        {
            "customer": "Priya Nair",
            "pnr": "SK4821X",
            "flight": "SK-204",
            "route": "Delhi → Goa",
            "date": "Wed 23 Sep 2026",
            "scheduled_departure": "18:40",
            "status": "Cancelled",
            "status_reason": "operational reasons",
            "delay_hours": None,
            "delay_minutes": None
        },
        {
            "customer": "Priya Nair",
            "pnr": "SK4821X",
            "flight": "Return",
            "route": "Goa → Delhi",
            "date": "Fri 25 Sep 2026",
            "scheduled_departure": "16:20",
            "status": "Unaffected",
            "status_reason": None,
            "delay_hours": None,
            "delay_minutes": None
        }
    ],
    "TR1190B": [
        {
            "customer": "Arvind Kulkarni",
            "pnr": "TR1190B",
            "flight": "SK-118",
            "route": "Mumbai → Bengaluru",
            "date": "Wed 23 Sep 2026",
            "scheduled_departure": "07:10",
            "status": "Delayed",
            "status_reason": "operational reasons",
            "delay_hours": 4,
            "delay_minutes": 0,
            "new_departure": "11:10"
        }
    ],
    "WL7742": [
        {
            "customer": "Meher Kaur",
            "pnr": "WL7742",
            "flight": "SK-305",
            "route": "Delhi → Hyderabad",
            "date": "Wed 23 Sep 2026",
            "scheduled_departure": "14:00",
            "status": "Delayed",
            "status_reason": "operational reasons",
            "delay_hours": 6,
            "delay_minutes": 0,
            "new_departure": "20:00"
        }
    ]
}

# Service Policies
POLICIES = {
    "cancellation_rebooking": {
        "name": "Cancellation Rebooking Rule",
        "description": "If a flight is cancelled by the airline, customer gets free rebooking or full refund",
        "conditions": {
            "trigger": "flight_cancelled",
            "airline_caused": True
        },
        "eligible_actions": [
            "Free rebooking on next available flight within 24 hours",
            "Full refund to original payment method"
        ],
        "prohibited_actions": [
            "Waiving on customer-caused cancellations"
        ]
    },
    "delay_compensation": {
        "name": "Delay Compensation Rule",
        "description": "Compensation based on delay duration",
        "rules": [
            {
                "delay_range": "under 3 hours",
                "compensation": "₹500 meal voucher"
            },
            {
                "delay_range": "3-5 hours",
                "compensation": "Meal voucher + lounge access"
            },
            {
                "delay_range": "over 5 hours",
                "compensation": "Meal voucher + hotel accommodation (delayed hours only)"
            }
        ]
    },
    "refund_processing": {
        "name": "Refund Processing Rule",
        "description": "Refunds for airline-caused cancellations",
        "conditions": {
            "processing_time": "7 business days",
            "issued_to": "original payment method only"
        }
    },
    "fare_difference": {
        "name": "Fare Difference Rule",
        "description": "Customer choosing higher-fare flight must pay difference",
        "conditions": {
            "waive_limit": 1500,  # rupees
            "requires_approval_above": 1500,
            "approval_needed_from": "supervisor"
        }
    },
    "loyalty_tier": {
        "name": "Loyalty Tier Rule",
        "description": "Gold and Platinum tier benefits",
        "benefits": {
            "Gold": "Priority rebooking (first access to next-available seats)",
            "Platinum": "Priority rebooking (first access to next-available seats)",
            "Silver": "Standard rebooking"
        },
        "note": "No additional compensation beyond standard policy"
    }
}

# Allowed and Prohibited Actions
AGENT_PERMISSIONS = {
    "allowed_actions": [
        "Rebook customer on next available flight within 24 hours at no charge (airline-caused)",
        "Issue meal vouchers per delay compensation rule",
        "Issue lounge access per delay compensation rule",
        "Arrange hotel accommodation for delayed-hours portion",
        "Initiate refund request for airline-caused cancellations",
        "Provide customer's own booking and flight status information"
    ],
    "prohibited_actions": [
        "Approve compensation beyond stated policy amounts",
        "Waive fare difference above ₹1,500",
        "Make exceptions for non-airline-caused disruptions",
        "Handle threats of legal action or formal complaints (must escalate immediately)",
        "Process refunds to different payment method than original"
    ]
}

# Scenario Context
SCENARIO_DATE = "Wednesday, 23 September 2026"

SCENARIOS = {
    "scenario_1": {
        "customer_ref": "SK4821X",
        "customer_name": "Priya Nair",
        "tier": "Gold",
        "issue": "Flight cancelled - wants full cash refund + business class upgrade",
        "flight": "SK-204 (Delhi → Goa)",
        "status": "Cancelled"
    },
    "scenario_2": {
        "customer_ref": "TR1190B",
        "customer_name": "Arvind Kulkarni",
        "tier": "Silver",
        "issue": "Flight delayed 4 hours - missing connecting meeting, wants hotel accommodation",
        "flight": "SK-118 (Mumbai → Bengaluru)",
        "status": "Delayed 4h"
    },
    "scenario_3": {
        "customer_ref": "WL7742",
        "customer_name": "Meher Kaur",
        "tier": "Platinum",
        "issue": "Flight delayed 6 hours - wants full night stay + move to higher-fare flight (₹2,000 difference)",
        "flight": "SK-305 (Delhi → Hyderabad)",
        "status": "Delayed 6h"
    }
}
