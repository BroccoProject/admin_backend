from abc import ABC, abstractmethod
from infrastructure.ai.schemas import RecipeDraft

class IRecipeParserAgent(ABC):
    """Interface for the recipe parser AI agent."""
    
    @abstractmethod
    async def parse_recipe(self, input_text: str, thread_id: str) -> RecipeDraft:
        """Parses recipe text (or handles feedback) and returns a structured draft."""
        pass
