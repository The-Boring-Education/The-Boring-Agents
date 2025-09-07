## NEW

"""Google Research Agent - Fetches or simulates Google information for subtopics."""

from typing import List, Dict
from ...core.base_agent import BaseAgent


class GoogleResearchAgent(BaseAgent):
    """Agent that retrieves supporting information from Google (or simulates it)."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logger.info("GoogleResearchAgent initialized")

    def fetch_info(self, subtopic: str) -> List[str]:
        """Fetch information for a given subtopic.
        
        For now, simulate results using the LLM (or extend to Google API).
        """
        try:
            prompt = f"Provide 3-4 concise bullet points explaining '{subtopic}' for an educational course."
            result = self.llm.invoke(prompt)

            if isinstance(result, str):
                return [line.strip("-• ") for line in result.split("\n") if line.strip()]
            elif isinstance(result, dict) and "content" in result:
                return [result["content"]]
            else:
                return [str(result)]

        except Exception as e:
            self.logger.error(f"Error fetching Google info for {subtopic}: {str(e)}")
            return [f"Could not fetch info for {subtopic}"]

    # Inside GoogleAgent
    def get_youtube_links(self, topic: str, max_results: int = 3):
        return [
            {"title": f"{topic} - Intro Video", "url": f"https://www.youtube.com/results?search_query={topic}+intro"},
            {"title": f"{topic} - Deep Dive", "url": f"https://www.youtube.com/results?search_query={topic}+deep+dive"},
            {"title": f"{topic} - Tutorial", "url": f"https://www.youtube.com/results?search_query={topic}+tutorial"},
        ][:max_results]
