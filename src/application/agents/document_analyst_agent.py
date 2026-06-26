from typing import Annotated, TypedDict, List
import json
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage
from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from src.domain.ports.i_llm_client import ILLMClient
from src.application.tools.search_document_tool import search_document
from src.application.tools.extract_section_tool import extract_section
from src.application.tools.summarize_section_tool import summarize_section

SYSTEM_PROMPT = """Sen kurumsal bir bankacılık belge analisti yapay zeka ajanısın.
Görevin; sana sunulan PDF belgelerinden (sözleşmeler, raporlar, yönetmelikler, mali tablolar) 
doğru, eksiksiz ve güvenilir bilgi çıkarmaktır.

Yanıt verirken:
- Belgeye dayalı olmayan bilgileri asla uydurma.
- Belirsiz ifadeleri olduğu gibi raporla; yorum katma.
- Bulduğun her bilgi için kaynak sayfa numarası ve bölüm başlığını belirt.
- Bir soruyu yanıtlayamıyorsan, hangi bölümde arama yaptığını ve neden bulamadığını açıkla.

Kullanabileceğin araçlar: belge arama (search_document), bölüm çıkarma (extract_section), 
özetleme (summarize_section).
"""

VALIDATOR_PROMPT = """Sen bir bankacılık belge analizi kalite kontrolcüsüsün.
Aşağıdaki orijinal soruyu ve üretilmiş taslak cevabı incele.

Orijinal Soru: {question}

Taslak Cevap: {draft_answer}

Değerlendir:
1. Cevap soruyu doğrudan yanıtlıyor mu?
2. Kaynak sayfa numarası veya bölüm adı belirtilmiş mi?
3. Belgeden desteklenmeyen/uydurulmuş bilgi var mı?

YALNIZCA JSON formatında, hiçbir ek açıklama yapmadan yanıt ver:
- Cevap yeterliyse: {{"verdict": "ok"}}
- Yetersizse: {{"verdict": "retry", "feedback": "Lütfen şu kısımları düzelt: [eksik/yanlış olan yerler]"}}
"""

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    deps: dict
    original_question: str
    validation_attempts: int
    validation_verdict: dict

class DocumentAnalystAgent:
    def __init__(self, chat_model: BaseChatModel, llm_client: ILLMClient):
        self.chat_model = chat_model
        self.llm_client = llm_client
        self.tools = [search_document, extract_section, summarize_section]
        self.llm_with_tools = self.chat_model.bind_tools(self.tools)
        
        # Build the ReAct + Validation graph
        self.graph = self._build_graph()
        
    def _build_graph(self):
        def call_model(state: AgentState):
            messages = state["messages"]
            if not any(isinstance(m, SystemMessage) for m in messages):
                sys_msg = SystemMessage(content=SYSTEM_PROMPT)
                messages = [sys_msg] + messages
            
            response = self.llm_with_tools.invoke(messages)
            return {"messages": [response]}
            
        def validate_response(state: AgentState) -> dict:
            last_content = state["messages"][-1].content
            question = state["original_question"]
            
            prompt = VALIDATOR_PROMPT.format(question=question, draft_answer=last_content)
            verdict_str = self.llm_client.complete([{"role": "user", "content": prompt}])
            
            try:
                # Basic cleanup to extract JSON if LLM added markdown backticks
                cleaned = verdict_str.strip()
                if cleaned.startswith("```json"):
                    cleaned = cleaned[7:]
                if cleaned.endswith("```"):
                    cleaned = cleaned[:-3]
                verdict = json.loads(cleaned.strip())
            except json.JSONDecodeError:
                verdict = {"verdict": "ok"}
            
            attempts = state.get("validation_attempts", 0) + 1
            return {"validation_verdict": verdict, "validation_attempts": attempts}

        def should_continue(state: AgentState) -> str:
            last_msg = state["messages"][-1]
            if getattr(last_msg, "tool_calls", None):
                return "tools"
            return "validator"
            
        def route_after_validation(state: AgentState) -> str:
            if state["validation_attempts"] >= 2:
                return END
            
            verdict = state.get("validation_verdict", {})
            if verdict.get("verdict") == "ok":
                return END
            
            feedback = verdict.get("feedback", "Lütfen cevabınızı gözden geçirin ve kaynak gösterin.")
            # Inject feedback as a human message so the agent corrects itself
            return "agent"

        def add_feedback(state: AgentState):
            feedback = state["validation_verdict"].get("feedback", "")
            msg = HumanMessage(content=f"Kalite Kontrol Geri Bildirimi:\n{feedback}\nLütfen cevabını bu geri bildirime göre düzelt.")
            return {"messages": [msg]}
            
        workflow = StateGraph(AgentState)
        workflow.add_node("agent", call_model)
        workflow.add_node("tools", ToolNode(self.tools))
        workflow.add_node("validator", validate_response)
        workflow.add_node("feedback_injector", add_feedback)
        
        workflow.add_edge(START, "agent")
        workflow.add_conditional_edges("agent", should_continue, {
            "tools": "tools",
            "validator": "validator"
        })
        workflow.add_edge("tools", "agent")
        workflow.add_conditional_edges("validator", route_after_validation, {
            "agent": "feedback_injector",
            END: END
        })
        workflow.add_edge("feedback_injector", "agent")
        
        return workflow.compile()
        
    def run(self, query: str, deps: dict) -> str:
        deps["llm_client"] = self.llm_client
        initial_state = {
            "messages": [HumanMessage(content=query)],
            "deps": deps,
            "original_question": query,
            "validation_attempts": 0,
            "validation_verdict": {}
        }
        
        result = self.graph.invoke(initial_state, config={"recursion_limit": 20})
        # Remove the feedback node messages if any, return the final AI message
        return result["messages"][-1].content
