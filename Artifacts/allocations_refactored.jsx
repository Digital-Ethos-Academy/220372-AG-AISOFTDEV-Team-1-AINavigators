import React from 'react';
import { ChevronLeft, ChevronRight, AlertTriangle } from 'lucide-react';

// --- TYPE DEFINITIONS ---
interface Staff {
  id: number;
  name: string;
  title: string;
  avatar: string;
  utilization: number;
}

interface Project {
  name: string;
  color: string;
}

interface Projects {
  [key: string]: Project;
}

interface Allocation {
  id: number;
  staffId: number;
  projectId: string;
  text: string;
  start: number;
  span: number;
  conflict?: boolean;
  stack?: number;
}


// --- DATA MOCKS ---
const staffData: Staff[] = [
  { id: 1, name: 'Sarah Chen', title: 'Senior Developer', avatar: 'https://i.pravatar.cc/150?u=sarahchen', utilization: 92 },
  { id: 2, name: 'David Smith', title: 'UI Designer', avatar: 'https://i.pravatar.cc/150?u=davidsmith', utilization: 78 },
  { id: 3, name: 'Maria Rodriguez', title: 'Project Manager', avatar: 'https://i.pravatar.cc/150?u=mariarodriguez', utilization: 65 },
  { id: 4, name: 'John Doe', title: 'Senior Developer', avatar: 'https://i.pravatar.cc/150?u=johndoe', utilization: 65 },
  { id: 5, name: 'Aisha Khan', title: 'Project Manager', avatar: 'https://i.pravatar.cc/150?u=aishakhan', utilization: 50 },
  { id: 6, name: 'Michael Lee', title: 'Project Manager', avatar: 'https://i.pravatar.cc/150?u=michaellee', utilization: 110 },
];

const projects: Projects = {
  'PROJ-001': { name: 'Blue', color: 'bg-blue-500' },
  'PROJ-002': { name: 'Purple', color: 'bg-purple-500' },
  'PROJ-003': { name: 'Green', color: 'bg-green-500' },
  'PROJ-004': { name: 'Orange', color: 'bg-orange-500' },
};

const allocations: Allocation[] = [
  { id: 1, staffId: 1, projectId: 'PROJ-001', text: 'PROJ-001 (8h)', start: 1, span: 2 },
  { id: 2, staffId: 1, projectId: 'PROJ-002', text: 'PROJ-002 (8h)', start: 3, span: 4 },
  { id: 3, staffId: 1, projectId: 'PROJ-001', text: 'PROJ-001 (8h)', start: 7, span: 1 },
  { id: 4, staffId: 2, projectId: 'PROJ-002', text: 'PROJ-002 (8h)', start: 1, span: 2 },
  { id: 5, staffId: 2, projectId: 'PROJ-003', text: 'PROJ-003 (8h)', start: 5, span: 3 },
  { id: 6, staffId: 3, projectId: 'PROJ-002', text: 'PROJ-002 (8h)', start: 3, span: 5 },
  { id: 7, staffId: 3, projectId: 'PROJ-004', text: 'PROJ-004 (8h)', start: 1, span: 2 },
  { id: 8, staffId: 4, projectId: 'PROJ-002', text: 'PROJ-002 (8h)', start: 1, span: 2 },
  { id: 9, staffId: 4, projectId: 'PROJ-002', text: 'PROJ-002 (8h)', start: 4, span: 2 },
  { id: 10, staffId: 4, projectId: 'PROJ-002', text: 'PROJ-002 (8h)', start: 7, span: 1 },
  { id: 11, staffId: 5, projectId: 'PROJ-001', text: 'PROJ-001 (8h)', start: 1, span: 1, conflict: false, stack: 1 },
  { id: 12, staffId: 5, projectId: 'PROJ-001', text: 'PROJ-001 (8h)', start: 1, span: 1, conflict: false, stack: 2 },
  { id: 13, staffId: 5, projectId: 'PROJ-002', text: 'PROJ-002 (8h)', start: 2, span: 1, conflict: false, stack: 1 },
  { id: 14, staffId: 5, projectId: 'PROJ-002', text: 'PROJ-002 (4h)', start: 3, span: 1, conflict: true, stack: 1 },
  { id: 15, staffId: 5, projectId: 'PROJ-001', text: 'PROJ-001 (8h)', start: 3, span: 1, conflict: false, stack: 2 },
  { id: 16, staffId: 5, projectId: 'PROJ-001', text: 'PROJ-001 (4h)', start: 4, span: 1, conflict: true, stack: 1 },
  { id: 17, staffId: 6, projectId: 'PROJ-003', text: 'PROJ-003 (4h)', start: 1, span: 1 },
];


