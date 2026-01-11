from fastmcp import Client as MCPClient
import asyncio
import threading
from typing import Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, Future
from functools import wraps
import random

class OSConnector:
    _thread_executor = ThreadPoolExecutor(
        max_workers=4,
        thread_name_prefix="OSConnector"
    )
    
    def __init__(self, session_id: str, url: str):
        self.client = None
        self.session_id = session_id
        self.url = url
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._init_lock = threading.Lock()
        self._initialized = False
        
        # 立即启动异步初始化
        self._initialize_async()
    
    def _initialize_async(self):
        """在新线程中执行异步初始化"""
        with self._init_lock:
            if not self._initialized:
                # 在新线程中创建事件循环并初始化
                future = self._thread_executor.submit(self._init_in_thread)
                # 等待初始化完成
                self.client, self._loop = future.result()
                self._initialized = True
    
    def _init_in_thread(self):
        """在线程中执行初始化"""
        # 为这个线程创建新的事件循环
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # 在事件循环中初始化 MCPClient
            client = MCPClient(self.url)
            
            # 执行健康检查
            async def init_and_check():
                async with client:
                    result = await client.call_tool(
                        name="health", 
                        arguments={"session_id": self.session_id}
                    )
                    structured_content = result.structured_content
                    assert structured_content["status"] == "ok"
            
            # 在新建的循环中运行检查
            loop.run_until_complete(init_and_check())
            
            return client, loop
        except Exception:
            loop.close()
            raise
    
    def _run_in_thread_loop(self, coro_func, *args, **kwargs):
        """在线程的事件循环中运行异步函数"""
        if not self._initialized:
            self._initialize_async()
        
        def _run():
            """在拥有事件循环的线程中运行"""
            try:
                # 确保我们在正确的事件循环中
                asyncio.set_event_loop(self._loop)
                return self._loop.run_until_complete(coro_func(*args, **kwargs))
            except RuntimeError as e:
                if "already running" in str(e):
                    # 如果循环已在运行，在后台任务中执行
                    future = asyncio.run_coroutine_threadsafe(
                        coro_func(*args, **kwargs), 
                        self._loop
                    )
                    return future.result()
                raise
        
        # 在同一个线程池中执行
        future = self._thread_executor.submit(_run)
        return future.result()
    
    async def _call_async(self, name: str, arguments: Dict[str, Any]):
        """原始的异步 call 方法实现"""
        if not self.client:
            raise RuntimeError("Connector not initialized")
        
        async with self.client:
            result = await self.client.call_tool(
                name=name, 
                arguments=arguments
            )
            return result
    
    async def call(self, name: str, arguments: Dict[str, Any]):
        """异步 call 方法 - 可以在异步环境中调用"""
        if not self._initialized:
            self._initialize_async()
        
        # 如果已经在正确的线程中，直接调用
        if threading.current_thread() == getattr(self._loop, "_thread", None):
            return await self._call_async(name, arguments)
        
        # 否则，在线程的事件循环中执行
        loop = asyncio.get_event_loop()
        
        def _sync_call():
            return self._run_in_thread_loop(
                self._call_async, name, arguments
            )
        
        return await loop.run_in_executor(
            self._thread_executor, 
            _sync_call
        )
    
    def _check_sync(self):
        """同步版本的 check 方法"""
        return self._run_in_thread_loop(
            self._check_async
        )
    
    async def _check_async(self):
        """异步 check 的实现"""
        if not self.client:
            raise RuntimeError("Connector not initialized")
        
        async with self.client:
            result = await self.client.call_tool(
                name="health", 
                arguments={"session_id": self.session_id}
            )
            structured_content = result.structured_content
            assert structured_content["status"] == "ok"
            return structured_content
    
    def now(self):
        result = self._run_in_thread_loop(
            self._call_async, 
            "now", 
            {"session_id": self.session_id}
        )
        structured_content = result.structured_content
        assert structured_content["status"] == "ok"
        return structured_content["output"]
    
    def step(self):
        result = self._run_in_thread_loop(
            self._call_async, 
            "_step", 
            {"session_id": self.session_id}
        )
        structured_content = result.structured_content
        assert structured_content["status"] == "ok"
        return structured_content["output"]
    
    def gen_past(self, start_year: int = 2015, k: int = 1):
        result = self._run_in_thread_loop(
            self._call_async,
            "_gen_past",
            {
                "start_year": start_year,
                "k": k,
                "session_id": self.session_id
            }
        )
        structured_content = result.structured_content
        assert structured_content["status"] == "ok"
        return structured_content["output"]
    
    def __del__(self):
        if hasattr(self, '_loop') and self._loop:
            try:
                # 安排关闭事件循环
                if not self._loop.is_closed():
                    self._loop.call_soon_threadsafe(self._loop.close)
            except:
                pass
    
    @classmethod
    def shutdown(cls):
        cls._thread_executor.shutdown(wait=True)

class DummyOSConnector:
    def __init__(self):
        pass

    def now(self):
        return "2026-01-01 08:00:00"
    
    def step(self):
        return self.now()
    
    def gen_past(self, start_year: int = 2026, k: int = 1):
        return [self.now()] * k

def uuid_rng(rng: random.Random):
    alphabet = "23456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    return ''.join(rng.choices(alphabet, k=22))

if __name__ == "__main__":
    connector = OSConnector(
        session_id="session_6H8SWvjiHiErn3cWZjtLkV",
        url="http://127.0.0.1:9000/mcp"
    )

    print(connector.gen_past(k=10))