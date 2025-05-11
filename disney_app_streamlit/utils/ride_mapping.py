import boto3
import logging
from botocore.exceptions import ClientError

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_ride_ids_from_names(ride_names):
    """
    Retrieves ride IDs for the given ride names from the DynamoDB table.
    
    Args:
        ride_names (list): List of ride names to get IDs for
    
    Returns:
        dict: Dictionary with status and either ride IDs or error message
    """
    try:
        logger.info(f"Getting ride IDs for {len(ride_names)} rides")
        
        # Initialize DynamoDB client with explicit region
        session = boto3.Session(region_name='us-west-2')
        dynamodb = session.resource('dynamodb')
        
        # Reference the table
        table = dynamodb.Table('rideMetaData')
        
        # Scan the table to get all items
        response = table.scan()
        items = response['Items']
        
        # Continue scanning if we have more items (pagination)
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response['Items'])
        
        # Create a mapping of ride names to ride IDs
        ride_map = {}
        for item in items:
            # Check for both possible attribute names
            name = item.get('name') or item.get('rideName')
            ride_id = item.get('id') or item.get('rideId')
            
            if name and ride_id:
                ride_map[name] = ride_id
        
        logger.info(f"Found {len(ride_map)} rides in the database")
        
        # Get the IDs for the requested ride names
        ride_ids = []
        missing_rides = []
        
        for ride_name in ride_names:
            if ride_name in ride_map:
                ride_ids.append(ride_map[ride_name])
            else:
                missing_rides.append(ride_name)
                
        if missing_rides:
            logger.warning(f"Could not find IDs for rides: {missing_rides}")
            
        return {
            "status": "success",
            "ride_ids": ride_ids,
            "missing_rides": missing_rides,
            "found_count": len(ride_ids)
        }
        
    except ClientError as e:
        logger.error(f"AWS error: {e}")
        return {
            "status": "error",
            "message": f"AWS error: {str(e)}"
        }
    except Exception as e:
        logger.error(f"Error getting ride IDs: {e}")
        return {
            "status": "error",
            "message": f"Error: {str(e)}"
        }