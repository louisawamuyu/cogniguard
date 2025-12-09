"""
DATABASE - Supabase Integration for CogniGuard
Complete version with all features.
"""

import os
from datetime import datetime
from typing import Dict, List, Optional

# Try to import Supabase
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    print("[DB] Supabase not installed. Run: pip install supabase")


class ThreatDatabase:
    """
    Database manager for CogniGuard
    
    Handles:
    - Saving threat detections
    - Retrieving threat history
    - Statistics and analytics
    """
    
    def __init__(self):
        """Initialize database connection"""
        
        print("[DB] Initializing Database Connection...")
        
        self.client: Optional[Client] = None
        self.connected = False
        
        if not SUPABASE_AVAILABLE:
            print("[DB] Supabase package not available")
            return
        
        # Get credentials from multiple sources
        supabase_url = None
        supabase_key = None
        
        # Method 1: Try Streamlit secrets (works in Streamlit Cloud)
        try:
            import streamlit as st
            supabase_url = st.secrets.get("SUPABASE_URL", None)
            supabase_key = st.secrets.get("SUPABASE_KEY", None)
            if supabase_url:
                print("[DB] Found credentials in Streamlit secrets")
        except:
            pass
        
        # Method 2: Try reading secrets file directly (works locally)
        if not supabase_url or not supabase_key:
            secrets_path = ".streamlit/secrets.toml"
            if os.path.exists(secrets_path):
                try:
                    with open(secrets_path, 'r') as f:
                        for line in f:
                            line = line.strip()
                            if line.startswith("SUPABASE_URL"):
                                supabase_url = line.split("=", 1)[1].strip().strip('"').strip("'")
                            if line.startswith("SUPABASE_KEY"):
                                supabase_key = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if supabase_url:
                        print("[DB] Found credentials in secrets.toml file")
                except Exception as e:
                    print(f"[DB] Error reading secrets file: {e}")
        
        # Method 3: Try environment variables (works in Docker/production)
        if not supabase_url:
            supabase_url = os.environ.get("SUPABASE_URL", None)
        if not supabase_key:
            supabase_key = os.environ.get("SUPABASE_KEY", None)
        if supabase_url and not supabase_key:
            print("[DB] Found credentials in environment variables")
        
        # Check if we have credentials
        if not supabase_url or not supabase_key:
            print("[DB] No Supabase credentials found")
            print("[DB] Please set SUPABASE_URL and SUPABASE_KEY")
            return
        
        # Connect to Supabase
        try:
            self.client = create_client(supabase_url, supabase_key)
            self.connected = True
            print("[DB] Connected to Supabase successfully!")
        except Exception as e:
            print(f"[DB] Connection failed: {e}")
            self.connected = False
    
    def is_connected(self) -> bool:
        """Check if database is connected"""
        return self.connected and self.client is not None
    
    # ════════════════════════════════════════════════════════════════════════
    # SAVE METHODS
    # ════════════════════════════════════════════════════════════════════════
    
    def log_threat(self, threat_data: Dict) -> bool:
        """
        Log a threat to database (simple version)
        
        Args:
            threat_data: Dictionary with threat info
        
        Returns:
            True if saved, False if error
        """
        if not self.is_connected():
            return False
        
        try:
            if 'timestamp' not in threat_data:
                threat_data['timestamp'] = datetime.now().isoformat()
            if 'created_at' not in threat_data:
                threat_data['created_at'] = datetime.now().isoformat()
            
            self.client.table('threats').insert(threat_data).execute()
            print(f"[DB] Threat saved: {threat_data.get('threat_type', 'Unknown')}")
            return True
        except Exception as e:
            print(f"[DB] Error saving threat: {e}")
            return False
    
    def save_threat(self,
                    message: str,
                    threat_level: str,
                    threat_type: str,
                    confidence: float,
                    explanation: str = "",
                    ai_provider: str = "Unknown",
                    user_id: str = "anonymous") -> bool:
        """
        Save a threat with individual parameters
        
        Args:
            message: The message that was analyzed
            threat_level: SAFE, LOW, MEDIUM, HIGH, CRITICAL
            threat_type: Type of threat detected
            confidence: How confident (0.0 to 1.0)
            explanation: Why it was flagged
            ai_provider: Which AI (OpenAI, Claude, Gemini)
            user_id: Who tested it
        
        Returns:
            True if saved, False if error
        """
        threat_data = {
            "message": message,
            "threat_level": threat_level,
            "threat_type": threat_type,
            "confidence": confidence,
            "explanation": explanation,
            "ai_provider": ai_provider,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "created_at": datetime.now().isoformat()
        }
        return self.log_threat(threat_data)
    
    # ════════════════════════════════════════════════════════════════════════
    # RETRIEVE METHODS
    # ════════════════════════════════════════════════════════════════════════
    
    def get_threats(self, limit: int = 100) -> List[Dict]:
        """Get recent threats from database"""
        if not self.is_connected():
            return []
        
        try:
            result = self.client.table('threats') \
                .select('*') \
                .order('created_at', desc=True) \
                .limit(limit) \
                .execute()
            return result.data
        except Exception as e:
            print(f"[DB] Error getting threats: {e}")
            return []
    
    def get_all_threats(self, limit: int = 100) -> List[Dict]:
        """Alias for get_threats()"""
        return self.get_threats(limit)
    
    def get_threats_by_level(self, threat_level: str) -> List[Dict]:
        """Get threats of a specific level"""
        if not self.is_connected():
            return []
        
        try:
            result = self.client.table('threats') \
                .select('*') \
                .eq('threat_level', threat_level) \
                .order('created_at', desc=True) \
                .execute()
            return result.data
        except Exception as e:
            print(f"[DB] Error: {e}")
            return []
    
    def get_threats_by_type(self, threat_type: str) -> List[Dict]:
        """Get threats of a specific type"""
        if not self.is_connected():
            return []
        
        try:
            result = self.client.table('threats') \
                .select('*') \
                .eq('threat_type', threat_type) \
                .order('created_at', desc=True) \
                .execute()
            return result.data
        except Exception as e:
            print(f"[DB] Error: {e}")
            return []
    
    # ════════════════════════════════════════════════════════════════════════
    # STATISTICS METHODS
    # ════════════════════════════════════════════════════════════════════════
    
    def get_threat_stats(self) -> Dict:
        """Get threat statistics (short name)"""
        return self.get_threat_statistics()
    
    def get_threat_statistics(self) -> Dict:
        """Get detailed threat statistics"""
        if not self.is_connected():
            return {
                "total": 0,
                "by_level": {},
                "by_type": {},
                "by_provider": {}
            }
        
        try:
            result = self.client.table('threats').select('*').execute()
            threats = result.data
            
            by_level = {}
            by_type = {}
            by_provider = {}
            
            for threat in threats:
                # Count by level
                level = threat.get('threat_level', 'UNKNOWN')
                by_level[level] = by_level.get(level, 0) + 1
                
                # Count by type
                ttype = threat.get('threat_type', 'UNKNOWN')
                by_type[ttype] = by_type.get(ttype, 0) + 1
                
                # Count by provider
                provider = threat.get('ai_provider', 'Unknown')
                by_provider[provider] = by_provider.get(provider, 0) + 1
            
            return {
                "total": len(threats),
                "by_level": by_level,
                "by_type": by_type,
                "by_provider": by_provider
            }
        except Exception as e:
            print(f"[DB] Error getting stats: {e}")
            return {
                "total": 0,
                "by_level": {},
                "by_type": {},
                "by_provider": {}
            }
    
    # ════════════════════════════════════════════════════════════════════════
    # DELETE METHODS
    # ════════════════════════════════════════════════════════════════════════
    
    def delete_threat(self, threat_id: int) -> bool:
        """Delete a single threat by ID"""
        if not self.is_connected():
            return False
        
        try:
            self.client.table('threats').delete().eq('id', threat_id).execute()
            print(f"[DB] Threat {threat_id} deleted")
            return True
        except Exception as e:
            print(f"[DB] Error deleting: {e}")
            return False
    
    def delete_all_threats(self) -> bool:
        """Delete ALL threats (use with caution!)"""
        if not self.is_connected():
            return False
        
        try:
            self.client.table('threats').delete().neq('id', 0).execute()
            print("[DB] All threats deleted!")
            return True
        except Exception as e:
            print(f"[DB] Error deleting all: {e}")
            return False


