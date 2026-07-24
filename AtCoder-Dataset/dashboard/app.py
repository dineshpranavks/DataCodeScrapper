import sys
import logging
from pathlib import Path
from flask import Flask

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from dashboard.routes import bp as main_bp
from dashboard.database import get_statistics

def create_app():
    app = Flask(__name__)
    
    app.register_blueprint(main_bp)
    
    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        from flask import render_template
        return render_template('404.html'), 404
        
    @app.errorhandler(500)
    def internal_server_error(e):
        from flask import render_template
        return render_template('500.html'), 500

    return app

if __name__ == "__main__":
    # Suppress default Werkzeug startup messages to match required output
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    
    app = create_app()
    
    print("================================")
    print("AtCoder Dataset Explorer")
    print("================================")
    print("Dashboard Started")
    print("Database Connected")
    
    stats = get_statistics()
    print(f"Loaded {stats.get('total_problems', 0)} Problems")
    
    print("Server Running")
    print("http://localhost:5000")
    
    app.run(host="localhost", port=5000, debug=True, use_reloader=False)
