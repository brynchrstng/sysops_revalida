import json
import boto3
from datetime import datetime, timedelta

client = boto3.client('dynamodb', region_name="ap-southeast-1")

def lambda_handler(event, context):

    driverId = event['pathParameters']["driverId"]
    rideId = event['pathParameters']["rideId"]
    body = json.loads(event['body'])
    acceptLocationN = body["acceptLocation"]["N"]
    acceptLocationW = body["acceptLocation"]["W"]
    
    

    queryResponse = client.query(
        TableName = "frab_revalida",
        IndexName = "frab_inverted_index",
        Select = "SPECIFIC_ATTRIBUTES",
        ProjectionExpression="PK, SK, #ts",
        KeyConditionExpression="SK = :rideId",
        ExpressionAttributeNames={
            "#ts": "timestamp"
        },
        ExpressionAttributeValues={
            ":rideId": {
                "S": "RIDE#" + rideId
            }
        }
    )

    pk = queryResponse["Items"][0]["PK"]["S"]
    sk = queryResponse["Items"][0]["SK"]["S"]
    timestamp = queryResponse["Items"][0]["timestamp"]["S"]
    
    response = client.update_item(
        TableName = "frab_revalida",
        Key = {
            "PK": {
                "S": pk
            },
            "SK": {
                "S": sk
            }
        },
        UpdateExpression="SET driverId=:driverId, #state=:state, acceptLocation=:acceptLocation, driverIdKey=:driverIdKey, stateDate=:stateDate REMOVE datePendingState",
        ExpressionAttributeNames={
            "#state": "state"
        },
        ExpressionAttributeValues={
            ":driverId": {
                "S": driverId
            },
            ":driverIdKey": {
                "S": "DR#" + driverId
            },
            ":state": {
                "S": "accepted"
            },
            ":stateDate": {
                "S": "accepted#" + timestamp
            },
            ":acceptLocation": {
                "M": {
                    "Longitude" : {
                        "S" : acceptLocationN
                    },
                    "Latitude" : {
                        "S" : acceptLocationW
                    }
                }
            }
        }
    )

    return {
        "statusCode": 200,
        "body": json.dumps({
            "rideId": rideId,
            "acceptLocation": {
                "N": acceptLocationN,
                "W": acceptLocationW
            },
            "createdAt": timestamp
        })
    }
