import datetime

def calculate(
        standing,
        walking,
        running,
        cycling,
        swimming,
        stretching):
    hours_on_feet = standing + walking + running
    hours_exercising = walking + running + cycling + swimming
    stretching_hours = min(stretching,hours_exercising/10)
    training_points = (min(hours_on_feet, hours_exercising) + stretching_hours) * 10

    return training_points

def is_team_victorweek(week_end_date, team_points):
    # Use threshold of 100 for 23/4/2017 and earlier.
    if week_end_date <= datetime.date(2017, 4, 23):
        return min(team_points) >= 100
    # Otherwise use 140.
    return min(team_points) >= 140
