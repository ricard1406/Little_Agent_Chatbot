📦 Download these models before running the application:
```bash
ollama pull qwen3:4b            (not required when use Claude)
ollama pull nomic-embed-text
```
📦 Installation

   ```bash
   wget https://github.com/ricard1406/Little_Agent_Chatbot/archive/refs/heads/main.zip
   unzip main.zip
   mv Little_Agent_Chatbot-main Little_Agent_Chatbot
   cd Little_Agent_Chatbot
   ```
   ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    pip install langchain langchain-community langchain-core langchain-ollama langchain-chroma sentence-transformers pypdf python-dotenv unstructured[pdf] tiktoken gradio
 mariadb langchain-anthropic
   ```
📦 Config your api_key
   ```bash
   [open your fav editor and set your openweather key, DB user and password, claude api_key]
   cd Little_Agent_Chatbot
   [vi] .env
   OPENWEATHER_API_KEY=your_api_key_here
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   ANTHROPIC_API_KEY=your_api_key_here
   ```
📦 Start app
   Usage

   Run the application:
   ```bash
   python3 Little_Agent_Chatbot text                     (text interface Ollama LLM)
   python3 Little_Agent_Chatbot graph                    (text interface Ollama LLM)

   python3 Little_Agent_Chatbot text --provider anthropic    (text interface Calude LLM)
   python3 Little_Agent_Chatbot graph --provider anthropic   (text interface Claude LLM)

   When use graph interface open your browser and run local URL:
   http://127.0.0.1:7860
   ```

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
