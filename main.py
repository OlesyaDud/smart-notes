import os
from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes


# Load environment variables
load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENVIRONMENT")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


# Initialize OpenAI and Pinecone
client = OpenAI(api_key=OPENAI_API_KEY)
pc = Pinecone(api_key=PINECONE_API_KEY)

# Index setup
index_name = "smart-notes"
dimension = 1536
metric = "cosine"

if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=dimension,
        metric=metric,
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )

index = pc.Index(index_name)

# Helper to get embedding
def get_embedding(text):
    response = client.embeddings.create(
        input=[text],
        model="text-embedding-ada-002"
    )
    embedding = response.data[0].embedding
    print(f"📐 First 10 dimensions of embedding for '{text}': {embedding[:10]}")
    return embedding


# --- Telegram handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("➕ Add Note", callback_data='add_note'),
            InlineKeyboardButton("🔍 Search Notes", callback_data='search_notes')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 Welcome to Smart Notes!\n\nYou can add and search your notes easily below:",
        reply_markup=reply_markup
    )


async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    note_text = " ".join(context.args)
    if not note_text:
        await update.message.reply_text("⚠️ *Please provide a note after* `/add <note>`.", parse_mode="Markdown")
        return

    embedding = get_embedding(note_text)
    vector_id = f"note-{index.describe_index_stats().total_vector_count}"
    index.upsert(vectors=[{
        "id": vector_id,
        "values": embedding,
        "metadata": {"text": note_text}
    }])

    keyboard = [
        [
            InlineKeyboardButton("Add Another", callback_data='add_note'),
            InlineKeyboardButton("Search Notes", callback_data='search_notes')
        ]
    ]
    await update.message.reply_text(
        "✅ *Note added successfully!*",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )



async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query_text = " ".join(context.args)
    if not query_text:
        await update.message.reply_text("⚠️ Please type your search after the `/search` command.", parse_mode="Markdown")
        return

    embedding = get_embedding(query_text)
    results = index.query(vector=embedding, top_k=3, include_metadata=True)

    if not results.matches:
        await update.message.reply_text("❌ No matches found.")
        return

    response = "🔍 *Top Matches:*\n\n"
    for match in results.matches:
        text = match['metadata']['text']
        score = match['score']
        response += f"• _{text}_ \n   (score: `{score:.2f}`)\n\n"

    keyboard = [
        [
            InlineKeyboardButton("➕ Add Note", callback_data='add_note'),
            InlineKeyboardButton("🔁 New Search", callback_data='search_notes')
        ]
    ]
    await update.message.reply_text(response, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")


async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'add_note':
        await query.message.reply_text("✍️ Just type: `/add your note`", parse_mode="Markdown")
    elif query.data == 'search_notes':
        await query.message.reply_text("🔎 Just type: `/search your keywords`", parse_mode="Markdown")


# --- Run everything ---
if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add))
    app.add_handler(CommandHandler("search", search))
    app.add_handler(CallbackQueryHandler(handle_buttons))

    print("🤖 Telegram bot running...")
    app.run_polling()