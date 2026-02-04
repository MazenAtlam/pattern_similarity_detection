import { useState, useEffect } from 'react';
import { getSequenceCount, detectPassSequence } from '../../utils/api';
import { Search } from "lucide-react";


const stages = [
  "Group Stage",
  "Round of 16",
  "Quarter-Finals",
  "Semi-Finals",
  "Final",
];

const groups = ["A", "B", "C", "D", "E", "F", "G", "H"];

const matchs = {
  "Group Stage": {
    "A": [
      ["Qatar vs Ecuador (ID: 3814)", 3814],
      ["Senegal vs Netherlands (ID: 3812)", 3812],
      ["Qatar vs Senegal (ID: 3829)", 3829],
      ["Netherlands vs Ecuador (ID: 3830)", 3830],
      ["Ecuador vs Senegal (ID: 3844)", 3844],
      ["Netherlands vs Qatar (ID: 3845)", 3845]
    ],
    "B": [
      ["England vs Iran (ID: 3813)", 3813],
      ["United States vs Wales (ID: 3815)", 3815],
      ["Wales vs Iran (ID: 3828)", 3828],
      ["England vs United States (ID: 3831)", 3831],
      ["Wales vs England (ID: 3846)", 3846],
      ["Iran vs United States (ID: 3847)", 3847]
    ],
    "C": [
      ["Argentina vs Saudi Arabia (ID: 3816)", 3816],
      ["Mexico vs Poland (ID: 3818)", 3818],
      ["Poland vs Saudi Arabia (ID: 3833)", 3833],
      ["Argentina vs Mexico (ID: 3835)", 3835],
      ["Poland vs Argentina (ID: 3850)", 3850],
      ["Saudi Arabia vs Mexico (ID: 3851)", 3851]
    ],
    "D": [
      ["Denmark vs Tunisia (ID: 3817)", 3817],
      ["France vs Australia (ID: 3819)", 3819],
      ["Tunisia vs Australia (ID: 3832)", 3832],
      ["France vs Denmark (ID: 3834)", 3834],
      ["Australia vs Denmark (ID: 3848)", 3848],
      ["Tunisia vs France (ID: 3849)", 3849]
    ],
    "E": [
      ["Germany vs Japan (ID: 3821)", 3821],
      ["Spain vs Costa Rica (ID: 3822)", 3822],
      ["Japan vs Costa Rica (ID: 3836)", 3836],
      ["Spain vs Germany (ID: 3839)", 3839],
      ["Japan vs Spain (ID: 3854)", 3854],
      ["Costa Rica vs Germany (ID: 3855)", 3855]
    ],
    "F": [
      ["Morocco vs Croatia (ID: 3820)", 3820],
      ["Belgium vs Canada (ID: 3823)", 3823],
      ["Belgium vs Morocco (ID: 3837)", 3837],
      ["Croatia vs Canada (ID: 3838)", 3838],
      ["Croatia vs Belgium (ID: 3852)", 3852],
      ["Canada vs Morocco (ID: 3853)", 3853]
    ],
    "G": [
      ["Switzerland vs Cameroon (ID: 3824)", 3824],
      ["Brazil vs Serbia (ID: 3827)", 3827],
      ["Cameroon vs Serbia (ID: 3840)", 3840],
      ["Brazil vs Switzerland (ID: 3842)", 3842],
      ["Serbia vs Switzerland (ID: 3858)", 3858],
      ["Cameroon vs Brazil (ID: 3859)", 3859]
    ],
    "H": [
      ["Uruguay vs South Korea (ID: 3825)", 3825],
      ["Portugal vs Ghana (ID: 3826)", 3826],
      ["South Korea vs Ghana (ID: 3841)", 3841],
      ["Portugal vs Uruguay (ID: 3843)", 3843],
      ["Ghana vs Uruguay (ID: 3856)", 3856],
      ["South Korea vs Portugal (ID: 3857)", 3857]
    ]
  },
  "Round of 16": [
    ["Netherlands vs United States (ID: 10502)", 10502],
    ["Argentina vs Australia (ID: 10503)", 10503],
    ["France vs Poland (ID: 10504)", 10504],
    ["England vs Senegal (ID: 10505)", 10505],
    ["Japan vs Croatia (ID: 10506)", 10506],
    ["Brazil vs South Korea (ID: 10507)", 10507],
    ["Morocco vs Spain (ID: 10508)", 10508],
    ["Portugal vs Switzerland (ID: 10509)", 10509]
  ],
  "Quarter-Finals": [
    ["Croatia vs Brazil (ID: 10510)", 10510],
    ["Netherlands vs Argentina (ID: 10511)", 10511],
    ["Morocco vs Portugal (ID: 10512)", 10512],
    ["England vs France (ID: 10513)", 10513]
  ],
  "Semi-Finals": [
    ["Argentina vs Croatia (ID: 10514)", 10514],
    ["France vs Morocco (ID: 10515)", 10515]
  ],
  "Final": [
    ["Argentina vs France (ID: 10517)", 10517],
    ["Croatia vs Morocco (ID: 10516)", 10516]
  ]
};

