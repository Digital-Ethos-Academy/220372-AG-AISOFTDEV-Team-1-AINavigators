# TripSplit - Setup Guide

This guide will help you set up your development environment for the TripSplit Capstone Project.

## Prerequisites

- **Python 3.10 or higher** (Python 3.13 recommended)
- **Git** (for version control)
- **Node.js 18+** and **npm** (for frontend in Phase 5)
- A **Google AI API key** (or other LLM provider)

---

## Step 1: Clone or Navigate to the Project

```bash
cd "C:\Users\640109\OneDrive - BOOZ ALLEN HAMILTON\Documents\AISE_Capstone\220372-AG-AISOFTDEV-Team-1-AINavigators"
```

---

## Step 2: Create a Virtual Environment

It's recommended to use a virtual environment to isolate project dependencies.

### Windows (PowerShell):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Windows (Command Prompt):
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

### Mac/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## Step 3: Install Dependencies

With your virtual environment activated, install all required packages:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This will install:
- LLM provider SDKs (Google AI, OpenAI, Anthropic, Hugging Face)
- Jupyter notebooks and IPython
- FastAPI and Uvicorn (for backend)
- SQLAlchemy (for database)
- Pydantic (for data validation)
- pytest (for testing)
- PlantUML (for diagrams)
- And many other utilities

---

## Step 4: Configure Environment Variables

### Create your `.env` file:

1. Copy the example environment file:
   ```bash
   copy .env.example .env
   ```

2. Open `.env` in your text editor

3. **Get a Google AI API Key** (recommended for Gemini models):
   - Visit: https://aistudio.google.com/app/apikey
   - Click "Create API Key"
   - Copy your key

4. **Paste your API key** into `.env`:
   ```env
   GOOGLE_API_KEY=your_actual_api_key_here
   ```

### Alternative: Using Other LLM Providers

If you prefer to use a different LLM provider, you can set one of these instead:

- **OpenAI (GPT models)**: https://platform.openai.com/api-keys
  ```env
  OPENAI_API_KEY=your_openai_api_key_here
  ```

- **Anthropic (Claude models)**: https://console.anthropic.com/
  ```env
  ANTHROPIC_API_KEY=your_anthropic_api_key_here
  ```

- **Hugging Face**: https://huggingface.co/settings/tokens
  ```env
  HUGGINGFACE_TOKEN=your_huggingface_token_here
  ```

---

## Step 5: Verify Installation

### Test Python Environment:
```bash
python --version
```
Should show Python 3.10 or higher.

### Test Package Installation:
```bash
python -c "import google.genai; print('✓ Google AI SDK installed')"
python -c "import fastapi; print('✓ FastAPI installed')"
python -c "import pydantic; print('✓ Pydantic installed')"
python -c "from dotenv import load_dotenv; print('✓ python-dotenv installed')"
```

All commands should print success messages.

---

## Step 6: Launch Jupyter Notebook

Start Jupyter to run the Phase 1 notebook:

```bash
jupyter notebook
```

This will open Jupyter in your browser. Navigate to:
```
Python Notebooks/Capstone_Phase1_Requirements_and_PRD.ipynb
```

---

## Step 7: Run Phase 1 Notebook

1. Open the notebook in Jupyter
2. Run Cell 1 (Setup) - this will:
   - Load your `.env` file
   - Initialize the LLM client
   - Verify your API key

You should see:
```
✓ LLM Client initialized: google - gemini-2.5-flash
```

3. Continue running cells sequentially to generate your artifacts

---

## Troubleshooting

### Error: "GOOGLE_API_KEY not found in .env file"

**Solution:**
1. Verify `.env` file exists in the project root
2. Check that your API key is correctly set: `GOOGLE_API_KEY=...`
3. Restart your Jupyter kernel: `Kernel` → `Restart`

### Error: "python-dotenv not installed"

**Solution:**
```bash
pip install python-dotenv
```

### Error: "Module not found"

**Solution:**
Make sure your virtual environment is activated and run:
```bash
pip install -r requirements.txt
```

### Error: "Client not initialized" or None values

**Solution:**
- Check your API key is valid
- Try a different model if one provider is having issues
- Check your internet connection

---

## Project Structure

After setup, your project should look like this:

```
220372-AG-AISOFTDEV-Team-1-AINavigators/
├── .env                          # Your API keys (DO NOT COMMIT)
├── .env.example                  # Template for .env
├── .gitignore                    # Git ignore rules
├── requirements.txt              # Python dependencies
├── SETUP.md                      # This file
├── README.md                     # Project overview
├── Artifacts/
│   ├── Documentation/            # Generated docs go here
│   ├── Backend/                  # Backend artifacts
│   └── Frontend/                 # Frontend artifacts
├── Python Notebooks/
│   └── Capstone_Phase1_Requirements_and_PRD.ipynb
├── utils/                        # Utility modules
└── IdeaBrainstorming/
    └── chosen-idea.md            # TripSplit project idea
```

---

## Next Steps

Once setup is complete:

1. ✅ Run `Capstone_Phase1_Requirements_and_PRD.ipynb` to generate:
   - User stories (`user_stories.json`)
   - Product Requirements Document (`prd.md`)
   - Pydantic validation model (`prd_validation_model.py`)

2. Move to **Phase 2**: Architecture and database design
3. Move to **Phase 3**: Backend development with FastAPI
4. Move to **Phase 4**: Testing and security
5. Move to **Phase 5**: Frontend development with React

---

## Additional Resources

- **Course Materials**: Reference Day 1-8 labs for detailed examples
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **Pydantic Documentation**: https://docs.pydantic.dev/
- **Google AI Documentation**: https://ai.google.dev/gemini-api/docs
- **PlantUML**: https://plantuml.com/

---

## Support

If you encounter issues not covered in this guide:
1. Check the error message carefully
2. Review the course materials
3. Consult the documentation for the specific tool/library
4. Reach out to your instructional team

Good luck with your capstone project! 🚀

