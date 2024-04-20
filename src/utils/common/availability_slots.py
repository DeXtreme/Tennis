# BEGIN: 7d8f6a4c7b3e
import calendar
import datetime
from datetime import time, date as _date, timedelta
from typing import Dict, List, Tuple, Union

import pendulum
from django.db.models import Q

from user.models import ProfessionalProfile
from utils.enums import CalendarStatusChoices, AvailabilityTimeFrameChoices


class InvalidInputException(Exception):
    pass


class Availability:
    @classmethod
    def get_availability_slots(
            cls,
            date: _date,
            booked_slots: List[Tuple[time, time]],
            availability_slots: List[Tuple[time, time]],
            timezone: str = "Africa/Accra",
            buffer_minutes: int = 1,
    ) -> List[Dict[str, Union[_date, str, time, time]]]:
        """
        Determine the availability of slots for a given date and time zone based on preset availability slots and bookings.
        Given a list of occupied slots, a date of interest, and timezone. Returns a list of free slots. on the given date in the given timezone.

        Args:
        - date: The date of interest
        - booked_slots: (List[Tuple[datetime, datetime]]): A list of booked slots, where each tuple contains the start time and end time of the slot.
        - availability_slots: (List[Tuple[datetime, datetime]]): A list of availability slots, where each tuple contains the start time and end time of the slot.
        - timezone (str, optional): The time zone to use for the availability window. Defaults to "Africa/Accra".
        - buffer_minutes (int, optional): The number of minutes to buffer the availability window by. Defaults to 1.
        Returns:
            list of dict: Each dict contains date, weekday, start_time, and end_time.
        - List[Dict[datetime.date, str, datetime.time, datetime.time]
        """

        if not isinstance(buffer_minutes, int) or buffer_minutes < 0:
            raise InvalidInputException("Buffer time must be a positive integer")
        if not isinstance(date, _date):
            raise InvalidInputException(
                "Invalid input type for 'date'. Expected datetime.date"
            )
        if not isinstance(booked_slots, list) or not all(
                isinstance(slot, tuple) and len(slot) == 2 for slot in booked_slots
        ):
            raise InvalidInputException(
                "Invalid input type or structure for 'booked_slots'. Expected List[Tuple[datetime.time, datetime.time]]."
            )
        if not isinstance(availability_slots, list) or not all(
                isinstance(slot, tuple) and len(slot) == 2 for slot in availability_slots
        ):
            raise InvalidInputException(
                f"Invalid input structure for 'availability_slots'. Expected List[Tuple[datetime.time, datetime.time]]. got {availability_slots}"
            )
        if not isinstance(timezone, str):
            raise InvalidInputException(
                "Invalid input type for 'timezone'. Expected str."
            )
        if not availability_slots:
            return []
        if not booked_slots:
            # If no booked slots, return availability slots as is
            return cls.format_output_list(availability_slots, date=date)

        date_with_timezone = pendulum.datetime(
            date.year, date.month, date.day
        ).in_timezone(timezone)

        start_of_day = date_with_timezone.start_of("day")
        end_of_day = start_of_day.add(days=1).subtract(seconds=1)

        availability_slots = [
            (
                pendulum.Time(start.hour, start.minute, start.second),
                pendulum.Time(end.hour, end.minute, end.second),
            )
            for start, end in availability_slots
        ]
        booked_slots = [
            (
                pendulum.Time(start.hour, start.minute, start.second),
                pendulum.Time(end.hour, end.minute, end.second),
            )
            for start, end in booked_slots
        ]

        booked_slots.sort(key=lambda x: x[0])
        availability_slots.sort(key=lambda x: x[0])

        free_slots = []
        available_slots = []

        effective_buffer = lambda: buffer_minutes if len(available_slots) else 0

        # Handle case when the first booked slot starts after the beginning of the day
        if booked_slots[0][0] > start_of_day.time():
            free_slots.append(
                dict(start_time=start_of_day.time(), end_time=booked_slots[0][0])
            )

        # Check and append free slots between booked slots
        for i in range(len(booked_slots) - 1):
            start, end = booked_slots[i][0], booked_slots[i][1]
            next_start, next_end = booked_slots[i + 1][0], booked_slots[i + 1][1]

            if next_start > end:
                free_slots.append(
                    dict(
                        start_time=end,
                        end_time=next_start,
                    )
                )

        # Handle case when the last booked slot ends before the end of the day
        if booked_slots[-1][1] < end_of_day.time():
            free_slots.append(
                dict(start_time=booked_slots[-1][1], end_time=end_of_day.time())
            )

        # Check if free slots are within the availability slots
        for free_start, free_end in [
            (item["start_time"], item["end_time"]) for item in free_slots
        ]:
            for avail_start, avail_end in availability_slots:
                if free_end < avail_start:
                    # Starts outside the availability slot
                    continue

                if (
                        free_start <= avail_start
                        and free_end <= avail_end
                        and free_end != avail_start
                ):
                    # Runs into an availability slot, truncate the start
                    available_slots.append(
                        dict(
                            date=date_with_timezone.format("YYYY-MM-DD"),
                            day=date_with_timezone.format("dddd"),
                            start_time=avail_start.add(
                                minutes=effective_buffer()
                            ).format("HH:mm:ss"),
                            end_time=free_end.format("HH:mm:ss"),
                        )
                    )
                    continue

                if free_start >= avail_start and free_end <= avail_end:
                    # Starts and ends within availability slot, append to available slots as is
                    available_slots.append(
                        dict(
                            date=date_with_timezone.format("YYYY-MM-DD"),
                            day=date_with_timezone.format("dddd"),
                            start_time=free_start.add(
                                minutes=effective_buffer()
                            ).format("HH:mm:ss"),
                            end_time=free_end.format("HH:mm:ss"),
                        )
                    )
                    continue

                if (
                        not free_start >= avail_end
                        and free_start >= avail_start <= free_end
                        and avail_end <= free_end
                ):
                    # Start in availability and ends outside availability slot, truncate the end
                    available_slots.append(dict(
                        date=date_with_timezone.format('YYYY-MM-DD'),
                        day=date_with_timezone.format('dddd'),
                        start_time=free_start.add(minutes=effective_buffer()).format('HH:mm:ss'),
                        end_time=avail_end.format('HH:mm:ss')
                    ))
        return available_slots

    @classmethod
    def get_professional_availability_slots(cls,
                                            professional,
                                            month: int = None,
                                            week: int = None,
                                            date: datetime.date = None,
                                            time_frame: AvailabilityTimeFrameChoices = None,
                                            timezone: str = "Africa/Accra",
                                            buffer_minutes: int = 1) -> List[
        Dict[str, Union[datetime.date, str, time, time]]]:

        filtered_booked_slots = professional.calendar.all()
        availability_slots = professional.availability.all()
        dates = cls.dates(date, time_frame, week, month)

        booked_slots = filtered_booked_slots.filter(
            start_time__date__in=dates, status=CalendarStatusChoices.SCHEDULED.name,
            start_time__gte=dates[0]
        ).order_by('start_time')

        available_slots = cls.days_available(dates, booked_slots, availability_slots, timezone, buffer_minutes)

        return available_slots

    @classmethod
    def format_output_list(cls, availabilities, date: _date) -> List:
        pd_date = pendulum.date(year=date.year, month=date.month, day=date.day)
        day = pd_date.format("dddd")
        date_string = pd_date.format("YYYY-MM-DD")
        date_of_availability = pd_date.format("YYYY-MM-D")
        if isinstance(availabilities, list):
            return [
                {
                    "start_time": start.strftime("%H:%M:%S"),
                    "end_time": end.strftime("%H:%M:%S"),
                    "day": day,
                    "date": date_string,
                }
                for start, end in availabilities
            ]
        raise InvalidInputException("Invalid input for formatting")

    @classmethod
    def dates(cls, date=None, time_frame=None, week=None, month=None, ):
        if not date:
            date = datetime.date.today()
        start_of_week = date - datetime.timedelta(days=date.weekday())
        dates = [date + datetime.timedelta(days=i) for i in range(7)]

        if time_frame == AvailabilityTimeFrameChoices.WEEK and week is not None:
            raise ValueError("Week and time_frame cannot be used together")
        if time_frame == AvailabilityTimeFrameChoices.MONTH and month is not None:
            raise ValueError("Month and time_frame cannot be used together")

        if time_frame == AvailabilityTimeFrameChoices.WEEK and week is None:
            dates = [date + datetime.timedelta(days=i) for i in range(7)]

        if week is not None and month is None:
            first_day_of_month = datetime.date(date.year, date.month, 1)
            target_week = date + datetime.timedelta(weeks=week - 1)
            dates = [target_week + datetime.timedelta(days=day) for day in range(7)]

        if week is not None and month is not None:
            first_day_of_month = datetime.date(date.year, month, 1)
            target_week = first_day_of_month + datetime.timedelta(weeks=week - 1)
            dates = [target_week + datetime.timedelta(days=day) for day in range(7)]

        if time_frame == AvailabilityTimeFrameChoices.MONTH:
            first_day_of_month = datetime.date(date.year, date.month, 1)
            _, last_day_of_month = calendar.monthrange(date.year, date.month)
            dates = [date + datetime.timedelta(days=i) for i in range(last_day_of_month)]

        if month is not None and week is None:
            first_day_of_month = datetime.date(date.year, month, 1)
            _, last_day_of_month = calendar.monthrange(date.year, month)
            dates = [first_day_of_month + datetime.timedelta(days=i) for i in range(last_day_of_month)]
            dates = [d for d in dates if d >= date]

        if time_frame == AvailabilityTimeFrameChoices.MONTH and week is not None:
            first_day_of_month = datetime.date(date.year, date.month, 1)
            target_week = first_day_of_month + datetime.timedelta(weeks=week - 1)
            dates = [target_week + datetime.timedelta(days=day) for day in range(7)]

        return dates


    @classmethod
    def days_available(cls, dates, booked_slots, availability_slots, timezone, buffer_minutes):
        available_slots = []
        if not availability_slots:
            return available_slots

        for date in dates:
            new_availability_slots = []
            date_with_timezone = pendulum.datetime(date.year, date.month, date.day).in_timezone(timezone)
            start_of_day = date_with_timezone.start_of('day')
            end_of_day = start_of_day.add(days=1).subtract(seconds=1)


            availability_slot = availability_slots.filter(
                Q(day=date.strftime('%A').upper()) | Q(date__month=date.month, date__day=date.day),

            )

            for availability in availability_slot:
                if availability.day and availability.day == date.strftime('%A').upper():
                    new_availability_slots.append(
                        (date, availability.opening_time, availability.closing_time))

                if availability.date:
                    new_availability_slots.append(
                        (pendulum.datetime(availability.date.year, availability.date.month, availability.date.day).in_timezone(timezone), availability.opening_time, availability.closing_time))


            slot_available = [(pendulum.Time(start.hour, start.minute, start.second),
                               pendulum.Time(end.hour, end.minute, end.second)) for day, start, end in
                              new_availability_slots]

            slot_available.sort(key=lambda x: x[0])

            free_slots = []
            effective_buffer = lambda: buffer_minutes if len(available_slots) else 0



            if not booked_slots:
                for date, opening, closing in new_availability_slots:

                    available_slots.append(
                        dict(
                            date=datetime.date(date.year, date.month, date.day),
                            day=date.strftime('%A'),
                            start_time=opening,
                            end_time=closing
                        )
                    )
            # Handle case when the first booked slot starts after the beginning of the day
            else:
                booking_slot = booked_slots.filter(
                    start_time__date=date
                ).order_by('start_time').values_list("start_time", "end_time")

                slots_booked = [(pendulum.Time(start.hour, start.minute, start.second),
                                 pendulum.Time(end.hour, end.minute, end.second)) for start, end in
                                [(start_time.time(), end_time.time()) for start_time, end_time in booking_slot]]

                slots_booked.sort(key=lambda x: x[0])

                available, free=cls.booking_free_period(slots_booked,new_availability_slots,start_of_day, end_of_day)
                free_slots.extend(free)
                available_slots.extend(available)

            # Check if free slots are within the availability slots
            get_available_slots=cls.free_slot_availability( free_slots, slot_available, date_with_timezone, effective_buffer)
            available_slots.extend(get_available_slots)
        return available_slots


    @classmethod
    def booking_free_period(cls, slots_booked, new_availability_slots, start_of_day, end_of_day):
        available_slots=[]
        free_slots=[]
        if not slots_booked:
            for date, opening, closing in new_availability_slots:
                available_slots.append(
                    dict(
                        date=datetime.date(date.year, date.month, date.day),
                        day=date.strftime('%A'),
                        start_time=opening,
                        end_time=closing
                    )
                )
        if slots_booked != [] and slots_booked[0][0] > start_of_day.time():
            free_slots.append(dict(
                start_time=start_of_day.time(),
                end_time=slots_booked[0][0]
            ))

        # Check and append free slots between booked slots

        if slots_booked:

            for i in range(len(slots_booked) - 1):
                start, end = slots_booked[i][0], slots_booked[i][1]
                next_start, next_end = slots_booked[i + 1][0], slots_booked[i + 1][1]
                if next_start > end:
                    free_slots.append(dict(
                        start_time=end,
                        end_time=next_start,
                    ))

        # Handle case when the last booked slot ends before the end of the day
        if slots_booked != [] and slots_booked[-1][1] < end_of_day.time():
            free_slots.append(dict(
                start_time=slots_booked[-1][1],
                end_time=end_of_day.time()
            ))
        return available_slots, free_slots

    @classmethod
    def free_slot_availability(cls, free_slots, slot_available,date_with_timezone,effective_buffer):
        available_slots=[]
        for free_start, free_end in [(item["start_time"], item["end_time"]) for item in free_slots]:
            for avail_start, avail_end in slot_available:
                if free_end < avail_start:
                    # Starts outside the availability slot
                    continue

                if free_start <= avail_start and free_end <= avail_end and free_end != avail_start:
                    # Runs into an availability slot, truncate the start
                    # [(Time(10, 30, 30), Time(22, 30, 30))]
                    # [(Time(19, 30, 30), Time(22, 30, 30))]

                    available_slots.append(dict(
                        date=datetime.date(date_with_timezone.year, date_with_timezone.month, date_with_timezone.day),
                        day=date_with_timezone.format('dddd'),
                        start_time=avail_start.add(minutes=effective_buffer()),
                        end_time=free_end
                    ))
                    continue

                if free_start >= avail_start and free_end <= avail_end:
                    # Starts and ends within availability slot, append to available slots as is
                    # [(Time(19, 30, 30), Time(20, 30, 30))]
                    # [(Time(10, 30, 30), Time(22, 30, 30))]
                    available_slots.append(dict(
                        date=datetime.date(date_with_timezone.year, date_with_timezone.month, date_with_timezone.day),
                        day=date_with_timezone.format('dddd'),
                        start_time=free_start.add(minutes=effective_buffer()),
                        end_time=free_end
                    ))
                    continue

                if not free_start >= avail_end and free_start >= avail_start and avail_start <= free_end and avail_end <= free_end:
                    # Start in availability and ends outside availability slot, truncate the end
                    # [(Time(19, 30, 30), Time(20, 30, 30))]
                    # [(Time(17, 30, 30), Time(18, 30, 30))]

                    available_slots.append(dict(
                        date=datetime.date(date_with_timezone.year, date_with_timezone.month, date_with_timezone.day),
                        day=date_with_timezone.format('dddd'),
                        start_time=free_start.add(minutes=effective_buffer()),
                        end_time=avail_end
                    ))

                if not free_start >= avail_end and free_start <= avail_start <= free_end and avail_end <= free_end:
                    # Start before in availability and ends before availability
                    # [(Time(8, 30, 30), Time(23, 30, 30))]
                    # [(Time(10, 30, 30), Time(22, 30, 30))]
                    available_slots.append(dict(
                        date=datetime.date(date_with_timezone.year, date_with_timezone.month, date_with_timezone.day),
                        day=date_with_timezone.format('dddd'),
                        start_time=avail_start,
                        end_time=avail_end
                    ))
        return available_slots
