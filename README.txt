========================================================================================
AI WORKSHOP PROJECTS - SETUP & RUN INSTRUCTIONS
========================================================================================

PREREQUISITES:
- Python
- A code editor (VS Code recommended)
- A web browser

========================================================================================
STEP 1: GET YOUR API KEYS
========================================================================================

IF USING GROQ:
Get Groq API Key from: https://console.groq.com/keys
Base URL for Groq: "https://api.groq.com/openai/v1/chat/completions"

========================================================================================
STEP 2: SETUP INSTRUCTIONS
========================================================================================

1. Unzip the AI_Workshop folder

2. Open VS Code (or any code editor) and navigate to the main "AI_Workshop" folder

3. Open terminal in the editor and install dependencies:
   pip install -r requirements.txt
   
   (If this fails, try: pip install -r requirements.txt --upgrade)

4. Set up environment variables:
   - If there's a .env file in the project folder: Update it with your API key, Base URL, and Model
   - If there's NO .env file: Open the *_Backend.py file and update the variables at the top

========================================================================================
STEP 3: RUN A PROJECT
========================================================================================

1. Navigate to the project folder you want to run (e.g., cd Chatbot)

2. Run the backend:
   python [ProjectName]_Backend.py
   
   Examples:
   - python Chatbot_Backend.py
   - python Clone_Backend.py

3. Once the backend is running, open the corresponding HTML frontend file in your browser

========================================================================================
PROJECT-SPECIFIC NOTES
========================================================================================

AI_Clone_Chatbot:
- Customize the AI personality by editing the system prompt in "Clone_Frontend.HTML"
- Make it sound like you, a celebrity, or any character you want!

========================================================================================
TROUBLESHOOTING
========================================================================================

COMMON ISSUES:

1. Module/Package errors:
   - Make sure you're in the AI_Workshop main folder when running pip install
   - Try: pip install -r requirements.txt --upgrade

2. Port already in use:
   - Close other running Python processes
   - Or modify the port number in the backend file

3. .env file not found:
   - No problem! Just update variables directly in the *_Backend.py file

4. Compatibility issues (Windows/Mac/IDE problems):
   - USE AI TO HELP! Copy your error message and paste it into ChatGPT, Claude, or Copilot
   - Ask: "I'm getting this error on [Windows/Mac], how do I fix it?"
   - Discuss solutions with your team

5. Python version issues:
   - Check your Python version: python --version
   - Make sure it's 3.8 or higher

========================================================================================
YOUR HOMEWORK
========================================================================================

✓ Experiment with different projects
✓ Hit errors and learn to troubleshoot
✓ Use AI assistants to help debug
✓ Discuss solutions with your team
✓ Customize and make projects your own
✓ HAVE FUN!

========================================================================================
QUESTIONS?
========================================================================================

Post in the team Slack channel or join office hrs, learn together!

Happy coding! 🚀
