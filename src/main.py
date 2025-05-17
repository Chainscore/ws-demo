import asyncio
from quart import Quart, websocket
from broker import broker
import splitter

app = Quart(__name__)

async def _receive() -> None:
    while True:
        topic = await websocket.receive()
        print(f"Received message: {topic}")

@app.websocket("/ws")
async def ws():
    topic = await websocket.receive()  # e.g., client sends: "news"
    task = asyncio.ensure_future(_receive())
    try:
        async for message in broker.subscribe(topic):
            await websocket.send(f"[{topic}] {message}")
    finally:
        task.cancel()
        await task

if __name__ == "__main__":
    # Start the splitter in the background
    @app.before_serving
    async def startup():
        app.splitter_task = asyncio.create_task(splitter.split_them_messages())
    
    # Clean up the task when shutting down
    @app.after_serving
    async def shutdown():
        app.splitter_task.cancel()
        try:
            await app.splitter_task
        except asyncio.CancelledError:
            pass
    
    # Run the app normally, which will also run the splitter task
    app.run(debug=True, host="0.0.0.0", port=5001)