from typing import Optional, Annotated, Union, Any, Dict
from usemotion_api_client import TaskPost, Task, TaskPatch, MoveTask
from pydantic import BaseModel, StrictStr, Field, validator, root_validator, ValidationError

from langchain_community.utils.usemotion.logger import logger
from langchain_community.tools.usemotion.modes import *
from langchain_community.utils.usemotion.date_functions import *


class TasksListInput(BaseModel):
    cursor: Optional[
        Annotated[
            StrictStr,
            Field(description="Use if a previous request returned a cursor. Will page through results")
        ]
    ] = None
    label: Optional[
        Annotated[
            StrictStr,
            Field(description="Limit tasks returned by label on the task")
        ]
    ] = None
    status: Optional[
        Annotated[
            StrictStr,
            Field(description="Limit tasks returned by the status on the task ")
        ]
    ] = None
    workspace_id: Optional[
        Annotated[
            StrictStr,
            Field(
                description="The id of the workspace you want tasks from. If not provided, will return tasks from all workspaces the user is a member of")
        ]
    ] = None
    project_id: Optional[
        Annotated[
            StrictStr,
            Field(description="Limit tasks returned to a given project")
        ]
    ] = None
    name: Optional[
        Annotated[
            StrictStr,
            Field(description="Limit tasks returned to those that contain this string. Case in-sensitive")
        ]
    ] = None
    assignee_id: Optional[
        Annotated[
            StrictStr,
            Field(description="Limit tasks returned to a specific assignee")
        ]
    ] = None
    headers: dict = None  # Used for integration_tests
    max_tasks = 25  # Used for integration_tests or to allow more tasks to be returned


class MotionInput(BaseModel):
    mode: Annotated[StrictStr, Field(description="This is the mode for this input")] = None

    task_id: Optional[
        Annotated[
            StrictStr,
            Field(description="This input is required for modes=(" +
                              # TODO: Fix below
                              ",".join(MODE.TASK_ID_REQUIRED_LIST)
                              # "Tasks Modes this is required for ???"
                              + ")")
        ]
    ] = None
    task_patch: Optional[
        Annotated[
            TaskPatch,
            Field(description="This input is required for mode=" + TASKS.UPDATE)
        ]
    ] = None
    task_post: Optional[
        Annotated[
            TaskPost,
            Field(description="This input is required for mode=" + TASKS.CREATE)
        ]
    ] = None
    task_list: Optional[
        Annotated[
            TasksListInput,
            Field(description="This input is required for mode=" + TASKS.LIST)
        ]
    ] = TasksListInput().dict()  # Set with empty tasks list
    move_task: Optional[
        Annotated[
            MoveTask,
            Field(description="This input is required for mode=" + TASKS.MOVE_WORKSPACE)
        ]
    ] = None

    @validator('mode')
    def mode_validate_enum(cls, mode):
        """Validates the mode enum"""
        if mode is None:
            raise ValueError("must be one of enum values (" + ",".join(MODE.LIST) + ")")

        # mode = value.get('mode')
        if mode not in MODE.LIST:
            raise ValueError("must be one of enum values (" + ",".join(MODE.LIST) + ")")

        return mode

    @validator('task_post', pre=True)
    def task_post_validate_due_date(cls, task_post):
        # Convert due date to iso8601 date
        due_date = None
        key_conversion = ['dueDate', 'due_date']
        for key in key_conversion:
            if key in task_post and task_post[key] is not None:
                due_date = task_post[key]
                # print('task_post[' + key + ']=' + dueDate + ' (old)')
                iso_date_string = get_iso_date_string(due_date)
                # iso_date = get_iso_date(due_date)
                # value[key] = iso_date
                task_post[key] = iso_date_string
                # print('task_post[' + key + ']=' + iso_date_string + ' (new)')

        return task_post

    @root_validator
    def validate_inputs(cls, values: Dict) -> Dict:
        validation_errors = []
        mode = values.get('mode')

        # try:

        if mode in MODE.TASK_ID_REQUIRED_LIST:
            if 'task_id' not in values or values['task_id'] is None:
                validation_errors.append("task_id cant be none for mode:" + mode)

        match mode:
            case TASKS.UPDATE:
                if 'task_patch' not in values or values['task_patch'] is None:
                    validation_errors.append("task_patch cant be none for mode:" + mode)
            case TASKS.RETRIEVE:
                """Do Nothing"""
            case TASKS.DELETE:
                """Do Nothing"""
            case TASKS.CREATE:
                if 'task_post' not in values or values['task_post'] is None:
                    validation_errors.append("task_post cant be none for mode:" + mode)
            case TASKS.LIST:
                if 'task_list' not in values or values['task_list'] is None:
                    # values['task_list']
                    validation_errors.append("task_list cant be none for mode:" + mode)
            case TASKS.UNASSIGN:
                """Do Nothing"""
            case TASKS.MOVE_WORKSPACE:
                if 'move_task' not in values or values['move_task'] is None:
                    validation_errors.append("move_task cant be none for mode:" + mode)
        # except KeyError as ke:
        #   validation_errors.append(str(ke) + ' is required')

        # Raise error if validation_errors > 0
        if len(validation_errors) > 0:
            raise ValueError("\n".join(validation_errors))
        return values

    '''
    @validator('motion_input', check_fields="mode")
    def motion_validate_params(cls, value):
        # TODO: Validate the motion input type based on the mode

        match value.get('mode'):
            case TASKS.CREATE:
                TaskPost.parse_obj(value)
            case TASKS.UPDATE:
                # TODO: Verify Task id and TaskPatch
                TaskPatch.parse_obj(value)

        return value
    '''

    def to_dict(self) -> Dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        """
        _dict = self.dict(
            by_alias=True,
            exclude={
            },
            exclude_none=True,
        )
        return _dict
