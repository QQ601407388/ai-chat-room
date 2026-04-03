# AI 聊天室

一个可以添加多个 AI 角色一起聊天的聊天室。

## 功能

- ✅ 添加多个 AI 角色
- ✅ 自定义角色人设 (System Prompt)
- ✅ 支持多种大模型 API (OpenAI 兼容格式)
- ✅ 每个角色独立配置 API Key
- ✅ 实时聊天室互动
- ✅ 角色启用/禁用

## 支持的 API

- OpenAI API
- Claude API (通过 API URL)
- GLM API
- Kimi API
- LongCat API
- 任何 OpenAI 兼容格式的 API

## 安装

```bash
pip install -r requirements.txt
```

## 运行

```bash
streamlit run app.py
```

## 使用方法

1. 在左侧添加新角色，填写：
   - 角色名称
   - 头像
   - 角色人设 (System Prompt)
   - API URL
   - API Key
   - 模型名称

2. 启用要参与聊天的角色

3. 在右侧输入消息，所有启用的 AI 角色都会回复

## 示例角色人设

```
你是一个温柔善良的助手，说话风格亲切，喜欢用表情符号。
回答问题时耐心详细，偶尔会开玩笑调节气氛。
```

## 项目结构

```
ai_chat_room/
├── app.py              # 主程序
├── requirements.txt     # 依赖
└── characters.json     # 角色配置 (自动生成)
```
