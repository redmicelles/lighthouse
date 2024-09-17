import json
from http import HTTPStatus

from utils.aws_ddb import create_task
from utils.aws_ddb import delete_task_by_id
from utils.aws_ddb import query_task_by_id
from utils.aws_ddb import update_task_by_id
from utils.exception_handler import exception_handler
from utils.schemas import CreateTaskSchema
from utils.schemas import RetrieveTaskSchema
from utils.schemas import UpdateTaskSchema
from typing import Any


@exception_handler
def router_function(event: Any):
    """
    Api routing function
    """
    req_method: str = event.get("requestContext", {}).get("http", {}).get("method")
    task_id: str = event.get("pathParameters", {}).get("id")
    status_code: int = HTTPStatus.OK.value
    match req_method.upper():
        case "POST":
            # validate request data
            task_data: dict = CreateTaskSchema.model_validate(
                json.loads(event.get("body", {}))
            ).model_dump()

            create_task(task_data)

            # parse response data
            body: dict = RetrieveTaskSchema.model_validate(
                query_task_by_id(task_data["taskId"])
            ).model_dump()

            # update response status code
            status_code: int = HTTPStatus.CREATED.value

        case "GET":
            query_resp: dict = query_task_by_id(task_id)

            # check if query returns data
            if not query_resp.get("Items"):
                return dict(
                    statusCode=HTTPStatus.NOT_FOUND.value,
                    body=json.dumps({}, indent=2),
                    headers={
                        "content-type": "application/json",
                    },
                )

            # parse response data
            body = RetrieveTaskSchema.model_validate(query_resp).model_dump()

        case "PUT":
            # check if query returns data
            if not query_task_by_id(task_id).get("Items"):
                return dict(
                    statusCode=HTTPStatus.NOT_FOUND.value,
                    body=json.dumps({"message": "Task not found!"}, indent=2),
                    headers={
                        "content-type": "application/json",
                    },
                )
            # validate request body
            task_data: dict = UpdateTaskSchema.model_validate(
                json.loads(event.get("body", {}))
            ).model_dump()

            update_task_by_id(task_id, task_data)

            # parse response data
            body = RetrieveTaskSchema.model_validate(
                query_task_by_id(task_id)
            ).model_dump()

        case "DELETE":
            # check if query returns data
            if not query_task_by_id(task_id).get("Items"):
                return dict(
                    statusCode=HTTPStatus.NOT_FOUND.value,
                    body=json.dumps({"message": "Task not found!"}, indent=2),
                    headers={
                        "content-type": "application/json",
                    },
                )
            delete_task_by_id(task_id)
            status_code = HTTPStatus.NO_CONTENT.value
            body = dict()

    return dict(
        isBase64Encoded=False,
        statusCode=status_code,
        body=json.dumps(body, indent=2),
        headers={
            "content-type": "application/json",
        },
    )


def handler(event, context):
    return router_function(event)