// --- ATOMIC & REUSABLE COMPONENTS ---

const UtilizationBadge = ({ value }: { value: number }) => {
  const colorClasses =
    value > 100 ? 'bg-red-100 text-red-700'
    : value >= 90 ? 'bg-red-100 text-red-700'
    : value > 70 ? 'bg-green-100 text-green-700'
    : value > 50 ? 'bg-yellow-100 text-yellow-600'
    : 'bg-yellow-100 text-yellow-600';
  
  return (
    <div className={`ml-auto flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-sm font-bold ${colorClasses}`}>
      {value}%
    </div>
  );
};

const AbsoluteAllocationBar = ({ allocation, project, rowIndex }: { allocation: Allocation, project: Project, rowIndex: number }) => (
  <div
    className={`${project.color} absolute flex cursor-pointer items-center rounded px-2 py-1 text-xs text-white shadow-sm`}
    style={{
      top: `${rowIndex * 72 + 8}px`,
      left: `calc(${(allocation.start - 1) * (100 / 7)}% + 4px)`,
      width: `calc(${allocation.span * (100 / 7)}% - 8px)`,
      height: '28px',
    }}
  >
    {allocation.text}
  </div>
);

const StackedAllocationItem = ({ allocation, project }: { allocation: Allocation, project: Project }) => (
  <div className={`${project.color} flex cursor-pointer items-center justify-between rounded px-2 py-0.5 text-xs text-white`}>
    <span>{allocation.text}</span>
    {allocation.conflict && <AlertTriangle className="h-3 w-3 fill-white text-red-700" />}
  </div>
);


// --- LAYOUT & SECTION COMPONENTS ---

const AppHeader = () => {
  const navItems = ['Dashboard', 'Projects', 'Clients', 'Reports', 'Settings'];
  return (
    <header className="bg-slate-800">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6 lg:px-8">
        <div className="text-xl font-bold text-white">StaffAlloc</div>
        <nav>
          <ul className="flex items-center space-x-6 text-sm font-medium text-slate-300">
            {navItems.map((item) => (
              <li key={item}>
                <a
                  href="#"
                  className={`transition-colors hover:text-white ${
                    item === 'Dashboard' ? 'relative text-white after:absolute after:-bottom-3 after:left-0 after:h-0.5 after:w-full after:bg-blue-500' : ''
                  }`}
                >
                  {item}
                </a>
              </li>
            ))}
          </ul>
        </nav>
      </div>
    </header>
  );
};

const PageHeader = () => (
  <div className="flex flex-wrap items-center justify-between gap-4">
    <h1 className="text-3xl font-bold text-slate-900">Team Allocations</h1>
    <div className="flex flex-wrap items-center gap-4">
      <div className="flex items-center gap-2 text-sm font-medium text-slate-600">
        <button aria-label="Previous month" className="p-1.5 hover:text-slate-900">
          <ChevronLeft className="h-5 w-5" />
        </button>
        <span>November 2025</span>
        <button aria-label="Next month" className="p-1.5 hover:text-slate-900">
          <ChevronRight className="h-5 w-5" />
        </button>
      </div>
      <div className="flex rounded-md border border-slate-300 bg-slate-200 p-0.5 text-sm">
        <button className="rounded-[5px] px-3 py-1">Week</button>
        <button className="rounded-[5px] bg-white px-3 py-1 text-blue-600 shadow-sm">Month</button>
      </div>
      <div className="flex items-center gap-2">
        <button className="rounded-md border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700 shadow-sm transition-colors hover:bg-slate-50">
          Export Schedule
        </button>
        <button className="rounded-md border border-blue-600 bg-blue-500 px-4 py-2 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-blue-600">
          Adjust Allocations
        </button>
      </div>
    </div>
  </div>
);

const StaffList = ({ staffList }: { staffList: Staff[] }) => (
  <div className="flex flex-col gap-2 pt-11">
    {staffList.map((staff) => (
      <div key={staff.id} className="flex h-[72px] items-center gap-3 pr-4">
        <img src={staff.avatar} alt={staff.name} className="h-12 w-12 rounded-full" />
        <div>
          <div className="font-semibold text-slate-900">{staff.name}</div>
          <div className="text-sm text-slate-500">{staff.title}</div>
        </div>
        <UtilizationBadge value={staff.utilization} />
      </div>
    ))}
  </div>
);

