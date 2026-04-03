from flask import Flask, render_template, request, jsonify, session
import openai
import json
import os
import time
import random

app = Flask(__name__)
app.secret_key = 'your-secret-key'

CONFIG_FILE = "characters.json"

def load_characters():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_characters(characters):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(characters, f, ensure_ascii=False, indent=2)

@app.route("/")
def index():
    characters = load_characters()
    messages = session.get("messages", [])
    return render_template("index.html", characters=characters, messages=messages)

@app.route("/api/characters", methods=["GET"])
def get_characters():
    return jsonify(load_characters())

@app.route("/api/characters", methods=["POST"])
def add_character():
    data = request.json
    characters = load_characters()
    
    char = {
        "id": data.get("id", ""),
        "name": data["name"],
        "avatar": data.get("avatar", "🤖"),
        "system_prompt": data["system_prompt"],
        "api_url": data["api_url"],
        "api_key": data["api_key"],
        "model": data["model"],
        "enabled": True
    }
    
    characters.append(char)
    save_characters(characters)
    return jsonify({"success": True})

@app.route("/api/characters/<char_id>", methods=["DELETE"])
def delete_character(char_id):
    characters = load_characters()
    characters = [c for c in characters if c["id"] != char_id]
    save_characters(characters)
    return jsonify({"success": True})

@app.route("/api/characters/<char_id>", methods=["PUT"])
def update_character(char_id):
    data = request.json
    characters = load_characters()
    
    for char in characters:
        if char["id"] == char_id:
            if "enabled" in data:
                char["enabled"] = data["enabled"]
            if "system_prompt" in data:
                char["system_prompt"] = data["system_prompt"]
            if "api_url" in data:
                char["api_url"] = data["api_url"]
            if "api_key" in data:
                char["api_key"] = data["api_key"]
            if "model" in data:
                char["model"] = data["model"]
            break
    
    save_characters(characters)
    return jsonify({"success": True})

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")
    enabled_chars = data.get("enabled_chars", [])
    
    characters = load_characters()
    enabled_chars_data = [c for c in characters if c["id"] in enabled_chars]
    
    messages = session.get("messages", [])
    
    if user_message:
        messages.append({"role": "user", "content": user_message, "name": "你", "avatar": "👤"})
    
    responses = []
    chat_history = []
    
    for char in enabled_chars_data:
        other_chars = [c for c in enabled_chars_data if c["id"] != char["id"]]
        
        if other_chars:
            other_names = "、".join([c["name"] for c in other_chars])
            interaction_prompt = f"""
当前聊天室成员: {other_names}
你们是一个聊天群，请积极和他们互动交流，可以：
- 回应其他人的观点
- 提问让别人回答
- 分享相关经历或看法
- 适当用@姓名的方式点名互动
"""
        else:
            interaction_prompt = ""
        
        system_prompt = char["system_prompt"] + interaction_prompt
        
        try:
            api_url = char["api_url"].rstrip('/')
            if not api_url.endswith('/v1'):
                api_url = api_url + "/v1"
            
            openai.api_key = char["api_key"]
            openai.api_base = api_url
            
            response = openai.ChatCompletion.create(
                model=char["model"],
                messages=[{"role": "system", "content": system_prompt}] + chat_history,
                temperature=0.8,
                max_tokens=2000
            )
            
            ai_response = response.choices[0].message.content
        except Exception as e:
            ai_response = f"错误: {str(e)}"
        
        msg = {
            "role": "assistant",
            "name": char["name"],
            "avatar": char["avatar"],
            "content": ai_response,
            "char_id": char["id"]
        }
        messages.append(msg)
        responses.append(msg)
        chat_history.append({"role": "assistant", "content": f"【{char['name']}】: {ai_response}"})
    
    session["messages"] = messages
    return jsonify({"responses": responses})

@app.route("/api/ai_talk", methods=["POST"])
def ai_talk():
    data = request.json
    enabled_chars = data.get("enabled_chars", [])
    
    characters = load_characters()
    enabled_chars_data = [c for c in characters if c["id"] in enabled_chars]
    
    messages = session.get("messages", [])
    
    responses = []
    chat_history = []
    
    for char in enabled_chars_data:
        other_chars = [c for c in enabled_chars_data if c["id"] != char["id"]]
        
        if messages and len(messages) >= 2:
            topic_context = "【聊天记录】\n"
            for m in messages[-6:]:
                name = m.get("name", "用户")
                content = m.get("content", "")[:150]
                topic_context += f"{name}: {content}\n"
            topic_context += "\n请根据以上对话，选择一个你感兴趣的角度参与讨论，可以：\n- 回应某个人的观点\n- 提出不同看法\n- 分享相关经历\n- 提出问题让大家回答"
        else:
            topic_context = "当前聊天室刚开始，请开启一个有趣的话题引发讨论。可以选择：科技前沿、社会热点、生活趣事、电影推荐等大家感兴趣的话题。"
        
        if other_chars:
            other_names = "、".join([c["name"] for c in other_chars])
            topic_context += f"\n\n当前聊天室成员: {other_names}。请积极和他们互动！"
        
        system_prompt = char["system_prompt"] + "\n\n" + topic_context
        
        try:
            api_url = char["api_url"].rstrip('/')
            if not api_url.endswith('/v1'):
                api_url = api_url + "/v1"
            
            openai.api_key = char["api_key"]
            openai.api_base = api_url
            
            response = openai.ChatCompletion.create(
                model=char["model"],
                messages=[{"role": "system", "content": system_prompt}] + chat_history,
                temperature=0.9,
                max_tokens=1000
            )
            
            ai_response = response.choices[0].message.content
        except Exception as e:
            ai_response = f"错误: {str(e)}"
        
        msg = {
            "role": "assistant",
            "name": char["name"],
            "avatar": char["avatar"],
            "content": ai_response,
            "char_id": char["id"]
        }
        messages.append(msg)
        responses.append(msg)
        chat_history.append({"role": "assistant", "content": f"【{char['name']}】: {ai_response}"})
    
    session["messages"] = messages
    return jsonify({"responses": responses})

@app.route("/api/clear", methods=["POST"])
def clear_messages():
    session["messages"] = []
    return jsonify({"success": True})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
