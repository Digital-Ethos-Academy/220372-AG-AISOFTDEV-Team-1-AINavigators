import React from 'react';
import { Cube, Sparkles, RefreshCw, BrainCircuit } from 'lucide-react';

// Type definitions for clarity
type TagType = 'High Priority' | 'Optimization' | 'Medium' | 'Financial' | 'Low Priority';

interface Recommendation {
  id: number;
  title: string;
  tags: TagType[];
  description: string;
  details: { label: string; value: string; avatars?: string[] }[];
  time: string;
  match: number;
}

const recommendationsData: Recommendation[] = [
  {
    id: 1,
    title: 'Staff Shortage Alert',
    tags: ['High Priority'],
    description: 'Project "Customer Portal Redesign" is potentially delayed. The current team lacks sufficient front-end expertise.',
    details: [
      { label: 'Required', value: 'Senior React Developer', avatars: ['SM'] },
    ],
    time: '2 hours ago',
    match: 85,
  },
  {
    id: 2,
    title: 'Staff Shortage Alert',
    tags: ['High Priority'],
    description: 'John Doe is double-booked for Sprint 4, assigned to both "Customer Portal Redesign". This overlap will cause delays.',
    details: [
        { label: 'Conflicting Role', value: 'Front-end Developer' },
        { label: 'Time Period', value: 'Sprint 3-5 (Nov 15 - Dec 31)', avatars: ['JD'] },
    ],
    time: '1 hour ago',
    match: 92,
  },
  {
    id: 3,
    title: 'Allocation Conflict Detected',
    tags: [],
    description: 'John Doe is double-booked this sprint to the internal project to balance workload.',
    details: [
      { label: 'Suggested Action', value: 'Sarrin Martinez (Nov 15 - Dec 30)', avatars: ['JIA'] },
    ],
    time: '3 hours ago',
    match: 90,
  },
  {
    id: 4,
    title: 'Allocation Conflict Detected',
    tags: ['Optimization', 'Medium'],
    description: 'Sarah\'s Mobile App knowledge. Consider assigning her to the Internal Tools Upgrade project.',
    details: [
      { label: 'Suggested Action', value: 'Reassign Sarah to Internal Tools' },
      { label: 'Time Period', value: 'Joins from one (Nov 15 - Dec 30)', avatars: ['SM'] },
    ],
    time: '5 hours ago',
    match: 88,
  },
  {
    id: 5,
    title: 'Optimization Opportunity',
    tags: ['Financial'],
    description: 'Upcoming holiday season is likely to increase capacity in the U.I./U.X. team.',
    details: [
      { label: 'Suggested Action', value: 'Loan person from Q4 project' },
      { label: 'Time Period', value: '(Oct 15 - Nov 30)', avatars: ['AI'] },
    ],
    time: '1 day ago',
    match: 76,
  },
  {
    id: 6,
    title: 'Capacity Forecast Warning',
    tags: [],
    description: 'Upcoming holiday season in December will reduced team capacity impacting project timelines.',
    details: [
      { label: 'Suggested Action', value: 'Pre-allocate: 2 Developers Q1' },
    ],
    time: '1 day ago',
    match: 72,
  },
  {
    id: 7,
    title: 'Skill Gap Identified',
    tags: [],
    description: 'The team lacks expertise in Cloud security, affecting project in Q1 2026.',
    details: [
      { label: 'Suggested Action', value: 'Training or New Hire Q1 2026', avatars: ['SM'] },
    ],
    time: '5 day ago',
    match: 5,
  },
  {
    id: 8,
    title: 'Skill Gap Identified',
    tags: ['High Priority', 'Low Priority'],
    description: 'The team lacks cloud security skills affecting Missing Skill project.',
    details: [
      { label: 'Predicted Reduction', value: 'Training or New Hire Q1 2026' },
    ],
    time: '5 day ago',
    match: 65,
  },
];

