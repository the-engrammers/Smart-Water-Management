import pulp


def schedule_pump(water_amount, energy_cost):

    model = pulp.LpProblem("PumpSchedule", pulp.LpMinimize)

    pump_hours = pulp.LpVariable("pump_hours", lowBound=0)

    # objective: minimize energy cost
    model += pump_hours * energy_cost

    # pump must provide enough water
    model += pump_hours >= water_amount

    model.solve()

    return pump_hours.value()