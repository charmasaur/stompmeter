import datetime

def calculate(
        date,
        standing,
        walking,
        running,
        cycling,
        swimming,
        stretching,
        eatingcarbs):
    hours_on_feet = standing + walking + running
    hours_exercising = walking + running + cycling + swimming
    training_points = (min(hours_on_feet, hours_exercising) + stretching) * 10

    # If it's near trailwalker then add the eating points
    if date >= datetime.date(2017, 9, 18) and date <= datetime.date(2017, 9, 21):
        training_points += eatingcarbs * 10

    return training_points

def is_team_victorweek(week_end_date, team_points):
    # Use threshold of 100 for 23/4/2017 and earlier.
    if week_end_date <= datetime.date(2017, 4, 23):
        return min(team_points) >= 100
    # Use threshold of 130 for 10/9/2017 and earlier.
    if week_end_date <= datetime.date(2017, 9, 10):
        return min(team_points) >= 130
    # Otherwise use 140.
    return min(team_points) >= 140
