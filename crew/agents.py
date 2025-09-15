import requests
from dotenv import load_dotenv
from crew.tools import generate_azure_dalle_image
import os
from crewai import Agent, LLM
from langchain_google_genai import ChatGoogleGenerativeAI
from crewai.tools import tool, BaseTool
from litellm import completion
from crew.tools import generate_poster
from crew.tools import ImageInsertTool
import feedparser

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'), override=True)

llm = LLM(
    provider="litellm",
    model="gemini/gemini-2.0-flash",
    api_key=os.environ.get("GEMINI_API_KEY"),
    temperature=0.5,
    verbose=True
)

# azure_image_llm = LLM(
#     provider="litellm",
#     model="azure/dall-e-3",
#     api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
#     api_base=os.environ.get("AZURE_OPENAI_ENDPOINT"),
#     deployment_id=os.environ.get("AZURE_OPENAI_DEPLOYMENT"),
#     temperature=0.5,
#     verbose=True
# )

# image_llm =LLM(
#     provider="litellm",
#     model="gemini/imagen-4.0-generate-00",
#     api_key="apikey",
#     temperature=0.5,
#     verbose=True
# )


@tool("get_trending_topics")
def get_trending_topics():
    """Fetches top 3 trending topics from selected tech blog RSS feeds."""
    feeds = {
        # "AI": "https://medium.com/feed/tag/artificial-intelligence",
        # "Angular": "https://dev.to/feed/tag/angular",
        # ".NET": "https://dev.to/feed/tag/dotnet",
        "MCP": "https://dev.to/feed/tag/mcp",
        # "ML": "https://medium.com/feed/tag/machine-learning"
    }
    
    topics = []
    for tag, url in feeds.items():
        feed = feedparser.parse(url)
        for entry in feed.entries[:1]:
            topics.append(f"{tag}: {entry.title}")
    return topics

trend_aggregator = Agent(
    role="Trend Aggregator",
    goal="Collect trending AI, Angular, .NET, MCP, ML topics from blogs like Medium and Dev.to.",
    backstory="You are skilled at scanning tech blogs and listing trending topics.",
    tools=[get_trending_topics],
    llm=llm
)

researcher = Agent(
    role="Researcher",
    goal="Summarize trending topics into key insights with supporting context.",
    backstory="You dive into articles and provide short, clear summaries.",
    verbose=True,
    llm=llm
)


idea_generator = Agent(
    role="Idea Generator",
    goal="Create LinkedIn post outlines with hooks and bullet points based on the research.",
    backstory="You are great at writing catchy, professional LinkedIn drafts.",
    verbose=True,
    llm=llm
)

summarizer = Agent(
    role="Summarizer",
    goal="Summarize the LinkedIn post idea into a single, concise line for image generation.",
    backstory="You are skilled at distilling ideas into short, clear prompts for visual content.",
    llm=llm,
    verbose=True
)

style_refiner = Agent(
    role="Style Refiner",
    goal="Enhance LinkedIn post content to match Vaibhav Sisinty’s style.",
    backstory="You are an expert at rewriting and refining content to match the engaging, actionable, and personal style of Vaibhav Sisinty’s LinkedIn posts.",
    llm=llm,
    verbose=True
)

class PosterTool(BaseTool):
    name: str = "GeneratePoster"
    description: str = "Creates a LinkedIn-style poster image from text"

    def _run(self, text: str, style: str = "LinkedIn post aesthetic") -> str:
        return generate_poster(text, style)


poster_tool = PosterTool()

class AzureDalleTool(BaseTool):
    name: str = "GenerateAzureDalleImage"
    description: str = "Generates an image using Azure DALL-E 3 and saves it to the images folder. Returns the file path."

    def _run(self, prompt: str, style: str = "vivid", size: str = "1024x1024") -> str:
        return generate_azure_dalle_image(prompt, style, size)

azure_dalle_tool = AzureDalleTool()

