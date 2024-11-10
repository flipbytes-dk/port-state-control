import asyncio
import uvicorn
from app.main import app

if __name__ == "__main__":
    # Force use of standard event loop before starting uvicorn
    asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
    uvicorn.run(app, host="0.0.0.0", port=8000, loop="asyncio") 