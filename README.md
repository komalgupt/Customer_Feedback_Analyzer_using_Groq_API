## Customer Feedback Analyzer Using Groq API and FastAPI
📌 Overview
The Customer Feedback Analyzer is a web application built with FastAPI that uses the Groq API for advanced AI-powered feedback analysis.
It processes customer feedback from manual input or file upload and returns a structured JSON containing:

Sentiment (Positive, Neutral, Negative)

Themes (Key topics discussed in feedback)

Highlights (Important points mentioned)

Original feedback text

The results can be viewed in the web interface and downloaded as an Excel file, stored in a runtime-generated downloads folder.

# 📂 Folder Structure

/Customer_feedback_analyzer_agent_1908
│
├── main.py               # FastAPI app entry point; defines routes and API endpoints

├── groq_agent.py         # Handles interaction with Groq API and feedback processing

├── utils.py              # Helper functions for file handling & data processing

├── requirements.txt      # Python dependencies

├── .env                  # Stores Groq API key (not in version control)

│
├── templates/
│   └── index.html        # Frontend template with feedback form and results

│
├── static/
│   └── style.css         # Frontend styling

│
└── downloads/            # Created at runtime for downloadable Excel results

# ⚙️ Workflow
User opens the web app.

Inputs multiple feedbacks manually (one per line) or uploads a supported file (.txt, .csv, .xlsx, .pdf, .docx).

On submission, main.py processes the input and calls Groq API via groq_agent.py.

Groq API returns structured JSON with sentiment, themes, and highlights.

utils.py converts results into an Excel file inside /downloads.

User can view JSON results on the web page and download Excel output.

# 🔐 Environment Variables & Security
Sensitive credentials like Groq API Key are stored in a .env file (excluded from GitHub).

Example .env file:
GROQ_API_KEY=your_actual_api_key_here
A .env.example file should be provided for collaborators with placeholder values.

🛠 Installation & Setup

1. Clone the repository
git clone https://github.com/your-username/Customer_feedback_analyzer_agent_1908.git
cd Customer_feedback_analyzer_agent_1908

2. Create virtual environment
python -m venv venv
venv\Scripts\activate   # Windows

3. Install dependencies
pip install -r requirements.txt

4. Create .env file
echo GROQ_API_KEY=your_actual_api_key_here > .env

5. Run FastAPI server
uvicorn main:app --reload
Open the browser and go to:
http://localhost:8000

🚀 Usage
Enter multiple customer feedbacks manually (one per line) or upload a supported file.

Click Analyze to process the feedback.

View JSON results (sentiment, themes, highlights).

 Future Enhancements
🌍 Multilingual feedback analysis

💡 Advanced visualization of feedback insights

🎨 More interactive & responsive frontend UI

## 🔑 Getting Groq API Key
Visit: Groq API Console

Enter a name for your key (e.g., Groq_API_key).

Copy your generated API key and add it to your .env file.
Download the Excel file from the provided link.

