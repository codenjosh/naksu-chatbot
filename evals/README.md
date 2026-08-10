# Promptfoo evaluations

This suite evaluates the same Gemini function used by the Streamlit chatbot.

## Run locally

From the project root, run:

```powershell
$env:PROMPTFOO_PYTHON = "$PWD\.venv\Scripts\python.exe"
npx promptfoo@latest eval -c promptfooconfig.yaml
```

Promptfoo uses the Python interpreter in `PROMPTFOO_PYTHON`, which loads the local `.env` file.
Keep `.env` private; it must contain `GOOGLE_API_KEY` for the evaluations to call Gemini.

To inspect a completed run in Promptfoo's local viewer:

```powershell
npx promptfoo@latest view
```

Promptfoo is a development-only tool. It is not required by the Streamlit app or the Render deployment.

## GitHub Actions

The workflow in `.github/workflows/promptfoo.yml` can be run manually from the
Actions tab, or runs after changes to the chatbot or evaluation files. Add a
repository secret named `GOOGLE_API_KEY` before using it.
