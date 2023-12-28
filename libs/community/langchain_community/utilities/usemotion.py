"""Util that calls Motion via API."""
import json
from datetime import datetime
from json import JSONDecodeError
from typing import Any, Dict, List, Optional, Union, Type

import dateparser
import dateutil.parser as isoparser
# from pydantic import BaseModel, Extra, root_validator
from pydantic import ValidationError
from langchain_core.pydantic_v1 import BaseModel, Extra, root_validator
from langchain_core.tools import ToolException
from langchain_core.utils import get_from_dict_or_env

import openapi_client
from aiagents.tools.motion.modes import *

from aiagents.utils.utillogger import logger
# Import all the models so the tool can use it to create input paramaters as needed
from openapi_client.models import *

from aiagents.tools.motion.motion_input import MotionInput
from aiagents.tools.motion.motion_list_tasks_input import MotionListTasksInput
from aiagents.tools.motion.motion_workspaces_list_input import MotionWorkspacesListInput


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
            from openapi_client import ApiClient
        except ImportError:
            raise ImportError(
                "Motion's openapi_client is not installed. "
                "Please install it with `pip install openapi_client`"
            )

        # Defining the host is optional and defaults to https://api.usemotion.com/v1
        # See configuration.py for a list of all supported configuration parameters.
        configuration = openapi_client.Configuration(
            host=motion_instance_url
        )

        # Configure API key authorization: Motion_API_Key
        configuration.api_key['Motion_API_Key'] = motion_api_key
        motion_api_client = openapi_client.ApiClient(configuration)
        values["motion"] = motion_api_client

        return values

    def parseParams_old(self, query: str) -> Dict[str, Any]:
        logger.info("parseParams query: %s" % query)
        # TODO: Create a list of param keys that need to be converted to ISO 8601 strings
        # Need to convert due dates into ISO 8601 format
        parsed_params = json.loads(query)
        logger.info("parseParams parsed_params: %s" % parsed_params)

        # TODO: Find all possible fields with aliases and add to the params key value for the non-aliased field name as well

        for k, v in parsed_params.items():
            if k == "due_date" or k == "dueDate":
                parsed_params[k] = getISODate(v)
        return parsed_params

    def parseParams(self, motion_input: MotionInput) -> MotionInput:
        if motion_input.get("dueDate") is not None:
            iso_date = getISODate(motion_input.get("dueDate"))
            motion_input['dueDate'] = iso_date
        return motion_input

    def _parse_input(
            self,
            model: Type[BaseModel],
            tool_input: Union[str, Dict],
    ) -> Union[str, Dict[str, Any]]:
        """Convert tool input to pydantic model."""
        result = model.model_validate(tool_input)
        parsed_input = {k: v for k, v in result.dict(by_alias=True).items() if k in tool_input}
        logger.info("_parse_input: %s" % parsed_input)
        return parsed_input

    def tasks_action(self, mode: str, motion_input: Dict[str, MotionInput] = None) -> str:
        try:
            import json
        except ImportError:
            raise ImportError(
                "json is not installed. Please install it with `pip install json`"
            )

        # Create an instance of the TaskAPI class
        api_instance = openapi_client.TasksApi(self.motion)

        logger.info("Mode(%s) MotionInput: %s" % (mode, motion_input))

        # Get params as json from query string
        if motion_input is not None:
            params = self.parseParams(motion_input.get('motion_input', {}))
        else:
            params = {}
        logger.info("Mode(%s) params: %s" % (mode, params))

        match mode:
            case TASKS.UPDATE:
                # Update Tasks Patch
                task_patch_dict = self._parse_input(openapi_client.TaskPatch, params)
                my_task_patch = openapi_client.TaskPatch.from_dict(task_patch_dict)
                # Call API to update the Task and get response
                out = api_instance.tasks_controller_update_task_without_preload_content(
                    task_id=params['task_id'],
                    task_patch=my_task_patch)
            case TASKS.RETRIEVE:
                # Call API to get the Task and get response
                out = api_instance.tasks_controller_get_by_id_without_preload_content(
                    task_id=params['task_id'])
            case TASKS.DELETE:
                # Call API to delete Task and get response
                out = api_instance.tasks_controller_delete_task_without_preload_content(
                    task_id=params['task_id'])
                try:
                    if out.status == 204:
                        out = "Task was unassigned"
                except Exception as e:
                    out = e
            case TASKS.CREATE:
                # Create Tasks Post
                #task_post_dict = self._parse_input(openapi_client.TaskPost, params)
                #logger.info("Mode(%s) task_post_dict: %s" % (mode, task_post_dict))
                #my_task_post = openapi_client.TaskPost.from_dict(task_post_dict)
                # Call API to create Task and get response
                my_task_post = motion_input.get('task_post')
                out = api_instance.tasks_controller_post_without_preload_content(my_task_post)
            case TASKS.LIST:
                # Call API to list Task and get response
                out = api_instance.tasks_controller_get_without_preload_content(
                    cursor=params.get('cursor'),
                    label=params.get('label'),
                    status=params.get('status'),
                    workspace_id=params.get('workspace_id'),
                    project_id=params.get('project_id'),
                    name=params.get('name'),
                    assignee_id=params.get('assignee_id'),
                )
            case TASKS.UNASSIGN:
                # Call API to delete assignee from Task and get response
                out = api_instance.tasks_controller_delete_assignee_without_preload_content(
                    task_id=params['task_id'])
                if out.status == 204:
                    out = "Task was unassigned"
                logger.info("Mode(%s) api_response after status check: %s" % (mode, out))
            case TASKS.MOVE_WORKSPACE:
                # Create the MoveTask
                my_move_task = MoveTask.from_dict(params['move_task'])
                logger.info("Mode(%s) MoveTask: %s" % (mode, my_move_task))
                # Call API to move Task and get response
                out = api_instance.tasks_controller_move_task_without_preload_content(
                    task_id=params['task_id'],
                    move_task=my_move_task)
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
        try:
            import json
        except ImportError:
            raise ImportError(
                "json is not installed. Please install it with `pip install json`"
            )

        # Create an instance of the TaskAPI class
        api_instance = openapi_client.WorkspacesApi(self.motion)

        logger.info("Mode(%s) MotionInput: %s" % (mode, motion_input))

        # Get params as json from query string
        if motion_input is not None:
            params = self.parseParams(motion_input.get('motion_input', {}))
        else:
            params = {}
        logger.info("Mode(%s) params: %s" % (mode, params))

        match mode:
            case WORKSPACES.LIST:
                inputs = MotionWorkspacesListInput.parse_obj(params)
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
        try:
            import json
        except ImportError:
            raise ImportError(
                "json is not installed. Please install it with `pip install json`"
            )
        params = json.loads(motion_input)
        jira_function = getattr(self.jira, params["function"])
        return jira_function(*params.get("args", []), **params.get("kwargs", {}))

    def run(self, mode: str, motion_input: Dict[str, MotionInput] = None) -> str:
        modeSplit = mode.split(".")
        parentMode = modeSplit[0]
        childMode = modeSplit[1]

        logger.info("parentMode: %s" % parentMode)
        logger.info("childMode: %s" % childMode)
        logger.info("motion_input: %s" % motion_input)

        try:
            match parentMode:
                case "task":
                    return self.tasks_action(mode, motion_input)

                case "recurring_task":
                    raise ToolException("This mode is not yet implemented for this tool.")
                    return self.recurring_tasks_action(mode, motion_input)

                case "comments":
                    raise ToolException("This mode is not yet implemented for this tool.")
                    return self.comments_action(mode, motion_input)

                case "projects":
                    raise ToolException("This mode is not yet implemented for this tool.")
                    return self.projects_action(mode, motion_input)

                case "workspaces":
                    #raise ToolException("This mode is not yet implemented for this tool.")
                    return self.workspaces_action(mode, motion_input)

                case "users":
                    raise ToolException("This mode is not yet implemented for this tool.")
                    return self.users_action(mode, motion_input)

                case "schedules":
                    raise ToolException("This mode is not yet implemented for this tool.")
                    return self.schedule_action(mode, motion_input)

                case _:
                    raise ToolException("This mode is not yet implemented for this tool.")
                    return self.other_action(mode, query)

        except ValidationError as ve:
            logger.info("Validation Error: Mode(%s) api_response: %s" % (mode, ve))
            raise ToolException(ve)


def getDateTime(text: str) -> datetime:
    return dateparser.parse(text)


def getISODate(text: str) -> str:
    # Convert the string into a datetime string
    dateTime = getDateTime(text)
    # Return the ISO
    date = isoparser.parse(dateTime.strftime("%Y-%m-%d"))
    return date.isoformat()
