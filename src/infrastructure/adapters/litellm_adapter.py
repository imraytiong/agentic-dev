import os
import logging
from typing import List, Dict, Any, Optional
import litellm
from litellm import acompletion
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class LiteLLMAdapterError(Exception):
    """Base exception for LiteLLM adapter."""
    pass

class BudgetExceededError(LiteLLMAdapterError):
    """Raised when the LLM budget is exceeded."""
    pass

class ILLMProvider:
    """
    Interface definition for ILLMProvider, representing the contract
    expected by the architecture for external LLM calls.
    """
    async def generate_content(self, model: str, messages: List[Dict[str, str]], **kwargs) -> Any:
        pass

class LiteLLMAdapter(ILLMProvider):
    def __init__(self):
        # Read LITELLM_BUDGET. Default to 0.0 meaning no budget set/enforced if missing
        self.budget_limit = float(os.getenv('LITELLM_BUDGET', '0.0'))
        self.current_spend = 0.0
        
        # We can use litellm.budget_manager but for a simple local test we can track it manually or rely on LiteLLM's internal mechanisms if properly configured.
        # Here we manually track it to ensure graceful failure on budget hit.

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
            
            # Simple cost tracking based on litellm's returned cost (if available, requires litellm.cost_calculator)
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
            # We must not leak raw litellm errors if possible, wrap them.
            if isinstance(e, BudgetExceededError):
                raise
            raise LiteLLMAdapterError(f"LLM Generation Error: {e}")
