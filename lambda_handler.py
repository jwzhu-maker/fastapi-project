import json
import uvicorn
from main import app
from aws_lambda_typing import LambdaContext  # This is a typing library to define Lambda event and context

def lambda_handler(event: dict, context: LambdaContext):
    if "httpMethod" in event:
        if event["httpMethod"] == "POST" and event["resource"] == "/api/v2/face/oauth/token":
            event["body"] = json.loads(event["body"])
            response = uvicorn.run(app, host="0.0.0.0", port=80)
            return response
    return {
        "statusCode": 400,
        "body": json.dumps("Invalid request"),
    }

