from dotenv import load_dotenv
import os
from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    print("OpenAI API Key Loaded Successfully")
else:
    print("API Key Missing")


# -------------------------------------------------
# MCP Client
# -------------------------------------------------
client = MultiServerMCPClient(
    {
        "filesystem": {
            "command": "npx", # executable used to start the MCP server
            "args": [ # arguments passed to the MCP server
                "-y",
                "@modelcontextprotocol/server-filesystem",
                "."
            ],
            "transport": "stdio", # communication method (stdio is most common locally)
        }
    }
)

# -------------------------------------------------
# Main Async Function
# -------------------------------------------------
async def main():

    # Load MCP tools
    tools = await client.get_tools()
    print("Loaded tools:")
    for tool in tools:
        print("-", tool.name)
    
    # Load MCP resources
    resource_context = ""
    try:
        print("\nLoading MCP Resources...\n")
        resources = await client.get_resources()
        if resources:
            print("Available Resources:\n")
            all_resource_contents = []
            for resource in resources:
                print(resource)
                try:
                    content = await client.read_resource(resource.uri)
                    resource_text = f"""
                    RESOURCE: {resource.name}
                    CONTENT: {content}
                    """
                    all_resource_contents.append(resource_text)
                except Exception as e:
                    print(f"Failed to read resource {resource.name}: {e}")
            resource_context = "\n\n".join(all_resource_contents)
        else:
            print("No resources available.")
    except Exception as e:
        print("\nThis MCP server does not support resources.")
        print("Error:", e)
    
    # Initialize LLM
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0
    )

    # Create agent
    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=f"""
        You are an AI assistant with access to MCP tools and MCP resources.
        Use the tools whenever needed.
        MCP Resource Context: {resource_context}
        """
    )

    queries = [
        "List all Python files in this directory and each subdirectory",
        "Read the contents of requirements.txt in the directory of Lab 12",
        "Summarize the current project structure"
    ]
    
    # Async agent calls
    for query in queries:
        print("\n" + "=" * 60)
        print("USER:", query)
        print("=" * 60)
        response = await agent.ainvoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": query
                    }
                ]
            }
        )

        print("\nASSISTANT RESPONSE:")
        print(response["messages"][-1].content)

    # Cleanup
    try:
        await client.aclose()
        print("\nMCP Client closed successfully.")
    except:
        pass


# -------------------------------------------------
# Run
# -------------------------------------------------
if __name__ == "__main__":
    asyncio.run(main())