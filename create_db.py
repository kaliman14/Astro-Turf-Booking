from app import app, db

# Ensure the application context is pushed before calling db.create_all()
with app.app_context():
    db.create_all()
    print("Database tables created successfully.")