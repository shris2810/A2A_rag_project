import logging
import httpx
from a2a.client import ClientFactory, ClientConfig, create_text_message_object
from a2a.types import AgentCard, Message
from a2a.utils import get_message_text

logger = logging.getLogger(__name__)

class AgentConnector:
    """
    Simple A2A Agent Connector that facilitates communication with other agents
    """
    
    def __init__(self, agent_card: AgentCard):
        """
        Initialize the connector with an agent card
        
        Args:
            agent_card: The AgentCard object containing agent connection details
        """
        self.agent_card = agent_card
    
    async def send_task(self, message: str, session_id: str = "") -> str:
        """
        Send a task/message to the connected agent
        
        Args:
            message: The message or task to send to the agent
            session_id: Session ID for conversation tracking
            
        Returns:
            Response from the agent
        """
        try:
            config = ClientConfig(httpx_client=httpx.AsyncClient(timeout=180.0))
            client = await ClientFactory.connect(self.agent_card, client_config=config)
            msg = create_text_message_object(content=message)
            final_text = ""
            
            async for event in client.send_message(msg):
                if isinstance(event, Message):
                    extracted = get_message_text(event)
                    if extracted:
                        final_text = extracted
                elif isinstance(event, tuple):
                    task, update = event
                    if update and getattr(update, "status", None) and getattr(update.status, "message", None):
                        extracted = get_message_text(update.status.message)
                        if extracted:
                            final_text = extracted
                    elif task and getattr(task, "status", None) and getattr(task.status, "message", None):
                        extracted = get_message_text(task.status.message)
                        if extracted:
                            final_text = extracted
                            
            return final_text or "No response received from agent."
                
        except Exception as e:
            logger.error(f"Error communicating with agent: {str(e)}", exc_info=True)
            return f"Error communicating with agent: {str(e)}"
