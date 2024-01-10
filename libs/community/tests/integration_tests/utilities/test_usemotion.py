"""Integration test for UseMotion API Wrapper."""
import json
import traceback

import pytest
import copy
from pydantic import ValidationError

from langchain_community.tools.usemotion.motion_input import MotionInput
from langchain_community.tools.usemotion.tool import UseMotionAction
from langchain_community.utilities.usemotion import UseMotionAPIWrapper
from langchain_community.tools.usemotion.modes import *
from langchain_community.utils.usemotion.date_functions import *
from langchain_core.tools import ToolException


def handle_error(error: ToolException) -> str:
    return (
            "The following errors occurred during test tool execution:"
            # + error.args[0]
            + str(error)
            + traceback.format_exc()  # TODO: Take this out after debugging
            + "Please fix any validation errors you can."
            + "Otherwise, Please try another tool."
    )


@pytest.mark.requires('usemotion-api-client')
class TestUseMotion:

    @pytest.fixture(scope='function')
    def motion_input_object(self):
        return MotionInput()

    @pytest.fixture(scope='function')
    def api_wrapper(self):
        return UseMotionAPIWrapper()

    @pytest.fixture(scope='function')
    def usemotion_action(self, api_wrapper):
        return UseMotionAction(
            name='test_action',
            description='testing the tool through the UseMotionAction class',
            api_wrapper=api_wrapper,
            # handle_tool_error=True,
            handle_tool_error=handle_error
        )

    @pytest.fixture(scope='function')
    def input_dict(self):
        return {
            "task_id": "aabbcc",
            "task_patch":
                {
                    "name": "test_task",
                    "this_key_doesnt_exist": True

                },
            "task_post":
                {
                    "name": "test_task",
                    "dueDate": "2024-01-08T23:45:08Z",
                    "workspaceId": "xxyyzz",
                },
            "task_list":
                {
                    "assignee_id": "cdq",
                    "headers": {"Prefer": "code=200, dynamic=true"}
                },
            "move_task":
                {
                    "workspaceId": "xxyyzz"
                }
        }

    @pytest.fixture(scope='function')
    def input_dict_invalid_mode(self, input_dict):
        mod_dict = copy.deepcopy(input_dict)
        mod_dict['mode'] = 'Invalid - Doesnt exist in enumlist'
        return mod_dict

    @pytest.fixture(scope='function')
    def input_dict_no_task_id(self, input_dict):
        mod_dict = copy.deepcopy(input_dict)
        del mod_dict['task_id']
        return mod_dict

    @pytest.fixture(scope='function')
    def input_dict_no_task_list(self, input_dict):
        mod_dict = copy.deepcopy(input_dict)
        del mod_dict['task_list']
        mod_dict['task_list'] = None
        return mod_dict

    @pytest.fixture(scope='function')
    def input_dict_no_task_post(self, input_dict):
        mod_dict = copy.deepcopy(input_dict)
        mod_dict['mode'] = TASKS.CREATE
        mod_dict.pop('task_post')
        return mod_dict

    @pytest.fixture(scope='function')
    def input_dict_no_task_post_workspace_id(self, input_dict):
        mod_dict = copy.deepcopy(input_dict)
        mod_dict['mode'] = TASKS.CREATE
        mod_dict['task_post'].pop('workspaceId')
        return mod_dict

    @pytest.fixture(scope='function')
    def input_dict_invalid_due_date(self, input_dict):
        mod_dict = copy.deepcopy(input_dict)
        mod_dict['mode'] = TASKS.CREATE
        mod_dict['task_post']['dueDate'] = 'Invalid date'
        return mod_dict

    @pytest.fixture(scope='function')
    def input_dict_invalid_due_date_recoverable(self, input_dict):
        mod_dict = copy.deepcopy(input_dict)
        mod_dict['mode'] = TASKS.CREATE
        mod_dict['task_post']['dueDate'] = 'today'
        return mod_dict

    @pytest.fixture(scope='function')
    def required_task_elements(self):
        return ['workspace', 'name', 'due_date', 'deadline_type', 'parent_recurring_task_id', 'completed',
                'creator', 'project', 'status', 'priority', 'labels', 'assignees', 'created_time',
                'scheduling_issue']

    @pytest.fixture(scope='function')
    def input_dict_no_move_task(self, input_dict):
        mod_dict = copy.deepcopy(input_dict)
        mod_dict['mode'] = TASKS.MOVE_WORKSPACE
        mod_dict.pop('move_task')
        return mod_dict

    @pytest.fixture(scope='function')
    def input_dict_no_move_task_workspace_id(self, input_dict):
        mod_dict = copy.deepcopy(input_dict)
        mod_dict['mode'] = TASKS.MOVE_WORKSPACE
        mod_dict['move_task'].pop('workspaceId')
        return mod_dict

    def test_date_functions(self) -> None:
        """Test date functions"""
        invalid_text_time = "Invalid time"
        valid_text_time = "today"
        with pytest.raises(ValueError) as excinfo:
            date_time = get_datetime(invalid_text_time)
        # print(excinfo)
        assert "invalid datetime" in str(excinfo.value), invalid_text_time + ' should raise ValueError'
        date_time = get_datetime(valid_text_time)
        assert isinstance(date_time, datetime) == True, valid_text_time + ' should be instance of datetime'

        with pytest.raises(ValueError) as excinfo:
            date_time = get_iso_date(invalid_text_time)
        # print(excinfo)
        assert "invalid datetime" in str(excinfo.value), invalid_text_time + ' should raise ValueError'
        date_time = get_iso_date(valid_text_time)
        assert isinstance(date_time, datetime) == True, valid_text_time + 'as iso_date should be instance of datetime'

        with pytest.raises(ValueError) as excinfo:
            date_time = get_iso_date_string(invalid_text_time)
        assert "invalid datetime" in str(excinfo.value), invalid_text_time + ' should raise ValueError'
        date_time = get_iso_date_string(valid_text_time)
        assert isinstance(date_time, str) == True, valid_text_time + ' should be instance of string'

    def test_motion_input(self, input_dict, input_dict_invalid_mode, motion_input_object) -> None:
        """Test the dict keys for motion input class"""
        with pytest.raises(ValidationError) as excinfo:
            motion_input_object.parse_obj(input_dict_invalid_mode)
        # print(excinfo)
        assert "mode" in str(excinfo.value) and "must be one of enum values" in str(excinfo.value)
        motion_input = motion_input_object.parse_obj(input_dict)
        assert isinstance(motion_input, MotionInput) == True, ' should be instance of MotionInput'
        # print(motion_input)

    def test_update_task(self, usemotion_action, input_dict, input_dict_no_task_id, required_task_elements,
                         motion_input_object) -> None:
        """Test the Update task Call that Creates a tasks on Motion."""
        mode = TASKS.UPDATE
        input_dict['mode'] = mode
        input_dict_no_task_id['mode'] = mode

        # Test the inputs
        with pytest.raises(ValidationError) as excinfo:
            motion_input_object.parse_obj(input_dict_no_task_id)
        # print(excinfo)
        assert "task_id cant be none" in str(excinfo.value)

        # Test the output
        usemotion_action.mode = mode
        output = usemotion_action.run(input_dict, color='yellow')
        # print(output)

        for element in required_task_elements:
            assert element in output

    def test_retrieve_task(self, usemotion_action, input_dict, input_dict_no_task_id, required_task_elements,
                           motion_input_object) -> None:
        """Test the Retrieve task Call that Creates a tasks on Motion."""
        mode = TASKS.RETRIEVE
        input_dict['mode'] = mode
        input_dict_no_task_id['mode'] = mode

        # Test the inputs
        with pytest.raises(ValidationError) as excinfo:
            motion_input_object.parse_obj(input_dict_no_task_id)
        assert "task_id cant be none" in str(excinfo.value)

        # Test the output
        usemotion_action.mode = mode
        output = usemotion_action.run(input_dict, color='yellow')

        for element in required_task_elements:
            assert element in output

    def test_delete_task(self, usemotion_action, input_dict, input_dict_no_task_id, motion_input_object) -> None:
        """Test the Delete task Call that Creates a tasks on Motion."""
        mode = TASKS.DELETE
        input_dict['mode'] = mode
        input_dict_no_task_id['mode'] = mode

        # Test the inputs
        with pytest.raises(ValidationError) as excinfo:
            motion_input_object.parse_obj(input_dict_no_task_id)
        assert "task_id cant be none" in str(excinfo.value)

        # Test the output
        usemotion_action.mode = mode
        output = usemotion_action.run(input_dict, color='yellow')
        assert "Task deleted successfully" in str(output)

    def test_create_task(self, usemotion_action, input_dict, input_dict_no_task_post,
                         input_dict_no_task_post_workspace_id,
                         input_dict_invalid_due_date, input_dict_invalid_due_date_recoverable,
                         required_task_elements, motion_input_object) -> None:
        """Test the Create task Call that Creates a tasks on Motion."""
        mode = TASKS.CREATE
        input_dict['mode'] = mode

        # Test the inputs
        with pytest.raises(ValidationError) as excinfo:
            motion_input_object.parse_obj(input_dict_no_task_post_workspace_id)
        # print(excinfo)
        assert "task_post -> workspaceId" in str(excinfo.value) and "field required" in str(excinfo.value)

        with pytest.raises(ValidationError) as excinfo:
            motion_input_object.parse_obj(input_dict_no_task_post)
        # print(excinfo)
        assert "task_post" in str(excinfo.value)

        with pytest.raises(ValidationError) as excinfo:
            motion_input_object.parse_obj(input_dict_invalid_due_date)
        # print(excinfo)
        assert "task_post" in str(excinfo.value) and "invalid datetime" in str(
            excinfo.value), 'Invalid dueDate should raise ValidationError'

        # Test the outputs
        # See if due date is auto-corrected
        motion_input_object.parse_obj(input_dict_invalid_due_date_recoverable)
        # api_wrapper.run(mode, input_dict_invalid_due_date_recoverable)

        usemotion_action.mode = mode
        output = usemotion_action.run(input_dict, color='yellow')

        for element in required_task_elements:
            assert element in output
        # print(output)

    def test_list_task(self, usemotion_action, input_dict, input_dict_no_task_list, required_task_elements,
                       motion_input_object) -> None:
        """Test the Retrieve task Call that Creates a tasks on Motion."""
        mode = TASKS.LIST
        input_dict['mode'] = mode
        input_dict_no_task_list['mode'] = mode

        # Test the inputs
        with pytest.raises(ValidationError) as excinfo:
            motion_input_object.parse_obj(input_dict_no_task_list)
        assert "task_list cant be none" in str(excinfo.value)

        # Test the output
        usemotion_action.mode = mode
        output = usemotion_action.run(input_dict, color='yellow')

        list_task_elements = ['tasks', 'meta', 'next_cursor', 'page_size']
        for element in list_task_elements:
            assert element in output

    def test_unassign_task(self, usemotion_action, input_dict, input_dict_no_task_id, motion_input_object) -> None:
        """Test the Unassign task Call that Creates a tasks on Motion."""
        mode = TASKS.UNASSIGN
        input_dict['mode'] = mode
        input_dict_no_task_id['mode'] = mode

        # Test the inputs
        with pytest.raises(ValidationError) as excinfo:
            motion_input_object.parse_obj(input_dict_no_task_id)
        assert "task_id cant be none" in str(excinfo.value)

        # Test the output
        usemotion_action.mode = mode
        output = usemotion_action.run(input_dict, color='yellow')
        assert "Task unassigned successfully" in str(output)

    def test_move_task(self, usemotion_action, input_dict, input_dict_no_task_id, input_dict_no_move_task,
                       input_dict_no_move_task_workspace_id, required_task_elements, motion_input_object) -> None:
        """Test the Move task Call that Creates a tasks on Motion."""
        mode = TASKS.MOVE_WORKSPACE
        input_dict['mode'] = mode
        input_dict_no_task_id['mode'] = mode

        # Test the inputs
        with pytest.raises(ValidationError) as excinfo:
            motion_input_object.parse_obj(input_dict_no_task_id)
        assert "task_id cant be none" in str(excinfo.value)

        with pytest.raises(ValidationError) as excinfo:
            motion_input_object.parse_obj(input_dict_no_move_task)
        assert "move_task cant be none" in str(excinfo.value)

        # Test the inputs
        with pytest.raises(ValidationError) as excinfo:
            motion_input_object.parse_obj(input_dict_no_move_task_workspace_id)
        # print(excinfo)
        assert "move_task -> workspaceId" in str(excinfo.value) and "field required" in str(excinfo.value)

        # Test the output
        usemotion_action.mode = mode
        output = usemotion_action.run(input_dict, color='yellow')

        for element in required_task_elements:
            assert element in output
