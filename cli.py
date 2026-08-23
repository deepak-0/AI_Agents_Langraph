import asyncio

from graph_app import build_graph
 
async def main():
    graph = build_graph(model_name="qwen2.5:14b")
    print("Welcome to the LangGraph Qwen2.5 CLI! Type 'exit' to quit.")
    while True:
        msg = input("Enter your question (or 'exit' to quit): ").strip()
        if msg.lower() == "exit":
            break
        result = await graph.ainvoke({"user_input": msg})
        print(f"Route: {result.get('route', 'chat')}")
        print(f"Output: {result.get('output', '')}\n")

if __name__ == "__main__":
    asyncio.run(main())
