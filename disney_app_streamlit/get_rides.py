import boto3

def get_all_ride_names_from_dynamodb():
    """
    Retrieves all ride names from the rideMetaData DynamoDB table and returns them as JSON.
    """
    try:
        # Initialize DynamoDB client
        dynamodb = boto3.resource('dynamodb')
        
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
        
        # Extract just the ride names (assuming each item has a 'rideName' attribute)
        ride_names = [item.get('name') for item in items if 'name' in item]
        
        # Create the JSON response
        result = {
            "status": "success",
            "count": len(ride_names),
            "rides": ride_names
        }
        
        return result
    
    except Exception as e:
        # Handle any errors
        error_result = {
            "status": "error",
            "message": str(e)
        }
        return error_result