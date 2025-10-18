from flask import Flask
import threading
import webbrowser
import os
import sys

def create_app():
    app = Flask(__name__)
    from routes import bp  
    app.register_blueprint(bp)
    return app

def run_flask():
    if not os.path.exists('templates'):
        os.makedirs('templates')
    app = create_app()
    app.run(port=5000, debug=False)

if __name__ == "__main__":
    run_flask()
