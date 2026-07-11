import React, { useState, useEffect } from 'react';
import MissionCard from '../../../components/mission-card';
import Timeline from '../../../components/timeline';

export default function MissionDashboard({ params }: { params: { id: string } }) {
  const { id } = params;
  const [mission, setMission] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // In a real app, we would fetch from our api client
    // For now, setting mock initial state
    setLoading(true);
    setTimeout(() => {
      setMission({
        id,
        title: "Initialize Core Architecture",
        status: "ACTIVE",
        progress: 45,
        description: "Set up the primary foundation for the OmniMind system."
      });
      setLoading(false);
    }, 500);
  }, [id]);

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-lg">Loading mission state...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-red-500">Error: {error}</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 max-w-6xl">
      <h1 className="text-3xl font-bold mb-8">Mission Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-1">
          <MissionCard mission={mission} />
        </div>
        
        <div className="md:col-span-2">
          <Timeline missionId={id} />
        </div>
      </div>
    </div>
  );
}
