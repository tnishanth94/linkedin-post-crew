from crew.agents import linkedin_post_agent
from crew.agents import style_refiner
from crew.agents import summarizer
from crew.agents import image_inserter
from crewai import Task
from crew.agents import trend_aggregator, researcher, idea_generator, image_creator

trend_task = Task(
    description="Fetch trending topics from Medium and Dev.to in AI, Angular, .NET, MCP, ML.",
    agent=trend_aggregator,
    expected_output="A list of trending topics with titles."
)

research_task = Task(
    description="Take one trending topic and summarize it in 3-4 bullet points.",
    agent=researcher,
    expected_output="Short summary with key insights."
)

idea_task = Task(
    description="Turn the summary into a LinkedIn post outline with a hook + 3-5 bullet points.",
    agent=idea_generator,
    expected_output="Draft LinkedIn post outline."
)

summarizer_task = Task(
    description="Summarize the LinkedIn post idea from idea_generator into a single, concise line for image generation.",
    agent=summarizer,
    expected_output="A one-line summary suitable as a prompt for DALL-E image generation."
)

style_task = Task(
    description="Refine the LinkedIn post content to match Vaibhav Sisinty’s style: engaging, actionable, and personal.",
    agent=style_refiner,
    expected_output="Content rewritten in Vaibhav Sisinty’s LinkedIn post style."
)

image_task = Task(
    name="LinkedIn Image Creation",
    description="Generate only 1 image using Azure DALL-E 3. The prompt must be a simple, one-line summary of the idea_generator's output.",
    agent=image_creator,
    expected_output="A file path to the generated poster image saved locally."
)

image_insert_Task = Task(
    name="Image Insert",
    description="Insert an image from the local images folder into the workflow output.",
    agent=image_inserter,
    expected_output="The file path of the inserted image from the images folder."
)

linkedin_post_task = Task(
    description="Create a LinkedIn post using the MCP server API. The post must reference the generated image and include the final refined post draft. Use the output from style_refiner as the post text and the output from image_creator as the image. Combine both in the post.",
    agent=linkedin_post_agent,
    expected_output="Response from the LinkedIn MCP server after posting. The post should include both the image and the refined content."
)