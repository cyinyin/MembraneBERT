import datetime

today = datetime.datetime.today()
year = today.year
print(year, type(year))

yy = "33d"
try:
    print(int(yy), )
except ValueError:
    pass
finally:
    yy = 10
print(yy, type(yy))
