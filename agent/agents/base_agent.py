import json
from datetime import datetime

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_ollama import ChatOllama

from ..core.logger_utils import setup_logger
from ..core.nira_memory import NiraMemory
from ..core.prompt import ConfigError, load_prompt
from ..tools import tools as default_tools

# fmt: off
# isort: off
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)
# isort: on
# fmt: on


class BaseAgent:
    def __init__(
        self,
        model_name=None,
        base_url=None,
        llm=None,
        log_file="chat.json",
        *,
        system_prompt: str | None = None,
        tool_list: list | None = None,
        max_iterations=15,
        max_bytes=1 * 1024 * 1024,
        backup_count=5,
    ) -> None:
        self.llm = llm or ChatOllama(
            model=model_name,
            base_url=base_url,
            reasoning=False,
            # temperature=0.3,
        )

        self.max_iterations = max_iterations
        self.agent_executor: AgentExecutor | None

        self.logger = setup_logger(
            self.__class__.__name__, log_file, max_bytes, backup_count
        )

        self.memory = NiraMemory(memory_key="chat_history", return_messages=True)

        try:
            config = load_prompt()
        except ConfigError:
            raise
        system_prompt = system_prompt or config.get(
            "system", "You are Nira - an AI assistant."
        )

        tools = tool_list or default_tools
        self.tool_list = tools

        if hasattr(self.llm, "bind_tools"):
            self.prompt = ChatPromptTemplate.from_messages(
                [
                    SystemMessagePromptTemplate.from_template(system_prompt),
                    MessagesPlaceholder("chat_history"),
                    HumanMessagePromptTemplate.from_template("{input}"),
                    MessagesPlaceholder("agent_scratchpad"),
                ]
            )

            agent = create_tool_calling_agent(self.llm, tools, self.prompt)
            self.agent_executor = AgentExecutor(
                agent=agent,
                tools=tools,
                memory=self.memory,
                verbose=False,
                handle_parsing_errors=True,
                max_iterations=max_iterations,
            )
        else:
            self.agent_executor = None

    def log_chat(self, question: str, response: str) -> None:
        """Log a chat interaction to the log file."""
        timestamp = datetime.now().isoformat()
        log_entry = {"t": timestamp, "q": question, "a": response}
        self.logger.info(json.dumps(log_entry, ensure_ascii=False))

    def ask(self, question: str) -> str:
        if self.agent_executor is not None:
            result = self.agent_executor.invoke({"input": question})
            response = result["output"] if isinstance(result, dict) else str(result)
        else:
            try:
                raw = self.llm.invoke(question)
                response = raw.content if hasattr(raw, "content") else str(raw)
            except AttributeError:
                response = self.llm.predict(question)
            self.memory.save_context(
                {self.memory.input_key: question},
                {self.memory.output_key: response},
            )

        self.log_chat(question, response)
        return response
