Project Overview (Simple Words)
This project is a two-part online dashboard used to check the health of industrial motors. It uses Python (Flask) for the main brain and a real-time data push (WebSocket) to show updates instantly.

1. How to Set It Up and Run It
    To run the project on your computer, follow these simple steps:
    Create a Workspace: Open your command line and run the first command to create a safe space for your Python code (venv). Then run the second command (activate) to start working in that space.
    Get the Tools: Use pip install... to download all the necessary libraries like Flask (the framework) and flask-socketio (for real-time updates).
    Build the Data: Run python setup_db.py. This creates your database file (app.db) and fills it with test information (users, zones, and motors).
    Start the Program: Run python app.py. This starts the web server and also starts the background process that simulates the real-time sensor data.
    View the Dashboard: Open your web browser and go to http://127.0.0.1:5000/.

2. What's Under the Hood (Technical Details)
A. Tools Used (Tech Stack)
    Backend (Server): Python Flask (This is the code that runs the logic).
    Database (Data Storage): SQLite (A simple file-based database).
    Real-Time Data: Flask-SocketIO (A library that allows the server to instantly push data to the browser).
    Security (Login): bcrypt (Securely scrambles passwords) and Flask Sessions (Keeps you logged in).
    Frontend (What you see): Standard HTML, CSS, and JavaScript. We also use Chart.js to draw the graphs.

B. Key Design Decisions
    Simple Structure (Monolithic): We put all the code (server, templates, and basic files) together in one Flask application to make it easy to build and test quickly.
    Instant Updates (WebSocket): We chose Flask-SocketIO to push sensor data immediately to the browser. This means the "Latest Readings" update without needing to refresh the entire page.
    Mock Data (Simulated): The historical charts and the real-time sensor readings are fake (simulated) data. This was done to guarantee that the charts and real-time features work perfectly, even without a physical motor sensor.

C. What the Dashboard Links Do (API Documentation)
    Your dashboard uses these specific links (Endpoints) to fetch and manage data:
    /login / /logout: For logging in and out.
    /api/zones: Gets the list of zones and their overall health status.
    /api/motors/<motor_id>/detail: Gets the specific details for one motor.
    /api/sensors/<motor_id>/history: Generates and sends the mock historical data for the chart.