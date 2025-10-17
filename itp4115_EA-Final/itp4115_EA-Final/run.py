from app import app

if __name__ == '__main__':
    # Explicitly set host, port, and debug to make local runs predictable
    # Disable the reloader to avoid intermittent restarts which can cause connection refusals
    app.run(host='0.0.0.0', port=8000, debug=True, use_reloader=False)