# ════════════════════════════════════════════════════════════════════════════
# TEST - Run when executed directly
# ════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("DATABASE CONNECTION TEST")
    print("=" * 60)
    
    # Create database connection
    db = ThreatDatabase()
    
    print("\n--- Connection Status ---")
    if db.is_connected():
        print("[OK] Database is connected!")
        
        # Test saving
        print("\n--- Testing Save ---")
        success = db.save_threat(
            message="Test message from database.py",
            threat_level="LOW",
            threat_type="test",
            confidence=0.5,
            explanation="This is a test entry"
        )
        if success:
            print("[OK] Test threat saved!")
        else:
            print("[ERROR] Could not save test threat")
        
        # Test statistics
        print("\n--- Statistics ---")
        stats = db.get_threat_statistics()
        print(f"Total threats in database: {stats['total']}")
        print(f"By level: {stats['by_level']}")
        print(f"By type: {stats['by_type']}")
        
    else:
        print("[ERROR] Database is NOT connected")
        print("\nTo fix this:")
        print("1. Create file: .streamlit/secrets.toml")
        print("2. Add your Supabase credentials:")
        print('   SUPABASE_URL = "https://xxx.supabase.co"')
        print('   SUPABASE_KEY = "your-key-here"')
    
    print("\n" + "=" * 60)
    input("Press Enter to close...")