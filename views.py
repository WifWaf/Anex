from flask import jsonify, request, render_template, make_response
import definitions
from models import User, Data, Device, Session
import uuid
from app import app
from validation import Validate
from errors import Err
from provision import Provision
from werkzeug.security import generate_password_hash, check_password_hash
from flask import abort
from user_session import UserSession
import json
import pickle


@app.route('/api/save_user_data/<uuid:skey>', methods=['POST'])
def save_user_data(skey):
    req_data = request.json
    pad_data = req_data.get('padData')
    mesh_colors = req_data.get('meshColor')

    print(pad_data)
    user_session = Validate.session_key(skey)
    json_pad_data = json.dumps(pad_data)
    json_mesh_colors = json.dumps(mesh_colors)

    if user_session is None:
        abort(400, "User not found")

    Provision.Register.user_data(user_session.user_id, json_pad_data, json_mesh_colors)
    return {"message": "User Authenticated, saving data"}, 200


@app.route('/api/load_user_data/<uuid:skey>', methods=['GET'])
def load_user_data(skey):
    print("Load Data Request")
    user_session = Validate.session_key(skey)

    if user_session is None:
        abort(400, "User not found")

    json_out = Provision.Request.user_data(user_session.user_id)

    if json_out is None:
        return jsonify({'message': 'No data found for the user.'}), 404

    return jsonify(json_out), 200


@app.route('/api/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    print("username: " + username, "password: " + password)
    Validate.username(username)
    Validate.password(password)

    if Validate.username_exists(username)[0] is False or Validate.password_exist(username, password)[0] is False:
        print("Incorrect Username or Password")
        abort(400, "Incorrect Username or Password")

    print(Validate.username_exists(username))
    print(Validate.password_exist(username, password))
    user = Validate.username_exists(username)[1]
    key = UserSession.create_session(user.id)
    return {"key": str(key)}, 200


@app.route('/api/create/device/<uuid:admin_pass>', methods={'GET'})
def create_new_device_id(admin_pass):
    _admin_pass = str(admin_pass)

    if _admin_pass != definitions.ADMIN_TOKEN:
        return Err.client_return(Err.ERROR_MESSAGES['ADMIN_ID'], admin_pass)

    gen_dev_id = str(uuid.uuid4())

    Provision.Register.device(gen_dev_id, "0.0 - DBG")

    return gen_dev_id


@app.route('/api/create/user/<uuid:admin_pass>/<string:user_name>/<string:user_email>/<string:password>', methods={'PUT'})
def create_user(admin_pass, user_name, user_email, password):
    _admin_pass = str(admin_pass)

    if _admin_pass != definitions.ADMIN_TOKEN:
        return Err.client_return(Err.ERROR_MESSAGES['ADMIN_ID'], admin_pass)

    print(admin_pass, user_name, user_email, password)
    Validate.email(user_email)
    Validate.password(password)
    Validate.username(user_name)
    Validate.username_exists(user_name)

    hashed_password = generate_password_hash(password)
    gen_user_id = str(uuid.uuid4())        # generate a random uuid4
    Provision.Register.user(gen_user_id, user_name, user_email, hashed_password)

    return gen_user_id


# DEBUG START --------------------------------------------------------------

@app.route('/api/list/data', methods={'GET'})
def list_all_data():
    data = Data.query.all()

    for row in data:
        print(row)  # print new user row

    return jsonify(data)


@app.route('/api/list/users', methods={'GET'})
def list_all_users():
    users = User.query.all()

    for row in users:
        print(row)  # print new user row

    return jsonify(users)


@app.route('/api/list/devices', methods={'GET'})
def list_all_devices():
    devices = Device.query.all()

    for row in devices:
        print(row)  # print new user row

    return jsonify(devices)

# DEBUG END ------------------------------------------------------------
