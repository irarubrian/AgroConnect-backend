from lib.app import create_app  # Imports your Flask app factory

app = create_app()              # Initializes your Flask app

if __name__ == "__main__":      # Runs the app with Flask's built-in server (for local dev)
    app.run()
