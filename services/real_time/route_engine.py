#the func Calculates travel time, service time, and load for moving to a delivery group

def calculate_transition(current_location, group, google_maps_service):
    """
    Computes the cost of moving from current location to a delivery group.

    Includes:
    - Travel time from current location to group center
    - Service time at the center
    - Total meals in the group
    """

    center = group.center

    travel_result = google_maps_service.travel_time_between_points(
        current_location.lat,
        current_location.lng,
        center.lat,
        center.lng
    )

    if "error" in travel_result:
        return None

    travel_time = travel_result["duration_min"]
    distance = travel_result["distance_km"]

    service_time = group.service_time
    meals = group.total_meals

    total_time = travel_time + service_time

    return {
        "travel_time": travel_time,
        "service_time": service_time,
        "total_time": total_time,
        "distance": distance,
        "meals": meals,
        "center_id": center.id
    }




#the func Checks whether moving to a delivery group is valid under time, capacity, and assignment constraints

def is_valid_transition(state, transition, group):
    """
    Validates if the next move is allowed in the VRP search.

    Checks:
    - Time constraint (within volunteer availability)
    - Capacity constraint (vehicle limit)
    - Group not already assigned in current route
    """

    if transition is None:
        return False

    # Time constraint
    if state["current_time"] + transition["total_time"] > state["max_time"]:
        return False

    # Capacity constraint
    if state["current_meals"] + transition["meals"] > state["max_meals"]:
        return False

    # Already used in this route
    if group.id in state["assigned_groups"]:
        return False

    return True




#the func Creates a new search state after selecting a delivery group and updates route, time, and capacity

def create_new_state(state, group, transition):
    """
    Builds a new VRP state after adding a delivery group.

    Updates:
    - Current location (moves to group end location)
    - Current time (adds travel + service time)
    - Current meals load
    - Route history
    - Assigned groups (local tracking)
    """

    return {
        "current_location": group.end_location,
        "current_time": state["current_time"] + transition["total_time"],
        "current_meals": state["current_meals"] + transition["meals"],
        "max_time": state["max_time"],
        "max_meals": state["max_meals"],

        # route history
        "route": state["route"] + [group.id],

        # local assignment tracking
        "assigned_groups": state["assigned_groups"].copy() | {group.id}
    }


#the func Expands a given state by generating all possible next valid states from available groups

def expand_state(state, groups, google_maps_service):
    """
    Generates all possible next VRP states from the current state.

    For each group:
    - Skips already assigned groups
    - Calculates transition cost
    - Validates constraints
    - Creates a new state if valid
    """

    new_states = []

    for group in groups:

        # skip groups already used in this route
        if group.id in state["assigned_groups"]:
            continue

        transition = calculate_transition(
            state["current_location"],
            group,
            google_maps_service
        )

        if not is_valid_transition(state, transition, group):
            continue

        new_state = create_new_state(state, group, transition)

        new_states.append(new_state)

    return new_states