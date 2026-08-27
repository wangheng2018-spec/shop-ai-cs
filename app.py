# -*- coding: utf-8 -*-
"""
店铺 AI 客服 · RAG 版
- 检索：jieba 分词 + 关键词匹配，从知识库找相关片段
- 生成：把相关片段 + 用户问题发给 DeepSeek，AI 基于你的真实资料回答
- 网页：Flask 提供聊天界面（手机也能打开）

运行：python app.py  → 浏览器打开 http://localhost:5000
"""

import os
import re
import jieba
import requests
from flask import Flask, request, jsonify, render_template_string

from knowledge_base import get_knowledge_base

# ============ 配置 ============
API_URL = "https://api.deepseek.com/chat/completions"
MODEL = "deepseek-chat"
API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")  # 从环境变量读，或下面直接填

# 如果环境变量没设，可以在这里填（不推荐硬编码，但本地用方便）
# API_KEY = "sk-你的key"

# 系统提示词 —— 客服人设 + RAG 用法
SYSTEM_PROMPT = """你是一家二手手机店铺的 AI 客服，老板卖 iPhone 为主。
你的回答要：
1. 口语化、热情、真诚，像真人客服，简短（一般 2~4 句）
2. 优先使用下面提供的【资料片段】回答，资料里有的信息就用资料里的
3. 资料里没有的，就诚实说"这个我帮您问下老板"，不要编造
4. 涉及价格，引导客户提供：型号+存储+电池效率，然后说帮忙估价
5. 涉及交易，强调：同城当面验机 / 外地顺丰保价 / 可走闲鱼平台
6. 涉及售后，强调：保修 30 天，非人为问题免费维修
7. 可以适当用 emoji，不要超过 3 个
8. 不知道的就转人工，不要瞎编

【资料片段】
{context}"""

