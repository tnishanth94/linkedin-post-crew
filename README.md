# linkedin-post-crew

Automated LinkedIn post creation using CrewAI multi-agent orchestration, with support for MCP server integration and AI-powered image generation.

## What does this codebase do?

This project automates the process of creating LinkedIn posts about trending tech topics (especially MCP server), using a crew of specialized AI agents. It fetches trends, summarizes content, generates post ideas, refines style, creates images, and posts to LinkedIn via MCP.

## How does it work?

- **Agents**: Each agent has a specific role (trend aggregator, researcher, idea generator, summarizer, style refiner, image creator, LinkedIn poster).
- **Tasks**: Each agent is assigned a task (fetch trends, summarize, generate ideas, refine style, create image, post to LinkedIn).
- **Tools**: Custom tools for image generation (Azure DALL-E, Google Gemini), RSS feed parsing, and MCP server API interaction.
- **CrewAI**: Orchestrates agents and tasks in a sequential workflow.

## Folder Structure

```
linkedin-post-crew/
│
├── main.py                # Entry point, runs the crew workflow
├── requirements.txt       # Python dependencies
├── README.md              # Project documentation
├── Linkedin Post Creator Crew.mp4  # Demo video (download/play only)
│
├── crew/
│   ├── agents.py          # Agent definitions and tools
│   ├── crew.py            # Crew and workflow orchestration
│   ├── tasks.py           # Task definitions for each agent
│   ├── tools.py           # Utility functions and image generation tools
│   └── __pycache__/       # Python cache files
│
└── images/
    └── *.png              # Generated images for LinkedIn posts
```

## Agents, Tasks, and Tools

- **Agents**: Trend Aggregator, Researcher, Idea Generator, Summarizer, Style Refiner, Image Creator, Image Inserter, LinkedIn Poster.
- **Tasks**: Fetch trending topics, summarize, generate post ideas, refine style, create images, insert images, post to LinkedIn.
- **Tools**: RSS feed parser, Azure DALL-E image generator, Google Gemini poster generator, MCP server API tools.

## Setup

1. Clone the repository:
   ```powershell
   git clone https://github.com/tnishanth94/linkedin-post-crew.git
   cd linkedin-post-crew
   ```

2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

3. Add your API keys to a `.env` file (see code for required keys).

4. Run the workflow:
   ```powershell
   python main.py
   ```

## Demo Video

[Download and watch the demo video](Linkedin%20Post%20Creator%20Crew.mp4)

## License

MIT

---

Let me know if you want any more details or want this pushed to your GitHub repo!
