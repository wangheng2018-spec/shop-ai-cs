# 🏪 Shop AI Customer Service (RAG Edition)

An **RAG (Retrieval-Augmented Generation)**-based AI customer service for second-hand phone shops. When customers ask questions, the AI retrieves relevant information from your real business data (knowledge base) and generates answers using the DeepSeek LLM—**no hallucinations, every answer is grounded in your actual data**.

## ✨ Features

- 💬 **Chat Interface**: Web-based conversations, works on both mobile and desktop
- 🧠 **RAG Retrieval**: jieba Chinese word segmentation + keyword matching to precisely locate relevant knowledge base snippets
- 🤖 **AI Generation**: DeepSeek LLM generates conversational responses based on retrieved data
- 📚 **Extensible Knowledge Base**: Trading methods, after-sales policies, phone specs, pricing, valuation assistant, available models, sales scripts—just add entries to `knowledge_base.py`
- 🛡️ **Anti-Hallucination**: If the information isn't in your knowledge base, the AI escalates to a human agent instead of making things up

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install flask jieba requests
```

### 2. Configure Your DeepSeek API Key
```bash
# Windows (persistent)
[Environment]::SetEnvironmentVariable("DEEPSEEK_API_KEY", "sk-your-key", "User")

# Or temporary (current session only)
$env:DEEPSEEK_API_KEY = "sk-your-key"
```
> No API key? Sign up at [platform.deepseek.com](https://platform.deepseek.com)—a $2 top-up lasts a long time.

### 3. Launch
```bash
python app.py
```
Open **http://localhost:5000** in your browser and start chatting.

### 4. LAN Access (for mobile devices)
After launching, connect your phone to the same WiFi and visit `http://your-computer-IP:5000` (find your IP with `ipconfig` on Windows).

## 🧠 How It Works (3-Step RAG Pipeline)

```
Customer Question → ① Retrieve (jieba tokenization matches knowledge base snippets)
                 → ② Generate (DeepSeek crafts a response from snippets + question)
                 → ③ Respond (conversational tone, persona-aware, hallucination-free)
```

**Why RAG instead of asking the AI directly?**
- The AI doesn't know your actual pricing, warranty policies, or trading methods—RAG "feeds" it this information
- Answers are grounded in evidence, building customer trust
- Updating knowledge only requires editing the knowledge base—no model retraining needed

## 📁 Project Structure

```
shop-ai-cs/
├── app.py              # Flask server + RAG retrieval + DeepSeek integration + chat UI
├── knowledge_base.py   # Knowledge base (your business data, freely expandable)
└── .gitignore          # Ignores cache/keys
```

## 📚 Adding Content to the Knowledge Base

Open `knowledge_base.py` and add an entry in this format:

```python
{
    "id": "custom-id",
    "keywords": ["keywords customers might use", "synonyms"],
    "content": "corresponding answer (accurate, specific)",
},
```

Save the file and restart the service to apply changes.

## 🔮 Roadmap

- [ ] Integrate WeChat / Official Account—customers can ask directly in WeChat
- [ ] Connect real transaction data (auto-updating valuations)
- [ ] Multi-turn conversation memory (remembering what the customer said earlier)
- [ ] Deploy to cloud server for true 24/7 availability

## 📄 License

Private project. All rights reserved.