# 🤖 Ollama & Ngrok Setup Guide (Final Version)

Since the automatic code fix was reverted (it caused routing issues), you **MUST** follow these steps to make Ollama accessible to the backend.

## 1. Stop Ollama
Make sure Ollama is **NOT** running. Check your system tray (bottom right, near clock) and Right Click -> Quit.

## 2. Start Ollama (PowerShell)
Open a new **PowerShell** window and run this **exact** block to allow external connections:

```powershell
# 1. Allow connections from anywhere
$env:OLLAMA_HOST = "0.0.0.0"
$env:OLLAMA_ORIGINS = "*"

# 2. Start Ollama
ollama serve
```

> **Keep this window open!** You should see logs like `Listening on 0.0.0.0:11434`.

## 3. Start Ngrok (New Terminal)
Open a separate terminal and run this **exact** command. The `--host-header` flag is critical to trick Ollama into accepting the traffic.

```bash
ngrok http 11434 --host-header="localhost:11434"
# OR if using npx
npx ngrok http 11434 --host-header="localhost:11434"
```

## 4. Connect Backend
1. Copy the `https://....ngrok-free.dev` URL from the ngrok terminal.
2. Paste it into your `backend/.env` file:
   ```env
   OLLAMA_URL=https://your-url.ngrok-free.dev
   ```
3. **Restart your backend** (`fastapi dev`) to apply the change.

## ✅ Verification
If everything is correct:
- **Browser:** Visiting `https://your-url.ngrok-free.dev` might still show "Deep 404" or a warning, but...
- **Backend:** The Chat feature in Fsociety will work!
