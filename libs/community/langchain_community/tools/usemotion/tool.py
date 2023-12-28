"""
This tool allows agents to interact with the atlassian-python-api library
and operate on a Jira instance. For more information on the
atlassian-python-api library, see https://atlassian-python-api.readthedocs.io/jira.html

To use this tool, you must first set as environment variables:
    JIRA_API_TOKEN
    JIRA_USERNAME
    JIRA_INSTANCE_URL

Below is a sample script that uses the Jira tool:

```python
from langchain_community.agent_toolkits.jira.toolkit import JiraToolkit
from langchain_community.utilities.jira import JiraAPIWrapper

jira = JiraAPIWrapper()
toolkit = JiraToolkit.from_jira_api_wrapper(jira)
```
"""
from typing import Optional, Type, Dict

from langchain.globals import get_verbose, set_verbose
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.pydantic_v1 import Field
from langchain_core.tools import BaseTool, ToolException
from pydantic import BaseModel, StrictStr, ValidationError

from aiagents.utils.motion import MotionAPIWrapper
# TODO: Check to make sure the imports below should go here ot in the toolkit file
# Import all the models so the tool can use it to create input parameters as needed
from openapi_client.models import *

from aiagents.tools.motion.motion_input import MotionInput
from aiagents.utils.utillogger import logger

set_verbose(True)

class UseMotionAction(BaseTool):
    """Tool that utilizes the Motion API."""

    name: str = ""
    description: str = ""
    mode: str = ""
    api_wrapper: MotionAPIWrapper = Field(default_factory=MotionAPIWrapper)
    args_schema: Type[BaseModel] = MotionInput
    verbose = get_verbose()

    def _run(
            self,
            # motion_input: Dict[str, MotionInput] = None,
            motion_input: MotionInput = None,
            run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the Motion API to run an operation."""
        logger.info("Mode(%s): motion_input:%s" % (self.mode, motion_input))
        return self.api_wrapper.run(mode=self.mode, motion_input=motion_input)
