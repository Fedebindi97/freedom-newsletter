import datetime


today = datetime.datetime.today().strftime('%Y-%m-%d')
today_minus_seven = (datetime.datetime.today() - datetime.timedelta(days=7)).strftime('%Y-%m-%d')
day_of_week_today = datetime.datetime.now().strftime('%A')
ts = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')