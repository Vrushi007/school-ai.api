from flask import Flask
from routes.lesson_plan import lesson_plan_bp

def create_app():
    """
    Application factory pattern
    """
    app = Flask(__name__)
    
    # Register blueprints
    app.register_blueprint(lesson_plan_bp)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)