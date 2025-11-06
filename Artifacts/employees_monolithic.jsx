tsx
import React from 'react';
import { Search, Plus, X, BarChart2, Calendar, CheckCircle } from 'lucide-react';

// Type definitions for our data structures
type Skill = {
  name: string;
  color: string;
};

type EmployeeStatus = {
  type: 'allocated' | 'leave' | 'gap' | 'multiple';
  value?: string | number;
  secondaryValue?: string;
};

type Employee = {
  id: number;
  name: string;
  title: string;
  email: string;
  avatarUrl: string;
  initials: string;
  initialsBgColor: string;
  skills: Skill[];
  status: EmployeeStatus;
};

// Mock Data based on the design
const employeeData: Employee[] = [
  {
    id: 1,
    name: 'Jane Smith',
    title: 'Software Engineer',
    email: '@mail',
    avatarUrl: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80',
    initials: 'JS',
    initialsBgColor: 'bg-blue-500',
    skills: [{ name: 'React', color: 'green' }, { name: 'Figma', color: 'blue' }],
    status: { type: 'gap', value: 'Gapst' },
  },
  {
    id: 2,
    name: 'Alex Morgan',
    title: 'UX Designer',
    email: '@mail',
    avatarUrl: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80',
    initials: 'AM',
    initialsBgColor: 'bg-orange-500',
    skills: [{ name: 'Liaison', color: 'orange' }, { name: 'Liaison', color: 'red' }],
    status: { type: 'multiple', value: 'View allocated', secondaryValue: 'On Leave' },
  },
  {
    id: 3,
    name: 'AM',
    title: 'Software Engineer',
    email: '@mail',
    avatarUrl: 'https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80',
    initials: 'SIUR',
    initialsBgColor: 'bg-teal-500',
    skills: [{ name: 'Engst', color: 'green' }, { name: 'Figma', color: 'yellow' }],
    status: { type: 'multiple', value: 'View allocated', secondaryValue: 'gap-6' },
  },
  {
    id: 4,
    name: 'David Lee',
    title: 'Software Engineer',
    email: '@mail',
    avatarUrl: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80',
    initials: 'JS',
    initialsBgColor: 'bg-orange-500',
    skills: [],
    status: { type: 'gap', value: 'gap-6' },
  },
  {
    id: 5,
    name: 'Alex Smith',
    title: 'Pmpmrce Bnsiie',
    email: '@mail',
    avatarUrl: 'https://images.unsplash.com/photo-1502685104226-ee32379fefbe?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80',
    initials: 'AM',
    initialsBgColor: 'bg-red-500',
    skills: [{ name: 'Roest', color: 'green' }, { name: 'Figma', color: 'yellow' }],
    status: { type: 'multiple', value: '78% allocated', secondaryValue: 'gap 6' },
  },
  {
    id: 6,
    name: 'David Lee',
    title: 'Project Manager',
    email: '@mail',
    avatarUrl: 'https://images.unsplash.com/photo-1463453091185-61582044d556?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80',
    initials: 'MBB',
    initialsBgColor: 'bg-teal-500',
    skills: [{ name: 'Assincd', color: 'yellow' }, { name: 'Eodetev', color: 'red' }],
    status: { type: 'multiple', value: '78% allocated', secondaryValue: 'On Leave' },
  },
  {
    id: 7,
    name: 'David Lee',
    title: 'Rroeijeerdisngjager',
    email: '@mail',
    avatarUrl: 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80',
    initials: 'JIS',
    initialsBgColor: 'bg-orange-500',
    skills: [{ name: 'AVIS', color: 'red' }, { name: 'Ennuw', color: 'pink' }],
    status: { type: 'multiple', value: '78% allocated', secondaryValue: 'On Leave' },
  },
  {
    id: 8,
    name: 'SQL',
    title: 'Bettentont@eproia',
    email: '@mail',
    avatarUrl: 'https://images.unsplash.com/photo-1517841905240-472988babdf9?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80',
    initials: 'AUG',
    initialsBgColor: 'bg-blue-500',
    skills: [],
    status: { type: 'multiple', value: '45% allocated', secondaryValue: '' },
  },
  {
    id: 9,
    name: 'Fnoc Fuipter',
    title: 'Setsksnrt & tnqtckter',
    email: '@mail',
    avatarUrl: 'https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80',
    initials: 'JSE',
    initialsBgColor: 'bg-green-500',
    skills: [{ name: 'Eaqceoi', color: 'blue' }, { name: 'Pipass', color: 'indigo' }],
    status: { type: 'multiple', value: '45% allocated', secondaryValue: 'On Leave' },
  },
  {
    id: 10,
    name: 'Las Finger',
    title: 'Rossinrak & equlitrelis',
    email: '@mail',
    avatarUrl: 'https://images.unsplash.com/photo-1522075469751-3a6694fb2f61?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80',
    initials: 'JWS',
    initialsBgColor: 'bg-blue-500',
    skills: [{ name: 'Figma', color: 'purple' }, { name: 'Sceintre', color: 'orange' }],
    status: { type: 'multiple', value: '45% allocated', secondaryValue: 'On Leave' },
  },
  {
    id: 11,
    name: 'AWS',
    title: 'Riecttvnf@bssimeer',
    email: '@mail',
    avatarUrl: 'https://images.unsplash.com/photo-1530268729831-4b0b9e170218?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80',
    initials: 'SIS',
    initialsBgColor: 'bg-red-500',
    skills: [{ name: 'AWS', color: 'blue' }, { name: 'AWS', color: 'blue' }],
    status: { type: 'multiple', value: '45% allocated', secondaryValue: 'gap 6' },
  },
  {
    id: 12,
    name: 'Florlundv',
    title: 'Rottwart@eositpiter',
    email: '@mail',
    avatarUrl: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80',
    initials: 'AJE',
    initialsBgColor: 'bg-orange-500',
    skills: [],
    status: { type: 'multiple', value: '06% allocated', secondaryValue: 'On Leave' },
  },
];

