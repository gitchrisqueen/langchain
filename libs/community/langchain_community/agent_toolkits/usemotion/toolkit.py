import traceback
from typing import Dict, List

from langchain_community.agent_toolkits.base import BaseToolkit
from langchain_community.tools import BaseTool
from langchain_core.tools import ToolException

from langchain_community.tools.usemotion.prompt import *
from langchain_community.tools.usemotion.tool import UseMotionAction
from langchain_community.utilities.usemotion import UseMotionAPIWrapper
from langchain_community.tools.usemotion.modes import *


class UseMotionToolkit(BaseToolkit):
    """Motion Toolkit.

    *Security Note*: This toolkit contains tools that can read and modify
        the state of a service; e.g., by creating, deleting, or updating,
        reading underlying data.

        See https://python.langchain.com/docs/security for more information.
    """

    tools: List[BaseTool] = []

    @classmethod
    def from_motion_api_wrapper(cls, motion_api_wrapper: UseMotionAPIWrapper) -> "UseMotionToolkit":
        operations: List[Dict] = [
            {
                "mode": TASKS.UPDATE,
                "name": mode_to_title(TASKS.UPDATE),
                "description": TASKS_PROMPT.UPDATE,
            },
            {
                "mode": TASKS.RETRIEVE,
                "name": mode_to_title(TASKS.RETRIEVE),
                "description": TASKS_PROMPT.RETRIEVE,
            },
            {
                "mode": TASKS.DELETE,
                "name": mode_to_title(TASKS.DELETE),
                "description": TASKS_PROMPT.DELETE,
            },
            {
                "mode": TASKS.CREATE,
                "name": mode_to_title(TASKS.CREATE),
                "description": TASKS_PROMPT.CREATE,
            },
            {
                "mode": TASKS.LIST,
                "name": mode_to_title(TASKS.LIST),
                "description": TASKS_PROMPT.LIST,
            },
            {
                "mode": TASKS.UNASSIGN,
                "name": mode_to_title(TASKS.UNASSIGN),
                "description": TASKS_PROMPT.UNASSIGN,
            },
            {
                "mode": TASKS.MOVE_WORKSPACE,
                "name": mode_to_title(TASKS.MOVE_WORKSPACE),
                "description": TASKS_PROMPT.MOVE_WORKSPACE,
            },

            {
                "mode": RECURRING_TASKS.CREATE,
                "name": mode_to_title(RECURRING_TASKS.CREATE),
                "description": RECURRING_TASKS_PROMPT.CREATE,
            },
            {
                "mode": RECURRING_TASKS.LIST,
                "name": mode_to_title(RECURRING_TASKS.LIST),
                "description": RECURRING_TASKS_PROMPT.LIST,
            },
            {
                "mode": RECURRING_TASKS.DELETE,
                "name": mode_to_title(RECURRING_TASKS.DELETE),
                "description": RECURRING_TASKS_PROMPT.DELETE,
            },

            {
                "mode": COMMENTS.CREATE,
                "name": mode_to_title(COMMENTS.CREATE),
                "description": COMMENTS_PROMPT.CREATE,
            },
            {
                "mode": COMMENTS.LIST,
                "name": mode_to_title(COMMENTS.LIST),
                "description": COMMENTS_PROMPT.LIST,
            },

            {
                "mode": PROJECTS.RETRIEVE,
                "name": mode_to_title(PROJECTS.RETRIEVE),
                "description": PROJECTS_PROMPT.RETRIEVE,
            },
            {
                "mode": PROJECTS.LIST,
                "name": mode_to_title(PROJECTS.LIST),
                "description": PROJECTS_PROMPT.LIST,
            },
            {
                "mode": PROJECTS.CREATE,
                "name": mode_to_title(PROJECTS.CREATE),
                "description": PROJECTS_PROMPT.CREATE,
            },

            {
                "mode": WORKSPACES.LIST_STATUSES,
                "name": mode_to_title(WORKSPACES.LIST_STATUSES),
                "description": WORKSPACES_PROMPT.LIST_STATUSES,
            },
            {
                "mode": WORKSPACES.LIST,
                "name": mode_to_title(WORKSPACES.LIST),
                "description": WORKSPACES_PROMPT.LIST,
            },

            {
                "mode": USERS.LIST,
                "name": mode_to_title(USERS.LIST),
                "description": USERS_PROMPT.LIST,
            },
            {
                "mode": USERS.GET_MY_USER,
                "name": mode_to_title(USERS.GET_MY_USER),
                "description": USERS_PROMPT.GET_MY_USER,
            },

            {
                "mode": SCHEDULES.GET,
                "name": mode_to_title(SCHEDULES.GET),
                "description": SCHEDULES_PROMPT.GET,
            },


        ]
        tools = [
            UseMotionAction(
                name=action["name"],
                description=action["description"],
                mode=action["mode"],
                api_wrapper=motion_api_wrapper,
                #handle_tool_error=True,
                handle_tool_error=_handle_error,
            )
            for action in operations
        ]
        return cls(tools=tools)

    def get_tools(self) -> List[BaseTool]:
        """Get the tools in the toolkit."""
        return self.tools


def mode_to_title(mode: str):
    return mode.replace(".", "_")


def _handle_error(error: ToolException) -> str:
    return (
            "The following errors occurred during tool execution:"
            #+ error.args[0]
            + str(error)
            #+ traceback.format_exc()  # TODO: Take this out after debugging
            + "Please fix any validation errors you can."
            + "Otherwise, Please try another tool."
    )



