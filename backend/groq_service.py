"""
Groq LLM service - Uses the exact models specified.
"""

from groq import Groq
from config import settings
import json
import re


class GroqService:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.fast_model  = "groq/compound-mini"   # fast, for sentiment + response
        self.smart_model = "openai/gpt-oss-120b"  # smart, for reasoning
        self.fallback    = "openai/gpt-oss-20b"   # fallback

    def _chat(self, model: str, messages: list, max_tokens: int = 500) -> str:
        try:
            resp = self.client.chat.completions.create(
                model=model,
                max_tokens=max_tokens,
                messages=messages
            )
            return resp.choices[0].message.content.strip()
        except Exception:
            resp = self.client.chat.completions.create(
                model=self.fallback,
                max_tokens=max_tokens,
                messages=messages
            )
            return resp.choices[0].message.content.strip()

    def extract_booking_reference(self, text: str) -> str:
        prompt = f"""Extract the booking reference code from this text.
Look for patterns like SK4821X, TR1190B, WL7742 (uppercase letters + numbers).
User message: "{text}"
Return ONLY the reference code, or "NOT_FOUND". No explanation."""
        result = self._chat(self.fast_model, [{"role": "user", "content": prompt}], max_tokens=20)
        # Clean up - take only the first word
        return result.split()[0] if result else "NOT_FOUND"

    def detect_sentiment_and_urgency(self, text: str) -> dict:
        prompt = f"""Analyze this customer message. Return ONLY valid JSON.
Message: "{text}"
Format: {{"sentiment":"neutral","urgency":"medium","mentions_legal_action":false,"escalation_signal":false}}"""
        response_text = self._chat(self.fast_model, [{"role": "user", "content": prompt}], max_tokens=150)
        try:
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception:
            pass
        return {"sentiment": "neutral", "urgency": "medium", "mentions_legal_action": False, "escalation_signal": False}

    def generate_agent_response(self, customer_message, customer_profile, booking_info,
                                applicable_policies, conversation_context, agent_state) -> dict:
        system_prompt = """You are SkyAssist, a professional empathetic airline customer support agent.
RULES:
- Only offer compensation that matches the exact policies provided
- Always show empathy and acknowledge customer frustration
- Be clear about what you cannot do and why
- If escalation needed, be clear about it
- Keep responses concise: 2-3 sentences + bullet points if needed"""

        user_prompt = f"""CUSTOMER: {customer_profile.get('name','Unknown')} | Tier: {customer_profile.get('loyalty_tier','Unknown')} | Ref: {customer_profile.get('booking_reference','Unknown')}
FLIGHT: {booking_info.get('flight','Unknown')} {booking_info.get('route','Unknown')} | Status: {booking_info.get('status','Unknown')}{f" | Delay: {booking_info.get('delay_hours',0)}h" if booking_info.get('delay_hours') else ""}
POLICIES: {json.dumps(applicable_policies, indent=1)}
ESCALATION NEEDED: {agent_state.get('escalation_needed', False)}
PRIOR CONTEXT: {conversation_context or 'First message'}
CUSTOMER MESSAGE: "{customer_message}"
Respond with empathy, state what is available per policy, and next steps."""

        response_text = self._chat(
            self.smart_model,
            [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            max_tokens=600
        )
        return {"response": response_text, "model_used": self.smart_model}
