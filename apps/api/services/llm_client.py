"""
LLM client service for handling both Ollama and Azure OpenAI providers.
Provides a unified interface for LLM interactions with provider-specific implementations.
"""
import logging
import os
from typing import Dict, List, Any
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_ollama import ChatOllama
from langchain_openai import AzureChatOpenAI

from ..utils.env import Settings

# Configure logging
logger = logging.getLogger(__name__)

# In-memory session storage: {session_id: [messages]}
# Format: {"session_123": [{"role": "user", "content": "hello"}, {"role": "assistant", "content": "hi"}]}
SESSION_STORE: Dict[str, List[Dict[str, str]]] = {}


class LLMClient:
    """
    Unified LLM client that abstracts Ollama and Azure OpenAI providers.
    Handles session management and message history.
    """
    
    def __init__(self, settings: Settings, system_prompt: str):
        """
        Initialize the LLM client with provider-specific configuration.
        
        Args:
            settings: Application settings containing provider configuration
            system_prompt: System prompt to prepend to conversations
        """
        self.settings = settings
        self.system_prompt = system_prompt
        self.client = self._initialize_client()
        
        logger.info(f"Initialized LLM client with provider: {settings.llm_provider}")
    
    def _initialize_client(self):
        """Initialize the appropriate LangChain client based on provider."""
        try:
            if self.settings.llm_provider == "ollama":
                logger.info(f"Connecting to Ollama: {self.settings.ollama_model} at {self.settings.ollama_base_url}")
                return ChatOllama(
                    model=self.settings.ollama_model,
                    base_url=self.settings.ollama_base_url,
                    temperature=0.7,
                )
            elif self.settings.llm_provider == "azure":
                logger.info(f"Connecting to Azure OpenAI: {self.settings.azure_openai_model}")
                return AzureChatOpenAI(
                    model=self.settings.azure_openai_model,
                    azure_endpoint=self.settings.azure_openai_endpoint,
                    api_key=self.settings.azure_openai_api_key,
                    api_version=self.settings.azure_openai_api_version,
                    temperature=0.7,
                )
            else:
                raise ValueError(f"Unsupported LLM provider: {self.settings.llm_provider}")
        except Exception as e:
            if self.settings.llm_provider == "ollama":
                logger.error(f"Failed to connect to Ollama. Is 'ollama serve' running? Error: {e}")
            elif self.settings.llm_provider == "azure":
                logger.error(f"Failed to connect to Azure OpenAI. Check your credentials. Error: {e}")
            raise
    
    def _get_session_history(self, session_id: str) -> List[Dict[str, str]]:
        """Get conversation history for a session."""
        return SESSION_STORE.get(session_id, [])
    
    def _save_to_session(self, session_id: str, role: str, content: str) -> None:
        """Save a message to session history."""
        if session_id not in SESSION_STORE:
            SESSION_STORE[session_id] = []
        
        SESSION_STORE[session_id].append({
            "role": role,
            "content": content
        })
        
        # Keep only last 20 messages to prevent memory bloat
        if len(SESSION_STORE[session_id]) > 20:
            SESSION_STORE[session_id] = SESSION_STORE[session_id][-20:]
    
    def _build_message_chain(self, session_id: str, user_message: str) -> List[Any]:
        """
        Build the complete message chain for the LLM.
        Includes system prompt + conversation history + new user message.
        """
        messages = []
        
        # Add system prompt
        messages.append(SystemMessage(content=self.system_prompt))
        
        # Add conversation history
        history = self._get_session_history(session_id)
        for msg in history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))
        
        # Add new user message
        messages.append(HumanMessage(content=user_message))
        
        return messages
    
    async def chat(self, session_id: str, user_message: str) -> str:
        """
        Process a chat message and return the AI response.
        
        Args:
            session_id: Unique session identifier
            user_message: User's input message
            
        Returns:
            AI assistant's response text
            
        Raises:
            Exception: If LLM call fails
        """
        try:
            logger.info(f"Processing chat for session {session_id}, message length: {len(user_message)}")
            
            # Build message chain with history
            messages = self._build_message_chain(session_id, user_message)
            
            # Log message count for debugging
            logger.debug(f"Sending {len(messages)} messages to {self.settings.llm_provider}")
            
            # Call the LLM
            response = await self.client.ainvoke(messages)
            
            # Extract response content
            assistant_reply = response.content if hasattr(response, 'content') else str(response)
            
            # Save both user message and assistant reply to session
            self._save_to_session(session_id, "user", user_message)
            self._save_to_session(session_id, "assistant", assistant_reply)
            
            logger.info(f"Successfully generated response for session {session_id}, reply length: {len(assistant_reply)}")
            return assistant_reply
            
        except Exception as e:
            logger.error(f"Chat failed for session {session_id}: {str(e)}")
            
            # Simple provider-specific hints
            if self.settings.llm_provider == "ollama" and "connection" in str(e).lower():
                logger.error("Hint: Make sure 'ollama serve' is running")
            elif self.settings.llm_provider == "azure" and ("401" in str(e) or "unauthorized" in str(e).lower()):
                logger.error("Hint: Check your Azure OpenAI API key")
            
            raise
    
    def get_session_count(self) -> int:
        """Get the number of active sessions (for monitoring)."""
        return len(SESSION_STORE)
    
    def clear_session(self, session_id: str) -> bool:
        """Clear a specific session's history."""
        if session_id in SESSION_STORE:
            del SESSION_STORE[session_id]
            logger.info(f"Cleared session {session_id}")
            return True
        return False
    
    def get_provider_info(self) -> Dict[str, str]:
        """Get current provider and model information."""
        if self.settings.llm_provider == "ollama":
            return {
                "provider": "ollama",
                "model": self.settings.ollama_model,
                "base_url": self.settings.ollama_base_url
            }
        else:
            return {
                "provider": "azure",
                "model": self.settings.azure_openai_model,
                "endpoint": self.settings.azure_openai_endpoint
            }
