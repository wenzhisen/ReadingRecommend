# -*- coding: utf-8 -*-
import os
from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify, url_for, send_from_directory
from flask_cors import *
import json
from globals import *
from utils import *
from BookRec import BookRec
import datetime
import jwt

app = Flask(__name__)
app.config['JSONIFY_MIMETYPE'] = "application/json;charset=utf-8"
# 处理跨域，在任何条件下都能访问
CORS(app, resources=r'/*')
SECRET_KEY = "your_secret_key_here"
users = {
    "admin": "password123"
}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

chatbot = BookRec()


@app.route('/agent', methods=["POST", "GET"])
def agent():
    data = request.get_data()
    data = json.loads(data)
    data = data["body"]
    data = json.loads(data)
    data = data['history']
    input = data[-1]["text"]
    data.pop()
    response = chatbot.response(input, data)
    return response


# 聊天接口
@app.route('/chat', methods=["POST"])
def chat():
    data = request.get_data()
    data = json.loads(data)
    input = data["input"]
    session_id = data["SessionId"]
    if session_id not in all_sessions_id:
        return jsonify({"answer": "SessionId不存在"}), 401  # 找不到数据
    history = sid2history[session_id].history
    response = chatbot.response(input, history)
    # 添加到历史记录
    sid2history[session_id].add({"role": "user", "text": input})
    sid2history[session_id].add({"role": "ai", "text": response})
    return jsonify({"answer": response}), 200


# 新建对话
@app.route('/new_session', methods=["GET"])
def new_session():
    new_session_id = generate_char_id()
    all_sessions_id.append(new_session_id)
    sid2history[new_session_id] = ChatHistory()
    return jsonify({"session_id": new_session_id})


# 返回所有SessionID
@app.route('/all_session_id', methods=["GET"])
def get_all_session_id():
    res = []
    for sid in all_sessions_id:
        a = ""
        if len(sid2history[sid].history) != 0:
            a = sid2history[sid].history[0]["text"]
        res.append({"SessionId": sid, "first_msg": a})
    return res


@app.route("/get_history", methods=["GET"])
def get_history():
    session_id = request.args.get("SessionId")
    if session_id not in all_sessions_id:
        return jsonify({"Error": "SessionId不存在"}), 401  # 找不到数据
    history = sid2history[session_id].history
    return jsonify(history)


@app.route("/clear", methods=["POST", "GET"])
def clear():
    sid2history.clear()
    all_sessions_id.clear()
    all_sessions_id.append("for_testing")  # for testing
    sid2history["for_testing"] = ChatHistory()
    sid2history["for_testing"].add({"role": "ai", "text": "你好，我是图书推荐机器人，你可以问我关于图书的问题。"})
    return jsonify({"msg": "清空成功"})


@app.route('/upload_file', methods=['POST'])
def upload_file():
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
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    # 验证用户名和密码
    if username in users and users[username] == password:
        # 生成JWT Token
        token = jwt.encode({
            'sub': username,
            'iat': datetime.datetime.utcnow(),
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)  # 设置token有效期为30分钟
        }, SECRET_KEY, algorithm="HS256")
        return jsonify({'token': token})
    else:
        return jsonify({'message': 'Invalid credentials'}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8000)
