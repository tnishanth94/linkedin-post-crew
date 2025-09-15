from crewai import Crew, Process
from crew.agents import trend_aggregator, researcher, idea_generator, summarizer, style_refiner, image_creator, image_inserter, linkedin_post_agent
from crew.tasks import trend_task, research_task, idea_task, summarizer_task, style_task, image_task, image_insert_Task, linkedin_post_task


def run_linkedin_crew():

    crew = Crew(
        agents=[trend_aggregator, researcher, idea_generator, summarizer, style_refiner, image_creator, linkedin_post_agent],
        tasks=[trend_task, research_task, idea_task, summarizer_task, style_task, image_task, linkedin_post_task],
        process=Process.sequential
    )

    result = crew.kickoff()
    print("\n=== Final Output ===")
    print(result)
