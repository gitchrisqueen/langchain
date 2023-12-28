# flake8: noqa
import types

# Tasks
TASKS = types.SimpleNamespace()
TASKS.UPDATE = "task.update"
TASKS.RETRIEVE = "task.retrieve"
TASKS.DELETE = "task.delete"
TASKS.CREATE = "task.create"
TASKS.LIST = "task.list"
TASKS.UNASSIGN = "task.unassign"
TASKS.MOVE_WORKSPACE = "task.move_workspace"

# Recurring Tasks
RECURRING_TASKS = types.SimpleNamespace()
RECURRING_TASKS.CREATE = "recurring_task.create"
RECURRING_TASKS.LIST = "recurring_task.list"
RECURRING_TASKS.DELETE = "recurring_task.delete"

# Comments
COMMENTS = types.SimpleNamespace()
COMMENTS.CREATE = "comments.create"
COMMENTS.LIST = "comments.list"

# Projects
PROJECTS = types.SimpleNamespace()
PROJECTS.RETRIEVE = "projects.retrieve"
PROJECTS.LIST = "projects.list"
PROJECTS.CREATE = "projects.create"

# Workspaces
WORKSPACES = types.SimpleNamespace()
WORKSPACES.LIST_STATUSES = "workspaces.list_statuses"
WORKSPACES.LIST = "workspaces.list"

# Users
USERS = types.SimpleNamespace()
USERS.LIST = "users.list"
USERS.GET_MY_USER = "users.get_my_user"

# Schedules
SCHEDULES = types.SimpleNamespace()
SCHEDULES.GET = "schedules.get"
