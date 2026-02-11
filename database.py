"""
DATABASE - Neon PostgreSQL Integration for CogniGuard
Cloud SQL database that works on Windows!
"""

import os
from datetime import datetime
from typing import Dict, List, Optional

# Try to import psycopg2
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False
    print("[DB] psycopg2 not installed. Run: pip install psycopg2-binary")


class ThreatDatabase:
    """
    Database manager for CogniGuard
    Uses Neon PostgreSQL for cloud storage
    """
    
    def __init__(self):
        """Initialize database connection"""
        
        print("[DB] Initializing Neon PostgreSQL Connection...")
        
        self.conn = None
        self.connected = False
        
        if not POSTGRES_AVAILABLE:
            print("[DB] psycopg2 package not available")
            return
        
        # Get credentials from multiple sources
        database_url = None
        
        # Method 1: Try Streamlit secrets
        try:
            import streamlit as st
            database_url = st.secrets.get("DATABASE_URL", None)
            if database_url:
                print("[DB] Found credentials in Streamlit secrets")
        except:
            pass
        
        # Method 2: Try reading secrets file directly
        if not database_url:
            secrets_path = ".streamlit/secrets.toml"
            if os.path.exists(secrets_path):
                try:
                    with open(secrets_path, 'r') as f:
                        for line in f:
                            line = line.strip()
                            if line.startswith("DATABASE_URL"):
                                database_url = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if database_url:
                        print("[DB] Found credentials in secrets.toml file")
                except Exception as e:
                    print(f"[DB] Error reading secrets file: {e}")
        
        # Method 3: Try environment variables
        if not database_url:
            database_url = os.environ.get("DATABASE_URL", None)
            if database_url:
                print("[DB] Found credentials in environment variables")
        
        # Check if we have credentials
        if not database_url:
            print("[DB] No database credentials found")
            print("[DB] Please set DATABASE_URL in secrets.toml")
            return
        
        # Connect to Neon PostgreSQL
        try:
            self.conn = psycopg2.connect(database_url)
            self.conn.autocommit = False
            self.connected = True
            print("[DB] Connected to Neon PostgreSQL successfully!")
            
            # Create tables
            self._create_tables()
            
        except psycopg2.Error as e:
            print(f"[DB] Connection failed: {e}")
            self.connected = False
        except Exception as e:
            print(f"[DB] Error: {e}")
            self.connected = False
    
    def _create_tables(self):
        """Create the threats table if it doesn't exist"""
        if not self.conn:
            return
        
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS threats (
                        id SERIAL PRIMARY KEY,
                        message TEXT,
                        threat_level VARCHAR(50),
                        threat_type VARCHAR(100),
                        confidence REAL,
                        explanation TEXT,
                        ai_provider VARCHAR(100) DEFAULT 'Unknown',
                        user_id VARCHAR(100) DEFAULT 'anonymous',
                        timestamp TIMESTAMPTZ,
                        created_at TIMESTAMPTZ DEFAULT NOW()
                    )
                """)
                
                # Create indexes for better performance
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_threats_created_at 
                    ON threats(created_at DESC)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_threats_level 
                    ON threats(threat_level)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_threats_type 
                    ON threats(threat_type)
                """)
                
            self.conn.commit()
            print("[DB] Threats table ready")
            
        except Exception as e:
            self.conn.rollback()
            print(f"[DB] Error creating table: {e}")
    
    def is_connected(self) -> bool:
        """Check if database is connected"""
        if not self.connected or not self.conn:
            return False
        
        # Check if connection is still alive
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("SELECT 1")
            return True
        except:
            self.connected = False
            return False
    
    # ════════════════════════════════════════════════════════════════════════
    # SAVE METHODS
    # ════════════════════════════════════════════════════════════════════════
    
    def log_threat(self, threat_data: Dict) -> bool:
        """Log a threat to database"""
        if not self.is_connected():
            return False
        
        try:
            # Add timestamps if missing
            now = datetime.now()
            if 'timestamp' not in threat_data:
                threat_data['timestamp'] = now
            if 'created_at' not in threat_data:
                threat_data['created_at'] = now
            
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO threats (
                        message, threat_level, threat_type, confidence,
                        explanation, ai_provider, user_id, timestamp, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
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
            self.conn.rollback()
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
            "timestamp": datetime.now(),
            "created_at": datetime.now()
        }
        return self.log_threat(threat_data)
    
    # ════════════════════════════════════════════════════════════════════════
    # RETRIEVE METHODS
    # ════════════════════════════════════════════════════════════════════════
    
    def _row_to_dict(self, row, columns) -> Dict:
        """Convert a row tuple to dictionary"""
        if row is None:
            return {}
        
        result = dict(zip(columns, row))
        
        # Convert datetime objects to ISO strings
        for key in ['timestamp', 'created_at']:
            if key in result and result[key] is not None:
                if hasattr(result[key], 'isoformat'):
                    result[key] = result[key].isoformat()
        
        return result
    
    def get_threats(self, limit: int = 100) -> List[Dict]:
        """Get recent threats from database"""
        if not self.is_connected():
            return []
        
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, message, threat_level, threat_type, confidence,
                           explanation, ai_provider, user_id, timestamp, created_at
                    FROM threats
                    ORDER BY created_at DESC
                    LIMIT %s
                """, (limit,))
                
                columns = ['id', 'message', 'threat_level', 'threat_type', 'confidence',
                          'explanation', 'ai_provider', 'user_id', 'timestamp', 'created_at']
                
                return [self._row_to_dict(row, columns) for row in cursor.fetchall()]
            
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
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, message, threat_level, threat_type, confidence,
                           explanation, ai_provider, user_id, timestamp, created_at
                    FROM threats
                    WHERE threat_level = %s
                    ORDER BY created_at DESC
                """, (threat_level,))
                
                columns = ['id', 'message', 'threat_level', 'threat_type', 'confidence',
                          'explanation', 'ai_provider', 'user_id', 'timestamp', 'created_at']
                
                return [self._row_to_dict(row, columns) for row in cursor.fetchall()]
            
        except Exception as e:
            print(f"[DB] Error: {e}")
            return []
    
    def get_threats_by_type(self, threat_type: str) -> List[Dict]:
        """Get threats of a specific type"""
        if not self.is_connected():
            return []
        
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, message, threat_level, threat_type, confidence,
                           explanation, ai_provider, user_id, timestamp, created_at
                    FROM threats
                    WHERE threat_type = %s
                    ORDER BY created_at DESC
                """, (threat_type,))
                
                columns = ['id', 'message', 'threat_level', 'threat_type', 'confidence',
                          'explanation', 'ai_provider', 'user_id', 'timestamp', 'created_at']
                
                return [self._row_to_dict(row, columns) for row in cursor.fetchall()]
            
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
            with self.conn.cursor() as cursor:
                # Get total count
                cursor.execute("SELECT COUNT(*) FROM threats")
                total = cursor.fetchone()[0]
                
                # Count by level
                cursor.execute("""
                    SELECT threat_level, COUNT(*) as count
                    FROM threats
                    WHERE threat_level IS NOT NULL
                    GROUP BY threat_level
                """)
                by_level = {row[0]: row[1] for row in cursor.fetchall()}
                
                # Count by type
                cursor.execute("""
                    SELECT threat_type, COUNT(*) as count
                    FROM threats
                    WHERE threat_type IS NOT NULL
                    GROUP BY threat_type
                """)
                by_type = {row[0]: row[1] for row in cursor.fetchall()}
                
                # Count by provider
                cursor.execute("""
                    SELECT ai_provider, COUNT(*) as count
                    FROM threats
                    WHERE ai_provider IS NOT NULL
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
            with self.conn.cursor() as cursor:
                cursor.execute("DELETE FROM threats WHERE id = %s", (threat_id,))
            self.conn.commit()
            print(f"[DB] Threat {threat_id} deleted")
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"[DB] Error deleting: {e}")
            return False
    
    def delete_all_threats(self) -> bool:
        """Delete ALL threats (use with caution!)"""
        if not self.is_connected():
            return False
        
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("DELETE FROM threats")
            self.conn.commit()
            print("[DB] All threats deleted!")
            return True
        except Exception as e:
            self.conn.rollback()
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
    print("NEON POSTGRESQL CONNECTION TEST")
    print("=" * 60)
    
    # Create database connection
    db = ThreatDatabase()
    
    print("\n--- Connection Status ---")
    if db.is_connected():
        print("[OK] Database is connected to Neon PostgreSQL!")
        
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
            msg = t.get('message', 'N/A')[:50]
            print(f"  - [{t.get('threat_level', '?')}] {t.get('threat_type', '?')}: {msg}...")
        
    else:
        print("[ERROR] Database is NOT connected")
        print("\nTo fix this:")
        print("1. Create account at neon.tech")
        print("2. Create a project")
        print("3. Copy the connection string")
        print("4. Add to .streamlit/secrets.toml:")
        print('   DATABASE_URL = "postgresql://user:pass@ep-xxx.neon.tech/dbname"')
    
    print("\n" + "=" * 60)
    input("Press Enter to close...")