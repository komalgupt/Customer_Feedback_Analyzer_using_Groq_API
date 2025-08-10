## Customer Feedback Analyzer Using Groq API and FastAPI
1. Assignment Overview
This project is a Customer Feedback Analyzer built with FastAPI backend that leverages the Groq API for advanced AI-powered feedback analysis. It processes customer feedback inputs (manual or file upload) and returns structured JSON output containing themes, highlights, sentiment, and the original feedback text. The frontend is built with HTML and CSS templates served through FastAPI. Results can be viewed on the web interface and downloaded as Excel files, stored in a runtime-generated downloads folder.
2. Folder & File Structure
# /Customer_feedback_analyzer_agent_1908
**│
├── main.py                  # FastAPI app entry point; defines routes and API endpoints
├── groq_agent.py            # Logic to interact with Groq API and perform feedback 
├── utils.py                 # Helper functions for data processing, file handling, and ex
├── requirements.txt         # Python package dependencies
├── .env                     # Groq API key 
├── templates/
│   └── index.html           # Frontend template with feedback form and results 
├── static/
│   └── style.css            # Stylesheet for frontend design
│
└── downloads/               # Created at runtime to save downloadable analysis results**
3. Key Functional Components
main.py
Implements FastAPI app. Handles HTTP GET for homepage and POST for analyzing feedback data. Uses groq_agent.py to query Groq API. Saves analysis results in downloadable Excel files inside the /downloads folder.
groq_agent.py
Contains functions that format and send feedback text to Groq API, parse returned JSON for sentiment, themes, and highlights.
utils.py
Utility functions to convert API results into Excel, manage file writing, and clean temporary files if needed.
.env file
Stores sensitive API keys securely. Loaded by the app at runtime but excluded from version control.
templates/index.html & static/style.css
Provide user interface for feedback input, file upload, displaying JSON output, and download links.
downloads folder
Dynamically created to save output files that users can download post analysis.
4. Workflow Overview
User accesses the web app home page served by FastAPI.
Inputs multiple feedbacks manually or uploads a file containing feedback.
On form submission, main.py processes input and calls groq_agent.py functions to send data to Groq API.
Groq API returns analyzed JSON with sentiment, themes, highlights.
utils.py processes this data into an Excel file saved inside /downloads.
The frontend displays the JSON results and provides a button to download the Excel file.
5. Environment Variables & Security
Sensitive keys like the Groq API key are stored in a .env file.
.env is excluded from GitHub and public sharing using .gitignore.
A .env.example file with placeholder variables should be provided for collaborators to set up their own environment.
6. Installation & Setup Instructions
1. Clone or download the repository.
2. Create a Python virtual environment and activate it
venv\Scripts\activate      
3.Install dependencies:
pip install -r requirements.txt
4.Create a .env file in the project root:
GROQ_API_KEY=your_actual_api_key_here
5.Run the FastAPI server:
uvicorn main:app --reload
6.Open a browser and go to http://localhost:8000
7. Usage Instructions
Enter multiple customer feedbacks manually (one per line) or upload a file in supported formats (.txt, .csv, .xlsx, .pdf, .docx).
Click the Analyze button to process feedback.
View the detailed JSON analysis of sentiment, themes, and highlights.
Download the results in Excel format via the provided link.
8. Future Enhancements 
Support for multilingual feedback analysis.
More interactive and responsive frontend UI.
9. Conclusion
This project showcases a lightweight yet powerful feedback analysis tool using FastAPI and Groq’s AI API. It provides companies an easy-to-use interface for extracting meaningful insights from customer feedback, with secure handling of sensitive API credentials and user-friendly result exports.

Note : To get the API key of Groq visit : https://console.groq.com/keys




Enter Name for your key (Whatever you want. Example : Groq_API_key) and then submit your API key has been generated and it is ready to use!
