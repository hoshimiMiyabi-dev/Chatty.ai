# Chatty.ai
A fast, modular Discord AI bot with multimodal vision support, persistent local memory, and custom PIL status cards powered by Groq API.

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/discord.py-v2.3.0+-5865F2.svg" alt="discord.py">
  <img src="https://img.shields.io/badge/Groq-API-orange.svg" alt="Groq API">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License">
</p>

# Features

* **High-Speed Inference**: Powered by Groq's low-latency Llama 3.3 and Qwen 3.6 Vision endpoints.
* **Tactical PIL Card Generator**: Custom dark-themed image renders for status, ping diagnostics, and user cards.
* **`sys_prompt.txt` Engine**: Hot-swap system instructions on the fly without restarting the process.
* **Multimodal Vision**: Native image attachment handling for visual chat queries.
* **Persistent Local Memory**: Channels maintain isolated chat histories saved cleanly to local JSON stores.
* **Modular Cog Architecture**: Clean separation between administrative controls, system analytics, and visual utilities.
* **Hybrid Command Dispatcher**: Supports both traditional prefix (`-`) and Discord Application Slash commands (`/`).

# Project Architecture

```
├── cogs/
│   ├── admin.py       # Live prompt updates, model strings, and channel access
│   ├── stats.py       # Performance analytics image card (-stats / /stats)
│   └── visuals.py     # Latency diagnostics & user profile cards (-ping, -usercard)
├── memory/            # Channel-specific conversation memory dumps (JSON)
├── config.py          # Environment variables, global state, & prompt loader
├── image_gen.py       # Pillow graphics rendering engine
├── main.py            # Bot core initialization, event listeners, & chat handlers
├── utils.py           # Text formatting, file I/O safety, & font resolution
├── sys_prompt.txt     # System prompt configuration file
├── Font.ttf           # (Optional) TrueType Font file used for PIL card rendering
├── .env               # Secrets and tokens (excluded from source control)
└── requirements.txt   # Python dependency list
```

# Setup & Installation

### 1. Prerequisites

* Python 3.10 or higher
* Discord Bot Token
* Groq API Key

# 2. Repository Setup

```
# Clone repository
git clone
https://github.com/user/chatty-ai
cd chatty-ai

# Install dependencies
pip install -r requirements.txt
```

* requirements are:
 ```
discord.py>=2.3.2
groq>=0.9.0
pillow>=10.0.0
python-dotenv>=1.0.0
```

# License

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Distributed under the MIT License. Click the badge above or view [LICENSE](LICENSE) for details.
