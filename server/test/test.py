from datetime import datetime
dt_obj = datetime.strptime('20.12.2016 09:34:43,76',
                           '%d.%m.%Y %H:%M:%S,%f')
millisec = dt_obj.timestamp() * 1000

print(millisec)