# 🏪 店铺 AI 客服（RAG 版）

基于 **RAG（检索增强生成）** 的二手手机店铺 AI 客服。客户问问题，AI 从你的真实经营资料（知识库）里检索相关内容，再结合 DeepSeek 大模型生成回答——**不瞎编，答案都来自你的真实资料**。

## ✨ 功能

- 💬 **聊天界面**：网页对话，手机/电脑都能用
- 🧠 **RAG 检索**：jieba 中文分词 + 关键词匹配，从知识库精准找到相关片段
- 🤖 **AI 生成**：DeepSeek 大模型基于检索到的资料生成口语化回答
- 📚 **知识库可扩展**：交易方式、售后保障、手机信息、价格、估价助手、在售机型、联系话术……加新知识只需往 `knowledge_base.py` 加条目
- 🛡️ **防瞎编**：资料里没有的内容，AI 会转人工，不胡编乱造

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install flask jieba requests
```

### 2. 配置 DeepSeek API Key
```bash
# Windows（永久生效）
[Environment]::SetEnvironmentVariable("DEEPSEEK_API_KEY", "sk-你的key", "User")

# 或临时（当前窗口）
$env:DEEPSEEK_API_KEY = "sk-你的key"
```
> 没有 Key？去 [platform.deepseek.com](https://platform.deepseek.com) 注册，充值 10 元能用很久。

### 3. 启动
```bash
python app.py
```
浏览器打开 **http://localhost:5000** 即可对话。

### 4. 局域网访问（手机也能用）
启动后手机连同一 WiFi，访问 `http://你的电脑IP:5000`（Windows 用 `ipconfig` 查 IP）。

## 🧠 工作原理（RAG 三步）

```
客户问题 → ① 检索（jieba 分词匹配知识库片段）
         → ② 生成（DeepSeek 基于片段 + 问题生成回答）
         → ③ 返回（口语化、带人设、防瞎编）
```

**为什么用 RAG 而不是直接问 AI？**
- AI 不知道你的真实报价、保修政策、交易方式——RAG 把这些"喂"给它
- 回答有据可依，客户更信任
- 知识更新只改知识库，不用重新训练模型

## 📁 项目结构

```
shop-ai-cs/
├── app.py              # Flask 服务 + RAG 检索 + DeepSeek 调用 + 聊天网页
├── knowledge_base.py   # 知识库（你的经营资料，可随意扩充）
└── .gitignore          # 忽略缓存/密钥
```

## 📚 知识库怎么加内容

打开 `knowledge_base.py`，按格式加一条：

```python
{
    "id": "自定义id",
    "keywords": ["客户会问的关键词", "同义词"],
    "content": "对应的回答内容（真实、具体）",
},
```

保存后重启服务即可生效。

## 🔮 下一步规划

- [ ] 接入微信/公众号，客户直接在微信里问
- [ ] 接入真实成交数据（自动更新估价）
- [ ] 多轮对话记忆（记住客户前面说过什么）
- [ ] 部署到云服务器，真正 24 小时在线

## 📄 许可证

私有项目，版权所有。
