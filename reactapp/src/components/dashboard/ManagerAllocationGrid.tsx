import { useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Calendar, Loader2 } from 'lucide-react';
import { fetchManagerAllocations, type ManagerAllocationsParams } from '../../api/reports';
import { Card } from '../common';
import DateRangeModal from './DateRangeModal';

interface ManagerAllocationGridProps {
  managerId: number;
}

export default function ManagerAllocationGrid({ managerId }: ManagerAllocationGridProps) {
  const today = new Date();
  const currentYear = today.getFullYear();
  const currentMonth = today.getMonth() + 1;

  // Default: current month + 12 months forward
  const [startYear, setStartYear] = useState(currentYear);
  const [startMonth, setStartMonth] = useState(currentMonth);
  
  // Calculate end date 12 months forward
  const calculateEndDate = () => {
    const totalMonths = currentMonth + 11; // 12 months forward (current + 11)
    const yearsToAdd = Math.floor(totalMonths / 12);
    const finalMonth = totalMonths % 12 || 12; // If 0, use 12 (December)
    return { year: currentYear + yearsToAdd, month: finalMonth };
  };
  
  const defaultEndDate = calculateEndDate();
  const [endYear, setEndYear] = useState(defaultEndDate.year);
  const [endMonth, setEndMonth] = useState(defaultEndDate.month);
  const [isDateRangeModalOpen, setIsDateRangeModalOpen] = useState(false);

  const params: ManagerAllocationsParams = {
    managerId,
    startYear,
    startMonth,
    endYear,
    endMonth
  };

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['manager-allocations', managerId, startYear, startMonth, endYear, endMonth],
    queryFn: () => fetchManagerAllocations(params),
    staleTime: 30_000,
    enabled: !!managerId
  });

  // Generate list of months for the date range
  const months = useMemo(() => {
    const result: Array<{ year: number; month: number; label: string }> = [];
    let year = startYear;
    let month = startMonth;

    while (year < endYear || (year === endYear && month <= endMonth)) {
      const date = new Date(year, month - 1, 1);
      const label = date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
      result.push({ year, month, label });

      month++;
      if (month > 12) {
        month = 1;
        year++;
      }
    }

    return result;
  }, [startYear, startMonth, endYear, endMonth]);

  const handleDateRangeUpdate = (data: { startYear: number; startMonth: number; endYear: number; endMonth: number }) => {
    setStartYear(data.startYear);
    setStartMonth(data.startMonth);
    setEndYear(data.endYear);
    setEndMonth(data.endMonth);
  };

  if (isLoading) {
    return (
      <Card>
        <div className="flex items-center justify-center py-12 text-sm text-slate-500">
          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          Loading allocation rollup...
        </div>
      </Card>
    );
  }

  if (isError) {
    return (
      <Card className="border-red-200 bg-red-50">
        <p className="text-sm text-red-600">
          Failed to load manager allocations: {error instanceof Error ? error.message : 'Unknown error'}
        </p>
      </Card>
    );
  }

  if (!data || data.employees.length === 0) {
    return (
      <Card>
        <p className="text-center text-sm text-slate-500 py-8">
          No employee allocations found for the selected date range.
        </p>
      </Card>
    );
  }

  return (
    <Card>
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-lg font-semibold text-slate-900">Employee Allocation Rollup</h3>
        <button
          type="button"
          onClick={() => setIsDateRangeModalOpen(true)}
          className="inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 transition hover:border-blue-200 hover:text-blue-600"
        >
          <Calendar className="h-3.5 w-3.5" />
          Change Date Range
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full border-collapse text-sm">
          <thead>
            <tr className="border-b border-slate-200 bg-slate-50">
              <th className="sticky left-0 z-10 bg-slate-50 px-4 py-3 text-left font-semibold text-slate-700">
                Employee
              </th>
              <th className="px-4 py-3 text-right font-semibold text-slate-700">
                Total Funded
              </th>
              {months.map((m) => (
                <th key={`${m.year}-${m.month}`} className="px-4 py-3 text-right font-semibold text-slate-700">
                  {m.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.employees.map((employee) => (
              <tr key={employee.employee_id} className="border-b border-slate-100 hover:bg-slate-50">
                <td className="sticky left-0 z-10 bg-white px-4 py-3 font-medium text-slate-900 hover:bg-slate-50">
                  {employee.employee_name}
                </td>
                <td className="px-4 py-3 text-right font-semibold text-slate-700">
                  {employee.total_funded_hours} hrs
                </td>
                {months.map((m) => {
                  const monthData = employee.monthly_totals.find(
                    (mt) => mt.year === m.year && mt.month === m.month
                  );

                  if (!monthData || monthData.total_hours === 0) {
                    return (
                      <td key={`${m.year}-${m.month}`} className="px-4 py-3 text-right text-slate-400">
                        -
                      </td>
                    );
                  }

                  // Color coding based on FTE percentage
                  let bgColor = 'bg-slate-50';
                  let textColor = 'text-slate-700';

                  if (monthData.fte_percentage > 100) {
                    bgColor = 'bg-red-100';
                    textColor = 'text-red-800';
                  } else if (monthData.fte_percentage === 100) {
                    bgColor = 'bg-yellow-100';
                    textColor = 'text-yellow-800';
                  } else if (monthData.fte_percentage >= 80) {
                    bgColor = 'bg-green-100';
                    textColor = 'text-green-800';
                  } else if (monthData.fte_percentage >= 40) {
                    bgColor = 'bg-blue-50';
                    textColor = 'text-blue-700';
                  }

                  return (
                    <td
                      key={`${m.year}-${m.month}`}
                      className={`px-4 py-3 text-right ${bgColor}`}
                    >
                      <div className={`font-medium ${textColor}`}>
                        {monthData.total_hours} hrs
                      </div>
                      <div className={`text-xs ${textColor}`}>
                        {monthData.fte_percentage.toFixed(0)}% FTE
                      </div>
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="mt-4 flex items-center gap-4 text-xs text-slate-600">
        <div className="flex items-center gap-2">
          <div className="h-4 w-4 rounded bg-red-100 border border-red-200"></div>
          <span>&gt;100% FTE (Overallocated)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="h-4 w-4 rounded bg-yellow-100 border border-yellow-200"></div>
          <span>100% FTE (Full)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="h-4 w-4 rounded bg-green-100 border border-green-200"></div>
          <span>80-99% FTE (High)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="h-4 w-4 rounded bg-blue-50 border border-blue-200"></div>
          <span>40-79% FTE (Medium)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="h-4 w-4 rounded bg-slate-50 border border-slate-200"></div>
          <span>&lt;40% FTE (Low)</span>
        </div>
      </div>

      <DateRangeModal
        open={isDateRangeModalOpen}
        onClose={() => setIsDateRangeModalOpen(false)}
        onSubmit={handleDateRangeUpdate}
        defaultValues={{
          startYear,
          startMonth,
          endYear,
          endMonth
        }}
      />
    </Card>
  );
}

