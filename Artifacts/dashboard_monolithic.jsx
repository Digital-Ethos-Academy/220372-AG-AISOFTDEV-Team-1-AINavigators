import React from 'react';
import { Bell, Briefcase, Users, BarChart3, Wand2, Plus, UserPlus, FileText, Bot, Dot } from 'lucide-react';

const LogoIcon = () => (
  <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M16 0L32 9.23761V27.7128L16 32L0 27.7128V9.23761L16 0Z" fill="#3B82F6"/>
    <path d="M16 12.9221L27.7128 6.92309V21.0769L16 25.0779L4.28711 21.0769V6.92309L16 12.9221Z" fill="white" fillOpacity="0.5"/>
    <path d="M16 4.61884L29.8564 12.9231L16 21.2274L2.14355 12.9231L16 4.61884Z" fill="white"/>
  </svg>
);

const UserAvatar = ({ initials, className, src }) => (
  src ? <img src={src} alt="User Avatar" className={`w-8 h-8 rounded-full ${className}`} /> :
  <div className={`flex items-center justify-center w-8 h-8 rounded-full text-xs font-bold text-gray-600 bg-gray-200 ${className}`}>
    {initials}
  </div>
);

export default function StaffAllocDashboard() {
  const recentActivity = [
    { initials: 'JD', name: 'JD', project: 'PROJ-007', role: '...', allocation: 35, status: 'Active', avatarUrl: null },
    { initials: 'AM', name: 'Lead Developer', project: 'Project Manager', role: 'Active', allocation: 40, status: 'Active', avatarUrl: null },
    { initials: 'AM', name: 'AM', project: 'PROJ-012', role: 'Planning', allocation: null, status: 'Active', avatarUrl: null },
    { initials: 'LK', name: 'LK', project: 'QA Engineer', role: '...', allocation: 30, status: 'Active', avatarUrl: null },
    { initials: 'RW', name: 'Bàll/Kèit Developer', project: 'UI/UX Designer', role: 'Planning', allocation: null, status: 'Active', avatarUrl: null },
    { initials: 'SP', name: 'Backend Developer', project: 'PROJ-009', role: 'Planning', allocation: null, status: 'Active', avatarUrl: null },
    { initials: 'IE', name: 'Business Analyst', project: '...', role: '...', allocation: 25, status: 'Active', avatarUrl: null },
    { initials: 'TC', name: 'TC', project: 'PROJ-002', role: 'Planning', allocation: null, status: 'Active', avatarUrl: "https://i.pravatar.cc/32?u=tc" },
  ];

  const aiRecommendations = [
    {
      category: 'Staffing',
      description: 'Suggesting staff for PROJ-015 based on skill set.',
      time: '3 hours ago',
      color: 'red'
    },
    {
      category: 'Forecast',
      description: 'Predicting staffing needs for upcoming Q1 projects.',
      time: '5 hours ago',
      color: 'red'
    },
     {
      category: 'Optimization',
      description: 'Reallocate underutilized staff from PROJ-004 to PROJ-011.',
      time: '1 day ago',
      color: 'purple'
    }
  ];

  return (
    <div className="bg-gray-50 min-h-screen font-sans">
      <header className="bg-white shadow-sm sticky top-0 z-10">
        <div className="max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-8">
              <div className="flex items-center gap-2">
                <LogoIcon />
                <span className="text-xl font-bold text-gray-800">StaffAlloc</span>
              </div>
              <nav className="hidden md:flex items-center space-x-6">
                <a href="#" className="text-sm font-semibold text-blue-600 border-b-2 border-blue-600 pb-1">Dashboard</a>
                <a href="#" className="text-sm font-medium text-gray-500 hover:text-gray-800">Projects</a>
                <a href="#" className="text-sm font-medium text-gray-500 hover:text-gray-800">Employees</a>
                <a href="#" className="text-sm font-medium text-gray-500 hover:text-gray-800">Allocations</a>
                <a href="#" className="text-sm font-medium text-gray-500 hover:text-gray-800">Reports</a>
              </nav>
            </div>
            <div className="flex items-center gap-4">
              <div className="relative">
                <Bell className="h-6 w-6 text-gray-500 hover:text-gray-700" />
                <span className="absolute -top-1 -right-1 flex h-4 w-4 items-center justify-center rounded-full bg-red-500 text-xs text-white">1</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="flex items-center justify-center w-8 h-8 rounded-full bg-gray-800 text-white text-sm font-bold">S</div>
                <span className="text-sm font-medium text-gray-700">Sarah</span>
              </div>
            </div>
          </div>
        </div>
      </header>
      
      <main className="max-w-screen-2xl mx-auto p-4 sm:p-6 lg:p-8 space-y-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">Welcome back, Sarah Martinez</h1>
          <p className="text-gray-500 mt-1">November 5, 2025</p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-blue-100 p-6 rounded-2xl flex items-center gap-5 transition-transform hover:scale-105 cursor-pointer">
            <div className="bg-blue-200 p-3 rounded-lg">
              <Briefcase className="h-8 w-8 text-blue-600" />
            </div>
            <div>
              <p className="text-4xl font-bold text-gray-800">12</p>
              <p className="text-sm text-gray-600">Active Projects</p>
            </div>
          </div>
          <div className="bg-green-100 p-6 rounded-2xl flex items-center gap-5 transition-transform hover:scale-105 cursor-pointer">
            <div className="bg-green-200 p-3 rounded-lg">
              <Users className="h-8 w-8 text-green-600" />
            </div>
            <div>
              <p className="text-4xl font-bold text-gray-800">47</p>
              <p className="text-sm text-gray-600">Total Employees</p>
            </div>
          </div>
          <div className="bg-purple-100 p-6 rounded-2xl flex items-center gap-5 transition-transform hover:scale-105 cursor-pointer">
            <div className="bg-purple-200 p-3 rounded-lg">
              <BarChart3 className="h-8 w-8 text-purple-600" />
            </div>
            <div>
              <p className="text-4xl font-bold text-gray-800">78%</p>
              <p className="text-sm text-gray-600">Utilization Rate</p>
            </div>
          </div>
          <div className="bg-red-100 p-6 rounded-2xl flex items-center gap-5 transition-transform hover:scale-105 cursor-pointer relative">
            <div className="bg-red-200 p-3 rounded-lg">
              <Wand2 className="h-8 w-8 text-red-600" />
            </div>
            <div>
              <p className="text-4xl font-bold text-gray-800">5</p>
              <p className="text-sm text-gray-600">Pending AI Recommendations</p>
            </div>
            <span className="absolute top-4 right-4 flex h-6 w-6 items-center justify-center rounded-full bg-red-500 text-sm font-bold text-white">5</span>
          </div>
        </div>

        <div>
          <h2 className="text-xl font-semibold text-gray-700">Quick Actions</h2>
          <div className="mt-4 flex flex-wrap gap-4">
            <button className="flex items-center gap-2 bg-blue-600 text-white font-semibold py-2.5 px-5 rounded-lg shadow-sm hover:bg-blue-700 transition focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2">
              <Plus className="h-5 w-5" /> Create New Project
            </button>
            <button className="flex items-center gap-2 bg-green-500 text-white font-semibold py-2.5 px-5 rounded-lg shadow-sm hover:bg-green-600 transition focus:outline-none focus:ring-2 focus:ring-green-400 focus:ring-offset-2">
              <UserPlus className="h-5 w-5" /> Assign Staff
            </button>
            <button className="flex items-center gap-2 bg-gray-200 text-gray-700 font-semibold py-2.5 px-5 rounded-lg hover:bg-gray-300 transition focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2">
              <FileText className="h-5 w-5" /> View Reports
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
          <div className="bg-white p-6 rounded-2xl shadow-sm lg:col-span-2">
            <h2 className="text-xl font-semibold text-gray-700">Recent Activity</h2>
            <div className="mt-4 overflow-x-auto">
              <table className="w-full text-sm text-left">
                <thead className="text-xs text-gray-500 uppercase border-b">
                  <tr>
                    <th scope="col" className="px-4 py-3 font-semibold">Employee Name</th>
                    <th scope="col" className="px-4 py-3 font-semibold">Project Code</th>
                    <th scope="col" className="px-4 py-3 font-semibold">Role</th>
                    <th scope="col" className="px-4 py-3 font-semibold">Allocation (hours)</th>
                    <th scope="col" className="px-4 py-3 font-semibold">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {recentActivity.map((activity, index) => (
                    <tr key={index} className="border-b hover:bg-gray-50">
                      <td className="px-4 py-4 whitespace-nowrap">
                        <div className="flex items-center gap-3">
                          <UserAvatar initials={activity.initials} src={activity.avatarUrl} />
                          <span className="font-medium text-gray-800">{activity.name}</span>
                        </div>
                      </td>
                      <td className="px-4 py-4 text-gray-600">{activity.project}</td>
                      <td className="px-4 py-4 text-gray-600">
                        <div className="flex items-center gap-2">
                           {activity.role === 'Planning' && <span className="h-2 w-2 rounded-full bg-yellow-400"></span>}
                           {activity.role === 'Active' && <span className="h-2 w-2 rounded-full bg-green-400"></span>}
                          <span>{activity.role}</span>
                        </div>
                      </td>
                      <td className="px-4 py-4 text-gray-600">{activity.allocation || '-'}</td>
                      <td className="px-4 py-4">
                        <span className="inline-block px-3 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800">
                          {activity.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="bg-white p-6 rounded-2xl shadow-sm">
            <div className="flex items-center gap-2">
              <Bot className="h-6 w-6 text-blue-600" />
              <h2 className="text-xl font-semibold text-gray-700">AI Recommendations</h2>
            </div>
            <div className="mt-4 space-y-4 max-h-[450px] overflow-y-auto pr-2">
              {aiRecommendations.map((rec, index) => (
                <div key={index} className="bg-gray-50 p-4 rounded-lg space-y-3">
                    <span className={`inline-block px-2.5 py-0.5 text-xs font-semibold rounded-full ${rec.color === 'red' ? 'bg-red-100 text-red-800' : 'bg-purple-100 text-purple-800'}`}>
                      {rec.category}
                    </span>
                  <p className="text-sm text-gray-700">{rec.description}</p>
                  <div className="flex items-center justify-between">
                    <div className="flex gap-2">
                      <button className="text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-lg py-1.5 px-4 transition">Accept</button>
                      <button className="text-sm font-semibold text-gray-600 bg-gray-200 hover:bg-gray-300 rounded-lg py-1.5 px-4 transition">Dismiss</button>
                    </div>
                    <span className="text-xs text-gray-400">{rec.time}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}