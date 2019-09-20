"""OpenAQ Air Quality Dashboard with Flask."""
from flask import Flask
import openaq
from flask_sqlalchemy import SQLAlchemy

APP = Flask(__name__)
api = openaq.OpenAQ() 

@APP.route('/')
def root():
    """Base view."""

    return str(Record.query.filter(Record.value>=10).all())
    # return str(get_LA_measurement_list())


def get_LA_measurement_list():
    status, body = api.measurements(city='Los Angeles', parameter='pm25')
    measurement_list = []
    for i in range(len(body['results'])):
        time = body['results'][i]['date']['utc']
        result = body['results'][i]['value']
        tpl = (time, result)
        measurement_list.append(tpl)
    return measurement_list

APP.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
DB = SQLAlchemy(APP)

class Record(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    datetime = DB.Column(DB.String(25))
    value = DB.Column(DB.Float, nullable=False)

    def __repr__(self):
        return str({'id':self.id, 'datetime':self.datetime, 'value':self.value})

@APP.route('/refresh')
def refresh():
    status, body = api.measurements(city='Los Angeles', parameter='pm25')
    """Pull fresh data from Open AQ and replace existing data."""
    DB.drop_all()
    DB.create_all()
    for result in body['results']:
        entry = Record(datetime=result['date']['utc'],value=result['value'])
        DB.session.add(entry)
    # TODO Get data from OpenAQ, make Record objects with it, and add to db
    DB.session.commit()
    return 'Data refreshed!'