const DonutChart = ({ percentage, label, size = 'large' }: { percentage: number, label: string, size?: 'large' | 'small' }) => {
    const isLarge = size === 'large';
    const chartSize = isLarge ? 160 : 100;
    const strokeWidth = isLarge ? 20 : 12;
    const radius = (chartSize - strokeWidth) / 2;
    const circumference = 2 * Math.PI * radius;
    const offset = circumference - (percentage / 100) * circumference;

    const gradientId = `gradient-${label.replace(/\s+/g, '-')}`;
    const colorStops = percentage > 85
        ? { stop1: '#3B82F6', stop2: '#60A5FA' } // Blue to Lighter Blue
        : { stop1: '#8B5CF6', stop2: '#A78BFA' }; // Purple to Lighter Purple for 78%

    if (percentage > 90) { // Green for 92%
      colorStops.stop1 = '#22C55E';
      colorStops.stop2 = '#4ADE80';
    }
  
    return (
        <div className="relative flex items-center justify-center" style={{ width: chartSize, height: chartSize }}>
            <svg width={chartSize} height={chartSize} viewBox={`0 0 ${chartSize} ${chartSize}`}>
                <defs>
                    <linearGradient id={gradientId} x1="0%" y1="0%" x2="0%" y2="100%">
                        <stop offset="0%" stopColor={colorStops.stop1} />
                        <stop offset="100%" stopColor={colorStops.stop2} />
                    </linearGradient>
                </defs>
                <circle className="text-slate-700" stroke="currentColor" strokeWidth={strokeWidth} fill="transparent" r={radius} cx={chartSize / 2} cy={chartSize / 2} />
                <circle
                    stroke={`url(#${gradientId})`}
                    strokeWidth={strokeWidth}
                    fill="transparent"
                    r={radius}
                    cx={chartSize / 2}
                    cy={chartSize / 2}
                    strokeDasharray={circumference}
                    strokeDashoffset={offset}
                    transform={`rotate(-90 ${chartSize / 2} ${chartSize / 2})`}
                    strokeLinecap="round"
                />
            </svg>
            <div className="absolute flex flex-col items-center justify-center">
                <span className={`${isLarge ? 'text-4xl' : 'text-2xl'} font-bold text-white`}>{percentage}%</span>
                {label && <span className={`${isLarge ? 'text-sm' : 'text-xs'} text-slate-400 mt-1`}>{label}</span>}
            </div>
        </div>
    );
};

const PriorityTag = ({ type }: { type: TagType }) => {
  const tagStyles: Record<TagType, string> = {
    'High Priority': 'bg-red-500/10 text-red-400 border border-red-500/20',
    'Optimization': 'bg-purple-500/10 text-purple-400 border border-purple-500/20',
    'Medium': 'bg-yellow-500/10 text-yellow-400 border border-yellow-500/20',
    'Financial': 'bg-yellow-500/10 text-yellow-400 border border-yellow-500/20',
    'Low Priority': 'bg-green-500/10 text-green-400 border border-green-500/20',
  };
  return (
    <span className={`px-2 py-1 text-xs font-semibold rounded-md ${tagStyles[type]}`}>
      {type}
    </span>
  );
};

