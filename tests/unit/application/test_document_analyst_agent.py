from unittest.mock import Mock
from src.application.agents.document_analyst_agent import DocumentAnalystAgent

def test_agent_initialization():
    mock_chat = Mock()
    mock_llm = Mock()
    agent = DocumentAnalystAgent(chat_model=mock_chat, llm_client=mock_llm)
    assert agent.chat_model is not None
