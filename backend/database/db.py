"""
Database Configuration
SQLite database setup and initialization
"""

import sqlite3
from datetime import datetime

DATABASE_PATH = 'safeher_travel.db'

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE_PATH, timeout=20)
    conn.row_factory = sqlite3.Row
    conn.execute('pragma journal_mode=wal')
    return conn

def init_database():
    """Initialize database with all required tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Emergency contacts
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS emergency_contacts (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            relationship TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # SOS alerts
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sos_alerts (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            resolved_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # Location history
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS location_history (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            accuracy REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # Chat messages
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_messages (
            id TEXT PRIMARY KEY,
            conversation_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            message TEXT NOT NULL,
            sender TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # Police stations
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS police_stations (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            address TEXT,
            city TEXT,
            district TEXT,
            state TEXT DEFAULT 'Tamil Nadu',
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            phone TEXT,
            station_type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Hospitals
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hospitals (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            address TEXT,
            city TEXT,
            district TEXT,
            state TEXT DEFAULT 'Tamil Nadu',
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            phone TEXT,
            emergency_phone TEXT,
            hospital_type TEXT,
            is_24x7 INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Safe zones
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS safe_zones (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            address TEXT,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            is_24x7 INTEGER DEFAULT 0,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Accommodations
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accommodations (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            address TEXT,
            city TEXT,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            phone TEXT,
            rating REAL,
            safety_rating REAL,
            safety_verified INTEGER DEFAULT 0,
            price_range TEXT,
            amenities TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    print("✓ Database tables created successfully")
    
    # Seed Tamil Nadu data
    seed_tn_data(conn)
    
    conn.close()

def seed_tn_data(conn):
    """Seed database with Tamil Nadu emergency services data"""
    cursor = conn.cursor()
    
    # Sample police stations in major TN cities
    police_stations = [
        ('ps1', 'Chennai Central Police Station', 'Egmore, Chennai', 'Chennai', 'Chennai', 13.0781, 80.2619, '044-28447000', 'Central'),
        ('ps2', 'T. Nagar Police Station', 'T. Nagar, Chennai', 'Chennai', 'Chennai', 13.0417, 80.2338, '044-24340740', 'Local'),
        ('ps3', 'Anna Nagar Police Station', 'Anna Nagar, Chennai', 'Chennai', 'Chennai', 13.0878, 80.2084, '044-26162222', 'Local'),
        ('ps4', 'Coimbatore City Police', 'RS Puram, Coimbatore', 'Coimbatore', 'Coimbatore', 11.0168, 76.9558, '0422-2305000', 'City'),
        ('ps5', 'Madurai Central Police', 'Tallakulam, Madurai', 'Madurai', 'Madurai', 9.9195, 78.1193, '0452-2534444', 'Central'),
        ('ps6', 'Trichy Junction Police', 'Junction, Trichy', 'Tiruchirappalli', 'Tiruchirappalli', 10.8080, 78.6867, '0431-2414100', 'Junction'),
        ('ps7', 'Salem Town Police', 'Fort Main Road, Salem', 'Salem', 'Salem', 11.6643, 78.1460, '0427-2413333', 'Town'),
        ('ps8', 'Tirunelveli Town Police', 'High Ground Road, Tirunelveli', 'Tirunelveli', 'Tirunelveli', 8.7139, 77.7567, '0462-2501234', 'Town'),
        ('ps9', 'Vellore Fort Police', 'Fort Main Road, Vellore', 'Vellore', 'Vellore', 12.9165, 79.1325, '0416-2222100', 'Fort'),
        ('ps10', 'Thanjavur Central Police', 'South Main Road, Thanjavur', 'Thanjavur', 'Thanjavur', 10.7870, 79.1378, '04362-230100', 'Central'),
        ('ps11', 'Thiruvallur Town Police Station', 'Kakkalur Road, Thiruvallur', 'Thiruvallur', 'Thiruvallur', 13.1439, 79.9132, '044-27660211', 'Town'),
        ('ps12', 'Thiruvallur All Women Police Station', 'Junction Road, Thiruvallur', 'Thiruvallur', 'Thiruvallur', 13.1480, 79.9080, '044-27665411', 'Women'),
    ]
    
    for station in police_stations:
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO police_stations 
                (id, name, address, city, district, latitude, longitude, phone, station_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, station)
        except Exception as e:
            print(f"Error inserting police station: {e}")
    
    # Sample hospitals
    hospitals = [
        ('h1', 'Apollo Hospital Chennai', 'Greams Road, Chennai', 'Chennai', 'Chennai', 13.0563, 80.2474, '044-28296000', '044-28296000', 'Multi-specialty', 1),
        ('h2', 'Fortis Malar Hospital', 'Adyar, Chennai', 'Chennai', 'Chennai', 13.0038, 80.2557, '044-42892222', '044-42892222', 'Multi-specialty', 1),
        ('h3', 'Government General Hospital', 'Park Town, Chennai', 'Chennai', 'Chennai', 13.0878, 80.2785, '044-25305000', '044-25305000', 'Government', 1),
        ('h4', 'Coimbatore Medical College', 'Avinashi Road, Coimbatore', 'Coimbatore', 'Coimbatore', 10.9979, 76.9669, '0422-2570170', '0422-2570170', 'Government', 1),
        ('h5', 'Government Rajaji Hospital', 'Palpannai, Madurai', 'Madurai', 'Madurai', 9.9402, 78.1348, '0452-2530451', '0452-2530451', 'Government', 1),
        ('h6', 'Mahatma Gandhi Memorial Hospital', 'Srirangam, Trichy', 'Tiruchirappalli', 'Tiruchirappalli', 10.8656, 78.6921, '0431-2770221', '0431-2770221', 'Government', 1),
        ('h7', 'Salem Government Hospital', 'Fort Main Road, Salem', 'Salem', 'Salem', 11.6643, 78.1560, '0427-2241111', '0427-2241111', 'Government', 1),
        ('h8', 'Tirunelveli Medical College', 'High Ground Road, Tirunelveli', 'Tirunelveli', 'Tirunelveli', 8.7300, 77.7100, '0462-2571501', '0462-2571501', 'Government', 1),
        ('h9', 'Christian Medical College Vellore', 'Ida Scudder Road, Vellore', 'Vellore', 'Vellore', 12.9252, 79.1344, '0416-2282020', '0416-2282020', 'Private', 1),
        ('ps10', 'Thanjavur Central Police', 'South Main Road, Thanjavur', 'Thanjavur', 'Thanjavur', 10.7870, 79.1378, '04362-230100', 'Central'),
        ('h11', 'Government Headquarters Hospital Thiruvallur', 'Chennai-Tiruttani Highway, Thiruvallur', 'Thiruvallur', 'Thiruvallur', 13.1384, 79.9074, '044-27660311', '044-27660311', 'Government', 1),
        ('h12', 'Rishi Hospital', 'MGR Nagar, Thiruvallur', 'Thiruvallur', 'Thiruvallur', 13.1500, 79.9200, '044-27661234', '044-27661234', 'Private', 1),
    ]
    
    for hospital in hospitals:
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO hospitals 
                (id, name, address, city, district, latitude, longitude, phone, emergency_phone, hospital_type, is_24x7)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, hospital)
        except Exception as e:
            print(f"Error inserting hospital: {e}")
    
    # Sample safe zones (24/7 public places)
    safe_zones = [
        ('sz1', 'Chennai Central Railway Station', 'railway_station', 'Periyamet, Chennai', 13.0827, 80.2707, 1, '24/7 railway station with police presence'),
        ('sz2', 'Chennai Airport', 'airport', 'Meenambakkam, Chennai', 12.9941, 80.1709, 1, 'International airport with 24/7 security'),
        ('sz3', 'Coimbatore Junction', 'railway_station', 'RS Puram, Coimbatore', 11.0078, 76.9618, 1, '24/7 railway station'),
        ('sz4', 'Madurai Junction', 'railway_station', 'West Marret Street, Madurai', 9.9258, 78.1198, 1, '24/7 railway station'),
        ('sz5', 'Phoenix Marketcity Chennai', 'shopping_mall', 'Velachery, Chennai', 12.9916, 80.2200, 0, 'Large shopping mall with security'),
    ]
    
    for zone in safe_zones:
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO safe_zones 
                (id, name, type, address, latitude, longitude, is_24x7, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, zone)
        except Exception as e:
            print(f"Error inserting safe zone: {e}")
    
    conn.commit()
    print("✓ Sample Tamil Nadu data seeded")

if __name__ == '__main__':
    init_database()
    print("\n✅ Database initialization complete!")
    print(f"Database created at: {DATABASE_PATH}")