📓 Smart Notes Telegram Bot
Smart Notes is a Telegram bot powered by OpenAI and Pinecone that helps you store and search your personal notes using semantic search and embeddings. Just message the bot with /add <your note> or /search <keywords> and it will do the rest!

✨ Features
📌 Add notes via simple Telegram commands

🔍 Semantic search with vector embeddings (using OpenAI's text-embedding-ada-002)

🧠 Stores and retrieves notes using Pinecone's vector database

🤖 Interactive Telegram UI with inline buttons

🌐 Serverless-ready setup with Pinecone and OpenAI API

🛠️ Tech Stack
Python

OpenAI API

Pinecone Vector DB

python-telegram-bot

dotenv for managing environment variables

🚀 Getting Started
Clone the repo

Install dependencies

nginx
Copy
Edit
pip install python-telegram-bot openai pinecone-client python-dotenv
Set up a .env file with:

ini
Copy
Edit
OPENAI_API_KEY=your_openai_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=your_pinecone_env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
Run the bot
