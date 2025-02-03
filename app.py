from flask import Flask, render_template, request, jsonify, session
import sqlite3
import requests
import uuid
import re

app = Flask(__name__)
app.secret_key = "48da6a7767a3b438c2c6b58475fad738c4d7b2d440b3b2ff818f6833b1448a61"
SERPER_API_KEY = '65d9720238b00ce9a4344d82062095edf02c873f'

INAPPROPRIATE_WORDS = [
    "كس",
    "نيج",
    "عير",
    "اغتصب",
    "كحبه",
    "كحبة",
    "كحاب",
    "بربوك",
    "برابيك",
    "نجت",
    "نياج",
    "سيته"
]

# Database utility functions
def execute_query(query, params=(), fetch=False):
    """Helper function to execute database queries."""
    try:
        conn = sqlite3.connect("chatbot.db")
        c = conn.cursor()
        c.execute(query, params)
        data = c.fetchall() if fetch else None
        conn.commit()
        conn.close()
        return data
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None

def init_db():
    """Initialize the database with necessary tables."""
    execute_query('''CREATE TABLE IF NOT EXISTS chats (id TEXT, user_id TEXT, query TEXT, response TEXT)''')

init_db()

# Search functions
def google_search(query):
    """Fetch improved search results from Serper API."""
    search_url = "https://google.serper.dev/search"
    headers = {"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"}
    payload = {"q": query, "num": 5}  # Get more results for better accuracy
    try:
        response = requests.post(search_url, json=payload, headers=headers)
        response.raise_for_status()
        search_results = response.json()
        if "organic" not in search_results:
            return {"summary": "No relevant results found.", "sources": []}

        summary_parts = []
        sources = []

        for index, result in enumerate(search_results["organic"][:3]):
            title = result.get("title", "No title")
            snippet = result.get("snippet", "No description available.")
            link = result.get("link", "#")
            summary_parts.append(f"<b>{title}</b>: {snippet}")
            sources.append({"text": f"🔗 Source {index + 1}", "url": link})

        return {"summary": "<br>".join(summary_parts), "sources": sources}

    except requests.exceptions.RequestException as e:
        return {"summary": f"⚠ Error fetching search results: {e}", "sources": []}

# Helper functions for filtering and responding
def check_inappropriate_words(query):
    """Check if the query contains any inappropriate words (case-insensitive)."""
    for word in INAPPROPRIATE_WORDS:
        if re.search(re.escape(word), query, re.IGNORECASE):  # Case-insensitive regex match
            return True
    return False

def check_greeting(query):
    """Check if the query contains any greeting keywords."""
    GREETINGS = ["hello", "hi", "hey", "greetings", "salut", "hola", "salam", "morning", "good morning", "هلو", "هلاو",
                 "شلونك", "مرحبا", "سلام", "السلام"]
    for greeting in GREETINGS:
        if greeting in query.lower():
            return True
    return False
def check_name_rlated(query):
    name_realtion = ["name","اسمك","شسمك"]
    for byeing in name_realtion:
        if byeing in query.lower():
            return True
    return False

def check_bye(query):
    Byeings = ["bye","ty","thank","tysm","شكرا","ممنون","تسلم","اشكرك","اودعناكم"]
    for byeing in Byeings:
        if byeing in query.lower():
            return True
    return False

def check_developer_related(query):
    developer_phrases = [
        "made you", "make you", "your programmer", "ur programmer",
        "you r programmer", "who made you", "who is your developer",
        "who created you", "who developed you", "who is your programmer",
        "who programmed you", "developer", "programmer", "creator",
        "who's your creator", "who's your developer","صانعك","سواك","مبرمجك","مطورك","مطور","مبرمج البوت","صنعك","برمجك"
    ]
    for phrase in developer_phrases:
        if phrase in query.lower():  # Case-insensitive match
            return True
    return False

def generate_bot_response(query):
    """Generate the response based on the query."""
    if check_inappropriate_words(query):
        return "Please be polite and respectful. / من فضلك كن مهذبًا ومحترمًا.", []
    elif check_greeting(query):
        return "Hello! How can I assist you today? / مرحبًا! كيف يمكنني مساعدتك اليوم?", []
    elif check_developer_related(query):
        return "I was created by Abdullah Altikrity!", []
    elif check_bye(query):
        return "تدلل,اذا تحتاج شيء بعد انه بالخدمه",[]
    elif check_name_rlated(query):
        return "My name is RoboBod ,I made by Abdullah",[]
    else:
        search_response = google_search(query)
        return search_response['summary'], search_response['sources']

# Main route
@app.route('/')
def index():
    if "user_id" not in session:
        session["user_id"] = str(uuid.uuid4())
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Handles user queries, stores history, and provides improved responses."""
    user_id = session["user_id"]
    user_query = request.form.get('query', '').strip()

    if not user_query:
        return jsonify({"response": "Please enter a message."})

    # Generate bot response
    bot_response, sources = generate_bot_response(user_query)

    # Prepare response HTML
    sources_html = "<br>".join([f"<a href='{src['url']}' target='_blank'>{src['text']}</a>" for src in sources])
    full_response = f"{bot_response}<br><br>🌍 Sources:<br>{sources_html}"

    # Save chat to history
    execute_query("INSERT INTO chats (id, user_id, query, response) VALUES (?, ?, ?, ?)",
                  (str(uuid.uuid4()), user_id, user_query, full_response))

    return jsonify({"response": full_response})

@app.route('/history', methods=['GET'])
def history():
    """Fetches chat history for the user."""
    user_id = session["user_id"]
    chat_history = execute_query("SELECT query, response FROM chats WHERE user_id = ? ORDER BY rowid DESC", (user_id,), fetch=True)
    return jsonify(chat_history)

if __name__ == "__main__":
    app.run(debug=True)
