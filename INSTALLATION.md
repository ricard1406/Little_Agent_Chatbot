# Little Agent Chatbot

A simple AI agent and RAG (Retrieval-Augmented Generation) project designed for learning purposes and as a foundation for building more complex AI applications.

## Features

- **Simple AI Agent**: Basic conversational AI capabilities using local language models
- **RAG Implementation**: Retrieval-Augmented Generation for enhanced responses using document knowledge
- **Local Model Support**: Works with Ollama-hosted models for privacy and offline usage
- **Document Processing**: PDF document ingestion and processing capabilities
- **Vector Database**: ChromaDB integration for efficient document retrieval
- **Web Interface**: Gradio-based user interface for easy interaction
- **Lightweight**: Tested on low-budget hardware configurations

## Requirements

- Python 3.8+
- Ollama installed on your system
- Sufficient disk space for language models

## Installation

1. **Clone the repository**
   ```bash
   git clone ricard1406/Little_Agent_Chatbot
   cd Little_Agent_Chatbot
   ```

2. **Create and activate virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install langchain langchain-community langchain-core langchain-ollama chromadb sentence-transformers pypdf python-dotenv unstructured[pdf] tiktoken gradio
   ```

4. **Install and setup Ollama models**
   ```bash
   # Choose one of the following models based on your hardware:
   ollama run qwen3:4b    # For better performance (requires more resources)
   # OR
   ollama run qwen3:1.7b  # For lower resource usage
   
   # Install embedding model
   ollama pull nomic-embed-text
   ```

## Usage

Run the application:
```bash
python3 Little_Agent_Chatbot
```

The application will start a Gradio web interface where you can interact with the chatbot and upload documents for RAG functionality.

## Model Performance

- **qwen3:4b**: it works on low-budget hardware.
- **qwen3:1.7b**: minimum hardware request i tested.
- **Enhanced models**: It is supposed using more powerful models will generally provide faster and better results

Both models have been tested and confirmed to work on low-budget hardware configurations.

## Project Structure

This project demonstrates:
- Basic AI agent implementation
- RAG system setup and configuration
- Document processing and embedding
- Vector database integration
- Simple web interface creation

## Contributing

This is a learning project. Feel free to fork, modify, and experiment with the code. Pull requests and suggestions are welcome!

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Disclaimer

**NO WARRANTY**: This software is provided "as is" without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose, and non-infringement. In no event shall the authors or copyright holders be liable for any claim, damages, or other liability, whether in an action of contract, tort, or otherwise, arising from, out of, or in connection with the software or the use or other dealings in the software.

**Educational Purpose**: This project is intended for educational and learning purposes. It is not designed for production use without proper testing, security review, and additional safeguards.

**Model Limitations**: The performance and accuracy of responses depend on the underlying language models used. Results may vary and should not be relied upon for critical decisions.

**Hardware Requirements**: Performance may vary significantly based on hardware specifications. Users are responsible for ensuring their system meets the requirements for their chosen models.

**Data Privacy**: When using local models, ensure you understand the data handling practices and comply with applicable privacy regulations in your jurisdiction.

## Support

For questions, issues, or contributions, please open an issue on the GitHub repository.

---

*Happy coding and learning!* 🤖✨
