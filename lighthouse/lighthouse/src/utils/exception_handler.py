import json
import logging
from http import HTTPStatus

from botocore.exceptions import ClientError
from pydantic import ValidationError

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

log_handler = logging.StreamHandler()
log_formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")

log_handler.setFormatter(log_formatter)
logger.addHandler(log_handler)



def exception_handler(func):
    """
    Exception handler decorator function
    """
    def wrapper(*args, **kwargs):
        try:
            output = func(*args, **kwargs)
            return output

        except ValidationError as e:
            return dict(
                isBase64Encoded=False,
                body=json.dumps(
                    {
                        "message": e.errors()[0].get("loc", "")[0].replace("\\", "")
                        + " "
                        + e.errors()[0].get("msg", "").replace("\\", "")
                    }
                ),
                statusCode=HTTPStatus.UNPROCESSABLE_ENTITY.value,
                headers={
                    "content-type": "application/json",
                },
            )
        except ClientError as e:
            logger.error(e)
            return dict(
                isBase64Encoded=False,
                body=json.dumps({"message": str(e)}),
                statusCode=HTTPStatus.FAILED_DEPENDENCY.value,
                headers={
                    "content-type": "application/json",
                },
            )
        except Exception as e:
            logger.error(e)
            return dict(
                isBase64Encoded=False,
                body=json.dumps({"message": "Unhandled exception"}),
                statusCode=HTTPStatus.INTERNAL_SERVER_ERROR,
                headers={
                    "content-type": "application/json",
                },
            )

    return wrapper
