from flask import Flask
from controller.volunteer_controller import volunteer_bp  # הקובץ שלך
from controller.recipient_request_controller import recipient_request_bp  # הקובץ שלך

from controller.ds_request_controller import ds_request_bp
app = Flask(__name__)
app.register_blueprint(volunteer_bp)
app.register_blueprint(ds_request_bp)
app.register_blueprint(recipient_request_bp)



@app.route('/')
def home():
    return "Server is running!"



if __name__ == '__main__':
    app.run(debug=True)




