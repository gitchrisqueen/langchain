from typing import Optional, Type, Union, Dict, List, Any

from langchain.globals import get_verbose, set_verbose
from langchain_core.callbacks import CallbackManagerForToolRun, Callbacks
from langchain_core.pydantic_v1 import Field
from langchain_core.tools import BaseTool
from pydantic import BaseModel

from langchain_community.utilities.usemotion import UseMotionAPIWrapper
# TODO: Check to make sure the imports below should go here ot in the toolkit file
# Import all the models so the tool can use it to create input parameters as needed
from usemotion_api_client.models import *

from langchain_community.tools.usemotion.motion_input import MotionInput
from langchain_community.utils.usemotion.logger import logger

set_verbose(True)


class UseMotionAction(BaseTool):
    """Tool that utilizes the Motion API."""

    name: str = ""
    description: str = ""
    mode: str = ""
    api_wrapper: UseMotionAPIWrapper = Field(default_factory=UseMotionAPIWrapper)
    args_schema: Type[BaseModel] = MotionInput
    verbose = get_verbose()

    def run(
            self,
            tool_input: Union[str, Dict],
            verbose: Optional[bool] = None,
            start_color: Optional[str] = "green",
            color: Optional[str] = "green",
            callbacks: Callbacks = None,
            *,
            tags: Optional[List[str]] = None,
            metadata: Optional[Dict[str, Any]] = None,
            run_name: Optional[str] = None,
            **kwargs: Any,
    ) -> Any:
        # Add mode to tool_input
        tool_input['mode'] = self.mode
        return super().run(tool_input=tool_input, verbose=verbose, start_color=start_color, color=color,
                           callbacks=callbacks, tags=tags, metadata=metadata, run_name=run_name, **kwargs)

    def _run(
            self,
            *,
            run_manager: Optional[CallbackManagerForToolRun] = None,
            **tool_kwargs
    ) -> str:
        """Use the Motion API to run an operation."""

        # Convert to MotionInput
        motion_input = MotionInput.construct(**tool_kwargs) # NOTE: Construct the motion_input object this was as the inputs have already been validated.

        #print('Verbose :' + str(get_verbose()))
        logger.info("Mode(%s): motion_input:%s" % (self.mode, motion_input))
        #print("Mode(%s): motion_input:%s" % (self.mode, motion_input))

        return self.api_wrapper.run(mode=self.mode, motion_input=motion_input)
