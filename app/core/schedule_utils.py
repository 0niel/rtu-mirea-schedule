import datetime


class ScheduleUtils:
    @staticmethod
    def get_week(date: datetime.datetime = None) -> int:
        """Возвращает номер учебной недели по дате

        Args:
            date (datetime.datetime, optional): Дата, для которой необходимо получить учебную неделю.
        """
        now = ScheduleUtils.now_date() if date is None else date
        start_date = ScheduleUtils.get_semester_start(date)

        if now.timestamp() < start_date.timestamp():
            return 1

        week = now.isocalendar()[1] - start_date.isocalendar()[1]

        if now.isocalendar()[2] != 0:
            week += 1

        return week

    @staticmethod
    def get_semester_start(date: datetime.datetime = None) -> datetime.datetime:
        """Возвращает дату начала семестра по дате

        Args:
            date (datetime.datetime, optional): Дата для расчёта начала семестра.
        """
        date = ScheduleUtils.now_date() if date is None else date
        if date.month >= 9:
            return ScheduleUtils.get_first_semester()
        else:
            return ScheduleUtils.get_second_semester()

    @staticmethod
    def now_date() -> datetime.datetime:
        moscow_offset = datetime.timezone(datetime.timedelta(hours=3))
        return datetime.datetime.now(moscow_offset)

    @staticmethod
    def get_first_semester() -> datetime.datetime:
        return datetime.datetime(ScheduleUtils.now_date().year, 9, 1)

    @staticmethod
    def get_second_semester() -> datetime.datetime:
        return datetime.datetime(ScheduleUtils.now_date().year, 2, 9)
