"""Util that calls Motion via API."""
import json

from json import JSONDecodeError
from typing import Any, Dict, List, Optional, Union, Type

# from pydantic import BaseModel, Extra, root_validator
from pydantic import ValidationError

from langchain_community.tools.usemotion.modes import TASKS
from langchain_core.pydantic_v1 import BaseModel, Extra, root_validator
from langchain_core.tools import ToolException
from langchain_core.utils import get_from_dict_or_env

import usemotion_api_client
from langchain_community.tools.usemotion.modes import *

from langchain_community.utils.usemotion.logger import logger
from langchain_community.utils.usemotion.date_functions import *
# Import all the models so the tool can use it to create input paramaters as needed
from usemotion_api_client.models import *

from langchain_community.tools.usemotion.modes import *
from langchain_community.tools.usemotion.motion_input import MotionInput, TasksListInput


# from langchain_community.tools.usemotion.motion_list_tasks_input import MotionListTasksInput
# from langchain_community.tools.motion.motion_workspaces_list_input import MotionWorkspacesListInput


# TODO: think about error handling, more specific api specs, and api rate limits
class UseMotionAPIWrapper(BaseModel):
    """Wrapper for Motion API."""

    DEFAULT_MOTION_API_URL: Optional[str] = "https://api.usemotion.com/v1"
    motion_api_client: Any  #: :meta private:
    motion_api_key: Optional[str] = None
    motion_instance_url: Optional[str] = None

    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.forbid

    @root_validator()
    def validate_environment(cls, values: Dict) -> Dict:
        """Validate that api key and python package exists in environment."""

        motion_api_key = get_from_dict_or_env(
            values, "motion_api_key", "MOTION_API_KEY"
        )
        values["motion_api_key"] = motion_api_key

        motion_instance_url = get_from_dict_or_env(
            values, "motion_instance_url", "MOTION_INSTANCE_URL"
        )
        # Use default url if none provided
        if motion_instance_url is None:
            motion_instance_url = UseMotionAPIWrapper.DEFAULT_MOTION_API_URL
        values["motion_instance_url"] = motion_instance_url

        try:
            from usemotion_api_client import ApiClient
        except ImportError:
            raise ImportError(
                "Motion's usemotion_api_client is not installed. "
                "Please install it with `pip install usemotion_api_client`"
            )

        # Defining the host is optional and defaults to https://api.usemotion.com/v1
        # See configuration.py for a list of all supported configuration parameters.
        configuration = usemotion_api_client.Configuration(
            host=motion_instance_url
        )

        # Configure API key authorization: Motion_API_Key
        configuration.api_key['Motion_API_Key'] = motion_api_key
        motion_api_client = usemotion_api_client.ApiClient(configuration)
        values["motion_api_client"] = motion_api_client

        return values

    def tasks_action(self, mode: str, motion_input: MotionInput) -> str:

        # Create an instance of the TaskAPI class
        api_instance = usemotion_api_client.TasksApi(self.motion_api_client)

        logger.info("Mode(%s) MotionInput: %s" % (mode, motion_input))

        match mode:
            case TASKS.UPDATE:
                # Call API to update the Task and get response
                out = api_instance.tasks_controller_update_task(
                    task_id=motion_input.task_id,
                    task_patch=motion_input.task_patch
                )
            case TASKS.RETRIEVE:
                # Call API to get the Task and get response
                out = api_instance.tasks_controller_get_by_id(
                    task_id=motion_input.task_id
                )
            case TASKS.DELETE:
                # Call API to delete Task and get response
                api_instance.tasks_controller_delete_task(
                    task_id=motion_input.task_id
                )
                out = {"message": "Task deleted successfully"}
            case TASKS.CREATE:
                # Call API to create Task and get response
                out = api_instance.tasks_controller_post(
                    task_post=motion_input.task_post
                )
            case TASKS.LIST:
                all_tasks = []

                # Get the task_list object
                task_list = motion_input.task_list

                # Pop off headers and convert to private arg if they exist (This is mainly used for testing)
                headers = task_list.pop('headers', None)
                max_tasks = task_list.pop('max_tasks', 25)

                while True:
                    # print('Task list | motion_input.task_list (before): %s' % task_list)
                    # Call API to list Task and get response
                    if headers is not None:
                        out = api_instance.tasks_controller_get(**task_list, _headers=headers)
                    else:
                        out = api_instance.tasks_controller_get(**task_list)

                    # Check for curser response and add to output
                    meta = getattr(out, 'meta', None)
                    tasks = out.tasks
                    # print('Task list | tasks size: %s' % len(out.tasks))

                    all_tasks.extend(tasks)
                    out.tasks = all_tasks

                    # print('Task list | all tasks size: %s' % len(all_tasks))
                    if max_tasks <= len(all_tasks):
                        break

                    if meta is not None:
                        # print('Task list | meta: %s' % meta)
                        next_cursor = getattr(meta, 'next_cursor', None)
                        if next_cursor is not None:
                            # print('Task list | next_cursor: %s' % next_cursor)
                            task_list['cursor'] = next_cursor
                            # print('Task list | task_list (after): %s' % task_list)
                        else:
                            break
                    else:
                        break
            case TASKS.UNASSIGN:
                # Call API to delete assignee from Task and get response
                api_instance.tasks_controller_delete_assignee(
                    task_id=motion_input.task_id
                )
                out = {"message": "Task unassigned successfully"}
            case TASKS.MOVE_WORKSPACE:
                # Call API to move Task and get response
                out = api_instance.tasks_controller_move_task(
                    task_id=motion_input.task_id,
                    move_task=motion_input.move_task

                )
            case _:
                raise ToolException("This mode is not yet implemented for this tool.")

        try:
            logger.info("Mode(%s) api_response before json check" % mode)
            out = out.json()
        except (JSONDecodeError, AttributeError):
            logger.info("Mode(%s) api_response was not a JSON: %s" % (mode, out))

        logger.info("Mode(%s) api_response: %s" % (mode, out))
        return out

    def workspaces_action(self, mode: str, motion_input: Dict[str, MotionInput] = None) -> str:

        # Create an instance of the TaskAPI class
        api_instance = usemotion_api_client.WorkspacesApi(self.motion)

        logger.info("Mode(%s) MotionInput: %s" % (mode, motion_input))

        # Get params as json from query string
        if motion_input is not None:
            params = self.parseParams(motion_input.get('motion_input', {}))
        else:
            params = {}
        logger.info("Mode(%s) params: %s" % (mode, params))

        match mode:
            case WORKSPACES.LIST:
                inputs = MotionInput.parse_obj(params)
                logger.info("Mode(%s) inputs: %s" % (mode, inputs))
                input_dict = inputs.model_dump(by_alias=True)
                logger.info("Mode(%s) input_dict: %s" % (mode, input_dict))
                out = api_instance.workspaces_controller_get_without_preload_content(**input_dict)
            case _:
                raise ToolException("This mode is not yet implemented for this tool.")

        try:
            logger.info("Mode(%s) api_response before json check" % mode)
            out = out.json()
        except (JSONDecodeError, AttributeError):
            logger.info("Mode(%s) api_response was not a JSON: %s" % (mode, out))

        logger.info("Mode(%s) api_response: %s" % (mode, out))
        return out

    def other(self, mode: str, motion_input: MotionInput) -> str:

        params = json.loads(motion_input)
        jira_function = getattr(self.jira, params["function"])
        return jira_function(*params.get("args", []), **params.get("kwargs", {}))

    def run(self, mode: str, motion_input: MotionInput) -> str:

        parent_mode = get_parent_mode(mode)
        logger.info("parent_mode: %s" % parent_mode)

        # Add the mode to the motion_input
        # motion_input.mode = mode
        logger.info("Mode(%s) motion_inputs: %s" % (mode, motion_input))

        try:
            match parent_mode:
                case TASKS.BASE:
                    return self.tasks_action(mode, motion_input)

                case RECURRING_TASKS.BASE:
                    raise ToolException("This mode is not yet implemented for this tool.")
                    return self.recurring_tasks_action(mode, motion_input)

                case COMMENTS.BASE:
                    raise ToolException("This mode is not yet implemented for this tool.")
                    return self.comments_action(mode, motion_input)

                case PROJECTS.BASE:
                    raise ToolException("This mode is not yet implemented for this tool.")
                    return self.projects_action(mode, motion_input)

                case WORKSPACES.BASE:
                    # raise ToolException("This mode is not yet implemented for this tool.")
                    return self.workspaces_action(mode, motion_input)

                case USERS.BASE:
                    raise ToolException("This mode is not yet implemented for this tool.")
                    return self.users_action(mode, motion_input)

                case SCHEDULES.BASE:
                    raise ToolException("This mode is not yet implemented for this tool.")
                    return self.schedule_action(mode, motion_input)

                case _:
                    raise ToolException("This mode is not yet implemented for this tool.")
                    return self.other_action(mode, query)

        except (ValidationError) as ve:
            logger.info("Mode(%s) -> ValidationError: %s" % (mode, ve))
            # TODO: skpping these for now | raise ToolException(e)
        except (Exception) as e:
            logger.info("Mode(%s) -> Exception: %s" % (mode, e))
            raise ToolException(e)