const TimelineHeader = () => (
    <div className="grid grid-cols-7 border-b border-slate-200">
        <div className="py-2 text-center text-sm font-medium text-slate-600">Mon 4</div>
        <div className="py-2 text-center text-sm font-medium text-slate-600"></div>
        <div className="py-2 text-center text-sm font-medium text-slate-600">Wed 6</div>
        <div className="py-2 text-center text-sm font-medium text-slate-600"></div>
        <div className="py-2 text-center text-sm font-medium text-slate-600">Fri 8</div>
        <div className="py-2 text-center text-sm font-medium text-slate-600"></div>
        <div className="py-2 text-center text-sm font-medium text-slate-600">Sun 10</div>
    </div>
);

const TimelineGrid = ({ staffList, allocations, projects }: { staffList: Staff[], allocations: Allocation[], projects: Projects }) => {
  // Memoize the staff index lookup for performance
  const staffIndexMap = React.useMemo(() => 
    new Map(staffList.map((staff, index) => [staff.id, index])), 
    [staffList]
  );
  
  return (
    <div className="overflow-x-auto">
      <TimelineHeader />
      <div className="relative">
        {/* Render grid rows and stacked allocations */}
        {staffList.map((staff) => (
          <div
            key={staff.id}
            className={`grid h-[72px] grid-cols-7 border-t border-slate-200 ${staff.id === 5 ? 'ring-2 ring-inset ring-red-400' : ''}`}
          >
            {[...Array(7)].map((_, dayIndex) => (
              <div
                key={dayIndex}
                className={`border-l border-slate-200 ${dayIndex === 0 ? 'border-l-0' : ''} ${staff.id === 5 ? 'relative space-y-1 p-1' : 'relative p-2'}`}
              >
                {/* Special handling for stacked/conflicting allocations */}
                {staff.id === 5 && allocations
                  .filter(a => a.staffId === staff.id && a.start === dayIndex + 1)
                  .map(alloc => (
                    <StackedAllocationItem key={alloc.id} allocation={alloc} project={projects[alloc.projectId]} />
                  ))
                }
              </div>
            ))}
          </div>
        ))}
        {/* Render absolutely positioned allocations over the grid */}
        {allocations
          .filter(a => a.staffId !== 5) // Render only non-stacked allocations
          .map(alloc => {
            const rowIndex = staffIndexMap.get(alloc.staffId);
            if (rowIndex === undefined) return null;
            return (
              <AbsoluteAllocationBar 
                key={alloc.id} 
                allocation={alloc} 
                project={projects[alloc.projectId]} 
                rowIndex={rowIndex} 
              />
            );
          })
        }
      </div>
    </div>
  );
};

const InfoSidebar = ({ projects }: { projects: Projects }) => (
  <div className="border-l border-slate-200 pl-6 pt-11">
    <div className="space-y-6">
      <div>
        <h3 className="font-semibold text-slate-900">Week Overview</h3>
        <div className="mt-2 space-y-1 text-sm text-slate-600">
          <p>Total team hours: 320h</p>
          <p>Average utilization: 78%</p>
          <div className="flex items-center gap-2 pt-2 text-red-600">
            <span className="flex h-6 w-6 items-center justify-center rounded-full bg-red-500 text-white">
              <AlertTriangle className="h-4 w-4" />
            </span>
            <span className="font-semibold">2 conflicts detected</span>
          </div>
        </div>
      </div>
      <div>
        <h3 className="font-semibold text-slate-900">Project Legend</h3>
        <ul className="mt-2 space-y-2 text-sm text-slate-600">
          {Object.entries(projects).map(([id, project]) => (
             id !== 'PROJ-004' && <li key={id} className="flex items-center gap-2">
              <span className={`h-3 w-3 rounded-sm ${project.color}`}></span>
              {`${id} (${project.name})`}
            </li>
          ))}
          {/* Manual correction for data inconsistency */}
           <li className="flex items-center gap-2">
              <span className="h-3 w-3 rounded-sm bg-green-500"></span>
              PROJ-001 (Orange)
            </li>
        </ul>
      </div>
    </div>
  </div>
);


// --- MAIN COMPONENT ---

export default function TeamAllocations() {
  return (
    <div className="min-h-screen bg-slate-100 font-sans text-slate-800">
      <AppHeader />
      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <PageHeader />
        <div className="mt-6 overflow-hidden rounded-lg bg-white p-6 shadow-md">
          <div className="grid grid-cols-[250px_1fr_220px] gap-6">
            <StaffList staffList={staffData} />
            <TimelineGrid staffList={staffData} allocations={allocations} projects={projects} />
            <InfoSidebar projects={projects} />
          </div>
        </div>
      </main>
    </div>
  );
}