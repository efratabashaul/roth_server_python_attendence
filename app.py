from flask import Flask
from controllers.user_controller import user_bp
from controllers.summarize_controller import summarize_bp
from controllers.law_controller import law_bp
app = Flask(__name__)

# רישום ה-Blueprint של כל קונטרולר
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(summarize_bp, url_prefix='/api')
app.register_blueprint(law_bp, url_prefix='/api')

if __name__ == '__main__':
    app.run(debug=True)
