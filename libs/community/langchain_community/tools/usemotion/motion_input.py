from typing import Optional, Annotated, Union, Any
from openapi_client import TaskPost, Task, TaskPatch
from pydantic import BaseModel, StrictStr, Field, Discriminator, Tag

from aiagents.utils.utillogger import logger
from aiagents.tools.motion.motion_list_tasks_input import MotionListTasksInput
from aiagents.tools.motion.motion_workspaces_list_input import MotionWorkspacesListInput
from aiagents.tools.motion.modes import *
import json


def get_model_discriminator(model: Any) -> str:
    logger.info("Model Class : %s" % model.__class__.__name__)
    # Loop through the types and return the one with the most properties or that doesn't fail

    json_schema = MotionInput.model_json_schema()
    refs = json_schema['properties']["motion_input"]["anyOf"][0]["oneOf"]
    logger.info("properties : %s" % refs)

    return model.__class__.__name__


class MotionInput(BaseModel):
    # query: Annotated[StrictStr, Field(
    #    description="Use the input from the user as query string")] = None
    # task_id: Optional[StrictStr] = None
    task_post: Annotated[Optional[TaskPost], Field(
        description="Use the input for mode: %s" % TASKS.CREATE)] = None
    motion_input: Optional[
        Annotated[
            Union[
                Annotated[TaskPost, Tag('taskpost')],
                Annotated[Task, Tag('task')],
                Annotated[TaskPatch, Tag('taskpatch')],
                Annotated[MotionListTasksInput, Tag('motionlisttasksinput')],
                Annotated[MotionWorkspacesListInput, Tag('motionworkspaceslistinput')]

            ],
            Discriminator(get_model_discriminator),
        ]
    ] = None
