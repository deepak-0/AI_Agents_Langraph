from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from ..schemas import ChatRequest, ChatResponse

router = APIRouter()


@router.get("/health")
def health_check():
    return {"status": "healthy"}


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, http_request: Request):
    graph = http_request.app.state.graph
    result = await graph.ainvoke({"user_input": request.user_input})
    return {
        "route": result.get("route", "chat"),
        "output": result.get("summary", result.get("output", "")),
    }


@router.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>LangGraph Agentic Assistant</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 900px;
                margin: 40px auto;
                padding: 20px;
                background-color: #f5f5f5;
            }

            h1, h3, h4 {
                text-align: center;
            }

            #chat {
                background: white;
                border: 1px solid #ccc;
                border-radius: 8px;
                padding: 20px;
                min-height: 400px;
                max-height: 600px;
                overflow-y: auto;
                margin-bottom: 20px;
            }

            .message {
                margin-bottom: 20px;
            }

            .user {
                font-weight: bold;
            }

            .assistant {
                margin-top: 5px;
                white-space: pre-wrap;
                font-family: monospace;
            }

            .route {
                font-size: 12px;
                color: gray;
                margin-top: 5px;
            }

            #input-area {
                display: flex;
                gap: 10px;
            }

            #prompt {
                flex: 1;
                padding: 12px;
                font-size: 16px;
                border-radius: 6px;
                border: 1px solid #aaa;
            }

            button {
                padding: 12px 24px;
                font-size: 16px;
                cursor: pointer;
                border: none;
                border-radius: 6px;
                background: #333;
                color: white;
            }

            button:hover {
                background: #555;
            }

            button:disabled {
                background: #999;
                cursor: not-allowed;
            }

            #status {
                margin-top: 10px;
                color: gray;
                font-size: 14px;
            }
        </style>
    </head>
    <body>
    <h1>LangGraph Agentic Assistant</h1>
    <h3> Powered by Qwen-2.5 , OpenAI Models orchestrated through LangGraph</h3>
    <h4> Authored by Deepak</h4>
    <div id="chat"></div>
    <div id="input-area">
        <input
            id="prompt"
            type="text"
            placeholder="Enter your prompt..."
            autocomplete="off"
        >
        <button id="sendButton" onclick="sendMessage()">Send</button>
    </div>
    <div id="status"></div>
    <script>
        async function sendMessage() {
            const promptInput = document.getElementById("prompt");
            const sendButton = document.getElementById("sendButton");
            const chat = document.getElementById("chat");
            const status = document.getElementById("status");

            const prompt = promptInput.value.trim();
            if (!prompt) {
                return;
            }

            const userMessage = document.createElement("div");
            userMessage.className = "message";

            const userLabel = document.createElement("div");
            userLabel.className = "user";
            userLabel.textContent = "You:";

            const userText = document.createElement("div");
            userText.textContent = prompt;

            userMessage.appendChild(userLabel);
            userMessage.appendChild(userText);
            chat.appendChild(userMessage);

            promptInput.value = "";
            sendButton.disabled = true;
            status.textContent = "LLM is Thinking... ";
            chat.scrollTop = chat.scrollHeight;

            try {
                const response = await fetch("/chat", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ user_input: prompt }),
                });

                if (!response.ok) {
                    throw new Error("Server returned HTTP " + response.status);
                }

                const data = await response.json();
                const assistantMessage = document.createElement("div");
                assistantMessage.className = "message";

                const assistantLabel = document.createElement("div");
                assistantLabel.className = "user";
                assistantLabel.textContent = "Assistant:";

                const assistantText = document.createElement("div");
                assistantText.className = "assistant";
                assistantText.textContent = data.output;

                const routeText = document.createElement("div");
                routeText.className = "route";
                routeText.textContent = "Route: " + data.route;

                assistantMessage.appendChild(assistantLabel);
                assistantMessage.appendChild(assistantText);
                assistantMessage.appendChild(routeText);
                chat.appendChild(assistantMessage);
            } catch (error) {
                const errorMessage = document.createElement("div");
                errorMessage.className = "message";
                errorMessage.textContent = "Error communicating with API: " + error.message;
                chat.appendChild(errorMessage);
            } finally {
                sendButton.disabled = false;
                promptInput.focus();
                status.textContent = "";
                chat.scrollTop = chat.scrollHeight;
            }
        }

        document.getElementById("prompt").addEventListener("keydown", function (event) {
            if (event.key === "Enter") {
                sendMessage();
            }
        });
    </script>
    </body>
    </html>
    """