const FifaForm = ({ isLoading, onSearchSuccess, onReset, onSearchStart }) => {
  // UI State
  const [selectedStage, setSelectedStage] = useState('');
  const [selectedGroup, setSelectedGroup] = useState('');
  const [selectedMatch, setSelectedMatch] = useState('');
  const [numPasses, setNumPasses] = useState(3);
  const [sequenceIndex, setSequenceIndex] = useState(0);

  // Logic State
  const [maxSeqIndex, setMaxSeqIndex] = useState(0);
  const [sequencePath, setSequencePath] = useState('');
  const [isCountLoading, setIsCountLoading] = useState(false);

  // Derived options
  const isGroupStage = selectedStage === 'Group Stage';

  // 1. Handle Stage Selection
  const handleStageChange = (e) => {
    const newStage = e.target.value;
    setSelectedStage(newStage);
    setSelectedMatch(''); // Reset match when stage changes
    if (onReset) onReset(); // Clear results
    // If not group stage, reset group
    if (newStage !== 'Group Stage') {
      setSelectedGroup('');
    }
  };

  // 2. Handle Group Selection
  const handleGroupChange = (e) => {
    setSelectedGroup(e.target.value);
    setSelectedMatch(''); // Reset match when group changes
    if (onReset) onReset(); // Clear results
  };

  // Helper: Get available matches based on selection
  const getMatchOptions = () => {
    if (!selectedStage) return [];

    if (selectedStage === 'Group Stage') {
      if (!selectedGroup) return [];
      return matchs['Group Stage'][selectedGroup] || [];
    }

    return matchs[selectedStage] || [];
  };

  // 3. Handle Match & NumPasses Change -> Update Sequence Path
  const updateSequencePath = (matchId, passes) => {
    if (!matchId) return;
    const baseFolder = 'data/fifa';
    const path = `${baseFolder}/fingerprints_${passes}pass.pkl`;
    setSequencePath(path);
  };

  const handleMatchChange = (e) => {
    const matchId = e.target.value;
    setSelectedMatch(matchId);
    if (onReset) onReset(); // Clear results
    updateSequencePath(matchId, numPasses);
  };

  const handleNumPassesChange = (e) => {
    // Only update UI state, do not trigger fetch
    const passes = parseInt(e.target.value, 10);
    setNumPasses(passes);
    if (onReset) onReset(); // Reset results immediately on change
  };

  const handleNumPassesCommit = () => {
    // Trigger sequence path update (and subsequent fetch) on slider release
    updateSequencePath(selectedMatch, numPasses);
  };

  // 4. Fetch Count when Sequence Path changes
  useEffect(() => {
    const fetchCount = async () => {
      if (!sequencePath) return;

      setIsCountLoading(true);
      try {
        // Fetch count
        const response = await getSequenceCount(sequencePath, selectedMatch);
        if (response && typeof response.sequences_count === 'number') {
          setMaxSeqIndex(response.sequences_count);
          setSequenceIndex(0); // Reset index
        } else {
          console.warn("Invalid count response:", response);
          setMaxSeqIndex(0);
        }
      } catch (error) {
        console.error("Failed to fetch sequence count:", error);
        setMaxSeqIndex(0);
      } finally {
        setIsCountLoading(false);
      }
    };

    fetchCount();
  }, [sequencePath, selectedMatch]);

  // 5. Handle Sequence Index Change (onRelease)
  const handleSeqIndexChange = (e) => {
    setSequenceIndex(parseInt(e.target.value, 10));
    if (onReset) onReset(); // Reset results immediately on change
  };

  const handleSeqIndexCommit = async () => {
    // Trigger detection API
    try {
      if (onSearchStart) onSearchStart();
      console.log(`Detecting sequence: Path=${sequencePath}, Index=${sequenceIndex}`);
      const response = await detectPassSequence({
        sequence_path: sequencePath,
        match_id: selectedMatch,
        sequence_index: sequenceIndex
      });
      console.log(response);
      if (response && response.status === 'success') {
        if (onSearchSuccess) {
          onSearchSuccess(response);
        }
      }
    } catch (error) {
      console.error("Error triggering detection:", error);
    }
  };

  return (
    <div className="card glass-card p-6">
      <div className="card-header">
        <h5 className="card-title text-xl font-bold mb-4 flex items-center gap-2">
          <Search
            style={{ width: "20px", height: "20px", color: "var(--primary)" }}
          />
          Search Match Sequences
        </h5>

        <div className="card-body grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
          <div className="row g-3 mb-4 w-full">
            {/* Stage Selection */}
            <div className="col-md-8 col-lg-4">
              <label className="form-label block text-sm font-medium mb-1">Stage</label>
              <select
                value={selectedStage}
                onChange={handleStageChange}
                className="form-select bg-light w-full"
              >
                <option value="">Select Stage</option>
                {stages.map(stage => (
                  <option key={stage} value={stage}>{stage}</option>
                ))}
              </select>
            </div>

            {/* Group Selection */}
            <div className="col-md-8 col-lg-4">
              <label className={`form-label block text-sm font-medium mb-1 ${!isGroupStage ? 'text-gray-500' : ''}`}>
                Group
              </label>
              <select
                value={selectedGroup}
                onChange={handleGroupChange}
                disabled={!isGroupStage}
                className="form-select bg-light w-full"
              >
                <option value="">Select Group</option>
                {groups.map(group => (
                  <option key={group} value={group}>Group {group}</option>
                ))}
              </select>
            </div>

            {/* Match Selection */}
            <div className="col-md-8 col-lg-4">
              <label className="form-label block text-sm font-medium mb-1">Match</label>
              <select
                value={selectedMatch}
                onChange={handleMatchChange}
                disabled={!selectedStage || (isGroupStage && !selectedGroup)}
                className="form-select bg-light w-full"
              >
                <option value="">Select Match</option>
                {getMatchOptions().map(([label, id]) => (
                  <option key={id} value={id}>{label}</option>
                ))}
              </select>
            </div>
          </div>
        </div>

        <div className={`grid grid-cols-1 ${maxSeqIndex > 0 ? 'md:grid-cols-2' : ''} gap-8 mb-6`}>
          {/* Number of Passes Slider */}
          <div className="form-group">
            <label className="block text-sm font-medium mb-2">
              Number of Passes: <span className="text-blue-400 font-bold">{numPasses}</span>
            </label>
            <input
              type="range"
              min="1"
              max="10"
              value={numPasses}
              onChange={handleNumPassesChange}
              onMouseUp={handleNumPassesCommit}
              onTouchEnd={handleNumPassesCommit}
              className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
            />
          </div>

          {/* Sequence Index Slider (Conditional) */}
          {maxSeqIndex > 0 && (
            <div className="form-group animate-fade-in">
              <label className="block text-sm font-medium mb-2">
                Sequence Index: <span className="text-green-400 font-bold">{sequenceIndex} / {maxSeqIndex}</span>
              </label>
              <input
                type="range"
                min="0"
                max={maxSeqIndex}
                value={sequenceIndex}
                onChange={handleSeqIndexChange}
                onMouseUp={handleSeqIndexCommit}
                onTouchEnd={handleSeqIndexCommit}
                className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-green-500"
              />
            </div>
          )}
        </div>

        {isCountLoading && (
          <div className="flex justify-center items-center py-2 animate-fade-in">
            <div className="spinner-border text-primary" role="status" style={{ width: '1.5rem', height: '1.5rem' }}>
              <span className="visually-hidden">Loading...</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default FifaForm;