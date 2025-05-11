import os
import boto3
from decimal import Decimal
from itertools import combinations
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


# AWS clients
dynamodb = boto3.resource("dynamodb")
location = boto3.client("location")


def lambda_handler(event, context):
    """
    AWS Lambda handler function to optimize route between rides

    Expected event format:
    {
        "latitude": float,
        "longitude": float,
        "rideIds": [string]
    }
    """
    try:
        # Check if API Gateway proxy integration was used:
        if "body" in event:
            # The body is a JSON string, so parse it.
            body = json.loads(event["body"])
        else:
            body = event

        # Parse input parameters
        user_lat = float(body.get("latitude", 0))
        user_lon = float(body.get("longitude", 0))
        ride_ids = body.get("rideIds", [])

        # Validate input
        if not ride_ids:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "No ride IDs provided"}),
            }
        if user_lat == 0 or user_lon == 0:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Invalid coordinates"}),
            }

        # Run optimization
        result = optimize_route(user_lat, user_lon, ride_ids)

        return {"statusCode": 200, "body": json.dumps(result, default=float_serializer)}

    except ValueError as e:
        return {"statusCode": 400, "body": json.dumps({"error": str(e)})}
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"Internal server error: {str(e)}"}),
        }


def float_serializer(obj):
    """Helper function to serialize Decimal objects for JSON"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


def load_rides(ride_ids):
    """Batch-read ride metadata + current wait from DynamoDB."""
    table = dynamodb.Table(os.getenv("RIDES_TABLE", "rideMetaData"))
    keys = [{"rideId": rid} for rid in ride_ids]
    response = dynamodb.batch_get_item(RequestItems={table.name: {"Keys": keys}})
    items = response["Responses"][table.name]
    # Decimal → float
    for it in items:
        it["lat"] = float(it["lat"])
        it["lon"] = float(it["lon"])
        it["waitTime"] = int(it.get("waitTime", 0))
    # Preserve original order supplied by the user
    by_id = {it["rideId"]: it for it in items}
    return [by_id[rid] for rid in ride_ids if rid in by_id]


def minutes_from_seconds(seconds):
    return seconds / 60.0  # Amazon Location returns seconds


def build_distance_matrix(start, rides):
    """Return an (n+1)×(n+1) walking-time matrix in minutes.
    Row/col 0 == guest position; 1..n == rides in order."""
    # Amazon Location Service expects [longitude, latitude] format
    coords = [(start[1], start[0])] + [(r["lon"], r["lat"]) for r in rides]

    # Amazon Location accepts up to 350×350 pairs in one request
    result = location.calculate_route_matrix(
        CalculatorName="Disney-Walk-Route-Calculator",
        DeparturePositions=coords[0:1],  # First coordinate as departure
        DestinationPositions=coords,  # All coordinates as destinations
        TravelMode="Walking",
    )

    n = len(coords)
    D = [[0.0] * n for _ in range(n)]

    # result["RouteMatrix"][i][j] = seconds from i→j, NaN if not routable
    for i, row in enumerate(result["RouteMatrix"]):
        for j, cell in enumerate(row):
            D[i][j] = minutes_from_seconds(cell["DurationSeconds"])
    return D


def held_karp(D, waits):
    """
    Optimal order through all rides using DP over subsets.
    D  :: (n+1)×(n+1) walk-time matrix, row/col 0 is the guest start.
    waits :: length n+1, waits[0]==0, waits[i] == queue minutes at ride i.
    Returns (best_order, best_total_time)
    """
    n = len(waits) - 1  # rides only
    FULL = 1 << n  # bit mask size

    # dp[mask][i] = best time to reach set 'mask', ending at ride i (1-based)
    dp = [[float("inf")] * (n + 1) for _ in range(FULL)]
    prev = [[None] * (n + 1) for _ in range(FULL)]

    # Initialise: go from start (0) straight to each ride i
    for i in range(1, n + 1):
        mask = 1 << (i - 1)
        dp[mask][i] = D[0][i] + waits[i]

    # Main DP
    for size in range(2, n + 1):  # subset sizes
        for subset in combinations(range(1, n + 1), size):
            mask = sum(1 << (i - 1) for i in subset)
            for j in subset:  # j = last ride in subset
                prev_mask = mask ^ (1 << (j - 1))
                best = float("inf")
                best_k = None
                for k in subset:  # k = ride before j
                    if k == j:
                        continue
                    cand = dp[prev_mask][k] + D[k][j] + waits[j]
                    if cand < best:
                        best = cand
                        best_k = k
                dp[mask][j] = best
                prev[mask][j] = best_k

    # Close tour: we do **not** return to start, so pick minimal end-ride
    full = FULL - 1
    best_end = min(range(1, n + 1), key=lambda j: dp[full][j])
    best_time = dp[full][best_end]

    # Reconstruct order
    order = []
    mask, j = full, best_end
    while j is not None:
        order.append(j)
        pj = prev[mask][j]
        mask ^= 1 << (j - 1)
        j = pj
    order.reverse()
    return order, best_time


def optimize_route(user_lat, user_lon, ride_ids):
    """
    Parameters
    ----------
    user_lat, user_lon : float  (current guest position)
    ride_ids           : list[str]  (rides the guest wants)

    Returns
    -------
    dict with ordered rides, totalTimeMinutes
    """
    # -- Fetch data ------------------------------------------------------------
    rides = load_rides(ride_ids)
    if len(rides) != len(ride_ids):
        missing = set(ride_ids) - {r["rideId"] for r in rides}
        raise ValueError(f"Ride IDs not found: {missing}")

    # -- Build matrices --------------------------------------------------------
    D = build_distance_matrix((user_lat, user_lon), rides)
    waits = [0.0] + [r["waitTime"] for r in rides]

    # -- Held–Karp -------------------------------------------------------------
    order_idx, total = held_karp(D, waits)

    ordered_rides = [rides[i - 1] for i in order_idx]  # shift back (1-based)

    return {
        "orderedRides": [
            {
                "rideId": r["rideId"],
                "name": r["name"],
                "lat": r["lat"],
                "lon": r["lon"],
                "waitTime": r["waitTime"],
            }
            for r in ordered_rides
        ],
        "totalTimeMinutes": round(total, 1),
    }
