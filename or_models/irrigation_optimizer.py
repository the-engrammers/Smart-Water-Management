import pulp


def optimize_irrigation(crop_need, water_available):

    model = pulp.LpProblem("IrrigationOptimization", pulp.LpMinimize)

    irrigation = pulp.LpVariable("irrigation", lowBound=0)

    # objective: minimize water usage
    model += irrigation

    # crop must receive enough water
    model += irrigation >= crop_need

    # cannot exceed available water
    model += irrigation <= water_available

    model.solve()

    return irrigation.value()