const RecommendationCard = ({ card }: { card: Recommendation }) => (
  <div className="bg-slate-800 rounded-xl p-6 border border-slate-700 flex flex-col hover:border-slate-600 transition-colors duration-300">
    <div className="flex-grow">
      <div className="flex justify-between items-start gap-4 mb-4">
        <h3 className="text-lg font-semibold text-slate-100">{card.title}</h3>
        <div className="flex gap-2 flex-shrink-0">
          {card.tags.map(tag => <PriorityTag key={tag} type={tag} />)}
        </div>
      </div>
      <p className="text-slate-400 text-sm mb-5 leading-relaxed">{card.description}</p>
      <div className="space-y-3 text-sm">
        {card.details.map((detail, index) => (
          <div key={index} className="flex justify-between items-center">
            <p><span className="font-semibold text-slate-400">{detail.label}: </span><span className="text-slate-300">{detail.value}</span></p>
            {detail.avatars && (
              <div className="flex items-center -space-x-2">
                {detail.avatars.map(avatar => (
                   <div key={avatar} className="w-8 h-8 rounded-full bg-slate-700 border-2 border-slate-800 flex items-center justify-center text-xs font-bold text-slate-300">
                     {avatar}
                   </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
    <div className="mt-6 pt-5 border-t border-slate-700">
      <div className="flex justify-between items-center mb-4">
        <div className="flex items-center gap-2">
          <button className="bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold py-2 px-4 rounded-lg transition-colors">Apply Recommendation</button>
          <button className="bg-slate-700/80 border border-slate-600 hover:bg-slate-700 text-slate-200 text-sm font-semibold py-2 px-4 rounded-lg transition-colors">View Details</button>
          <button className="text-slate-400 hover:text-white text-sm font-semibold transition-colors">Dismiss</button>
        </div>
      </div>
       <div className="flex justify-between items-center text-xs text-slate-500">
        <span>Generated {card.time}</span>
        <div className="flex items-center gap-2">
          <span>{card.match}% match</span>
          <RefreshCw className="h-4 w-4 cursor-pointer hover:text-slate-300 transition-colors" />
        </div>
      </div>
    </div>
  </div>
);

export default function AIRecommendationsView() {
  const filters = [
    { name: 'All', count: 6 },
    { name: 'Staffing', count: 3 },
    { name: 'Conflicts', count: 1 },
    { name: 'Priority1', count: 1, isIcon: true },
    { name: 'Priority2', count: 2, isIcon: true },
    { name: 'Workload Balance', count: 1 },
  ];

  return (
    <div className="bg-slate-900 min-h-screen text-white font-sans p-4 sm:p-6 lg:p-8">
      <header className="flex justify-between items-center mb-8">
        <div className="flex items-center gap-3">
          <Cube size={32} className="text-blue-500" />
          <span className="text-2xl font-bold text-slate-100">StaffAlloc</span>
        </div>
        <nav className="hidden md:flex items-center gap-2 bg-slate-800/80 border border-slate-700 p-1 rounded-xl">
          {['Dashboard', 'Projects', 'Staff', 'Reports', 'AI Assistant'].map((item) => (
            <a key={item} href="#" className={`text-sm font-medium px-4 py-2 rounded-lg transition-colors ${item === 'AI Assistant' ? 'bg-slate-700 text-white' : 'text-slate-300 hover:bg-slate-700/50 hover:text-white'}`}>
              {item}
            </a>
          ))}
        </nav>
        <button className="bg-slate-800 border border-slate-700 hover:bg-slate-700 text-slate-200 text-sm font-semibold py-2.5 px-5 rounded-lg transition-colors">
          Refresh Recommendations
        </button>
      </header>
      
      <main className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          <div className="flex items-center gap-3 mb-2">
            <Sparkles className="text-blue-400 h-8 w-8" />
            <h1 className="text-3xl font-bold text-slate-100">AI-Driven Staffing Recommendations</h1>
          </div>
          <p className="text-slate-400 mb-8">Smart suggestions to optimize your team allocation</p>
          
          <div className="flex items-center gap-2 mb-8 flex-wrap">
            {filters.map((filter, index) => (
              <button key={index} className={`flex items-center justify-center text-sm font-semibold rounded-full transition-colors ${
                filter.isIcon ? 'w-8 h-8' : 'px-4 py-1.5'
              } ${index === 0 ? 'bg-blue-600 text-white' : 'bg-slate-800 text-slate-300 hover:bg-slate-700 border border-slate-700'}`}>
                {!filter.isIcon && <span>{filter.name}</span>}
                <span className={`flex items-center justify-center text-xs font-medium rounded-full ${
                  filter.isIcon ? 'w-full h-full' : 'ml-2 px-2 py-0.5'
                } ${index === 0 ? 'bg-blue-500' : 'bg-slate-600 text-slate-200'}`}>
                  {filter.count}
                </span>
              </button>
            ))}
          </div>

          <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
            {recommendationsData.map((card) => <RecommendationCard key={card.id} card={card} />)}
          </div>
        </div>
        
        <aside className="lg:col-span-1">
          <div className="bg-slate-800 rounded-xl p-6 border border-slate-700 sticky top-8">
            <div className="flex items-center gap-3 mb-8">
              <BrainCircuit className="h-6 w-6 text-blue-400" />
              <h2 className="text-xl font-semibold text-slate-100">AI Insights</h2>
            </div>
            
            <div className="flex flex-col items-center gap-8">
              <DonutChart percentage={78} label="Utilized" size="large" />
              
              <div className="w-full text-sm">
                <h3 className="font-semibold text-slate-200 mb-3">Upcoming Capacity Gaps</h3>
                <div className="bg-slate-900/50 rounded-lg p-4 space-y-2 border border-slate-700">
                  <p className="text-slate-300">Dec 2023: <span className="text-red-400">-2 developers</span></p>
                  <ul className="list-disc list-inside text-slate-400 pl-2 space-y-1">
                    <li>AWS</li>
                    <li>Machine Learning</li>
                    <li>-3 data scientists</li>
                    <li>Azure</li>
                  </ul>
                </div>
              </div>
              
              <div className="w-full text-sm">
                <h3 className="font-semibold text-slate-200 mb-3">Top Skills in Demand</h3>
                <div className="bg-slate-900/50 rounded-lg p-4 border border-slate-700">
                  <div className="flex flex-wrap gap-2">
                    {['React', 'Python', 'Go', 'DevOps', 'Machine Learning', 'Data Science'].map(skill => (
                      <span key={skill} className="bg-slate-700 text-slate-300 text-xs font-medium px-2.5 py-1 rounded-full">{skill}</span>
                    ))}
                  </div>
                </div>
              </div>

              <div className="w-full border-t border-slate-700 pt-8">
                 <h3 className="font-semibold text-slate-200 mb-4 text-center text-sm">Model Accuracy</h3>
                 <div className="flex justify-center">
                    <DonutChart percentage={92} label="" size="small" />
                 </div>
              </div>

            </div>
            <p className="text-xs text-slate-500 text-center mt-8">Last Updated: 10 minutes ago</p>
          </div>
        </aside>
      </main>
    </div>
  );
}