from ..core.prompt import load_prompt
from ..tools.sysops.check_website_tool import check_website_tool
from ..tools.sysops.run_bash_command_tool import run_bash_command_tool
from .base_agent import BaseAgent

SYSOPS_TOOLS = [run_bash_command_tool, check_website_tool]


class SysOpsAgent(BaseAgent):
    tool_list = SYSOPS_TOOLS

    def __init__(self, **kwargs):
        config = load_prompt()
        super().__init__(
            system_prompt=config.get("sysops_system"),
            tool_list=self.tool_list,
            **kwargs,
        )
