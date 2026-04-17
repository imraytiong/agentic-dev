from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

class ActiveFocus(BaseModel):
    module_path: Optional[str] = Field(default=None, description="The current AndroidX module path being analyzed")
    current_files_in_context: List[str] = Field(default_factory=list, description="Files currently being focused on")
    head_sha: Optional[str] = Field(default=None, description="The specific commit SHA being analyzed")

class PendingInterrupt(BaseModel):
    intent: str = Field(..., description="The reason the agent yielded execution (e.g., 'disambiguate_path')")
    options: List[str] = Field(default_factory=list, description="The list of options presented to the user")
    original_request: str = Field(..., description="The original user request that led to the interrupt")

class JetpackWizState(BaseModel):
    status: str = Field(default="initialized", description="Current lifecycle state of the agent")
    is_cloning: bool = Field(default=False, description="Flag indicating if the repo is currently being cloned in the background")
    is_indexing: bool = Field(default=False, description="Flag indicating if the repo directory structure is currently being indexed")
    has_indexed: bool = Field(default=False, description="Flag indicating if the indexing has been successfully completed for this session")
    clone_start_time: Optional[float] = Field(default=None, description="Timestamp of when the clone started")
    pending_notifications: List[str] = Field(default_factory=list, description="Queue of proactive messages to deliver to the user")
    pending_queries: List[str] = Field(default_factory=list, description="Queue of user queries received during background initialization")
    active_focus: ActiveFocus = Field(default_factory=ActiveFocus)
    command_history: List[str] = Field(default_factory=list, description="Array of the last 5 executed command strings")
    cached_summaries: Dict[str, str] = Field(default_factory=dict, description="Ledger of LLM-generated summaries keyed by commit hash or path")
    pending_interrupt: Optional[PendingInterrupt] = Field(default=None, description="Active interrupt waiting for user response")

class JetpackWizRequest(BaseModel):
    query: str = Field(..., description="The natural language command from the user")
    user_reply: Optional[str] = Field(default=None, description="The user's response to a pending interrupt (e.g., a selection number)")

class JetpackWizResponse(BaseModel):
    message: str = Field(..., description="The final response or summary to the user")
    is_interrupt: bool = Field(default=False, description="True if the agent yielded execution for disambiguation")
