import boto3
import logging
from botocore.exceptions import ClientError

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_dynamodb_connection():
    """
    Test connection to DynamoDB and print table contents
    """
    try:
        # List all available regions for debugging
        logger.info("Available regions:")
        ec2 = boto3.client('ec2')
        regions = [region['RegionName'] for region in ec2.describe_regions()['Regions']]
        logger.info(f"AWS Regions: {regions}")
        
        # Try to connect with explicit region
        logger.info("Attempting to connect to DynamoDB in us-west-2")
        session = boto3.Session(region_name='us-west-2')  # Change this to your region
        dynamodb = session.resource('dynamodb')
        
        # List tables
        client = session.client('dynamodb')
        tables = client.list_tables()
        logger.info(f"Available tables: {tables['TableNames']}")
        
        # Check if our table exists
        if 'rideMetaData' in tables['TableNames']:
            logger.info("rideMetaData table found!")
            
            # Reference the table
            table = dynamodb.Table('rideMetaData')
            
            # Get table info
            table_info = client.describe_table(TableName='rideMetaData')
            logger.info(f"Table info: {table_info}")
            
            # Scan a few items
            logger.info("Scanning table for sample items")
            response = table.scan(Limit=5)
            
            # Print the items
            items = response.get('Items', [])
            logger.info(f"Found {len(items)} sample items")
            
            for i, item in enumerate(items):
                logger.info(f"Item {i+1}: {item}")
                
            return True
        else:
            logger.error("rideMetaData table not found!")
            return False
            
    except ClientError as e:
        logger.error(f"AWS error: {e}")
        return False
    except Exception as e:
        logger.error(f"General error: {e}")
        return False

if __name__ == "__main__":
    success = test_dynamodb_connection()
    if success:
        print("DynamoDB connection test successful!")
    else:
        print("DynamoDB connection test failed!")