// Reusable Skill Pill Component
const SkillPill: React.FC<{ skill: Skill }> = ({ skill }) => {
  const colorClasses: { [key: string]: string } = {
    green: 'bg-green-100 text-green-700',
    blue: 'bg-blue-100 text-blue-700',
    orange: 'bg-orange-100 text-orange-700',
    red: 'bg-red-100 text-red-700',
    yellow: 'bg-yellow-100 text-yellow-700',
    pink: 'bg-pink-100 text-pink-700',
    indigo: 'bg-indigo-100 text-indigo-700',
    purple: 'bg-purple-100 text-purple-700',
  };
  return (
    <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${colorClasses[skill.color] || 'bg-gray-100 text-gray-700'}`}>
      {skill.name}
    </span>
  );
};

// Employee Card Component
const EmployeeCard: React.FC<{ employee: Employee }> = ({ employee }) => {
  return (
    <div className="bg-white rounded-xl shadow-md border border-slate-200/75 p-4 flex flex-col items-center text-center transition-shadow hover:shadow-lg">
      <div className="relative w-full flex justify-center mb-3">
        <div className="relative">
          <img src={employee.avatarUrl} alt={employee.name} className="w-20 h-20 rounded-full" />
          <span className={`absolute -top-1 -right-1 flex items-center justify-center w-7 h-7 text-white text-xs font-bold rounded-full border-2 border-white ${employee.initialsBgColor}`}>
            {employee.initials}
          </span>
        </div>
        <button className="absolute top-0 right-0 p-1.5 bg-slate-100 hover:bg-slate-200 rounded-full text-slate-500 hover:text-slate-700" aria-label="Add to project">
          <Plus size={14} />
        </button>
      </div>
      <h3 className="font-semibold text-slate-800 text-lg">{employee.name}</h3>
      <p className="text-slate-500 text-sm">{employee.title}</p>
      <p className="text-slate-400 text-sm mb-3">{employee.email}</p>
      
      <div className="flex flex-wrap justify-center gap-2 mb-4 h-5">
        {employee.skills.map((skill, index) => (
          <SkillPill key={index} skill={skill} />
        ))}
      </div>
      
      <hr className="w-full border-t border-slate-200 my-2" />
      
      <div className="w-full flex justify-between items-center text-sm">
        <a href="#" className="text-blue-600 font-semibold hover:underline">View Details</a>
        <div className="flex items-center gap-3 text-slate-500">
          <span>{employee.status.value}</span>
          {employee.status.type === 'multiple' && employee.status.secondaryValue && <span>{employee.status.secondaryValue}</span>}
        </div>
      </div>
    </div>
  );
};

// SVG Donut Chart Component
const DonutChart = () => {
  const data = [{ percent: 47, color: '#3B82F6' }, { percent: 38, color: '#A7F3D0' }, { percent: 15, color: '#E5E7EB' }];
  const circumference = 2 * Math.PI * 28;
  let accumulatedPercent = 0;

  return (
    <svg viewBox="0 0 64 64" className="w-32 h-32 transform -rotate-90">
      {data.map((item, index) => {
        const strokeDashoffset = circumference * (1 - accumulatedPercent / 100);
        const strokeDasharray = `${(circumference * item.percent) / 100} ${circumference}`;
        accumulatedPercent += item.percent;
        return (
          <circle
            key={index}
            r="28"
            cx="32"
            cy="32"
            fill="transparent"
            stroke={item.color}
            strokeWidth="8"
            strokeDasharray={strokeDasharray}
            strokeDashoffset={strokeDashoffset}
          />
        );
      })}
    </svg>
  );
};

// Main Component
export default function StaffAllocDashboard() {
  const navLinks = ['Dashboard', 'Projects', 'Employees'];
  const filterPills = ['All', 'Developers', 'Designers', 'Managers', 'Data Scientists'];
  const availabilityCalendarDays = Array(35).fill(0).map((_, i) => ({ day: i, level: Math.floor(Math.random() * 4) }));
  const availabilityColors = ['bg-slate-100', 'bg-green-200', 'bg-green-400', 'bg-green-600'];

  return (
    <div className="bg-slate-50 min-h-screen font-sans">
      {/* Header */}
      <header className="bg-white border-b border-slate-200">
        <div className="max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2">
              <div className="bg-blue-500 w-8 h-8 rounded-md flex items-center justify-center">
                <BarChart2 size={20} className="text-white transform rotate-90" />
              </div>
              <span className="font-bold text-xl text-slate-800">StaffAlloc</span>
            </div>
            <nav className="hidden md:flex md:gap-8">
              {navLinks.map((link) => (
                <a 
                  key={link} 
                  href="#" 
                  className={`text-sm font-medium ${link === 'Dashboard' ? 'text-blue-600 border-b-2 border-blue-600' : 'text-slate-500 hover:text-slate-700'} py-5`}
                >
                  {link}
                </a>
              ))}
            </nav>
            <div className="flex md:hidden">
              {/* Mobile menu button would go here */}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="max-w-screen-2xl mx-auto p-4 sm:p-6 lg:p-8">
        <div className="grid grid-cols-1 lg:grid-cols-[1fr_384px] gap-8">
          
          {/* Left Column: Team Members Grid */}
          <div className="flex flex-col gap-6">
            {/* Page Header */}
            <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start">
              <div>
                <h1 className="text-3xl font-bold text-slate-900">Team Members</h1>
                <p className="mt-1 text-slate-500">Manage employee profiles, skills, and availability</p>
              </div>
              <button className="mt-4 sm:mt-0 flex items-center gap-2 bg-blue-500 text-white font-semibold px-4 py-2.5 rounded-lg shadow-sm hover:bg-blue-600 focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-blue-500">
                <Plus size={18} />
                Add Employee
              </button>
            </div>

            {/* Filter & Search Bar */}
            <div className="flex flex-col sm:flex-row items-center gap-4">
              <div className="relative w-full sm:w-auto sm:flex-grow">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={20} />
                <input 
                  type="text" 
                  placeholder="Search employees..." 
                  className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div className="flex items-center gap-2 flex-wrap">
                {filterPills.map((pill) => (
                  <button 
                    key={pill}
                    className={`px-3 py-1.5 text-sm font-medium rounded-lg border ${pill === 'All' ? 'bg-blue-500 text-white border-blue-500' : 'bg-white text-slate-700 border-slate-300 hover:bg-slate-50'}`}
                  >
                    {pill}
                  </button>
                ))}
              </div>
            </div>

            {/* Employee Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4 gap-6">
              {employeeData.map(emp => <EmployeeCard key={emp.id} employee={emp} />)}
            </div>
          </div>
          
          {/* Right Column: Sidebar */}
          <aside className="space-y-6">
            <div className="bg-white p-6 rounded-xl shadow-md border border-slate-200/75">
              <div className="flex justify-between items-center mb-4">
                <h3 className="font-semibold text-slate-800">Additional Filters</h3>
                <button className="text-slate-400 hover:text-slate-600">
                  <X size={20} />
                </button>
              </div>
              <div className="flex items-center gap-6 text-sm">
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded-full border-4 border-blue-500 bg-white"></div>
                  <span className="font-medium text-slate-700">Availability</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded-full border-2 border-slate-300"></div>
                  <span className="font-medium text-slate-700">Skill Level</span>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-md border border-slate-200/75">
              <h3 className="font-semibold text-slate-800 mb-2">Team Overview</h3>
              <p className="text-slate-500 text-sm mb-4">Total employees: 47</p>
              <div className="flex items-center gap-6">
                <DonutChart />
                <div className="space-y-2 text-sm">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-blue-500"></div>
                    <span className="text-slate-600">47%</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-green-200"></div>
                    <span className="text-slate-600">38%</span>
                  </div>
                   <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-gray-300"></div>
                    <span className="text-slate-600">15%</span>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="bg-white p-6 rounded-xl shadow-md border border-slate-200/75">
              <h3 className="font-semibold text-slate-800">Top skills in demand</h3>
              <p className="text-slate-500 text-sm mb-4">Available (37% (38%))</p>
              <div className="flex items-end h-24 gap-4">
                <div className="flex-1 flex flex-col items-center justify-end gap-1">
                  <span className="text-xs text-slate-500">25</span>
                  <div className="w-full bg-blue-500 rounded-t-sm" style={{ height: '70%' }}></div>
                </div>
                <div className="flex-1 flex flex-col items-center justify-end gap-1">
                  <span className="text-xs text-slate-500"></span>
                   <div className="w-full bg-blue-500 rounded-t-sm" style={{ height: '100%' }}></div>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-md border border-slate-200/75">
              <h3 className="font-semibold text-slate-800 mb-4">Availability calendar</h3>
              <div className="flex justify-between items-center text-xs text-slate-500 mb-4">
                <div className="flex items-center gap-2"><div className="w-2 h-2 rounded-sm bg-green-200"></div>React</div>
                <div className="flex items-center gap-2"><div className="w-2 h-2 rounded-sm bg-green-400"></div>Python</div>
                <div className="flex items-center gap-2"><div className="w-2 h-2 rounded-sm bg-green-600"></div>AWS</div>
              </div>
              <div className="grid grid-cols-7 gap-1 text-center text-xs font-medium text-slate-400 mb-2">
                <span>M</span><span>T</span><span>W</span><span>T</span><span>F</span><span>S</span><span>S</span>
              </div>
              <div className="grid grid-cols-7 gap-1">
                {availabilityCalendarDays.map(day => (
                  <div key={day.day} className={`w-full aspect-square rounded-sm ${availabilityColors[day.level]}`}></div>
                ))}
              </div>
            </div>
          </aside>

        </div>
      </main>
    </div>
  );
}