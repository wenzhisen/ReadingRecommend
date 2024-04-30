# -*- coding: utf-8 -*-
import os
from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify, url_for, send_from_directory, redirect
from flask_cors import *
import json
from globals import *
# from utils import *
import datetime
import jwt
import hashlib
import time

app = Flask(__name__)
app.config['JSONIFY_MIMETYPE'] = "application/json;charset=utf-8"
# 处理跨域，在任何条件下都能访问
CORS(app, resources=r'/*')
SECRET_KEY = "your_secret_key_here"
users = {
    "000000": "password123"
}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ExpiredSignatureError = 1
InvalidTokenError = 2

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def get_suffix(filename):
    print(filename)
    return filename.rsplit('.', 1)[1]


def generate_char_id():
    m2 = hashlib.md5()
    m2.update(str(time.time()).encode('utf-8'))

    return m2.hexdigest()[8:-8]

def load_txt(file_name):
    pass


def load_pdf(file_name):
    pass


def load_file(file_name):
    pass


def decode_auth_token(request_):
    """
    此函数用于解析和验证JWT。
    如果token有效，返回用户名。
    如果token无效，返回相应的错误信息。
    """
    try:
        # 解码 JWT
        data = request.headers["token"]
        payload = jwt.decode(data, SECRET_KEY, algorithms=["HS256"])
        return payload['sub']  # 返回用户名
    except jwt.ExpiredSignatureError:
        return ExpiredSignatureError  # token过期
    except Exception as e:
        return InvalidTokenError  # token无效


# @app.route('/agent', methods=["POST", "GET"])
def agent():
    data = request.get_data()
    data = json.loads(data)
    data = data["body"]
    data = json.loads(data)
    data = data['history']
    input = data[-1]["text"]
    data.pop()
    response = "这是一个测试接口，你可以在这里测试你的对话模型。"
    return response


# 聊天接口
@app.route('/chat', methods=["POST"])
def chat():
    auth = decode_auth_token(request)
    if auth == ExpiredSignatureError:
        return jsonify({'message': "无效Token，请重新登陆"}), 401
    if auth == InvalidTokenError:
        return jsonify({'message': "无效Token，请重新登陆"}), 401

    data = request.get_data()
    data = json.loads(data)
    input = data["input"]
    session_id = data["SessionId"]
    if session_id not in all_sessions_id:
        return jsonify({"answer": "SessionId不存在"}), 401  # 找不到数据
    history = sid2history[session_id].history
    response = "这是一个测试接口，你可以在这里测试你的对话模型。"
    # 添加到历史记录
    sid2history[session_id].add({"role": "user", "text": input})
    sid2history[session_id].add({"role": "ai", "text": response})
    return jsonify({"answer": response}), 200


# 新建对话
@app.route('/new_session', methods=["GET"])
def new_session():
    auth = decode_auth_token(request)
    if auth == ExpiredSignatureError:
        return jsonify({'message': "无效Token，请重新登陆"}), 401
    if auth == InvalidTokenError:
        return jsonify({'message': "无效Token，请重新登陆"}), 401

    new_session_id = generate_char_id()
    all_sessions_id.append(new_session_id)
    sid2history[new_session_id] = ChatHistory()
    return jsonify({"session_id": new_session_id})


# 返回所有SessionID
@app.route('/all_session_id', methods=["GET"])
def get_all_session_id():
    auth = decode_auth_token(request)
    if auth == ExpiredSignatureError:
        return jsonify({'message': "无效Token，请重新登陆"}), 401
    if auth == InvalidTokenError:
        return jsonify({'message': "无效Token，请重新登陆"}), 401

    res = []
    for sid in all_sessions_id:
        a = ""
        if len(sid2history[sid].history) != 0:
            a = sid2history[sid].history[0]["text"]
        res.append({"SessionId": sid, "first_msg": a})
    return res


@app.route("/get_history", methods=["GET"])
def get_history():
    auth = decode_auth_token(request)
    if auth == ExpiredSignatureError:
        return jsonify({'message': "无效Token，请重新登陆"}), 401
    if auth == InvalidTokenError:
        return jsonify({'message': "无效Token，请重新登陆"}), 401

    session_id = request.args.get("SessionId")
    if session_id not in all_sessions_id:
        return jsonify({"Error": "SessionId不存在"}), 401  # 找不到数据
    history = sid2history[session_id].history
    return jsonify(history)


@app.route("/clear", methods=["POST", "GET"])
def clear():
    auth = decode_auth_token(request)
    if auth == ExpiredSignatureError:
        return jsonify({'message': "无效Token，请重新登陆"}), 401
    if auth == InvalidTokenError:
        return jsonify({'message': "无效Token，请重新登陆"}), 401

    sid2history.clear()
    all_sessions_id.clear()
    all_sessions_id.append("for_testing")  # for testing
    sid2history["for_testing"] = ChatHistory()
    sid2history["for_testing"].add({"role": "ai", "text": "你好，我是图书推荐机器人，你可以问我关于图书的问题。"})
    return jsonify({"msg": "清空成功"})


@app.route('/upload_file', methods=['POST'])
def upload_file():
    auth = decode_auth_token(request)
    if auth == ExpiredSignatureError:
        return jsonify({'message': "无效Token，请重新登陆"}), 401
    if auth == InvalidTokenError:
        return jsonify({'message': "无效Token，请重新登陆"}), 401

    file = request.files['file']
    session_id = request.args.get("SessionId")
    if session_id not in all_sessions_id:
        return jsonify({"msg": "SessionId不存在"}), 401
    if file and allowed_file(file.filename):
        filename = generate_char_id() + "-" + secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        file_url = "get_file/" + filename

        prompt = f"我上传了一个文件，文件名为{filename}。文件内容已经以文本向量嵌入的形式存储在FAISS向量数据库中。你可以使用matchCorpusInFaissByEmb工具查询这个文件的内容。"
        load_file(filename)
        sid2history[session_id].add({"role": "user", "text": prompt})

        return jsonify({"file_url": file_url})
    else:
        return jsonify({"msg": "文件格式不支持"}), 400


@app.route('/get_file/<filename>', methods=['GET'])
def get_file(filename):
    auth = decode_auth_token(request)
    if auth == ExpiredSignatureError:
        return jsonify({'message': "无效Token，请重新登陆"}), 401
    if auth == InvalidTokenError:
        return jsonify({'message': "无效Token，请重新登陆"}), 401

    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/login', methods=['POST'])
def login():
    telephone = request.json.get('telephone')
    password = request.json.get('password')

    # 验证用户名和密码
    if telephone in users and users[telephone] == password:
        # 生成JWT Token
        token = jwt.encode({
            'sub': telephone,
            'iat': datetime.datetime.utcnow(),
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)  # 设置token有效期为30分钟
        }, SECRET_KEY, algorithm="HS256")
        print(token)
        return jsonify({'token': token})
    else:
        return jsonify({'message': 'Invalid credentials'}), 401


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8000)
