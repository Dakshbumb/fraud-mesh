"""
FraudMesh Gemini Explainer

Generates natural language fraud explanations using Google Gemini API.
Provides human-readable analysis of fraud detection decisions.
"""

import os
import json
import time
from typing import Dict, Optional
import asyncio

import google.generativeai as genai
from models import FraudExplanation, Recommendation, Confidence


class GeminiExplainer:
    """
    Google Gemini integration for fraud explanation generation.
    
    Generates structured natural language explanations for flagged
    transactions, including fraud pattern classification, key signals,
    and recommended actions.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Gemini explainer.
        
        Args:
            api_key: Google Gemini API key (defaults to GEMINI_API_KEY env var)
        """
        if api_key is None:
            api_key = os.getenv("GEMINI_API_KEY")
        
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Use Gemini Pro model
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Generation config
        self.generation_config = {
            'temperature': 0.7,
            'top_p': 0.95,
            'top_k': 40,
            'max_output_tokens': 600,
        }
        
        self.timeout = 5.0  # 5 second timeout
    
    def _build_prompt(self, fraud_case_context: Dict) -> str:
        """
        Build structured prompt for Gemini.
        
        Args:
            fraud_case_context: Complete fraud case context
        
        Returns:
            Formatted prompt string
        """
        txn = fraud_case_context["transaction"]
        score = fraud_case_context["fraud_score"]
        history = fraud_case_context["entity_history"]
        features = fraud_case_context["graph_features"]
        neighborhood = fraud_case_context["neighborhood"]
        
        # Format triggered rules as bullet points
        rules_text = "\n".join(f"- {rule}" for rule in score["triggered_rules"])
        
        prompt = f"""You are a fraud detection expert analyzing a flagged transaction.

Transaction Details:
- ID: {txn['id']}
- Amount: ${txn['amount']:,.2f}
- Time: {txn['timestamp']}
- Merchant: {txn['merchant_id']}
- Device: {txn['device_id']}
- IP: {txn['ip_address']}
- Channel: {txn['channel']}

Fraud Score: {score['score']:.2%} (Risk Level: {score['risk_level']})

Triggered Risk Signals:
{rules_text if rules_text else "- No specific rules triggered"}

Graph Analysis:
- Account age: {history['account_age_days']} days
- Total transactions: {history['transaction_count']}
- Transaction velocity: {features['velocity']:.1f} txns/hour
- Device sharing: {features['device_sharing_count']} users
- IP sharing: {features['ip_sharing_count']} users
- Geographic distance: {features['geographic_distance_km']:.0f} km from previous
- Average amount: ${features['avg_amount']:.2f}
- Connected entities: {neighborhood['connected_entities']}
- Fraud ring detected: {neighborhood['fraud_ring_detected']}

Model Contributions:
- GNN score: {score['gnn_contribution']:.2%}
- Structural rules: {score['structural_contribution']:.2%}
- Temporal rules: {score['temporal_contribution']:.2%}

Provide a fraud explanation in VALID JSON format with these exact keys:
{{
  "headline": "One-sentence summary of the fraud type detected",
  "explanation": "2-3 sentences connecting all the signals into a coherent fraud narrative",
  "fraud_pattern": "One of: Account Takeover, Synthetic Identity Fraud, Money Mule Operation, Coordinated Fraud Ring, Card-Not-Present Fraud, Velocity Abuse",
  "recommended_action": "One of: Approve, Review, Block, Escalate (with brief reason)",
  "confidence": "One of: Low, Medium, High",
  "key_signal": "The single most important risk signal in one phrase"
}}

Respond ONLY with valid JSON. No additional text."""
        
        return prompt
    
    async def explain_fraud_async(self, fraud_case_context: Dict) -> FraudExplanation:
        """
        Generate fraud explanation asynchronously.
        
        Args:
            fraud_case_context: Complete fraud case context
        
        Returns:
            FraudExplanation object
        """
        start_time = time.time()
        
        try:
            # Build prompt
            prompt = self._build_prompt(fraud_case_context)
            
            # Call Gemini API with timeout
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    self.model.generate_content,
                    prompt,
                    generation_config=self.generation_config
                ),
                timeout=self.timeout
            )
            
            # Extract response text
            response_text = response.text
            
            # Parse JSON response
            try:
                # Clean up response (remove markdown code blocks if present)
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0].strip()
                elif "```" in response_text:
                    response_text = response_text.split("```")[1].split("```")[0].strip()
                
                explanation_data = json.loads(response_text)
                
                explanation = FraudExplanation(
                    headline=explanation_data.get("headline", "Suspicious transaction detected"),
                    narrative=explanation_data.get("explanation", "Multiple fraud signals detected."),
                    fraud_pattern=explanation_data.get("fraud_pattern", "Unknown Pattern"),
                    key_signal=explanation_data.get("key_signal", "Multiple risk factors"),
                    recommendation=explanation_data.get("recommended_action", "Review"),
                    confidence=explanation_data.get("confidence", "Medium"),
                    generation_time_ms=int((time.time() - start_time) * 1000)
                )
                
                return explanation
                
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return self._create_fallback_explanation(
                    fraud_case_context,
                    response_text,
                    int((time.time() - start_time) * 1000)
                )
        
        except asyncio.TimeoutError:
            # Timeout fallback
            return self._create_fallback_explanation(
                fraud_case_context,
                "Gemini API timeout",
                int((time.time() - start_time) * 1000)
            )
        
        except Exception as e:
            # General error fallback
            return self._create_fallback_explanation(
                fraud_case_context,
                f"Error: {str(e)}",
                int((time.time() - start_time) * 1000)
            )
    
    def explain_fraud(self, fraud_case_context: Dict) -> FraudExplanation:
        """
        Generate fraud explanation synchronously.
        
        Args:
            fraud_case_context: Complete fraud case context
        
        Returns:
            FraudExplanation object
        """
        # Run async function in sync context
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.explain_fraud_async(fraud_case_context))
    
    def _create_fallback_explanation(
        self,
        fraud_case_context: Dict,
        error_msg: str,
        generation_time_ms: int
    ) -> FraudExplanation:
        """
        Create rule-based fallback explanation when Gemini API fails.
        
        Args:
            fraud_case_context: Fraud case context
            error_msg: Error message
            generation_time_ms: Time taken
        
        Returns:
            FraudExplanation object
        """
        score = fraud_case_context["fraud_score"]
        features = fraud_case_context["graph_features"]
        
        # Determine fraud pattern from triggered rules
        fraud_pattern = score.get("fraud_pattern", "Unknown Pattern")
        
        # Generate headline based on pattern
        headlines = {
            "Account Takeover": "Potential account takeover detected",
            "Synthetic Identity Fraud": "Synthetic identity fraud indicators present",
            "Money Mule Operation": "Money mule activity suspected",
            "Coordinated Fraud Ring": "Coordinated fraud ring activity detected",
            "Card-Not-Present Fraud": "Card-not-present fraud suspected",
            "Velocity Abuse": "Unusual transaction velocity detected",
            "Unknown Pattern": "Suspicious transaction pattern detected"
        }
        headline = headlines.get(fraud_pattern, "Fraud indicators detected")
        
        # Generate narrative from triggered rules
        rules = score.get("triggered_rules", [])
        if rules:
            narrative = f"This transaction triggered {len(rules)} fraud signals. " + \
                       f"Key concerns include: {', '.join(rules[:2])}."
        else:
            narrative = "Multiple fraud indicators detected based on graph analysis and behavioral patterns."
        
        # Determine recommendation based on score
        score_value = score.get("score", 0.5)
        if score_value >= 0.8:
            recommendation = "Block"
            confidence = "High"
        elif score_value >= 0.6:
            recommendation = "Review"
            confidence = "Medium"
        else:
            recommendation = "Review"
            confidence = "Low"
        
        # Identify key signal
        if features.get("device_sharing_count", 0) > 0:
            key_signal = "Device sharing with multiple users"
        elif features.get("velocity", 0) > 5:
            key_signal = "High transaction velocity"
        elif rules:
            key_signal = rules[0].split(":")[0] if ":" in rules[0] else rules[0]
        else:
            key_signal = "Multiple risk factors"
        
        return FraudExplanation(
            headline=headline,
            narrative=narrative,
            fraud_pattern=fraud_pattern,
            key_signal=key_signal,
            recommendation=recommendation,
            confidence=confidence,
            generation_time_ms=generation_time_ms
        )
