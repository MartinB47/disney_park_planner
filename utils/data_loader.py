import boto3
from botocore.exceptions import ClientError

def get_all_rides():
    """
    Mock function to get all rides (replace with your actual DynamoDB function)
    """
    try:
        # Initialize DynamoDB client with explicit region
        session = boto3.Session(region_name='us-west-2')  # Replace with your region
        dynamodb = session.resource('dynamodb')
        
        # Reference the table
        table = dynamodb.Table('rideMetaData')
        
        # Scan the table to get all items
        response = table.scan()
        
        # Extract ride names from the response
        items = response['Items']
        
        # Continue scanning if we have more items (pagination)
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response['Items'])
        
        # Extract just the ride names
        ride_names = [item.get('rideName') for item in items if 'rideName' in item]
        
        # Create the JSON response
        result = {
            "status": "success",
            "count": len(ride_names),
            "rides": ride_names
        }
        
        return result
    
    except ClientError as e:
        # Handle AWS-specific errors
        error_result = {
            "status": "error",
            "message": str(e),
            "error_code": e.response['Error']['Code'] if 'Error' in e.response else "Unknown"
        }
        return error_result
    except Exception as e:
        # Handle any other errors
        error_result = {
            "status": "error",
            "message": str(e)
        }
        return error_result