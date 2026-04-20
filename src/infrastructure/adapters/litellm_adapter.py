import logging
from typing import List, Dict, Any, Optional
import litellm
from litellm import acompletion
from pydantic import BaseModel

from universal_core.interfaces import ILLMProvider

logger = logging.getLogger(__name__)

class LiteLLMAdapterError(Exception):
    """Base exception for LiteLLM adapter."""
    pass

class BudgetExceededError(LiteLLMAdapterError):
    """Raised when the LLM budget is exceeded."""
    pass

class LiteLLMAdapter(ILLMProvider):
    def __init__(self, budget_limit: float = 0.0):
        # Architect Mandate: No os.getenv. Strictly injected.
        # CTO Mandate: Preserve FinOps logic.
        self.budget_limit = budget_limit
        self.current_spend = 0.0

    async def generate_content(self, model: str, messages: List[Dict[str, str]], **kwargs) -> Any:
        try:
            # CTO Mandate: Fail gracefully if budget exceeded
            if self.budget_limit > 0 and self.current_spend >= self.budget_limit:
                raise BudgetExceededError(f"LLM Budget of ${self.budget_limit} exceeded. Current spend: ${self.current_spend}")

            response = await acompletion(
                model=model,
                messages=messages,
                **kwargs
            )
            
            # Simple cost tracking
            try:
                cost = litellm.completion_cost(completion_response=response)
                self.current_spend += cost
                logger.info(f"LLM Call Cost: ${cost:.6f} | Total Spend: ${self.current_spend:.6f} / ${self.budget_limit}")
            except Exception as e:
                logger.debug(f"Could not calculate cost: {e}")

            return response
            
        except litellm.exceptions.BudgetExceededError as e:
            raise BudgetExceededError(f"LiteLLM internal budget exceeded: {e}")
        except litellm.exceptions.AuthenticationError as e:
            raise LiteLLMAdapterError(f"LLM Authentication error: {e}")
        except litellm.exceptions.RateLimitError as e:
            raise LiteLLMAdapterError(f"LLM Rate limit exceeded: {e}")
        except Exception as e:
            if isinstance(e, BudgetExceededError):
                raise
            raise LiteLLMAdapterError(f"LLM Generation Error: {e}")
