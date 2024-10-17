# Author: Joey
# Email: zengjiayi666@gmail.com
# Date: :call strftime("%Y-%m-%d %H:%M")
# Description: 
# Version: 1.0
#
# if __name__ == "__main__": 
import os
import openai
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import asyncio
from openai import OpenAI, AsyncOpenAI
import json

# 设置你的OpenAI API密钥
api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL")
client = AsyncOpenAI(api_key=api_key, base_url=base_url)

app = FastAPI()

html = """
<!DOCTYPE html>
<html>
<head>
    <title>WebSocket Chat</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
</head>
<body class="bg-gray-100 h-screen flex items-center justify-center">
    <div class="bg-white p-6 rounded-lg shadow-lg w-full max-w-lg">
        <h1 class="text-2xl font-bold mb-4">WebSocket Chat</h1>
        <div id="messages" class="border border-gray-300 p-4 h-64 overflow-y-scroll mb-4 bg-gray-50 rounded"></div>
        <div class="flex">
            <input id="input" type="text" class="flex-1 border border-gray-300 p-2 rounded mr-2" autocomplete="off"/>
            <button onclick="sendMessage()" class="bg-blue-500 hover:bg-blue-600 text-white p-2 rounded">Send</button>
        </div>
    </div>

    <script>
        const ws = new WebSocket("ws://localhost:8000/ws");
        const messagesDiv = document.getElementById("messages");
        const input = document.getElementById("input");
        let currentModelMessage = '';

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            const message = document.createElement("div");
            if (data.type === "user") {
                message.textContent = "用户: " + data.message;
                message.classList.add("bg-blue-100", "text-blue-800");
            } else if (data.type === "model") {
                if (data.end) {
                    message.textContent = "模型: " + currentModelMessage;
                    message.classList.add("bg-green-100", "text-green-800");
                    currentModelMessage = '';
                    messagesDiv.appendChild(message);
                    message.classList.add("message", "p-2", "rounded", "mb-2");
                } else {
                    currentModelMessage += data.message + ' ';
                }
            }
            messagesDiv.appendChild(message);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        };

        ws.onerror = (event) => {
            console.error("WebSocket error observed:", event);
        };

        ws.onclose = (event) => {
            const message = document.createElement("div");
            message.classList.add("message", "p-2", "rounded", "mb-2");
            message.textContent = "WebSocket closed";
            messagesDiv.appendChild(message);
        };

        function sendMessage() {
            const message = input.value;
            ws.send(JSON.stringify({ type: "user", message: message }));
            const userMessage = document.createElement("div");
            userMessage.classList.add("message", "user", "bg-blue-100", "text-blue-800", "p-2", "rounded", "mb-2");
            userMessage.textContent = "用户: " + message;
            messagesDiv.appendChild(userMessage);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
            input.value = '';
        }
    </script>
</body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(content=html)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        async for message in websocket.iter_text():
            data = json.loads(message)
            user_message = data.get("message", "")
            # await websocket.send_text(json.dumps({
            #     "type": "user",
            #     "message": user_message
            # }))
            messages = [{"role": "user", "content": user_message}]
            await stream_openai_response(websocket, messages)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await websocket.close()

async def stream_openai_response(websocket: WebSocket, messages):
    try:
        stream = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            stream=True,
        )
        async for chunk in stream:
            message = chunk.choices[0].delta.content or ""
            await websocket.send_text(json.dumps({
                "type": "model",
                "message": message,
                "end": False
            }))
        await websocket.send_text(json.dumps({
            "type": "model",
            "message": "",
            "end": True
        }))
    except Exception as e:
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": str(e)
        }))
