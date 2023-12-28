# flake8: noqa
import types

# Tasks
TASKS_PROMPT = types.SimpleNamespace()
TASKS_PROMPT.UPDATE = """
    Useful when you need to update a calendar task
    """
TASKS_PROMPT.RETRIEVE = """
    Useful when you need to retrieve a calendar task
    """
TASKS_PROMPT.DELETE = """
    Useful when you need to delete a calendar task
    """
TASKS_PROMPT.CREATE = """ 
    Useful when you need to create a calendar task.
"""
TASKS_PROMPT.LIST = """
    Useful when you need a list of calendar tasks.
"""
TASKS_PROMPT.UNASSIGN = """
    Useful when you need to delete an assignee from a calendar task
"""
TASKS_PROMPT.MOVE_WORKSPACE = """
    Useful when you need to move a Motion task to a workspace 
"""

# Recurring Tasks
RECURRING_TASKS_PROMPT = types.SimpleNamespace()
RECURRING_TASKS_PROMPT.CREATE = """Useful when you need to create a recurring Motion task"""
RECURRING_TASKS_PROMPT.LIST = """Useful when you need a list of recurring Motion tasks"""
RECURRING_TASKS_PROMPT.DELETE = """Useful when you need to delete a recurring Motion task"""

# Comments
COMMENTS_PROMPT = types.SimpleNamespace()
COMMENTS_PROMPT.CREATE = """Useful when you need to create a comment on a Motion task"""
COMMENTS_PROMPT.LIST = """Useful when you need a list of Motion comments"""

# Projects
PROJECTS_PROMPT = types.SimpleNamespace()
PROJECTS_PROMPT.RETRIEVE = """Useful when you need to retrieve a Motion project"""
PROJECTS_PROMPT.LIST = """Useful when you need a list of Motion projects"""
PROJECTS_PROMPT.CREATE = """Useful when you need to create a Motion project"""

# Workspaces
WORKSPACES_PROMPT = types.SimpleNamespace()
WORKSPACES_PROMPT.LIST_STATUSES = """Useful when you need a list of Motion workspaces filtered by a status"""
WORKSPACES_PROMPT.LIST = """Useful when you need a list of Motion workspaces"""

# Users
USERS_PROMPT = types.SimpleNamespace()
USERS_PROMPT.LIST = """Useful when you need a list of Motion users"""
USERS_PROMPT.GET_MY_USER = """Useful when you need the Motion user that represents the current user"""

# Schedules
SCHEDULES_PROMPT = types.SimpleNamespace()
SCHEDULES_PROMPT.GET = """Useful when you need a Motion schedule"""
