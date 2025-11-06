import React from 'react';
import { Search, Plus, User, MoreHorizontal, ChevronDown } from 'lucide-react';

// TypeScript types for better code organization
type Status = 'Active' | 'Planning' | 'On Hold';
type Manager = { type: 'text'; name: string } | { type: 'avatar'; name: string; avatarUrl: string } | { type: 'count'; count: number };

type Project = {
  id: string;
  code: string;
  name: string;
  client: string;
  manager: Manager;
  sprints: number;
  status: Status;
};

// Dummy data to populate the table, matching the design
const projectsData: Project[] = [
  { id: '1', code: 'PROJ-2024-001', name: 'Customer Portal Redesign', client: 'Acme Corp', manager: { type: 'text', name: 'Mark T.' }, sprints: 12, status: 'Active' },
  { id: '2', code: 'MOJ-2024-003', name: 'Cloud Migration Project', client: 'Global Systems Inc.', manager: { type: 'avatar', name: 'Sarah K.', avatarUrl: 'https://i.pravatar.cc/150?u=sarah' }, sprints: 8, status: 'Active' },
  { id: '3', code: 'CPR-2024-002', name: 'Data Warehouse Build', client: 'Global Solutions Co.', manager: { type: 'count', count: 5 }, sprints: 6, status: 'Planning' },
  { id: '4', code: 'DWB-2024-004', name: 'Website Revamp', client: 'Alex L.', manager: { type: 'count', count: 6 }, sprints: 6, status: 'Active' },
  { id: '5', code: 'WRV-2024-005', name: 'Website Revamp', client: 'Fashion Hub', manager: { type: 'count', count: 4 }, sprints: 6, status: 'Active' },
  { id: '6', code: 'ITD-2024-006', name: 'Internal Tool Development', client: 'Tech Innovations', manager: { type: 'count', count: 7 }, sprints: 5, status: 'Active' },
  { id: '7', code: 'SAU-2024-007', name: 'Security Audit', client: 'StaffAlloc Inc.', manager: { type: 'count', count: 3 }, sprints: 4, status: 'Planning' },
  { id: '8', code: 'SUP-2024-008', name: 'System Upgrade', client: 'CyberSafe Partners', manager: { type: 'count', count: 4 }, sprints: 7, status: 'On Hold' },
  { id: '9', code: 'SUP-2024-009', name: 'System Upgrade', client: 'TuberSafe Partners', manager: { type: 'avatar', name: 'John Doe', avatarUrl: 'https://i.pravatar.cc/150?u=john' }, sprints: 7, status: '...' },
  { id: '10', code: 'EAP-2024-010', name: 'System Upgrade', client: 'Eurariit Corp', manager: { type: 'count', count: 5 }, sprints: 1, status: '...' },
];

// Helper component for Status Pills
const StatusPill: React.FC<{ status: Status | '...' }> = ({ status }) => {
  const baseClasses = "px-3 py-1 text-xs font-semibold rounded-full inline-block";
  switch (status) {
    case 'Active':
      return <span className={`${baseClasses} bg-green-100 text-green-800`}>Active</span>;
    case 'Planning':
      return <span className={`${baseClasses} bg-yellow-100 text-yellow-800`}>Planning</span>;
    case 'On Hold':
      return <span className={`${baseClasses} bg-orange-100 text-orange-800`}>On Hold</span>;
    default:
        return null;
  }
};

// Helper component for Manager cell
const ManagerCell: React.FC<{ manager: Manager }> = ({ manager }) => {
  switch (manager.type) {
    case 'text':
      return <span className="text-gray-800">{manager.name}</span>;
    case 'avatar':
      return (
        <div className="flex items-center justify-center">
          <img src={manager.avatarUrl} alt={manager.name} className="w-7 h-7 rounded-full" />
        </div>
      );
    case 'count':
      return (
        <div className="flex items-center justify-center">
          <span className="flex items-center justify-center w-7 h-7 bg-blue-100 text-blue-700 rounded-full text-xs font-bold">
            {manager.count}
          </span>
        </div>
      );
  }
};

