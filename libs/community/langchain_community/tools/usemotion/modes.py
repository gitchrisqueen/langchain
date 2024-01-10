# flake8: noqa
import types

MODE = types.SimpleNamespace()
MODE.SEP = "."  # This is the mode separator (i.e parent.child)

def fullName(parentName: str, childName: str):
    return parentName + MODE.SEP + childName


# Tasks
TASKS = types.SimpleNamespace()
TASKS.BASE = "task"
TASKS.UPDATE = fullName(TASKS.BASE, "update")
TASKS.RETRIEVE = fullName(TASKS.BASE, "retrieve")
TASKS.DELETE = fullName(TASKS.BASE, "delete")
TASKS.CREATE = fullName(TASKS.BASE, "create")
TASKS.LIST = fullName(TASKS.BASE, "list")
TASKS.UNASSIGN = fullName(TASKS.BASE, "unassign")
TASKS.MOVE_WORKSPACE = fullName(TASKS.BASE, "move_workspace")

# Recurring Tasks
RECURRING_TASKS = types.SimpleNamespace()
RECURRING_TASKS.BASE = "recurring_task"
RECURRING_TASKS.CREATE = fullName(RECURRING_TASKS.BASE, "create")
RECURRING_TASKS.LIST = fullName(RECURRING_TASKS.BASE, "list")
RECURRING_TASKS.DELETE = fullName(RECURRING_TASKS.BASE, "delete")

# Comments
COMMENTS = types.SimpleNamespace()
COMMENTS.BASE = "comments"
COMMENTS.CREATE = fullName(COMMENTS.BASE, "create")
COMMENTS.LIST = fullName(COMMENTS.BASE, "list")

# Projects
PROJECTS = types.SimpleNamespace()
PROJECTS.BASE = "projects"
PROJECTS.RETRIEVE = fullName(PROJECTS.BASE, "retrieve")
PROJECTS.LIST = fullName(PROJECTS.BASE, "list")
PROJECTS.CREATE = fullName(PROJECTS.BASE, "create")

# Workspaces
WORKSPACES = types.SimpleNamespace()
WORKSPACES.BASE = "workspaces"
WORKSPACES.LIST_STATUSES = fullName(WORKSPACES.BASE, "list_statuses")
WORKSPACES.LIST = fullName(WORKSPACES.BASE, "list")

# Users
USERS = types.SimpleNamespace()
USERS.BASE = "users"
USERS.LIST = fullName(USERS.BASE, "list")
USERS.GET_MY_USER = fullName(USERS.BASE, "get_my_user")

# Schedules
SCHEDULES = types.SimpleNamespace()
SCHEDULES.BASE = "schedules"
SCHEDULES.GET = fullName(USERS.BASE, "get")

# List of All modes
MODE.LIST = [TASKS.UPDATE, TASKS.RETRIEVE, TASKS.DELETE, TASKS.CREATE, TASKS.LIST, TASKS.UNASSIGN, TASKS.MOVE_WORKSPACE,
                     RECURRING_TASKS.CREATE, RECURRING_TASKS.LIST, RECURRING_TASKS.DELETE,
                     COMMENTS.CREATE, COMMENTS.LIST,
                     PROJECTS.RETRIEVE, PROJECTS.LIST, PROJECTS.CREATE,
                     WORKSPACES.LIST_STATUSES, WORKSPACES.LIST,
                     USERS.LIST, USERS.GET_MY_USER,
                     SCHEDULES.GET
                     ]

MODE.TASK_ID_REQUIRED_LIST = [TASKS.UPDATE, TASKS.RETRIEVE, TASKS.DELETE, TASKS.UNASSIGN, TASKS.MOVE_WORKSPACE]



def get_mode_split(fullmode:str) -> list[str]:
    return fullmode.split(MODE.SEP)

def get_parent_mode(fullmode: str) -> str:
    return get_mode_split(fullmode)[0]
def get_child_mode(fullmode: str) ->str:
    return get_mode_split(fullmode)[1]