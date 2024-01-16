from web432 import create_app, db

# Create the app instance
app = create_app()

# Manually create tables when the app starts
with app.app_context():
    db.create_all()

# Start the Flask development server
if __name__ == "__main__":
    app.run(debug=True)