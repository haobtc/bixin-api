import pendulum


def utc_now():
    return pendulum.now('UTC')
