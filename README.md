# Welcome Desk HR Onboarding Expert

A local FastAPI chat UI for general HR onboarding and policy questions. It sends the conversation to an Azure AI Foundry OpenAI-compatible deployment and does not use a local knowledge-base file.

## Configure and run (PowerShell)

1. Create a virtual environment (skip this if `.venv` already exists):

   ```powershell
   python -m venv .venv
   ```

2. Install dependencies:

   ```powershell
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

3. Copy the exact endpoint and API key from the new project's deployment page into `.env`. The file must use these names:

   ```text
   AZURE_ENDPOINT=https://<your-resource>.services.ai.azure.com/openai/v1
   AZURE_DEPLOYMENT=gpt-5-mini
   AZURE_API_KEY=paste-your-key
   ```

4. Start the server:

   ```powershell
   .\.venv\Scripts\python.exe -m uvicorn app:app --reload --port 8000
   ```

5. Open http://localhost:8000.

## Deploy to Netlify

Netlify serves the HTML directly and uses the included serverless function for `/chat`. In the Netlify project settings, set the build publish directory to `.` and add these environment variables under **Project configuration > Environment variables**:

```text
AZURE_ENDPOINT=https://<your-resource>.services.ai.azure.com/openai/v1
AZURE_DEPLOYMENT=gpt-5-mini
AZURE_API_KEY=your-real-key
```

Trigger a new deploy after changing environment variables. Netlify does not inject newly added variables into an already-created deploy. The `netlify.toml` file configures the function and routes `/chat` to it. The Python FastAPI app remains the local development backend.

## Troubleshooting

- `uvicorn --reload` watches `.py` files but **not** `.env`. After changing `.env`, fully stop the server with `Ctrl+C` and restart the uvicorn command.
- A 401 `Access denied due to invalid subscription key or wrong API endpoint` error means Azure rejected the request. Check the terminal log for the real exception, then verify that the key and endpoint match the new project's deployment page exactly.
- If the published site says `Missing or placeholder setting(s)`, the named variable is not available to the Netlify Function or still contains a template value. Set it under **Environment variables**, ensure the scope includes **Functions**, then trigger a new deploy.
- Isolate backend errors from the browser/UI with this quick PowerShell test:

  ```powershell
  Invoke-RestMethod -Uri http://localhost:8000/chat -Method Post -ContentType 'application/json' -Body '{"messages":[{"role":"user","content":"hi"}]}'
  ```

The server returns a generic error to the browser and logs the underlying exception server-side. API keys are never hardcoded or logged.