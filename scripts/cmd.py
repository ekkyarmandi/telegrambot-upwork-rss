def sec2pass(sec):
    '''
    Converting seconds to Hours and Minute
    :param sec: int -> seconds
    :return timestr: str -> formatted seconds
    '''
    m, _ = divmod(sec, 60)
    if m <= 60:
        if m == 1: return f"{int(m):d} minute ago"
        else: return f"{int(m):d} minutes ago"
    elif m > 1440:
        d, m = divmod(m, 1440)
        return f"{int(d):d} days and {int(m/60):d} hours ago"
    elif m > 60:
        h, m = divmod(m, 60)
        if m == 1: return f"{int(h):d} hours and {int(m):d} minute ago"
        else: return f"{int(h):d} hours and {int(m):d} minutes ago"