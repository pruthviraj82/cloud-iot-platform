import os
import sqlite3
from app import create_app, db

def reset_database():
    print("🔄 Resetting database...")
    
    # Delete existing database
    db_path = 'instance/users.db'
    if os.path.exists(db_path):
        os.remove(db_path)
        print("🗑️ Old database deleted")
    
    # Create new database with updated schema
    app = create_app()
    with app.app_context():
        db.create_all()
        print("✅ New database created with updated schema!")
        print("📊 Tables created:")
        print("   - User (with created_at column)")
        print("   - DeviceConnection")
        
        # Test creating a user
        from app.models import User
        test_user = User(email="test@example.com")
        test_user.set_password("password123")
        db.session.add(test_user)
        db.session.commit()
        print("👤 Test user created: test@example.com / password123")
        
        # Create sample data file
        from app.routes import ensure_data_file
        ensure_data_file()
        print("📁 Sample data file created")

if __name__ == "__main__":
    reset_database()