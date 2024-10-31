# Author: Joey
# Email: zengjiayi666@gmail.com
# Date: :call strftime("%Y-%m-%d %H:%M")
# Description: 
# Version: 1.0
#
# if __name__ == "__main__": 
import os
from time import sleep
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from openai import AsyncOpenAI
import json
import re
from duckduckgo_search import DDGS
from typing import Callable, List, Dict, Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor
import requests
from dataclasses import dataclass
from contextlib import asynccontextmanager
from landing_page import landing_page

# OpenAI client setup
api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL")
client = AsyncOpenAI(api_key=api_key, base_url=base_url)

@dataclass
class UserSettings:
    search_engine: str = "searxng"
    search_url: Optional[str] = "http://192.168.31.2:8080/search?q="
    api_key: Optional[str] = api_key
    base_url: Optional[str] = base_url
    model: str = "gpt-4o-mini"

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[WebSocket, UserSettings] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[websocket] = UserSettings()

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            del self.active_connections[websocket]

    def get_settings(self, websocket: WebSocket) -> UserSettings:
        return self.active_connections.get(websocket, UserSettings())

    def update_settings(self, websocket: WebSocket, settings: dict):
        current_settings = self.get_settings(websocket)
        
        # Update settings with new values
        current_settings.search_engine = settings.get('searchEngine', current_settings.search_engine)
        current_settings.search_url = settings.get('searchUrl', current_settings.search_url)
        current_settings.api_key = settings.get('apiKey', current_settings.api_key)
        current_settings.base_url = settings.get('baseUrl', current_settings.base_url)
        current_settings.model = settings.get('model', current_settings.model)
        
        self.active_connections[websocket] = current_settings

app = FastAPI()
manager = ConnectionManager()
thread_pool = ThreadPoolExecutor(max_workers=2)

@app.get("/")
async def get():
    return HTMLResponse(content=landing_page)

def search_searxng_sync(keywords: List[str], perspective: str) -> List[Dict]:
    """
    使用 SearxNG 搜索引擎进行同步搜索
    """
    results = []
    search_query = " ".join(keywords)
    search_url = f"http://192.168.31.2:8080/search?q={search_query}"
    
    try:
        response = requests.get(search_url, params={'format': 'json'})
        response_data = response.json()
        
        for result in response_data['results']:
            results.append({
                "title": result.get("title", "相关观点"),
                "content": result.get("content", ""),
                "source": result.get("url", "SearxNG"),
                "perspective": perspective
            })

        # 没有拿到专门的新闻接口，根据需要添加
        for result in response_data.get('news', []):
            results.append({
                "title": f"新闻: {result.get('title', '相关新闻')}",
                "content": result.get("content", ""),
                "source": result.get("url", "SearxNG News"),
                "perspective": perspective
            })

    except Exception as e:
        print(f"搜索过程中出现错误: {str(e)}")
        
    return results

def search_duckduckgo_sync(keywords: List[str], perspective: str) -> List[Dict]:
    """
    使用 DuckDuckGo 搜索引擎进行同步搜索
    """
    results = []
    search_query = " ".join(keywords)
    
    try:
        with DDGS() as ddgs:
            # 获取文本搜索结果
            search_results = list(ddgs.text(
                search_query,
                max_results=5  # 限制结果数量
            ))
            
            # 处理搜索结果
            for result in search_results:
                results.append({
                    "title": result.get("title", "相关观点"),
                    "content": result.get("body", ""),
                    "source": result.get("link", "DuckDuckGo"),
                    "perspective": perspective
                })

            # 获取相关新闻
            news_results = list(ddgs.news(
                search_query,
                max_results=3  # 限制新闻结果数量
            ))
            
            # 处理新闻结果
            for news in news_results:
                results.append({
                    "title": f"新闻: {news.get('title', '相关新闻')}",
                    "content": news.get("body", ""),
                    "source": news.get("link", "DuckDuckGo News"),
                    "perspective": perspective
                })
            sleep(5)

    except Exception as e:
        print(f"搜索过程中出现错误: {str(e)}")
        
    return results