# 聊天网页（内嵌 HTML，简单版）
CHAT_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>店铺 AI 客服</title>
<style>
  body { font-family: "Microsoft YaHei",sans-serif; background:#f0f4f8; margin:0; padding:16px; }
  .wrap { max-width:560px; margin:0 auto; background:#fff; border-radius:16px; box-shadow:0 2px 16px rgba(0,0,0,.08); overflow:hidden; }
  .head { background:linear-gradient(135deg,#2563eb,#0ea5e9); color:#fff; padding:16px 20px; }
  .head h1 { margin:0; font-size:18px; }
  .head p { margin:4px 0 0; font-size:12px; opacity:.85; }
  .chat { padding:16px; height:400px; overflow-y:auto; background:#fafbfc; }
  .msg { margin-bottom:12px; display:flex; }
  .msg.user { justify-content:flex-end; }
  .msg .bubble { max-width:78%; padding:10px 14px; border-radius:14px; font-size:14px; line-height:1.6; white-space:pre-wrap; }
  .msg.bot .bubble { background:#fff; border:1px solid #e5e7eb; border-top-left-radius:4px; }
  .msg.user .bubble { background:linear-gradient(135deg,#2563eb,#0ea5e9); color:#fff; border-top-right-radius:4px; }
  .input-row { display:flex; padding:12px; border-top:1px solid #e5e7eb; gap:8px; }
  .input-row input { flex:1; padding:10px 14px; border:1.5px solid #e5e7eb; border-radius:20px; font-size:14px; outline:none; }
  .input-row input:focus { border-color:#2563eb; }
  .input-row button { padding:10px 20px; border:none; border-radius:20px; background:#2563eb; color:#fff; font-size:14px; cursor:pointer; font-weight:600; }
  .input-row button:disabled { opacity:.5; }
  .typing { color:#9ca3af; font-size:12px; padding:4px 6px; }
  .quick { padding:0 16px 12px; display:flex; gap:8px; flex-wrap:wrap; }
  .quick button { padding:6px 12px; border-radius:16px; border:1px solid #bfdbfe; background:#eff6ff; color:#1d4ed8; font-size:12px; cursor:pointer; }
</style>
</head>
<body>
<div class="wrap">
  <div class="head">
    <h1>🏪 店铺 AI 客服</h1>
    <p>二手手机 · 估价 / 在售 / 售后，有问必答</p>
  </div>
  <div class="chat" id="chat">
    <div class="msg bot"><div class="bubble">你好呀！我是店铺 AI 客服 👋 可以帮你：① 估价（发型号+内存+电池）② 介绍在售机器 ③ 解答售后/交易问题。想问什么？</div></div>
  </div>
  <div class="quick">
    <button onclick="ask('iPhone 16 Pro Max 256G 多少钱？')">💰 问价格</button>
    <button onclick="ask('怎么交易？能走闲鱼吗？')">📦 交易方式</button>
    <button onclick="ask('有保修吗？坏了怎么办？')">🛡️ 售后</button>
    <button onclick="ask('电池效率多少？')">🔋 电池</button>
  </div>
  <div class="input-row">
    <input id="input" placeholder="输入你的问题..." onkeydown="if(event.key==='Enter')send()">
    <button id="sendBtn" onclick="send()">发送</button>
  </div>
</div>
<script>
const chat = document.getElementById('chat');
function addMsg(role, text) {
  const div = document.createElement('div');
  div.className = 'msg ' + role;
  div.innerHTML = '<div class="bubble"></div>';
  div.querySelector('.bubble').textContent = text;
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
}
async function ask(q) { document.getElementById('input').value = q; send(); }
async function send() {
  const input = document.getElementById('input');
  const q = input.value.trim();
  if (!q) return;
  addMsg('user', q);
  input.value = '';
  const btn = document.getElementById('sendBtn');
  btn.disabled = true;
  const typing = document.createElement('div');
  typing.className = 'typing'; typing.textContent = '正在输入...';
  chat.appendChild(typing); chat.scrollTop = chat.scrollHeight;
  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({message: q})
    });
    const data = await res.json();
    typing.remove();
    addMsg('bot', data.reply || '（没收到回复，稍后再试）');
  } catch(e) {
    typing.remove();
    addMsg('bot', '网络错误，请稍后再试');
  }
  btn.disabled = false;
}
</script>
</body>
</html>"""

app = Flask(__name__)


def retrieve(query, top_k=4):
    """RAG 检索：jieba 分词 + 关键词匹配，返回最相关的知识片段"""
    words = set(jieba.lcut(query))
    scored = []
    for item in get_knowledge_base():
        kws = set(item["keywords"])
        if not kws:
            continue
        hit = len(words & kws)
        if hit > 0:
            scored.append((hit, item["id"], item["content"]))
    scored.sort(key=lambda x: -x[0])
    if not scored:
        # 兜底
        for item in get_knowledge_base():
            if item["id"] == "fallback":
                return [item["content"]]
        return []
    return [c for _, _, c in scored[:top_k]]


def chat_with_ai(user_msg, context_list):
    """调 DeepSeek 生成回答"""
    context = "\n\n".join(context_list)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT.format(context=context)},
        {"role": "user", "content": user_msg},
    ]
    resp = requests.post(
        API_URL,
        headers={"Authorization": "***" + API_KEY, "Content-Type": "application/json"},
        json={"model": MODEL, "messages": messages, "temperature": 0.6, "max_tokens": 500},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()


@app.route("/")
def index():
    return render_template_string(CHAT_HTML)


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_msg = (data or {}).get("message", "").strip()
    if not user_msg:
        return jsonify({"reply": "请说点什么吧"})
    if not API_KEY:
        return jsonify({"reply": "⚠️ 服务端还没配置 DeepSeek API Key。请设置环境变量 DEEPSEEK_API_KEY 后重启服务。"})
    try:
        ctx = retrieve(user_msg)
        reply = chat_with_ai(user_msg, ctx)
        return jsonify({"reply": reply, "context_ids": [c[:30] for c in ctx]})
    except Exception as e:
        return jsonify({"reply": f"出错了：{e}。请稍后再试或转人工。"})


if __name__ == "__main__":
    print("=" * 46)
    print("店铺 AI 客服 · RAG 版")
    print("请先在环境变量设置 DEEPSEEK_API_KEY")
    print("浏览器打开: http://localhost:5000")
    print("=" * 46)
    app.run(host="0.0.0.0", port=5000, debug=False)
