"""
AI Integration Module for CogniGuard
Handles communication with real AI systems (OpenAI, Claude, Gemini)
"""

import streamlit as st
from openai import OpenAI
from anthropic import Anthropic
import google.generativeai as genai
from typing import Dict, List, Optional
import time

class AIIntegrationManager:
    """
    Manages connections to multiple real AI systems
    Supports: OpenAI (ChatGPT), Anthropic (Claude), Google (Gemini)
    """
    
    def __init__(self):
        """
        Initialize the AI manager
        Sets up connections to all available AI services
        """
        # Get API keys from Streamlit secrets (secure!)
        self.openai_key = st.secrets.get("OPENAI_API_KEY", None)
        self.anthropic_key = st.secrets.get("ANTHROPIC_API_KEY", None)
        self.gemini_key = st.secrets.get("GEMINI_API_KEY", None)
        
        # Initialize OpenAI client
        if self.openai_key:
            self.openai_client = OpenAI(api_key=self.openai_key)
        else:
            self.openai_client = None
        
        # Initialize Anthropic (Claude) client
        if self.anthropic_key:
            self.anthropic_client = Anthropic(api_key=self.anthropic_key)
        else:
            self.anthropic_client = None
        
        # Initialize Gemini client
        if self.gemini_key:
            genai.configure(api_key=self.gemini_key)
            self.gemini_client = genai.GenerativeModel('gemini-pro-latest')
        else:
            self.gemini_client = None
    
    def chat_with_openai(self, 
                         user_message: str, 
                         model: str = "gpt-3.5-turbo",
                         system_prompt: str = None) -> Dict:
        """
        Send a message to ChatGPT and get response
        """
        
        if not self.openai_client:
            return {
                "success": False,
                "error": "OpenAI API key not configured",
                "response": None
            }
        
        try:
            messages = []
            
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            messages.append({"role": "user", "content": user_message})
            
            start_time = time.time()
            
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            end_time = time.time()
            
            ai_response = response.choices[0].message.content
            
            return {
                "success": True,
                "response": ai_response,
                "model": model,
                "provider": "OpenAI",
                "tokens_used": response.usage.total_tokens,
                "cost_estimate": self._estimate_cost(response.usage.total_tokens, "openai", model),
                "response_time": round(end_time - start_time, 2)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response": None
            }
    
    def chat_with_claude(self, 
                         user_message: str, 
                         model: str = "claude-sonnet-4-20250514",
                         system_prompt: str = None) -> Dict:
        """
        Send a message to Claude and get response
        """
        
        if not self.anthropic_client:
            return {
                "success": False,
                "error": "Anthropic API key not configured",
                "response": None
            }
        
        try:
            start_time = time.time()
            
            params = {
                "model": model,
                "max_tokens": 500,
                "messages": [
                    {"role": "user", "content": user_message}
                ]
            }
            
            if system_prompt:
                params["system"] = system_prompt
            
            response = self.anthropic_client.messages.create(**params)
            
            end_time = time.time()
            
            ai_response = response.content[0].text
            
            total_tokens = response.usage.input_tokens + response.usage.output_tokens
            
            return {
                "success": True,
                "response": ai_response,
                "model": model,
                "provider": "Anthropic (Claude)",
                "tokens_used": total_tokens,
                "cost_estimate": self._estimate_cost(total_tokens, "anthropic", model),
                "response_time": round(end_time - start_time, 2)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response": None
            }
    
    def chat_with_gemini(self, 
                         user_message: str, 
                         model: str = "gemini-pro-latest",
                         system_prompt: str = None) -> Dict:
        """
        Send a message to Gemini and get response
        """
        
        if not self.gemini_client:
            return {
                "success": False,
                "error": "Gemini API key not configured",
                "response": None
            }
        
        try:
            start_time = time.time()
            
            full_message = user_message
            if system_prompt:
                full_message = f"{system_prompt}\n\nUser: {user_message}"
            
            response = self.gemini_client.generate_content(full_message)
            
            end_time = time.time()
            
            ai_response = response.text
            
            estimated_tokens = len(user_message + ai_response) // 4
            
            return {
                "success": True,
                "response": ai_response,
                "model": model,
                "provider": "Google (Gemini)",
                "tokens_used": estimated_tokens,
                "cost_estimate": 0.0,
                "response_time": round(end_time - start_time, 2)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response": None
            }
    
    def chat(self, 
             user_message: str,
             provider: str = "openai",
             model: str = None,
             system_prompt: str = None) -> Dict:
        """
        Universal chat function - works with any AI provider
        """
        
        provider = provider.lower()
        
        if provider == "openai":
            model = model or "gpt-3.5-turbo"
            return self.chat_with_openai(user_message, model, system_prompt)
        
        elif provider == "claude" or provider == "anthropic":
            model = model or "claude-sonnet-4-20250514"
            return self.chat_with_claude(user_message, model, system_prompt)
        
        elif provider == "gemini" or provider == "google":
            model = model or "gemini-pro-latest"
            return self.chat_with_gemini(user_message, model, system_prompt)
        
        else:
            return {
                "success": False,
                "error": f"Unknown provider: {provider}. Use 'openai', 'claude', or 'gemini'",
                "response": None
            }
    
    def _estimate_cost(self, tokens: int, provider: str, model: str) -> float:
        """
        Estimate cost of API call
        """
        pricing = {
            "openai": {
                "gpt-3.5-turbo": 0.002 / 1000,
                "gpt-4": 0.03 / 1000,
                "gpt-4-turbo": 0.01 / 1000
            },
            "anthropic": {
                "claude-sonnet-4-202505142": 0.003 / 1000,
                "claude-3-opus-20240229": 0.015 / 1000,
                "claude-3-haiku-20240307": 0.00025 / 1000
            },
            "gemini": {
                "gemini-pro-latest": 0.0
            }
        }
        
        if provider in pricing and model in pricing[provider]:
            price_per_token = pricing[provider][model]
            return round(tokens * price_per_token, 4)
        
        return 0.0
    
    def get_available_providers(self) -> List[str]:
        """
        Get list of AI providers that are configured
        """
        providers = []
        
        if self.openai_client:
            providers.append("OpenAI (ChatGPT)")
        if self.anthropic_client:
            providers.append("Anthropic (Claude)")
        if self.gemini_client:
            providers.append("Google (Gemini)")
        
        return providers
    
    def is_configured(self, provider: str = None) -> bool:
        """
        Check if AI integration is properly set up
        """
        if provider:
            provider = provider.lower()
            if provider == "openai":
                return self.openai_client is not None
            elif provider in ["claude", "anthropic"]:
                return self.anthropic_client is not None
            elif provider in ["gemini", "google"]:
                return self.gemini_client is not None
        
        return (self.openai_client is not None or 
                self.anthropic_client is not None or 
                self.gemini_client is not None)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def did_ai_refuse(response_text: str) -> bool:
    """
    Check if the AI refused a malicious request
    
    Returns True if the AI said NO to a bad request (which is GOOD!)
    This prevents false positives where AI mentions bad things while refusing
    """
    
    if not response_text:
        return False
    
    response_lower = response_text.lower()
    
    # Phrases that indicate AI is REFUSING to help with something bad
    refusal_phrases = [
        # Direct refusals
        "i can't",
        "i cannot",
        "i won't",
        "i will not",
        "i'm not able to",
        "i am not able to",
        "i'm unable to",
        "i am unable to",
        "i must decline",
        "i have to decline",
        "i'm not going to",
        "i am not going to",
        
        # Safety/guideline mentions
        "against my guidelines",
        "safety guidelines",
        "my guidelines",
        "maintain my safety",
        "ethical guidelines",
        "i'm designed to",
        "i am designed to",
        "my boundaries",
        "testing my boundaries",
        
        # Offering alternatives (sign of refusal)
        "instead, i'd be happy to",
        "instead i'd be happy to",
        "instead, i can",
        "instead i can",
        "i'd be happy to help with",
        "i would be happy to help with",
        "happy to discuss",
        "legitimate alternatives",
        "appropriate channels",
        "responsible disclosure",
        
        # Cannot assist phrases
        "not able to assist",
        "cannot assist with",
        "can't assist with",
        "cannot help with that",
        "can't help with that",
        "cannot provide information on",
        "can't provide information on",
        "won't provide",
        "cannot provide",
        
        # Educational pivot (common refusal pattern)
        "from an educational perspective",
        "legitimate cybersecurity",
        "ethical security research",
        "best practices"
    ]
    
    # Check if any refusal phrase is in the response
    for phrase in refusal_phrases:
        if phrase in response_lower:
            return True
    
    return False


