import boto3
from botocore.exceptions import ClientError
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_all_ride_names_from_dynamodb():
    """
    Retrieves all ride names from the rideMetaData DynamoDB table and returns them as JSON.
    """
    try:
        # Initialize DynamoDB client with explicit region
        logger.info("Initializing DynamoDB client")
        session = boto3.Session(region_name='us-west-2')  # Make sure this is your correct region
        dynamodb = session.resource('dynamodb')
        
        # Reference the table
        logger.info("Accessing rideMetaData table")
        table = dynamodb.Table('rideMetaData')
        
        # Scan the table to get all items
        logger.info("Scanning table for items")
        response = table.scan()
        
        # Extract items from the response
        items = response['Items']
        logger.info(f"Initial scan returned {len(items)} items")
        
        # Continue scanning if we have more items (pagination)
        while 'LastEvaluatedKey' in response:
            logger.info("Scanning for additional items")
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response['Items'])
        
        # Log the first item to see its structure
        if items:
            logger.info(f"Sample item structure: {items[0]}")
        
        # Try both 'name' and 'rideName' attributes
        ride_names = []
        for item in items:
            if 'name' in item:
                ride_names.append(item['name'])
            elif 'rideName' in item:
                ride_names.append(item['rideName'])
            # Add any other potential attribute names here
        
        logger.info(f"Extracted {len(ride_names)} ride names")
        
        # Create the JSON response
        result = {
            "status": "success",
            "count": len(ride_names),
            "rides": ride_names
        }
        
        return result
    
    except ClientError as e:
        # Handle AWS-specific errors
        logger.error(f"AWS error: {e}")
        error_result = {
            "status": "error",
            "message": str(e),
            "error_code": e.response['Error']['Code'] if 'Error' in e.response else "Unknown"
        }
        return error_result
    except Exception as e:
        # Handle any other errors
        logger.error(f"General error: {e}")
        error_result = {
            "status": "error",
            "message": str(e)
        }
        return error_result