async def generic_search(keywords: List[str], perspective: str, sync_search_func: Callable[[List[str], str], List[Dict]]) -> List[Dict]:
    """
    异步包装同步搜索函数
    """
    loop = asyncio.get_event_loop()
    results = await loop.run_in_executor(
        thread_pool, 
        sync_search_func, 
        keywords, 
        perspective
    )
    return results

async def get_openai_client(settings: UserSettings) -> AsyncOpenAI:
    """
    Create an OpenAI client with user-specific settings
    """
    api_key = settings.api_key or os.getenv("OPENAI_API_KEY")
    base_url = settings.base_url or os.getenv("OPENAI_BASE_URL")
    
    return AsyncOpenAI(api_key=api_key, base_url=base_url)

async def perform_search(keywords: List[str], perspective: str, settings: UserSettings) -> List[Dict]:
    """
    Perform search using the selected search engine
    """
    if settings.search_engine == "duckduckgo":
        return await generic_search(keywords, perspective, search_duckduckgo_sync)
    else:  # default to searxng
        return await generic_search(keywords, perspective, search_searxng_sync)

async def process_search_results(results: List[Dict]) -> List[Dict]:
    """
    处理和清理搜索结果
    """
    processed_results = []
    for result in results:
        # 清理和格式化内容
        content = result["content"]
        
        # 限制内容长度
        if len(content) > 300:
            content = content[:297] + "..."

        # 确保标题不为空
        title = result["title"] if result["title"] else "相关观点"

        processed_results.append({
            "title": title,
            "content": content,
            "source": result["source"],
            "perspective": result["perspective"]
        })

    return processed_results

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    
    try:
        async for message in websocket.iter_text():
            data = json.loads(message)
            
            if data["type"] == "settings_update":
                # Handle settings update
                manager.update_settings(websocket, data["settings"])
                await websocket.send_text(json.dumps({
                    "type": "settings_updated",
                    "message": "Settings updated successfully"
                }))
                
            elif data["type"] == "search":
                query = data["message"]
                settings = manager.get_settings(websocket)
                
                # Create OpenAI client with user settings
                client = await get_openai_client(settings)
                
                # Generate keywords
                keywords_prompt = f"""
                请分析以下话题，生成两组包含话题内容的搜索关键词：
                1. 支持该话题的积极简洁关键词（3-5个）,包含能够独立搜索到话题的完整信息
                2. 反对该话题的消极简洁关键词（3-5个）,包含能够独立搜索到话题的完整信息
                话题：{query}

                请以JSON格式返回，格式如下：
                {{
                    "positive": ["关键词1", "关键词2", "关键词3"],
                    "negative": ["关键词1", "关键词2", "关键词3"]
                }}
                """

                try:
                    # Get keywords using user's OpenAI settings
                    response = await client.chat.completions.create(
                        model=settings.model,
                        messages=[{"role": "user", "content": keywords_prompt}],
                        max_tokens=300,
                    )

                    cleaned_content = re.sub(r'```json|```', '', response.choices[0].message.content)
                    keywords = json.loads(cleaned_content)
                    
                    # Send keywords to frontend
                    await websocket.send_text(json.dumps({
                        "type": "keywords",
                        "positive": keywords["positive"],
                        "negative": keywords["negative"]
                    }))

                    # Perform parallel searches using selected search engine
                    positive_search = perform_search(keywords["positive"], "positive", settings)
                    negative_search = perform_search(keywords["negative"], "negative", settings)
                    
                    # Wait for all searches to complete
                    all_results = await asyncio.gather(positive_search, negative_search)
                    
                    # Process and send results
                    for results in all_results:
                        processed_results = await process_search_results(results)
                        for result in processed_results:
                            await websocket.send_text(json.dumps({
                                "type": "result",
                                "perspective": result["perspective"],
                                "title": result["title"],
                                "content": result["content"],
                                "source": result["source"]
                            }))

                except json.JSONDecodeError as e:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": f"关键词生成失败: {str(e)}"
                    }))
                except Exception as e:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": f"搜索过程中出现错误: {str(e)}"
                    }))

    except Exception as e:
        print(f"WebSocket Error: {e}")
    finally:
        manager.disconnect(websocket)
        await websocket.close()