from flask import Flask,jsonify,request,url_for, redirect
from flask_sqlalchemy import SQLAlchemy
import time
import calendar
from db_config import *


def make_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASEURI
    app.config['SECRET_KEY'] = "random string"
    return app

app = make_app()

db = SQLAlchemy(app)



class Store(db.Model):
    id = db.Column('id', db.Integer, primary_key = True,autoincrement=True)
    store_key = db.Column(db.String(10))
    value = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime)
    
    def __init__(self,key,value,epoch):
        self.store_key = key
        self.value = value
        self.timestamp = epoch
        
#Get all key-values from database

@app.route('/vaultdragon/queryall')
def queryall():
    stores = Store.query.all()
    res = []
    for store in stores:
        result = {}
        for i in store.__dict__:
            print store.__dict__[i]
            if i[0] == '_':
                continue
            else:
                result[i] = store.__dict__[i]
        res.append(result)
                
    r = {}
    r['result'] = res

    return jsonify(**r)

#Query by key name

@app.route('/vaultdragon/<mykey>', methods=['GET'])
def queryByKey(mykey):
    
    query_string = request.args.get('timestamp')
    
    if query_string is None:
        store = db.session.query(Store).filter_by(store_key=mykey).first()
    else:
        store = db.session.query(Store).filter_by(store_key=mykey,timestamp=query_string).first()
    print query_string
    if store is None:
        return 'Sorry no such key found!'
    else:
        return 'Value: '+store.value
    
#Insert/Update key-value

@app.route('/vaultdragon/add', methods=['POST'])
def addValue():
    data = request.get_json()
    
    json_key = data.keys() 
    json_value = data.values()
    if not request.json:
        abort(400)
        
    if not json_key[0] or not json_value[0]:
        return 'Please give a key and a value.'
    
    if is_duplicate_key(json_key):
        store = db.session.query(Store).filter_by(store_key=json_key).first()
        store.value = json_value
        store.timestamp = get_epoch()
        db.session.commit()
        return 'Updated'
    
    store = Store(json_key,json_value,get_epoch())
    
    db.session.add(store)
    db.session.commit()
    return 'Added'

#Error handlers

@app.errorhandler(500)
def server_error(e):
    return 'Try with valid data'

@app.errorhandler(400)
def invalid_data_error(e):
    return 'Try with valid data'

@app.errorhandler(404)
def page_not_found(e):
    return 'Try with valid URL'


def is_duplicate_key(key):
    key = db.session.query(Store).filter_by(store_key=key).first()
    if key:
        return True
    else:
        return False
    
def get_epoch():
    return calendar.timegm(time.gmtime())

def to_date(epoch):
    return time.gmtime(epoch/1000)

if __name__ == '__main__':
    db.create_all()
    app.run(debug=False)