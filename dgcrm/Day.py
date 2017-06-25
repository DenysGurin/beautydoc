import operator

from datetime import datetime, timedelta, timezone, date, time

class Day(object):

    def update_event(self, event):
        event_start = event.data_time
        event_end = event.data_time + timedelta(hours=event.duration.hour, minutes=event.duration.minute)
        return event_start, event_end, True

    def create_period(self):
        return Period()

    def time_periods(self):
        period_list = {}
        event_list = list(self.event_list)
        print(event_list)
        start_perion = self.start_day
        end_periond = start_perion + timedelta(minutes=30)
        to_update = False
        if len(event_list) > 0:
            event_start, event_end, to_update = Day.update_event(self, event_list[0])


        while start_perion < self.end_day:
            # print(start_perion, end_periond, event_list[0].data_time, event_list[0].data_time >= start_perion, event_list[0].data_time < end_periond)
            if len(event_list) > 0:
                if event_list[0].data_time >= start_perion and event_list[0].data_time < end_periond: 
                    to_update = False
                    if not to_update:
                        event_start, event_end, to_update = Day.update_event(self, event_list[0])
                    period_list[str(start_perion)] = event_list.pop(0)
                    start_perion += timedelta(minutes=30)
                    end_periond += timedelta(minutes=30)
                    
                elif event_start < start_perion and event_end > end_periond:
                    start_perion += timedelta(minutes=30)
                    end_periond += timedelta(minutes=30)

                else:
                    if not to_update:
                        event_start, event_end, to_update = Day.update_event(self, event_list[0])
                    period_list[str(start_perion)] = None
                    start_perion += timedelta(minutes=30)
                    end_periond += timedelta(minutes=30)
            else:
                period_list[str(start_perion)] = None
                start_perion += timedelta(minutes=30)
                end_periond += timedelta(minutes=30)
            print(start_perion, end_periond)
        print(period_list.values())
        return period_list

    def __init__(self, event_list=None, start_day=time(9, 0, 0), end_day=time(20, 0, 0)):
        self.event_list = event_list
        self.day_date = datetime.date(datetime.now(timezone.utc))
        self.start_day = datetime.combine(self.day_date, start_day)
        self.end_day = datetime.combine(self.day_date, end_day)
        print(self.start_day, self.end_day)
        self.time_periods = Day.time_periods(self)
        self.sorted_time_periods = sorted(self.time_periods.items(), key=operator.itemgetter(0))
        

    def getPeriods(self):
        return self.time_periods

    def __iter__(self):
        return iter(self.sorted_time_periods)