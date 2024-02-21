from datetime import datetime

from flask import Flask, request, Response
from flask_admin.base import Admin, AdminIndexView, expose
from flask_sqlalchemy import SQLAlchemy
from flask_admin.contrib.sqla import ModelView
from flask_cors import CORS
from flask_basicauth import BasicAuth
from werkzeug.exceptions import HTTPException

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

app.config['SECRET_KEY'] = 'y0uw111n3v3rgu3ss'

app.config['DATABASE_FILE'] = 'db.sqlite'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + app.config['DATABASE_FILE']
app.config['SQLALCHEMY_ECHO'] = True
app.config['BASIC_AUTH_USERNAME'] = 'admin'
app.config['BASIC_AUTH_PASSWORD'] = 'password'
# app.config['BASIC_AUTH_FORCE'] = True

db = SQLAlchemy(app)
basic_auth = BasicAuth(app)


class Connection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=datetime.now)
    name = db.Column(db.String(128))
    phone = db.Column(db.String(128))
    tariff = db.Column(db.String(128))
    speed = db.Column(db.String(128))


class AuthException(HTTPException):
    def __int__(self, message):
        super().__init__(message, Response(
            message, 401,
            {'WWW-Authenticate': 'Basic realm="Login Required"'}
        ))


class ConnectionModelView(ModelView):
    column_list = ['id', 'date_created', 'name', 'phone', 'tariff', 'speed']
    column_labels = {'id': 'ID', 'date_created': 'Created Date'}
    column_searchable_list = ['id', 'tariff', 'phone', 'speed']
    column_sortable_list = ['id', 'date_created', 'name', 'phone', 'tariff', 'speed']

    def is_accessible(self):
        return basic_auth.authenticate()

    def inaccessible_callback(self, name, **kwargs):
        return basic_auth.challenge()


class SecureAdminIndexView(AdminIndexView):
    @expose()
    @basic_auth.required
    def index(self):
        return super(SecureAdminIndexView, self).index()


admin = Admin(app, name='MTS', template_mode='bootstrap3', index_view=SecureAdminIndexView())
admin.add_view(ConnectionModelView(Connection, db.session))

with app.app_context():
    db.create_all()


@app.route('/')
def hello_world():  # put application's code here
    return 'hi'


@app.post('/api/create')
def create_connect():
    data = request.get_json()
    name = data["name"]
    phone = data["phoneNumber"]
    tariff = data["tariffName"]
    speed = data["speed"]
    new_user = Connection(name=name, phone=phone, tariff=tariff, speed=speed)
    db.session.add(new_user)
    db.session.commit()
    return ''


if __name__ == '__main__':
    app.run(debug=True)
