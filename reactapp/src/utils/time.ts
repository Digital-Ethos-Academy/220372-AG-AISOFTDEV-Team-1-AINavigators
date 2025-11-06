import dayjs from 'dayjs';
import minMax from 'dayjs/plugin/minMax';
import type { MonthlyHourOverride, Project } from '../types/api';
dayjs.extend(minMax)
export interface TimelineMonth {
  year: number;
  month: number;
  label: string;
  start: dayjs.Dayjs;
}

export interface TimelineSprint {
  index: number;
  label: string;
  start: dayjs.Dayjs;
  end: dayjs.Dayjs;
  year: number;
  month: number;
}

export function buildMonthlyTimeline(project: Project, horizonInMonths = 12): TimelineMonth[] {
  const start = dayjs(project.start_date).startOf('month');
  const months: TimelineMonth[] = [];

  const totalDays = project.sprints * 14;
  const projectedEnd = dayjs(project.start_date).add(totalDays, 'day');
  const endMonth = dayjs.max(start.add(horizonInMonths - 1, 'month'), projectedEnd).startOf('month');

  let cursor = start;
  while (cursor.isBefore(endMonth) || cursor.isSame(endMonth)) {
    months.push({
      year: cursor.year(),
      month: cursor.month() + 1,
      label: cursor.format('MMM YYYY'),
      start: cursor
    });
    cursor = cursor.add(1, 'month');
  }

  return months;
}

export function buildSprintTimeline(project: Project): TimelineSprint[] {
  const start = dayjs(project.start_date).startOf('day');
  const sprints: TimelineSprint[] = [];

  for (let i = 0; i < project.sprints; i += 1) {
    const sprintStart = start.add(i * 14, 'day');
    const sprintEnd = sprintStart.add(13, 'day');
    sprints.push({
      index: i + 1,
      label: `Sprint ${i + 1}`,
      start: sprintStart,
      end: sprintEnd,
      year: sprintStart.year(),
      month: sprintStart.month() + 1
    });
  }

  return sprints;
}

export function countBusinessDays(year: number, month: number): number {
  const date = new Date(year, month - 1, 1);
  const end = new Date(year, month, 0);
  let businessDays = 0;

  while (date <= end) {
    const day = date.getDay();
    if (day !== 0 && day !== 6) {
      businessDays += 1;
    }
    date.setDate(date.getDate() + 1);
  }

  return businessDays;
}

export function getMonthlyWorkHours(
  year: number,
  month: number,
  overrides: MonthlyHourOverride[]
): number {
  const override = overrides.find((o) => o.year === year && o.month === month);
  if (override) {
    return override.overridden_hours;
  }

  const businessDays = countBusinessDays(year, month);
  return businessDays * 8;
}

