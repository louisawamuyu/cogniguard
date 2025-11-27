"""
Database Module for CogniGuard
Handles saving and retrieving threat detections from Supabase
"""

import streamlit as st
from supabase import create_client, Client
from datetime import datetime
from typing import Dict, List, Optional

class ThreatDatabase:
    """
    Simple database manager for storing threat detections
    
    Think of this as a librarian who:
    - Saves threats to the database (filing)
    - Retrieves threats when you ask (searching)
    - Counts threats for statistics (organizing)
    """
    
    def __init__(self):
        """
        Set up connection to Supabase database
        """
        # Get credentials from secrets
        supabase_url = st.secrets.get("SUPABASE_URL", None)
        supabase_key = st.secrets.get("SUPABASE_KEY", None)
        
        # Connect to database
        if supabase_url and supabase_key:
            self.supabase: Client = create_client(supabase_url, supabase_key)
            self.connected = True
        else:
            self.supabase = None
            self.connected = False
    
    def is_connected(self) -> bool:
        """
        Check if database is connected and ready
        
        Returns:
        - True if connected, False if not
        """
        return self.connected
    
    def save_threat(self, 
                    message: str,
                    threat_level: str,
                    threat_type: str,
                    confidence: float,
                    explanation: str,
                    ai_provider: str = "Unknown",
                    user_id: str = "anonymous") -> bool:
        """
        Save a threat detection to the database
        
        Parameters:
        - message: The message that was analyzed
        - threat_level: SAFE, LOW, MEDIUM, HIGH, CRITICAL
        - threat_type: Type of threat detected
        - confidence: How confident (0.0 to 1.0)
        - explanation: Why it was flagged
        - ai_provider: Which AI (OpenAI, Claude, Gemini)
        - user_id: Who tested it (default: anonymous)
        
        Returns:
        - True if saved successfully, False if error
        """
        
        if not self.connected:
            print("❌ Database not connected")
            return False
        
        try:
            # Prepare data to save
            data = {
                "message": message,
                "threat_level": threat_level,
                "threat_type": threat_type,
                "confidence": confidence,
                "explanation": explanation,
                "ai_provider": ai_provider,
                "user_id": user_id
            }
            
            # Save to database
            result = self.supabase.table("threats").insert(data).execute()
            
            print(f"✅ Threat saved to database: {threat_type}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving to database: {e}")
            return False
    
    def get_all_threats(self, limit: int = 100) -> List[Dict]:
        """
        Get all threats from the database
        
        Parameters:
        - limit: Maximum number to retrieve (default: 100)
        
        Returns:
        - List of threat records
        """
        
        if not self.connected:
            return []
        
        try:
            result = self.supabase.table("threats")\
                .select("*")\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()
            
            return result.data
            
        except Exception as e:
            print(f"❌ Error retrieving threats: {e}")
            return []
    
    def get_threats_by_level(self, threat_level: str) -> List[Dict]:
        """
        Get threats of a specific level (e.g., all CRITICAL threats)
        
        Parameters:
        - threat_level: SAFE, LOW, MEDIUM, HIGH, CRITICAL
        
        Returns:
        - List of matching threats
        """
        
        if not self.connected:
            return []
        
        try:
            result = self.supabase.table("threats")\
                .select("*")\
                .eq("threat_level", threat_level)\
                .order("created_at", desc=True)\
                .execute()
            
            return result.data
            
        except Exception as e:
            print(f"❌ Error retrieving threats: {e}")
            return []
    
    def get_threat_statistics(self) -> Dict:
        """
        Get statistics about threats in the database
        
        Returns:
        - Dictionary with counts and percentages
        """
        
        if not self.connected:
            return {
                "total": 0,
                "by_level": {},
                "by_provider": {},
                "by_type": {}
            }
        
        try:
            # Get all threats
            all_threats = self.get_all_threats(limit=10000)
            
            # Count by level
            by_level = {}
            for threat in all_threats:
                level = threat.get("threat_level", "UNKNOWN")
                by_level[level] = by_level.get(level, 0) + 1
            
            # Count by provider
            by_provider = {}
            for threat in all_threats:
                provider = threat.get("ai_provider", "Unknown")
                by_provider[provider] = by_provider.get(provider, 0) + 1
            
            # Count by type
            by_type = {}
            for threat in all_threats:
                threat_type = threat.get("threat_type", "Unknown")
                by_type[threat_type] = by_type.get(threat_type, 0) + 1
            
            return {
                "total": len(all_threats),
                "by_level": by_level,
                "by_provider": by_provider,
                "by_type": by_type
            }
            
        except Exception as e:
            print(f"❌ Error getting statistics: {e}")
            return {
                "total": 0,
                "by_level": {},
                "by_provider": {},
                "by_type": {}
            }
    
    def delete_all_threats(self) -> bool:
        """
        ⚠️ DELETE ALL threats from database
        Use with caution!
        
        Returns:
        - True if successful
        """
        
        if not self.connected:
            return False
        
        try:
            # This deletes EVERYTHING!
            result = self.supabase.table("threats").delete().neq("id", 0).execute()
            print("🗑️ All threats deleted from database")
            return True
            
        except Exception as e:
            print(f"❌ Error deleting threats: {e}")
            return False