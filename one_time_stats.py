import stats_handler2

for x in range(1, 649):
    stats_handler2.log_event('page_load')

stats_handler2.create_database()