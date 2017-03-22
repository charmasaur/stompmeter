def calculate(
        standing,
        walking,
        running,
        cycling,
        swimming,
        stretching):
    hours_on_feet = standing + walking + running
    hours_exercising = walking + running + cycling + swimming
    training_points = (min(hours_on_feet, hours_exercising) + stretching) * 10

    return training_points

def is_team_victorweek(team_points):
    return min(team_points) >= 100