image_creator = Agent(
    role="Image Creator",
    goal="Generate visually appealing LinkedIn posters from ideas",
    backstory="An AI artist skilled in creating professional LinkedIn posters.",
    tools=[azure_dalle_tool],
    llm=llm,
    verbose=True
)

image_insert_tool = ImageInsertTool()

image_inserter = Agent(
    role="Image Inserter",
    goal="Insert an image from the local images folder into the workflow output.",
    backstory="You are responsible for selecting and inserting images from the images folder.",
    tools=[image_insert_tool],
    llm=llm,
    verbose=True
)

mcp_url = "https://apollo-6eirblcyo-composio.vercel.app/v3/mcp/fde600a7-0f62-44a3-b8ec-2a6570454354/mcp?useComposioHelperActions=true"

class InitiateMCPConnectionTool(BaseTool):
    name: str = "InitiateMCPConnection"
    description: str = "Initiates a connection with the MCP server to authenticate."

    def _run(self) -> str:
        payload = {
            "jsonrpc": "2.0",
            "method": "COMPOSIO_INITIATE_CONNECTION",
            "params": {},
            "id": 1
        }
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }
        try:
            response = requests.post(mcp_url, json=payload, headers=headers)
            if response.status_code == 200:
                return f"Connection initiated successfully. Response: {response.text}"
            else:
                return f"MCP connection error: {response.status_code} - {response.text}"
        except Exception as e:
            return f"MCP connection exception: {str(e)}"

class GetLinkedInMyInfoTool(BaseTool):
    name: str = "GetLinkedInMyInfo"
    description: str = "Gets LinkedIn user info from the MCP server. Use after initiating connection."

    def _run(self) -> str:
        payload = {
            "jsonrpc": "2.0",
            "method": "LINKEDIN_GET_MY_INFO",
            "params": {},
            "id": 2
        }
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }
        try:
            response = requests.post(mcp_url, json=payload, headers=headers)
            if response.status_code == 200:
                return f"Successfully retrieved user info. Response: {response.text}"
            else:
                return f"LinkedIn info error: {response.status_code} - {response.text}"
        except Exception as e:
            return f"LinkedIn info exception: {str(e)}"

class CreateLinkedInPostTool(BaseTool):
    name: str = "CreateLinkedInPost"
    description: str = "Creates a LinkedIn post with provided commentary (text) and an optional image. Use after confirming connection."

    def _run(self, commentary: str, image_url: str = None) -> str:
        """
        Posts text and an optional image to LinkedIn.
        Args:
            commentary (str): The text content of the post.
            image_url (str): The URL of the image to include, if any.
        """
        params = {
            "commentary": commentary,
            "visibility": "PUBLIC"
        }
        if image_url:
            params["image_url"] = image_url
            params["post_type"] = "image"
        
        payload = {
            "jsonrpc": "2.0",
            "method": "LINKEDIN_CREATE_LINKED_IN_POST",
            "params": params,
            "id": 3
        }
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }
        try:
            response = requests.post(mcp_url, json=payload, headers=headers)
            if response.status_code == 200:
                return f"Post created successfully! Response: {response.text}"
            else:
                return f"LinkedIn post creation error: {response.status_code} - {response.text}"
        except Exception as e:
            return f"LinkedIn post creation exception: {str(e)}"

initiate_connection_tool = InitiateMCPConnectionTool()
get_linkedin_info_tool = GetLinkedInMyInfoTool()
create_linkedin_post_tool = CreateLinkedInPostTool()

linkedin_post_agent = Agent(
    role="LinkedIn Poster",
    goal="Create a LinkedIn post using the MCP server API.",
    backstory="You are responsible for posting refined content to LinkedIn via the MCP server.",
    tools=[
        initiate_connection_tool,
        get_linkedin_info_tool,
        create_linkedin_post_tool
    ],
    llm=llm,
    verbose=True
)
