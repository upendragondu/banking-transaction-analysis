
from flask import Flask


def create_app():
    app = Flask(__name__)

    from app.routes import api
    app.register_blueprint(api)

    @app.get("/")
    def home():
        return {
            "message": "Banking Transaction Analysis API",
            "status": "running",
            "mode": "educational_simulation"
        }, 200

    @app.get("/health")
    def health():
        return {"status": "healthy"}, 200

    return app
