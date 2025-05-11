# ------------------------------------------------------------------------------
# file: optimize_route.py
# ------------------------------------------------------------------------------

import os
import time
import boto3
from decimal import Decimal
from itertools import combinations

# AWS clients
dynamodb = boto3.resource("dynamodb")
table     = dynamodb.Table(os.getenv("RIDES_TABLE", "rideMetaData"))

location  = boto3.client("location")               # Amazon Location Service

# ------------------------------------------------------------------------------
# 1. Data access helpers
# ------------------------------------------------------------------------------

def load_rides(ride_ids):
    """Batch-read ride metadata + current wait from DynamoDB."""
    keys = [{"rideId": rid} for rid in ride_ids]
    response = table.batch_get_items(RequestItems={
        table.name: {"Keys": keys}
    })
    items = response["Responses"][table.name]
    # Decimal → float
    for it in items:
        it["lat"]      = float(it["lat"])
        it["lon"]      = float(it["lon"])
        it["waitTime"] = int(it.get("waitTime", 0))
    # Preserve original order supplied by the user
    by_id = {it["rideId"]: it for it in items}
    return [by_id[rid] for rid in ride_ids if rid in by_id]

def minutes_from_seconds(seconds):
    return seconds / 60.0         # Amazon Location returns seconds

def build_distance_matrix(start, rides):
    """Return an (n+1)×(n+1) walking-time matrix in minutes.
       Row/col 0 == guest position; 1..n == rides in order."""
    coords = [start] + [(r["lat"], r["lon"]) for r in rides]
    
    # Amazon Location accepts up to 350×350 pairs in one request
    result = location.calculate_route_matrix(
        CalculatorName="DisneyWalk",
        DeparturePositions=[coords[0]],
        DestinationPositions=coords,
        TravelMode="Walking"
    )

    n = len(coords)
    D = [[0.0] * n for _ in range(n)]
    
    # result["RouteMatrix"][i][j] = seconds from i→j, NaN if not routable
    for i, row in enumerate(result["RouteMatrix"]):
        for j, cell in enumerate(row):
            D[i][j] = minutes_from_seconds(cell["DurationSeconds"])
    return D

# ------------------------------------------------------------------------------
# 2. Held–Karp exact TSP with service-time weights
# ------------------------------------------------------------------------------

def held_karp(D, waits):
    """
    Optimal order through all rides using DP over subsets.
    D  :: (n+1)×(n+1) walk-time matrix, row/col 0 is the guest start.
    waits :: length n+1, waits[0]==0, waits[i] == queue minutes at ride i.
    Returns (best_order, best_total_time)
    """
    n = len(waits) - 1            # rides only
    FULL = 1 << n                 # bit mask size

    # dp[mask][i] = best time to reach set 'mask', ending at ride i (1-based)
    dp   = [[float("inf")] * (n + 1) for _ in range(FULL)]
    prev = [[None] * (n + 1)       for _ in range(FULL)]

    # Initialise: go from start (0) straight to each ride i
    for i in range(1, n + 1):
        mask = 1 << (i - 1)
        dp[mask][i] = D[0][i] + waits[i]

    # Main DP
    for size in range(2, n + 1):                  # subset sizes
        for subset in combinations(range(1, n + 1), size):
            mask = sum(1 << (i - 1) for i in subset)
            for j in subset:                      # j = last ride in subset
                prev_mask = mask ^ (1 << (j - 1))
                best = float("inf"); best_k = None
                for k in subset:                  # k = ride before j
                    if k == j: continue
                    cand = dp[prev_mask][k] + D[k][j] + waits[j]
                    if cand < best:
                        best = cand; best_k = k
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

# ------------------------------------------------------------------------------
# 3. Public function
# ------------------------------------------------------------------------------

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

    ordered_rides = [rides[i - 1] for i in order_idx]   # shift back (1-based)

    return {
        "orderedRides": [
            {
                "rideId": r["rideId"],
                "name":   r["name"],
                "lat":    r["lat"],
                "lon":    r["lon"],
                "waitTime": r["waitTime"]
            }
            for r in ordered_rides
        ],
        "totalTimeMinutes": round(total, 1)
    }

# ------------------------------------------------------------------------------
# Example local test -----------------------------------------------------------
if __name__ == "__main__":
    # Hard-code sample input for a quick test
    start_lat, start_lon = 33.8101, -117.9190
    rides = [
        "c23af6ba-8515-406a-8a48-d0818ba0bfc9",  # Peter Pan's Flight
        "9d401ad3-49b2-469f-ac73-93eb429428fb",  # Mr. Toad's Wild Ride
        "90ee50d4-7cc9-4824-b29d-2aac801acc29"   # Pinocchio's Daring Journey
    ]
    print(optimize_route(start_lat, start_lon, rides))