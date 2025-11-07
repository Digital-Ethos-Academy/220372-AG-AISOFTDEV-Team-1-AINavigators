"""Reporting utilities shared across analytics endpoints."""

from __future__ import annotations

import calendar
from datetime import date, timedelta
from typing import Dict, List, Mapping, Sequence, Tuple


def standard_month_hours(year: int, month: int) -> int:
    """Return the number of working hours in a month assuming 8h weekdays."""

    cal = calendar.Calendar()
    business_days = sum(
        1
        for day, weekday in cal.itermonthdays2(year, month)
        if day != 0 and weekday < 5
    )
    return business_days * 8


def month_label(year: int, month: int) -> str:
    """Returns a short label such as 'Jan 2025'."""

    return f"{calendar.month_abbr[month]} {year}"


def normalize_month(year: int, month: int) -> Tuple[int, int]:
    """Normalise a month value ensuring 1 <= month <= 12."""

    if month < 1 or month > 12:
        raise ValueError("month must be between 1 and 12")
    return year, month


def iter_months(start: date, end: date) -> List[Tuple[int, int]]:
    """Yield (year, month) pairs from start through end inclusive."""

    if end < start:
        return []

    current = date(start.year, start.month, 1)
    last = date(end.year, end.month, 1)

    months: List[Tuple[int, int]] = []
    while current <= last:
        months.append((current.year, current.month))
        # Move to first day of next month
        if current.month == 12:
            current = date(current.year + 1, 1, 1)
        else:
            current = date(current.year, current.month + 1, 1)
    return months


def add_months(start: date, months: int) -> date:
    """Return a date advanced by the provided number of months (end-of-month safe)."""

    year = start.year + (start.month - 1 + months) // 12
    month = (start.month - 1 + months) % 12 + 1
    day = min(start.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def default_project_end(start: date, sprints: int) -> date:
    """
    Estimate a project end date based on the sprint count (14-day sprints).

    Used as a fallback for burn-down charts when no allocations exist yet.
    """

    total_days = sprints * 14
    return start + timedelta(days=total_days)


MonthKey = Tuple[int, int]


def month_capacity_hours(
    year: int,
    month: int,
    overrides: Mapping[MonthKey, int] | None = None,
) -> int:
    """Return capacity hours for a month, respecting project overrides when provided."""

    if overrides:
        override = overrides.get((year, month))
        if override is not None and override > 0:
            return override

    hours = standard_month_hours(year, month)
    return max(hours, 1)


def planned_hours_distribution(
    total_hours: float,
    month_windows: Sequence[MonthKey],
    overrides: Mapping[MonthKey, int] | None = None,
) -> List[float]:
    """Return a proportional distribution of planned burn hours across months."""

    if not month_windows:
        return []

    capacities = [month_capacity_hours(year, month, overrides) for year, month in month_windows]
    total_capacity = sum(capacities)

    if total_capacity <= 0:
        if not month_windows:
            return []
        total_capacity = len(month_windows)
        capacities = [1 for _ in month_windows]

    scale = total_hours / total_capacity if total_capacity else 0.0
    raw = [capacity * scale for capacity in capacities]
    rounded = [round(value, 2) for value in raw]

    # Adjust final element for rounding drift so totals align
    difference = round(total_hours - sum(rounded), 2)
    if rounded:
        rounded[-1] = round(rounded[-1] + difference, 2)

    return rounded


def build_burn_down_series(
    total_hours: float,
    month_windows: Sequence[MonthKey],
    actual_allocations: Mapping[MonthKey, float],
    overrides: Mapping[MonthKey, int] | None = None,
) -> List[Dict[str, object]]:
    """
    Construct burn-down data points with planned vs. actual trajectories.
    """

    planned_distribution = planned_hours_distribution(
        total_hours, month_windows, overrides
    )

    if len(planned_distribution) < len(month_windows):
        planned_distribution = list(planned_distribution) + [0.0] * (
            len(month_windows) - len(planned_distribution)
        )

    planned_remaining = float(total_hours)
    actual_remaining = float(total_hours)
    series: List[Dict[str, object]] = []

    for index, (month, planned_burn) in enumerate(
        zip(month_windows, planned_distribution), start=1
    ):
        year, month_num = month
        actual_burn = float(actual_allocations.get(month, 0.0))
        planned_remaining = max(planned_remaining - planned_burn, 0.0)
        actual_remaining = max(actual_remaining - actual_burn, 0.0)

        series.append(
            {
                "label": month_label(year, month_num),
                "planned_hours": round(planned_remaining, 2),
                "actual_hours": round(actual_remaining, 2),
                "planned_burn_hours": round(planned_burn, 2),
                "actual_burn_hours": round(actual_burn, 2),
                "capacity_hours": month_capacity_hours(year, month_num, overrides),
                "sprint_index": index,
                "date": date(year, month_num, 1).isoformat(),
            }
        )

    return series

