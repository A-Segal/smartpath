from flask import Flask
from controller.volunteer_controller import volunteer_bp  # הקובץ שלך

app = Flask(__name__)
app.register_blueprint(volunteer_bp)

if __name__ == '__main__':
    app.run(debug=True)