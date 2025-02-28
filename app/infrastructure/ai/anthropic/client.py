from typing import Any, Dict, Optional
import anthropic
from app.core.config.settings import get_settings
from app.core.logging.logging_config import logger
from app.shared.exceptions.base import AppException

settings = get_settings()

class ClaudeClient:
    """Client for interacting with Anthropic's Claude API"""
    
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = "claude-3-opus-20240229"  # Latest model version
        self.logger = logger

    async def generate_response(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None
    ) -> str:
        """Generate a response from Claude"""
        try:
            message = await self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return message.content

        except Exception as e:
            self.logger.error(f"Claude API error: {str(e)}", exc_info=True)
            raise AppException(f"Failed to generate response: {str(e)}")

    async def analyze_document(
        self,
        document: str,
        instruction: str,
        max_tokens: int = 2000
    ) -> str:
        """Analyze a document with specific instructions"""
        try:
            prompt = f"{instruction}\n\nDocument:\n{document}"
            return await self.generate_response(prompt, max_tokens=max_tokens)

        except Exception as e:
            self.logger.error(f"Document analysis error: {str(e)}", exc_info=True)
            raise AppException(f"Failed to analyze document: {str(e)}")

    async def chat_with_context(
        self,
        messages: list,
        context: Optional[str] = None,
        system_prompt: Optional[str] = None
    ) -> str:
        """Chat with context from previous messages"""
        try:
            formatted_messages = []
            
            if context:
                formatted_messages.append({
                    "role": "system",
                    "content": f"Context:\n{context}"
                })
                
            formatted_messages.extend(messages)
            
            message = await self.client.messages.create(
                model=self.model,
                messages=formatted_messages,
                system=system_prompt
            )
            return message.content

        except Exception as e:
            self.logger.error(f"Chat error: {str(e)}", exc_info=True)
            raise AppException(f"Failed to process chat: {str(e)}") 