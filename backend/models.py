from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class LoyaltyTier(str, Enum):
    SILVER = "Silver"
    GOLD = "Gold"
    PLATINUM = "Platinum"

class FlightStatus(str, Enum):
    SCHEDULED = "Scheduled"
    DELAYED = "Delayed"
    CANCELLED = "Cancelled"
    UNAFFECTED = "Unaffected"

# Customer Models
class CustomerProfile(BaseModel):
    name: str
    loyalty_tier: LoyaltyTier
    booking_reference: str
    contact_email: str
    contact_phone: str
    travel_history: Dict[str, Any]
    prior_complaints: int = 0

# Flight/Booking Models
class FlightInfo(BaseModel):
    booking_reference: str
    flight_number: str
    route: str
    date: str
    scheduled_departure: str
    status: FlightStatus
    delay_hours: Optional[int] = None
    delay_minutes: Optional[int] = None

class BookingData(BaseModel):
    customer_name: str
    pnr: str
    flight: str
    route: str
    date: str
    scheduled_departure: str
    status: str
    notes: Optional[str] = None

# Chat Models
class ChatRequest(BaseModel):
    message: str
    conversation_history: List[Dict[str, str]] = Field(default_factory=list)
    customer_reference: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    action_summary: Optional[str] = None
    escalation_required: bool = False
    escalation_reason: Optional[str] = None
    actions_taken: List[Dict[str, Any]] = Field(default_factory=list)
    policy_applied: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

# Policy Models
class CompensationRule(BaseModel):
    delay_threshold_hours: float
    meal_voucher: bool
    lounge_access: bool
    hotel_accommodation: bool
    amount: Optional[int] = None

class ServicePolicy(BaseModel):
    name: str
    description: str
    conditions: Dict[str, Any]
    eligible_actions: List[str]
    prohibited_actions: List[str]

# Agent State
class AgentState(BaseModel):
    conversation_id: str
    customer_identified: bool
    customer_tier: Optional[LoyaltyTier] = None
    booking_found: bool
    booking_reference: Optional[str] = None
    flight_status: Optional[FlightStatus] = None
    issue_type: Optional[str] = None
    compensation_eligible: bool = False
    escalation_needed: bool = False
    messages: List[Dict[str, str]] = Field(default_factory=list)
