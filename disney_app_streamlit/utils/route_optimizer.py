import requests
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def optimize_routes(latitude, longitude, ride_ids):
    """
    Calls the route optimization API to get the optimal route.
    
    Args:
        latitude (float): User's latitude
        longitude (float): User's longitude
        ride_ids (list): List of ride IDs to include in the route
        
    Returns:
        dict: API response or error information
    """
    try:
        logger.info(f"Optimizing routes for {len(ride_ids)} rides")
        
        # API endpoint
        url = "https://rg1uo7bmxd.execute-api.us-west-2.amazonaws.com/Optimize-Routes"
        
        # Prepare request payload
        payload = {
            "latitude": latitude,
            "longitude": longitude,
            "rideIds": ride_ids
        }
        
        # Set headers
        headers = {
            "Content-Type": "application/json"
        }
        
        # Make the API call
        logger.info(f"Calling API with payload: {payload}")
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        # Check if the request was successful
        if response.status_code == 200:
            logger.info("API call successful")
            return {
                "status": "success",
                "data": response.json()
            }
        else:
            logger.error(f"API call failed with status code {response.status_code}")
            return {
                "status": "error",
                "message": f"API call failed with status code {response.status_code}",
                "details": response.text
            }
            
    except requests.RequestException as e:
        logger.error(f"Request error: {e}")
        return {
            "status": "error",
            "message": f"Request error: {str(e)}"
        }
    except Exception as e:
        logger.error(f"Error optimizing routes: {e}")
        return {
            "status": "error",
            "message": f"Error: {str(e)}"
        }