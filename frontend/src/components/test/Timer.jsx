import { useState, useEffect } from 'react';

export default function Timer({ duration, onTimeUp }) {
  const [timeLeft, setTimeLeft] = useState(duration);
  
  useEffect(() => {
    setTimeLeft(duration);
  }, [duration]);

  useEffect(() => {
    if (timeLeft <= 0) {
      onTimeUp && onTimeUp();
      return;
    }
    
    const timer = setInterval(() => {
      setTimeLeft((prev) => prev - 1);
    }, 1000);
    
    return () => clearInterval(timer);
  }, [timeLeft, onTimeUp]);
  
  const formatTime = (seconds) => {
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hrs > 0) {
      return `${hrs}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };
  
  const isWarning = timeLeft < 300; // Last 5 minutes
  const isCritical = timeLeft < 60; // Last 1 minute
  
  return (
    <div className={`
      px-4 py-2 rounded-lg font-mono text-lg font-bold
      ${isCritical ? 'bg-red-100 text-red-700 animate-pulse' :
        isWarning ? 'bg-yellow-100 text-yellow-700' :
        'bg-primary-100 text-primary-700'}
    `}>
      ⏱️ {formatTime(timeLeft)}
    </div>
  );
}
