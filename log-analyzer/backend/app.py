from flask import Flask
from flask_cors import CORS
from config import Config
from routes.auth import auth_bp
from routes.upload import upload_bp
from routes.analysis import analysis_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    
    # Initialize configuration
    config = config_class()
    config.init_app(app)
    
    # Set Flask configuration
    app.config['DEBUG'] = config.DEBUG
    app.config['HOST'] = config.HOST
    app.config['PORT'] = config.PORT
    app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH
    app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER
    app.config['ALLOWED_EXTENSIONS'] = config.ALLOWED_EXTENSIONS
    app.config['MAX_LOG_SIZE'] = config.MAX_LOG_SIZE
    app.config['OPENAI_API_KEY'] = config.OPENAI_API_KEY
    
    # Enable CORS for frontend communication
    CORS(app, origins=['https://log-analyzer-sepia.vercel.app', 'https://log-analyzer-suparshwa31s-projects.vercel.app', 'https://log-analyzer-git-main-suparshwa31s-projects.vercel.app'], supports_credentials=True)
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(upload_bp, url_prefix='/api/upload')
    app.register_blueprint(analysis_bp, url_prefix='/api/analysis')
    
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'message': 'Log Analyzer API is running'}
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(
        debug=app.config['DEBUG'], 
        host=app.config['HOST'], 
        port=app.config['PORT']
    )
