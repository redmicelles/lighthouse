import boto3
from botocore.config import Config

my_config: Config = Config(
    connect_timeout=1.0,
    read_timeout=1.0,
    retries={"mode": "legacy", "total_max_attempts": 3},
)

client = boto3.client("dynamodb", config=my_config)


def create_task(request_body: dict) -> None:
    statement: str = "INSERT INTO TasksTable value {}".format(request_body)
    client.execute_statement(Statement=statement)


def query_task_by_id(task_id: str) -> dict:
    statement: str = "SELECT * FROM TasksTable WHERE taskId=?"
    params: list = [{"S": task_id}]
    resp: dict = client.execute_statement(Statement=statement, Parameters=params)
    return resp


def update_task_by_id(task_id: str, request_body: dict) -> dict:
    statement: str = "UPDATE TasksTable {} WHERE taskId=?".format(
        (" ").join([f"SET {key}='{val}'" for (key, val) in request_body.items()])
    )
    params: list = [{"S": task_id}]
    resp: dict = client.execute_statement(Statement=statement, Parameters=params)
    return resp


def delete_task_by_id(task_id: str) -> None:
    statement = "DELETE FROM TasksTable WHERE taskId=?"
    params: list = [{"S": task_id}]
    client.execute_statement(Statement=statement, Parameters=params)
