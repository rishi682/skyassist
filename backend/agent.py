"""
Main Agent Logic - Orchestrates customer interactions.
Combines LLM, policy engine, and business logic.
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from groq_service import GroqService
from policy_engine import PolicyEngine
from data import CUSTOMERS, BOOKINGS, POLICIES, AGENT_PERMISSIONS, SCENARIO_DATE

class AirlineAgent:
    def __init__(self):
        self.groq = GroqService()
        self.policy_engine = PolicyEngine()
        self.conversation_id = str(uuid.uuid4())
        self.audit_log = []
        
    def process_customer_message(self, 
                                customer_message: str,
                                conversation_history: List[Dict] = None) -> Dict:
        """
        Main entry point for processing customer messages.
        Returns structured response with actions and metadata.
        """
        
        if conversation_history is None:
            conversation_history = []
        
        # Step 1: Extract booking reference from message
        booking_ref = self.groq.extract_booking_reference(customer_message)
        
        # Step 2: Detect sentiment and urgency
        sentiment = self.groq.detect_sentiment_and_urgency(customer_message)
        
        # Step 3: Look up customer and booking
        customer_profile, booking_info, lookup_status = self._lookup_customer_booking(booking_ref)
        
        # Step 4: Analyze what the customer is asking for
        request_analysis = self._analyze_customer_request(customer_message)
        
        # Step 5: Get applicable policies
        applicable_policies = []
        if booking_info:
            applicable_policies = self.policy_engine.get_applicable_policies(
                booking_info.get("status", "Unknown"),
                customer_profile.get("loyalty_tier", "Unknown") if customer_profile else "Unknown"
            )
        
        # Step 6: Build agent state
        agent_state = self._build_agent_state(
            customer_profile,
            booking_info,
            request_analysis,
            sentiment
        )
        
        # Step 7: Check if escalation needed
        escalation_needed, escalation_reason = self.policy_engine.check_escalation_needed(
            request_analysis,
            sentiment
        )
        agent_state["escalation_needed"] = escalation_needed
        
        # Step 8: Generate response from LLM
        response_data = self.groq.generate_agent_response(
            customer_message=customer_message,
            customer_profile=customer_profile or {},
            booking_info=booking_info or {},
            applicable_policies=applicable_policies,
            conversation_context=self._build_context_from_history(conversation_history),
            agent_state=agent_state
        )
        
        # Step 9: Determine actions to take
        actions_taken = self._determine_actions(
            booking_info,
            request_analysis,
            applicable_policies,
            escalation_needed
        )
        
        # Step 10: Audit log
        self._log_interaction(
            customer_message,
            response_data["response"],
            customer_profile,
            actions_taken,
            escalation_needed
        )
        
        # Build final response
        return {
            "response": response_data["response"],
            "action_summary": self._summarize_actions(actions_taken),
            "escalation_required": escalation_needed,
            "escalation_reason": escalation_reason if escalation_needed else None,
            "actions_taken": actions_taken,
            "policy_applied": applicable_policies[0].get("name", None) if applicable_policies else None,
            "metadata": {
                "conversation_id": self.conversation_id,
                "customer_name": customer_profile.get("name", "Unknown") if customer_profile else "Not identified",
                "booking_reference": booking_ref if booking_ref != "NOT_FOUND" else None,
                "customer_tier": customer_profile.get("loyalty_tier", "Unknown") if customer_profile else None,
                "booking_found": booking_info is not None,
                "sentiment": sentiment.get("sentiment", "unknown"),
                "urgency": sentiment.get("urgency", "unknown"),
                "timestamp": datetime.now().isoformat(),
                "scenario_date": SCENARIO_DATE
            }
        }
    
    def _lookup_customer_booking(self, booking_ref: str) -> Tuple[Optional[Dict], Optional[Dict], str]:
        """Look up customer and booking information"""
        
        if booking_ref == "NOT_FOUND":
            return None, None, "booking_ref_not_provided"
        
        if booking_ref not in CUSTOMERS:
            return None, None, "booking_ref_not_found"
        
        customer = CUSTOMERS[booking_ref]
        bookings = BOOKINGS.get(booking_ref, [])
        
        if not bookings:
            return customer, None, "customer_found_no_booking"
        
        # Return first active booking
        booking = bookings[0]
        return customer, booking, "success"
    
    def _analyze_customer_request(self, message: str) -> Dict:
        """Analyze what the customer is requesting"""
        
        message_lower = message.lower()
        
        analysis = {
            "is_complaint": any(word in message_lower for word in ["cancel", "delay", "problem", "issue", "help"]),
            "is_compensation_request": any(word in message_lower for word in ["compensation", "refund", "hotel", "voucher", "upgrade", "money"]),
            "is_rebooking_request": any(word in message_lower for word in ["rebook", "different flight", "earlier", "later", "alternative"]),
            "requests_beyond_policy": any(word in message_lower for word in ["extra", "more than", "exception", "additional", "besides"]),
            "is_angry": any(word in message_lower for word in ["angry", "furious", "unacceptable", "ridiculous", "terrible"]),
            "demands_count": sum(1 for word in ["refund", "upgrade", "hotel", "voucher", "compensation"] if word in message_lower),
            "fare_difference_requested": self._extract_amount(message)
        }
        
        return analysis
    
    def _extract_amount(self, text: str) -> int:
        """Extract rupee amounts from text"""
        import re
        amounts = re.findall(r'₹(\d+)|rs\.?\s*(\d+)', text, re.IGNORECASE)
        if amounts:
            # Return the largest amount found
            return max(int(a[0] or a[1]) for a in amounts)
        return 0
    
    def _build_agent_state(self, 
                          customer_profile: Optional[Dict],
                          booking_info: Optional[Dict],
                          request_analysis: Dict,
                          sentiment: Dict) -> Dict:
        """Build agent state for decision making"""
        
        state = {
            "customer_identified": customer_profile is not None,
            "customer_tier": customer_profile.get("loyalty_tier") if customer_profile else None,
            "booking_found": booking_info is not None,
            "flight_status": booking_info.get("status") if booking_info else None,
            "issue_type": None,
            "compensation_eligible": False,
            "escalation_needed": False,
            "sentiment": sentiment.get("sentiment"),
            "urgency": sentiment.get("urgency"),
        }
        
        # Determine issue type
        if booking_info:
            if booking_info.get("status") == "Cancelled":
                state["issue_type"] = "cancellation"
                state["compensation_eligible"] = True
            elif booking_info.get("status") == "Delayed":
                state["issue_type"] = "delay"
                delay_hours = booking_info.get("delay_hours", 0)
                state["compensation_eligible"] = delay_hours > 0
        
        return state
    
    def _build_context_from_history(self, conversation_history: List[Dict]) -> str:
        """Build context string from conversation history"""
        
        if not conversation_history:
            return ""
        
        context_parts = []
        for msg in conversation_history[-3:]:  # Last 3 messages for context
            role = msg.get("role", "unknown").capitalize()
            content = msg.get("content", "")
            context_parts.append(f"{role}: {content}")
        
        return "\n".join(context_parts)
    
    def _determine_actions(self,
                          booking_info: Optional[Dict],
                          request_analysis: Dict,
                          applicable_policies: List[Dict],
                          escalation_needed: bool) -> List[Dict]:
        """Determine what actions to take"""
        
        actions = []
        
        if not booking_info:
            actions.append({
                "action": "request_booking_reference",
                "message": "Ask customer for booking reference",
                "priority": "high"
            })
            return actions
        
        status = booking_info.get("status")
        
        # Handle cancellation
        if status == "Cancelled":
            actions.append({
                "action": "offer_rebooking_or_refund",
                "details": "Free rebooking within 24h or full refund to original payment method",
                "priority": "high"
            })
            
            if request_analysis.get("is_compensation_request"):
                if request_analysis.get("requests_beyond_policy"):
                    actions.append({
                        "action": "escalate",
                        "reason": "Customer requesting compensation beyond policy",
                        "priority": "high"
                    })
                else:
                    actions.append({
                        "action": "apply_loyalty_benefits",
                        "details": "Apply priority rebooking if Gold/Platinum",
                        "priority": "medium"
                    })
        
        # Handle delay
        elif status == "Delayed":
            delay_hours = booking_info.get("delay_hours", 0)
            delay_minutes = booking_info.get("delay_minutes", 0)
            compensation = self.policy_engine.calculate_delay_compensation(delay_hours * 60 + delay_minutes)
            
            if compensation["meal_voucher"]:
                actions.append({
                    "action": "issue_meal_voucher",
                    "amount": "₹500",
                    "priority": "high"
                })
            
            if compensation["lounge_access"]:
                actions.append({
                    "action": "grant_lounge_access",
                    "priority": "high"
                })
            
            if compensation["hotel_accommodation"]:
                actions.append({
                    "action": "arrange_hotel",
                    "details": f"For {delay_hours}h {delay_minutes}m delay only",
                    "priority": "high"
                })
            
            # Check for escalation
            if request_analysis.get("fare_difference_requested", 0) > 1500:
                actions.append({
                    "action": "escalate",
                    "reason": "Fare difference > ₹1,500 needs supervisor approval",
                    "priority": "high"
                })
        
        if escalation_needed:
            actions.append({
                "action": "escalate_to_human",
                "reason": "Complex situation or policy exception needed",
                "priority": "critical"
            })
        
        return actions
    
    def _summarize_actions(self, actions: List[Dict]) -> str:
        """Create summary of actions taken"""
        
        if not actions:
            return None
        
        summaries = []
        for action in actions:
            action_type = action.get("action", "").replace("_", " ").title()
            if action.get("details"):
                summaries.append(f"{action_type}: {action['details']}")
            else:
                summaries.append(action_type)
        
        return " | ".join(summaries[:3])  # Max 3 actions in summary
    
    def _log_interaction(self,
                        customer_msg: str,
                        agent_response: str,
                        customer_profile: Optional[Dict],
                        actions: List[Dict],
                        escalation: bool) -> None:
        """Log interaction for audit trail"""
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "conversation_id": self.conversation_id,
            "customer_name": customer_profile.get("name", "Unknown") if customer_profile else "Unknown",
            "customer_message": customer_msg[:100],  # First 100 chars
            "agent_response": agent_response[:100],  # First 100 chars
            "actions_taken": len(actions),
            "escalation": escalation
        }
        
        self.audit_log.append(log_entry)

# Create global agent instance
agent = AirlineAgent()
