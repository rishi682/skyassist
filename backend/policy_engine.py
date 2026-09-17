"""
Policy Engine - Enforces airline policies and determines valid actions.
Single source of truth for policy decisions.
"""

from typing import Dict, List, Optional, Tuple
from data import POLICIES, AGENT_PERMISSIONS, BOOKINGS, CUSTOMERS

class PolicyEngine:
    def __init__(self):
        self.policies = POLICIES
        self.permissions = AGENT_PERMISSIONS
        
    def get_applicable_policies(self, 
                                flight_status: str, 
                                loyalty_tier: str) -> List[Dict]:
        """Get applicable policies based on flight status and customer tier"""
        
        applicable = []
        
        if flight_status == "Cancelled":
            applicable.append(self.policies["cancellation_rebooking"])
            applicable.append(self.policies["refund_processing"])
        
        elif flight_status == "Delayed":
            applicable.append(self.policies["delay_compensation"])
        
        # Always include relevant policies
        applicable.append(self.policies["fare_difference"])
        applicable.append(self.policies["loyalty_tier"])
        
        return applicable
    
    def calculate_delay_compensation(self, delay_minutes: int) -> Dict:
        """Calculate compensation for flight delay"""
        
        delay_hours = delay_minutes / 60
        compensation = {
            "delay_hours": delay_hours,
            "delay_minutes": delay_minutes,
            "meal_voucher": False,
            "lounge_access": False,
            "hotel_accommodation": False,
            "amount": 0,
            "policy_applied": None
        }
        
        if delay_hours >= 5:
            compensation["meal_voucher"] = True
            compensation["lounge_access"] = True
            compensation["hotel_accommodation"] = True
            compensation["policy_applied"] = "Over 5 hours delay"
            compensation["amount"] = 500  # meal voucher base
            
        elif delay_hours >= 3:
            compensation["meal_voucher"] = True
            compensation["lounge_access"] = True
            compensation["policy_applied"] = "3-5 hours delay"
            compensation["amount"] = 500
            
        elif delay_hours > 0:
            compensation["meal_voucher"] = True
            compensation["policy_applied"] = "Under 3 hours delay"
            compensation["amount"] = 500
        
        return compensation
    
    def is_cancellation_eligible(self, flight_status: str, booking_reference: str) -> bool:
        """Check if cancellation is eligible for rebooking/refund"""
        
        if flight_status != "Cancelled":
            return False
        
        # All airline-caused cancellations are eligible
        return True
    
    def can_rebook_priority(self, loyalty_tier: str) -> bool:
        """Check if customer gets priority rebooking based on tier"""
        
        return loyalty_tier.lower() in ["gold", "platinum"]
    
    def get_fare_difference_approval_needed(self, fare_difference: int) -> Tuple[bool, str]:
        """Check if fare difference requires supervisor approval"""
        
        if fare_difference <= self.policies["fare_difference"]["conditions"]["waive_limit"]:
            return False, f"Can waive up to ₹{self.policies['fare_difference']['conditions']['waive_limit']}"
        else:
            return True, f"Requires supervisor approval for ₹{fare_difference}"
    
    def validate_action(self, action: str, context: Dict) -> Tuple[bool, str]:
        """Validate if an action is allowed"""
        
        if action in self.permissions["prohibited_actions"]:
            return False, f"Action prohibited: {action}"
        
        if action not in self.permissions["allowed_actions"]:
            return False, f"Action not permitted: {action}"
        
        return True, f"Action allowed: {action}"
    
    def check_escalation_needed(self, 
                               request_summary: Dict,
                               customer_sentiment: Dict) -> Tuple[bool, str]:
        """Determine if request needs human escalation"""
        
        escalation_reasons = []
        
        # Check for legal threats
        if customer_sentiment.get("mentions_legal_action", False):
            escalation_reasons.append("Legal action mentioned")
        
        # Check for excessive compensation requests
        if request_summary.get("requests_beyond_policy", False):
            escalation_reasons.append("Compensation exceeds policy limits")
        
        # Check for angry + high demands
        if (customer_sentiment.get("sentiment") == "angry" and 
            request_summary.get("demands_count", 0) > 2):
            escalation_reasons.append("Angry customer with multiple demands")
        
        # Check for ambiguous fare difference waive
        if request_summary.get("fare_difference_requested", 0) > 1500:
            escalation_reasons.append("Fare difference > ₹1,500 requires approval")
        
        needs_escalation = len(escalation_reasons) > 0
        reason = " | ".join(escalation_reasons) if escalation_reasons else "No escalation needed"
        
        return needs_escalation, reason
    
    def get_allowed_actions_for_scenario(self, 
                                        flight_status: str,
                                        loyalty_tier: str) -> List[str]:
        """Get list of allowed actions for this specific scenario"""
        
        actions = []
        
        if flight_status == "Cancelled":
            actions.extend([
                "Offer free rebooking on next available flight",
                "Offer full refund to original payment method",
                "Apply loyalty tier priority if Gold/Platinum"
            ])
        
        elif flight_status == "Delayed":
            delay_context = self._get_delay_info()
            if delay_context:
                compensation = self.calculate_delay_compensation(delay_context["minutes"])
                
                if compensation["meal_voucher"]:
                    actions.append("Issue ₹500 meal voucher")
                if compensation["lounge_access"]:
                    actions.append("Grant lounge access")
                if compensation["hotel_accommodation"]:
                    actions.append("Arrange hotel accommodation (delayed hours only)")
        
        return actions
    
    def _get_delay_info(self) -> Optional[Dict]:
        """Helper to get delay info from current context"""
        # This would be set from the agent state
        return None
    
    def check_policy_compliance(self, proposed_action: Dict) -> Tuple[bool, str]:
        """Check if proposed action complies with all policies"""
        
        compliance_issues = []
        
        action_type = proposed_action.get("action_type")
        
        # Check compensation amount
        if action_type == "compensation":
            amount = proposed_action.get("amount", 0)
            if amount > 500:  # Base compensation limit
                compliance_issues.append(f"Compensation exceeds standard ₹500 policy")
        
        # Check refund method
        if action_type == "refund":
            refund_method = proposed_action.get("refund_method")
            if refund_method != "original_payment_method":
                compliance_issues.append(f"Refunds must go to original payment method")
        
        # Check fare waiver
        if action_type == "fare_waiver":
            amount = proposed_action.get("amount", 0)
            if amount > 1500:
                compliance_issues.append(f"Fare waiver > ₹1,500 requires supervisor approval")
        
        is_compliant = len(compliance_issues) == 0
        reason = " | ".join(compliance_issues) if compliance_issues else "Compliant"
        
        return is_compliant, reason

# Create global policy engine instance
policy_engine = PolicyEngine()
