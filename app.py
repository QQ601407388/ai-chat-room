import streamlit as st
import json
import os
from datetime import datetime

st.set_page_config(
    page_title="AI 聊天室",
    page_icon="💬",
    layout="wide"
)

CONFIG_FILE = "characters.json"

def load_characters():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_characters(characters):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(characters, f, ensure_ascii=False, indent=2)

def call_ai_api(api_url: str, api_key: str, model: str, system_prompt: str, messages: list):
    import requests
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    all_messages = [{"role": "system", "content": system_prompt}] + messages
    
    payload = {
        "model": model,
        "messages": all_messages,
        "temperature": 0.8,
        "max_tokens": 2000
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"错误: {str(e)}"

def main():
    st.title("💬 AI 聊天室")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "characters" not in st.session_state:
        st.session_state.characters = load_characters()
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.header("🤖 AI 角色管理")
        
        with st.expander("➕ 添加新角色", expanded=False):
            with st.form("add_character"):
                name = st.text_input("角色名称", placeholder="例如：小爱同学")
                avatar = st.selectbox("头像", ["🤖", "👾", "🦊", "🐱", "🐶", "🦁", "🐼", "🦄", "👻", "🤡"])
                system_prompt = st.text_area(
                    "角色人设 (System Prompt)", 
                    placeholder="定义这个AI角色的性格、说话风格、知识背景等...",
                    height=150
                )
                
                st.subheader("API 配置")
                api_url = st.text_input(
                    "API URL",
                    placeholder="https://api.openai.com/v1/chat/completions",
                    help="支持 OpenAI 兼容格式的 API"
                )
                api_key = st.text_input("API Key", type="password")
                model = st.text_input("模型名称", placeholder="gpt-4o-mini, claude-3-haiku, glm-4-flash 等")
                
                submitted = st.form_submit_button("添加角色", type="primary")
                
                if submitted and name and system_prompt and api_url and api_key and model:
                    char = {
                        "id": datetime.now().strftime("%Y%m%d%H%M%S"),
                        "name": name,
                        "avatar": avatar,
                        "system_prompt": system_prompt,
                        "api_url": api_url,
                        "api_key": api_key,
                        "model": model,
                        "enabled": True
                    }
                    st.session_state.characters.append(char)
                    save_characters(st.session_state.characters)
                    st.success(f"角色 '{name}' 添加成功！")
                    st.rerun()
        
        st.subheader("已添加的角色")
        
        for char in st.session_state.characters:
            with st.container():
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    enabled = st.checkbox(
                        f"{char['avatar']} {char['name']}", 
                        value=char.get("enabled", True),
                        key=f"enable_{char['id']}"
                    )
                with col_b:
                    if st.button("🗑️", key=f"del_{char['id']}"):
                        st.session_state.characters = [c for c in st.session_state.characters if c["id"] != char["id"]]
                        save_characters(st.session_state.characters)
                        st.rerun()
                
                char["enabled"] = enabled
        
        st.divider()
        
        if st.button("🗑️ 清空聊天记录", type="secondary"):
            st.session_state.messages = []
            st.rerun()
    
    with col2:
        st.header("💬 聊天室")
        
        enabled_chars = [c for c in st.session_state.characters if c.get("enabled", True)]
        
        if not enabled_chars:
            st.info("👈 请先添加并启用至少一个 AI 角色")
        
        chat_container = st.container()
        with chat_container:
            for msg in st.session_state.messages:
                if msg["role"] == "user":
                    st.chat_message("user", avatar="👤").write(msg["content"])
                elif msg["role"] == "assistant":
                    st.chat_message("assistant", avatar=msg.get("avatar", "🤖")).write(f"**{msg.get('name', 'AI')}**: {msg['content']}")
        
        if prompt := st.chat_input("输入消息...", disabled=len(enabled_chars) == 0):
            st.chat_message("user", avatar="👤").write(prompt)
            
            user_msg = {"role": "user", "content": prompt}
            st.session_state.messages.append(user_msg)
            
            chat_history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[:-1]]
            
            for char in enabled_chars:
                with st.spinner(f"{char['avatar']} {char['name']} 正在回复..."):
                    ai_response = call_ai_api(
                        char["api_url"],
                        char["api_key"],
                        char["model"],
                        char["system_prompt"],
                        chat_history
                    )
                    
                    ai_msg = {
                        "role": "assistant",
                        "name": char["name"],
                        "avatar": char["avatar"],
                        "content": ai_response
                    }
                    st.session_state.messages.append(ai_msg)
                    
                    st.chat_message("assistant", avatar=char["avatar"]).write(f"**{char['name']}**: {ai_response}")
            
            st.rerun()

if __name__ == "__main__":
    main()
