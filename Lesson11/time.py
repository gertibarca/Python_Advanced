import datetime


timeObj = datetime.time(12, 30, 45, 651651)


print(timeObj.hour)
print(timeObj.minute)
print(timeObj.second)
print(timeObj.microsecond)

dateobj = datetime.date(2010, 1, 1)

print(dateobj.year)
print(dateobj.month)
print(dateobj.day)

specificDate = datetime.datetime(2010, 1, 1, 4, 25, 54, 54545)
foramtimiiDates = specificDate.strftime("%m%Y%d")
print(foramtimiiDates)

utc = datetime.datetime.now(datetime.timezone.utc)
print(utc)

currenttime = datetime.timedelta(hours=3)

costumTime = utc.replace(tzinfo=datetime.timezone(currenttime))
print(costumTime)
