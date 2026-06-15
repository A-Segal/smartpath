from services.real_time.route_engine import expand_state

# the func Finds the best possible route for a volunteer using state-space search (VRP optimization)
def search_best_route(initial_state, groups, google_maps_service):
    """
    Main VRP engine that finds the optimal delivery route.

    Objective:
    1. Maximize number of groups served
    2. Minimize total time (tie breaker)
    """

    from collections import deque

    queue = deque()
    queue.append(initial_state)

    best_state = initial_state

    while queue:

        state = queue.popleft()

        next_states = expand_state(state, groups, google_maps_service)

        for new_state in next_states:

            queue.append(new_state)

            # update best solution
            if (
                len(new_state["route"]) > len(best_state["route"])
                or (
                    len(new_state["route"]) == len(best_state["route"])
                    and new_state["current_time"] < best_state["current_time"]
                )
            ):
                best_state = new_state

    return best_state