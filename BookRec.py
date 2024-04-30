from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain.agents.format_scratchpad.openai_tools import format_to_openai_tool_messages
from langchain.agents import AgentExecutor
from tools import *
from prompts import table_info_prompt, characters
from typing import List, Dict


class BookRec:
    def __init__(self):
        self.tools = [queryStuHistory, queryBookByISBN, queryBookByChara, matchBookByEmb, listAllCharacter,
                      getStudentChara, search, matchCorpusInFaissByEmb]

        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", """你是一个儿童书籍推荐师。儿童会与你聊天，你需要在聊天过程中了解儿童的兴趣爱好以及某些缺点。你需要跟你的观察为孩子推荐适合他们阅读的书本。
                在必要的时候你可以使用我们提供给你的工具查询合适的书籍。记住，你面对的是小孩子，所以你的回复必须是有趣、得体、符合他们年龄的。
                下面是数据库的关系表：
                <tables>
                {table_info}
                </tables>
                下面是用户可能存在的品格：
                <characters>
                {characters}
                </characters>
                """),
                # ("system", "接下来跟你聊天的人都是'大漂亮'， 你需要称呼ta是'大漂亮'，并用二次元的口吻与ta交流。"),
                MessagesPlaceholder(variable_name="chat_memory"),
                ("user", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad")
            ]
        )
        llm = ChatOpenAI(model_name="gpt-3.5-turbo-0125")
        self.chat_model = llm.bind_tools(self.tools)
        self.agent = (
                {
                    "input": lambda x: x["input"],
                    "table_info": lambda x: x["table_info"],
                    "chat_memory": lambda x: x["chat_memory"],
                    "characters": lambda x: x["characters"],
                    "agent_scratchpad": lambda x: format_to_openai_tool_messages(x["intermediate_steps"])
                }
                | self.prompt
                | self.chat_model
                | OpenAIToolsAgentOutputParser()
        )
        self.executor = AgentExecutor(agent=self.agent, tools=self.tools, verbose=True)

    def response(self, query: str, history) -> str:
        chat_history = []
        for item in history:
            role = item["role"]
            sentence = item["text"]
            if role == "user":
                chat_history.append(HumanMessage(content=sentence))
            elif role == "ai":
                chat_history.append(AIMessage(content=sentence))

        return self.executor.invoke({"input": query, "table_info": table_info_prompt, "characters": characters, "chat_memory": chat_history})[
            "output"]