def get_refusal_result():
    """
    Returns a safe analysis result for when AI refused an attack
    """
    from core.detection_engine import ThreatLevel
    
    class RefusalAnalysis:
        def __init__(self):
            self.threat_level = ThreatLevel.SAFE
            self.threat_type = "ATTACK_REFUSED"
            self.confidence = 0.95
            self.explanation = "AI successfully refused the malicious request"
            self.refused = True
    
    return RefusalAnalysis()

def send_to_ai_and_analyze(message: str, 
                           ai_manager: AIIntegrationManager,
                           engine,
                           sender_context: Dict,
                           receiver_context: Dict,
                           provider: str = "openai",
                           model: str = None,
                           system_prompt: str = None) -> Dict:
    """
    Send message to any AI provider and analyze with CogniGuard
    
    This function:
    1. Sends message to selected AI
    2. Gets response
    3. Analyzes both for threats
    4. Returns complete analysis
    
    Parameters:
    - message: User's message to the AI
    - ai_manager: The AI integration manager
    - engine: CogniGuard detection engine
    - sender_context: Context about the sender
    - receiver_context: Context about the receiver
    - provider: Which AI to use ("openai", "claude", "gemini")
    - model: Specific model to use
    - system_prompt: Instructions for the AI
    
    Returns:
    - Dictionary with success status, AI response, and threat analyses
    """
    
    print(f"📨 Sending message to {provider}...")
    
    # Step 1: Send to selected AI provider
    try:
        ai_result = ai_manager.chat(
            user_message=message,
            provider=provider,
            model=model,
            system_prompt=system_prompt
        )
    except Exception as e:
        print(f"❌ Error calling AI: {e}")
        return {
            "success": False,
            "error": f"Failed to call {provider}: {str(e)}"
        }
    
    # Step 2: Check if AI call was successful
    if not ai_result.get("success", False):
        error_msg = ai_result.get("error", "Unknown error from AI provider")
        print(f"❌ AI call failed: {error_msg}")
        return {
            "success": False,
            "error": error_msg
        }
    
    # Step 3: Extract AI response (now we KNOW it exists)
    ai_response = ai_result.get("response", "")
    
    if not ai_response:
        print("❌ AI response is empty")
        return {
            "success": False,
            "error": "AI returned an empty response"
        }
    
    print(f"✅ Got response from {provider}")
    
    # Step 4: Analyze user message for threats
    print("🔍 Analyzing user message...")
    try:
        user_message_analysis = engine.detect(
            message=message,
            sender_context=sender_context,
            receiver_context=receiver_context
        )
        print(f"✅ User message analysis: {user_message_analysis.threat_level.name}")
    except Exception as e:
        print(f"⚠️ Error analyzing user message: {e}")
        # Create a safe fallback
        from core.detection_engine import ThreatLevel
        
        class SafeAnalysis:
            def __init__(self):
                self.threat_level = ThreatLevel.SAFE
                self.threat_type = "ANALYSIS_ERROR"
                self.confidence = 0.0
                self.explanation = f"Could not analyze: {str(e)}"
        
        user_message_analysis = SafeAnalysis()
    
        # Step 5: Analyze AI response for threats
    print("🔍 Analyzing AI response...")
    
    # ✅ FIRST: Check if AI REFUSED the request (this is GOOD!)
    if did_ai_refuse(ai_response):
        print("✅ AI REFUSED the malicious request - marking as SAFE")
        ai_response_analysis = get_refusal_result()
    else:
        # Only run threat detection if AI didn't refuse
        try:
            ai_response_analysis = engine.detect(
                message=ai_response,
                sender_context={'role': 'ai_assistant', 'intent': 'help_user', 'provider': provider},
                receiver_context=sender_context
            )
            print(f"✅ AI response analysis: {ai_response_analysis.threat_level.name}")
        except Exception as e:
            print(f"⚠️ Error analyzing AI response: {e}")
            # Create a safe fallback
            from core.detection_engine import ThreatLevel
            
            class SafeAnalysis:
                def __init__(self):
                    self.threat_level = ThreatLevel.SAFE
                    self.threat_type = "ANALYSIS_ERROR"
                    self.confidence = 0.0
                    self.explanation = f"Could not analyze: {str(e)}"
            
            ai_response_analysis = SafeAnalysis()
    
    print(f"✅ AI response analysis: {ai_response_analysis.threat_level.name}")
    
    # Step 6: Build the complete result
    result = {
        "success": True,
        "user_message": message,
        "ai_response": ai_response,
        "user_message_threat_analysis": user_message_analysis,
        "ai_response_threat_analysis": ai_response_analysis,
        "metadata": {
            "provider": ai_result.get("provider", provider),
            "model": ai_result.get("model", model or "unknown"),
            "tokens_used": ai_result.get("tokens_used", 0),
            "cost": ai_result.get("cost_estimate", 0.0),
            "response_time": ai_result.get("response_time", 0.0)
        }
    }
    
    print("✅ Analysis complete!")
    return result