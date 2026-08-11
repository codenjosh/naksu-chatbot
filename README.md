# Naksu AI

A Streamlit chatbot that supports Google Gemini and a locally running Ollama
model. It includes Langfuse observability and a Promptfoo regression suite for
testing Gemini responses before deployment.

## Features

- Clean Streamlit chat interface with model selection and prompt suggestions
- Google Gemini chat with bounded conversation history and clear quota errors
- Local Llama 3.2 chat through Ollama
- Langfuse tracing for Gemini requests
- Promptfoo checks for core Gemini response behavior
- Docker-ready deployment for Render

## Requirements

- Python 3.11+
- A Google Gemini API key
- Ollama only if you want to use the local Llama option

## Local setup

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_google_api_key
LANGFUSE_PUBLIC_KEY=your_langfuse_public_key
LANGFUSE_SECRET_KEY=your_langfuse_secret_key
LANGFUSE_BASE_URL=https://cloud.langfuse.com
OLLAMA_URL=http://localhost:11434
```

`LANGFUSE_*` variables are optional if you do not use Langfuse. Never commit
the `.env` file.

Start the app:

```powershell
streamlit run app.py
```

## Using local Llama

Install Ollama, then download and serve the model:

```powershell
ollama pull llama3.2
ollama serve
```

Select **Llama 3 (Local)** in the sidebar. The default local endpoint is
`http://localhost:11434`.

If the Streamlit app runs in Docker on Windows or macOS, set this instead:

```env
OLLAMA_URL=http://host.docker.internal:11434
```

Ollama on your computer cannot be reached by Render. A Render deployment needs
its own Ollama private service, or you should select Gemini instead.

## Gemini quota errors

Gemini can return `429 RESOURCE_EXHAUSTED` when the API key reaches its request
quota. Wait for the quota to reset, reduce request frequency, or enable billing
for the Google AI project. The app shows this as a clear in-chat message.

## Promptfoo evaluations

Promptfoo evaluates the same Gemini code path used by the chatbot.

Run the suite locally:

```powershell
$env:PROMPTFOO_PYTHON = "$PWD\.venv\Scripts\python.exe"
npx promptfoo@latest eval -c promptfooconfig.yaml
```

The GitHub Actions workflow is intentionally manual to avoid spending Gemini
free-tier quota on every push. Add `GOOGLE_API_KEY` as a repository Actions
secret, then run **Promptfoo evaluations** from the repository's **Actions**
tab.

## Deploying with Docker and Render

Build and run the container locally:

```powershell
docker build -t naksu-ai .
docker run --rm -p 8501:8501 --env-file .env naksu-ai
```

For Render, deploy this repository using the included `Dockerfile`, then add
these environment variables in the Render dashboard:

```text
GOOGLE_API_KEY
LANGFUSE_PUBLIC_KEY
LANGFUSE_SECRET_KEY
LANGFUSE_BASE_URL
```

Do not add the `.env` file to GitHub or Render source control.

## Project structure

```text
.
├── app.py                     # Streamlit user interface
├── chatbot.py                 # Gemini, Ollama, and Langfuse integration
├── evals/
│   ├── gemini_provider.py     # Promptfoo provider for the chatbot
│   └── README.md              # Evaluation details
├── promptfooconfig.yaml       # Promptfoo test cases
├── .github/workflows/
│   └── promptfoo.yml          # Manual GitHub Actions evaluation workflow
├── Dockerfile
└── requirements.txt
```
