"""
run.py
Application Entry Point
------------------------
This is the file you run to start the Flask development server.
It imports the app factory and creates the application instance.

Usage:
    python run.py
    OR
    flask run
"""

from app import create_app

# Create the Flask application using our factory function
app = create_app()

if __name__ == '__main__':
    # Run the development server
    # debug=True: auto-reloads on code changes and shows error details
    # host='0.0.0.0': makes it accessible on your local network
    # port=5000: the default Flask port
    app.run(debug=True, host='0.0.0.0', port=5000)
