async def date_span(start, end, delta):
    current_date = start
    while current_date <= end:
        yield current_date
        current_date += delta