export default function ProjectsView() {
  return (
    <div className="bg-slate-50 min-h-screen font-sans">
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-10">
              <div className="text-2xl font-bold text-blue-600">StaffAlloc</div>
              <nav className="hidden md:flex space-x-8">
                <a href="#" className="text-gray-600 hover:text-gray-900 text-sm font-medium">Dashboard</a>
                <a href="#" className="text-blue-600 border-b-2 border-blue-600 text-sm font-medium" aria-current="page">Projects</a>
                <a href="#" className="text-gray-600 hover:text-gray-900 text-sm font-medium">Employees</a>
                <a href="#" className="text-gray-600 hover:text-gray-900 text-sm font-medium">Reports</a>
              </nav>
            </div>
            <div className="flex items-center gap-3">
              <button className="p-2 bg-blue-600 text-white rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500" aria-label="User menu">
                <User size={18} />
              </button>
              <span className="text-sm font-medium text-gray-700">John D.</span>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="bg-white rounded-xl shadow-md p-6 lg:p-8">
          {/* Page Header */}
          <div className="flex flex-col md:flex-row justify-between md:items-start gap-4 mb-6">
            <div>
              <h1 className="text-3xl font-extrabold text-gray-900">Projects</h1>
              <p className="mt-1 text-gray-600">Manage and track all project allocations.</p>
            </div>
            <div className="flex items-center gap-3 w-full md:w-auto">
              <div className="relative flex-grow">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
                <input
                  type="search"
                  placeholder="Search..."
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <button className="flex-shrink-0 flex items-center gap-2 bg-blue-600 text-white font-semibold px-4 py-2 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors">
                <Plus size={18} />
                Create New Project
              </button>
            </div>
          </div>

          {/* Filter Bar */}
          <div className="flex flex-col md:flex-row items-start md:items-center gap-4 mb-6">
            <div className="relative w-full md:w-auto md:flex-grow max-w-xs">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
              <input
                type="search"
                placeholder="Search projects..."
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 text-sm"
              />
            </div>
            <button className="flex items-center justify-between w-full md:w-auto text-sm bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-50">
              Status (All)
            </button>
            <button className="flex items-center justify-between w-full md:w-auto text-sm bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-50">
              Date Range
            </button>
            <p className="text-sm text-gray-500 md:ml-auto whitespace-nowrap">Showing 12 projects</p>
          </div>

          {/* Projects Table */}
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left text-gray-600">
              <thead className="bg-gray-50 text-xs text-gray-500 uppercase tracking-wider">
                <tr>
                  <th scope="col" className="px-4 py-3 font-medium">Project Code Project Name</th>
                  <th scope="col" className="px-4 py-3 font-medium">Client</th>
                  <th scope="col" className="px-4 py-3 font-medium text-center">Manager</th>
                  <th scope="col" className="px-4 py-3 font-medium text-center">Sprints</th>
                  <th scope="col" className="px-4 py-3 font-medium text-center">Status</th>
                  <th scope="col" className="px-4 py-3 font-medium text-center">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {projectsData.slice(0, 8).map((project) => (
                  <tr key={project.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-4 py-4 whitespace-nowrap">
                      <div>
                        <a href="#" className="font-semibold text-blue-600 hover:underline">{project.code}</a>
                        <div className="text-gray-800">{project.name}</div>
                      </div>
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap text-gray-800">{project.client}</td>
                    <td className="px-4 py-4 whitespace-nowrap text-center"><ManagerCell manager={project.manager} /></td>
                    <td className="px-4 py-4 whitespace-nowrap text-gray-800 text-center">{project.sprints}</td>
                    <td className="px-4 py-4 whitespace-nowrap text-center"><StatusPill status={project.status} /></td>
                    <td className="px-4 py-4 whitespace-nowrap text-center">
                      <button className="text-gray-500 hover:text-gray-800 p-1 rounded-full hover:bg-gray-100" aria-label="More options">
                        <MoreHorizontal size={20} />
                      </button>
                    </td>
                  </tr>
                ))}
                {/* Last two rows have slightly different layout to match image */}
                 <tr className="hover:bg-gray-50 transition-colors">
                    <td className="px-4 py-4 whitespace-nowrap">
                      <div>
                        <a href="#" className="font-semibold text-blue-600 hover:underline">System Upgrade</a>
                      </div>
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap text-gray-800">TuberSafe Partners</td>
                    <td className="px-4 py-4 whitespace-nowrap text-center"><ManagerCell manager={projectsData[8].manager} /></td>
                    <td className="px-4 py-4 whitespace-nowrap text-gray-800 text-center">7</td>
                    <td className="px-4 py-4 whitespace-nowrap text-center">...</td>
                    <td className="px-4 py-4 whitespace-nowrap text-center">
                      <button className="text-gray-500 hover:text-gray-800 p-1 rounded-full hover:bg-gray-100" aria-label="More options">
                        <MoreHorizontal size={20} />
                      </button>
                    </td>
                  </tr>
                   <tr className="hover:bg-gray-50 transition-colors">
                    <td className="px-4 py-4 whitespace-nowrap">
                      <div>
                        <a href="#" className="font-semibold text-blue-600 hover:underline">System Upgrade</a>
                      </div>
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap text-gray-800">Eurariit Corp</td>
                    <td className="px-4 py-4 whitespace-nowrap text-center"><ManagerCell manager={projectsData[9].manager} /></td>
                    <td className="px-4 py-4 whitespace-nowrap text-gray-800 text-center">1</td>
                    <td colSpan={3} className="px-4 py-4 whitespace-nowrap">
                        <nav className="flex items-center justify-start gap-1 text-sm text-gray-600">
                            <a href="#" className="px-3 py-1 rounded-md bg-blue-100 text-blue-600 font-medium">1</a>
                            <a href="#" className="px-3 py-1 rounded-md hover:bg-gray-100">2</a>
                            <a href="#" className="px-3 py-1 rounded-md hover:bg-gray-100">3</a>
                            <span className="px-3 py-1">...</span>
                            <a href="#" className="px-3 py-1 rounded-md hover:bg-gray-100">Next &gt;</a>
                        </nav>
                    </td>
                  </tr>
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </div>
  );
}