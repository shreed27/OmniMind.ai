import React from 'react';

export default function MissionCard({ mission }: { mission: any }) {
  if (!mission) {
    return <div className="border rounded-lg p-4 bg-gray-50 text-gray-500">No mission data</div>;
  }

  return (
    <div className="border rounded-lg p-6 bg-white shadow-sm flex flex-col gap-4">
      <div className="flex justify-between items-start">
        <h2 className="text-xl font-semibold">{mission.title}</h2>
        <span className="px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800">
          {mission.status}
        </span>
      </div>
      
      <p className="text-gray-600 text-sm">
        {mission.description}
      </p>
      
      <div>
        <div className="flex justify-between text-sm mb-1">
          <span>Progress</span>
          <span>{mission.progress}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className="bg-blue-600 h-2 rounded-full" 
            style={{ width: `${mission.progress}%` }}
          ></div>
        </div>
      </div>
    </div>
  );
}
