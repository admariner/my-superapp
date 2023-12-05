import typing as t
from functools import cached_property

from langchain.agents import (AgentExecutor, AgentType, initialize_agent,
                              load_tools)
from langchain.tools import BaseTool

from src.generative_ai.large_language_models.chatbots import Chatbot, ModelArgs


class ChatbotTools(Chatbot):
    available_tools = ["google-search", "wikipedia"]

    def __init__(
        self,
        tool_names: t.List[str] | None = None,
        **model_kwargs: t.Unpack[ModelArgs],
    ) -> None:
        super().__init__(**model_kwargs)
        self.tool_names = tool_names or []
        self.memory.input_key = "input"

    @cached_property
    def tools(self) -> t.List[BaseTool]:
        return load_tools(tool_names=self.tool_names)

    @classmethod
    def update_human_msg_prompt_template(
        cls,
        agent: AgentExecutor,
        text_to_add: str,
        input_variable_to_add: str | None = None,
    ) -> AgentExecutor:
        template = agent.agent.llm_chain.prompt.messages[2].prompt.template
        part1, part2 = template.split("\n\nUSER'S INPUT")
        part1 += text_to_add
        updated_template = "\n\nUSER'S INPUT".join([part1, part2])
        agent.agent.llm_chain.prompt.messages[2].prompt.template = updated_template
        if input_variable_to_add:
            agent.agent.llm_chain.prompt.messages[2].prompt.input_variables.append(
                input_variable_to_add
            )
            agent.agent.llm_chain.prompt.input_variables.append(input_variable_to_add)
        return agent

    @cached_property
    def chain(self) -> AgentExecutor:
        agent = initialize_agent(
            llm=self.llm,
            memory=self.memory,
            verbose=True,
            agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            agent_kwargs={
                "input_variables": [
                    "input",
                    "chat_history",
                    "agent_scratchpad",
                    "language",
                ]
            },
            tools=self.tools,
            handle_parsing_errors=True,
            return_intermediate_steps=False,
        )
        agent = self.update_human_msg_prompt_template(
            agent=agent,
            text_to_add="\nThe final answer must come in {language}, in the format of a markdown code snippet of a json blob with a single action.",
            input_variable_to_add="language",
        )
        return agent

    def ask(
        self,
        query: str,
        language: str | None = None,
    ) -> str:
        return self.chain.run(
            input=query,
            language=language or "the input language",
            callbacks=self.callbacks,
        )
