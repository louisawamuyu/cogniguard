"""
DATABASE - SQLite/Turso Integration for CogniGuard
Uses local SQLite for development, can connect to Turso in production.
"""

import os
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional


class ThreatDatabase:
    """
    Database manager for CogniGuard
    Uses local SQLite database (works everywhere!)
    """
    
    def __init__(self, db_path: str = "cogniguard.db"):
        """Initialize database connection"""
        
        print("[DB] Initializing SQLite Database...")
        
        self.db_path = db_path
        self.conn = None
        self.connected = False
        
        try:
            # Connect to local SQLite database
            self.conn = sqlite3.connect(db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row  # Enable dict-like access
            self.connected = True
            print(f"[DB] Connected to SQLite: {db_path}")
            
            # Create tables
            self._create_tables()
            
        except Exception as e:
            print(f"[DB] Connection failed: {e}")
            self.connected = False
    
    def _create_tables(self):
        """Create the threats table if it doesn't exist"""
        if not self.conn:
            return
        
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS threats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message TEXT,
                    threat_level TEXT,
                    threat_type TEXT,
                    confidence REAL,
                    explanation TEXT,
                    ai_provider TEXT DEFAULT 'Unknown',
                    user_id TEXT DEFAULT 'anonymous',
                    timestamp TEXT,
                    created_at TEXT
                )
            """)
            self.conn.commit()
            print("[DB] Threats table ready")
        except Exception as e:
            print(f"[DB] Error creating table: {e}")
    
    def is_connected(self) -> bool:
        """Check if database is connected"""
        return self.connected and self.conn is not None
    
    # ════════════════════════════════════════════════════════════════════════
    # SAVE METHODS
    # ════════════════════════════════════════════════════════════════════════
    
    def log_threat(self, threat_data: Dict) -> bool:
        """Log a threat to database"""
        if not self.is_connected():
            return False
        
        try:
            if 'timestamp' not in threat_data:
                threat_data['timestamp'] = datetime.now().isoformat()
            if 'created_at' not in threat_data:
                threat_data['created_at'] = datetime.now().isoformat()
            
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO threats (
                    message, threat_level, threat_type, confidence,
                    explanation, ai_provider, user_id, timestamp, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                threat_data.get('message', ''),
                threat_data.get('threat_level', 'UNKNOWN'),
                threat_data.get('threat_type', 'unknown'),
                threat_data.get('confidence', 0.0),
                threat_data.get('explanation', ''),
                threat_data.get('ai_provider', 'Unknown'),
                threat_data.get('user_id', 'anonymous'),
                threat_data.get('timestamp'),
                threat_data.get('created_at')
            ))
            self.conn.commit()
            
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
        """Save a threat with individual parameters"""
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
    
    def _rows_to_dicts(self, rows) -> List[Dict]:
        """Convert sqlite3.Row objects to list of dictionaries"""
        return [dict(row) for row in rows]
    
    def get_threats(self, limit: int = 100) -> List[Dict]:
        """Get recent threats from database"""
        if not self.is_connected():
            return []
        
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT * FROM threats
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))
            
            return self._rows_to_dicts(cursor.fetchall())
            
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
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT * FROM threats
                WHERE threat_level = ?
                ORDER BY created_at DESC
            """, (threat_level,))
            
            return self._rows_to_dicts(cursor.fetchall())
            
        except Exception as e:
            print(f"[DB] Error: {e}")
            return []
    
    def get_threats_by_type(self, threat_type: str) -> List[Dict]:
        """Get threats of a specific type"""
        if not self.is_connected():
            return []
        
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT * FROM threats
                WHERE threat_type = ?
                ORDER BY created_at DESC
            """, (threat_type,))
            
            return self._rows_to_dicts(cursor.fetchall())
            
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
            cursor = self.conn.cursor()
            
            # Get total count
            cursor.execute("SELECT COUNT(*) FROM threats")
            total = cursor.fetchone()[0]
            
            # Count by level
            cursor.execute("""
                SELECT threat_level, COUNT(*) as count
                FROM threats
                GROUP BY threat_level
            """)
            by_level = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Count by type
            cursor.execute("""
                SELECT threat_type, COUNT(*) as count
                FROM threats
                GROUP BY threat_type
            """)
            by_type = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Count by provider
            cursor.execute("""
                SELECT ai_provider, COUNT(*) as count
                FROM threats
                GROUP BY ai_provider
            """)
            by_provider = {row[0]: row[1] for row in cursor.fetchall()}
            
            return {
                "total": total,
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
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM threats WHERE id = ?", (threat_id,))
            self.conn.commit()
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
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM threats")
            self.conn.commit()
            print("[DB] All threats deleted!")
            return True
        except Exception as e:
            print(f"[DB] Error deleting all: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.connected = False
            print("[DB] Connection closed")


# ════════════════════════════════════════════════════════════════════════════
# TEST - Run when executed directly
# ════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("SQLITE DATABASE CONNECTION TEST")
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
        
        # Test retrieval
        print("\n--- Recent Threats ---")
        threats = db.get_threats(limit=5)
        for t in threats:
            print(f"  - [{t['threat_level']}] {t['threat_type']}: {t['message'][:50]}...")
        
    else:
        print("[ERROR] Database is NOT connected")
    
    print("\n" + "=" * 60)
    input("Press Enter to close...")