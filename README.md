# 🤖 Little Agent Chatbot 🤖

- A lightweight local AI agent chatbot powered by Ollama and LangChain/LangGraph with RAG capabilities.
- Tested LLM: qwen3:1.7b; qwen3:4b; granite3.3:2b; llama3.2:3b; cogito:3b
- Dual provider support: a) local Ollama LLM b) remote Claude LLM (API-key required) 
- Tested on low-budget hardware 8GB RAM.
- Included tools: real time weather, calculate, local documents RAG, local SQL database query and update.

## 🌟 Overview

Little Agent Chatbot is a simple yet powerful local AI assistant that runs entirely on your machine. Built for learning and experimentation, it combines the power of LLMs with advanced retrieval-augmented generation (RAG) to create an intelligent chatbot that can work with your personal documents and provide real-time information.

## ✨ Key Features

- **🏠 Fully Local**: Runs completely on your machine - no data leaves your device
- **💰 Budget-Friendly**: Works on low-resource hardware using efficient models.
- **🏠 Dual provider**: a) local Ollama LLM b) remote Claude LLM (API-key required)
- **📚 RAG Integration**: Upload and chat with your PDF documents using ChromaDB and Nomic embeddings
- **🌐 Real-Time Data**: Get live weather information and perform calculations
- **🔧 Agent Framework**: Extensible agent system built with Langchain
- **💻 Easy Interface**: Clean web interface powered by Gradio
- **💻 Interface Options**: Graphic web interface or classic text interface.
- **🔓 Open Source**: MIT licensed and fully customizable

## 🚀 Tech Stack

- **LLM Backend**: [Ollama](https://ollama.ai/) with Qwen3 model (1.7B or 4B variants)
- **Agent Framework**: [Langchain](https://python.langchain.com/) ecosystem
- **Vector Database**: [ChromaDB](https://www.trychroma.com/) for document embeddings
- **Embeddings**: Nomic-embed-text for semantic search
- **Document Processing**: PyPDF, Unstructured, TikToken
- **Web Interface**: [Gradio](https://gradio.app/)
- **Language**: Python
- **License**: MIT

## 🎯 What Makes This Special?

- **Privacy First**: Your conversations and documents stay on your device
- **Cost Effective**: No API costs - runs on your hardware
- **Educational**: Perfect for learning about AI agents and RAG systems
- **Extensible**: Easy to modify and add new capabilities
- **Lightweight**: Designed to work on modest hardware setups

## 📖 Usage

### Basic Chat
Simply type your questions and the AI will respond using the local Qwen3 model.

### Document Upload
Upload PDF documents to enable RAG functionality. The chatbot will be able to answer questions based on your documents.

### Agent Capabilities
- **Weather Information**: Get real-time weather data
- **Calculations**: Perform mathematical operations
- **Document Q&A**: Query your uploaded PDFs

## 🏗️ Architecture

```
User Input → Gradio Interface → Langchain Agent → Ollama/Qwen3 → Response
                                      ↓
                              RAG System (PDF Documents)
                                      ↓
                              External Tools (Weather, Calculator)
```

## 🔧 Configuration

Customize the chatbot by modifying:
- Model parameters in `config.py`
- Agent tools and capabilities
- UI appearance and behavior
- RAG document processing settings

## 🤝 Contributing

Contributions are welcome! This project is designed for learning and experimentation. Feel free to:
- Add new agent capabilities
- Improve the UI/UX
- Enhance document processing
- Add new LLM models
- Fix bugs and improve performance

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎓 Educational Purpose

This project is perfect for:
- Learning about AI agents and RAG systems
- Understanding local LLM deployment
- Experimenting with Langchain framework
- Building privacy-focused AI applications
- Exploring document-based AI interactions

## 🔮 Future Enhancements

- Support for more document formats
- Additional agent tools and capabilities
- Multi-language support
- Voice interface integration
- Mobile-friendly interface

## 📞 Support

If you encounter issues or have questions:
- Open an issue on GitHub
- Check the documentation
- Review the example configurations

## 🌟 Star the Project

If you find this project helpful, please give it a star! It helps others discover the project and motivates continued development.

---

**Made with ❤️ for the AI community**

*Happy chatting with your local AI agent!* 🚀
