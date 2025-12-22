import { useState, useEffect, useCallback, useRef } from 'react';

/**
 * TestTimer - Countdown timer with warning banners and auto-submit
 * 
 * Features:
 * - Countdown display (MM:SS)
 * - 5-minute warning banner
 * - 1-minute critical warning
 * - Auto-submit when time expires
 * - Pause/resume capability (for admin use)
 */
export default function TestTimer({
  initialSeconds,
  onTimeUp,
  onWarning,
  warningThresholds = [300, 60], // 5 min, 1 min in seconds
  isPaused = false,
  showWarningBanner = true
}) {
  const [remainingSeconds, setRemainingSeconds] = useState(initialSeconds);
  const [currentWarning, setCurrentWarning] = useState(null);
  const [hasAutoSubmitted, setHasAutoSubmitted] = useState(false);
  const intervalRef = useRef(null);
  const warningsShownRef = useRef(new Set());

  // Calculate warning level
  const getWarningLevel = (seconds) => {
    if (seconds <= 60) return 'critical'; // 1 minute
    if (seconds <= 300) return 'warning'; // 5 minutes
    return null;
  };

  // Format seconds as MM:SS or HH:MM:SS if over an hour
  const formatTime = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
      return `${hours}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Timer tick
  useEffect(() => {
    if (isPaused || remainingSeconds <= 0) {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      return;
    }

    intervalRef.current = setInterval(() => {
      setRemainingSeconds(prev => {
        const newTime = prev - 1;
        
        // Check warning thresholds
        warningThresholds.forEach(threshold => {
          if (newTime === threshold && !warningsShownRef.current.has(threshold)) {
            warningsShownRef.current.add(threshold);
            onWarning?.(threshold);
          }
        });
        
        return newTime;
      });
    }, 1000);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [isPaused, remainingSeconds, onWarning, warningThresholds]);

  // Handle time up
  useEffect(() => {
    if (remainingSeconds <= 0 && !hasAutoSubmitted) {
      setHasAutoSubmitted(true);
      onTimeUp?.();
    }
  }, [remainingSeconds, hasAutoSubmitted, onTimeUp]);

  // Update warning level
  useEffect(() => {
    setCurrentWarning(getWarningLevel(remainingSeconds));
  }, [remainingSeconds]);

  const warningLevel = getWarningLevel(remainingSeconds);

  return (
    <div className="relative">
      {/* Timer display */}
      <div className={`
        inline-flex items-center gap-2 px-4 py-2 rounded-lg font-mono text-lg font-bold
        ${warningLevel === 'critical' 
          ? 'bg-red-600 text-white animate-pulse' 
          : warningLevel === 'warning'
            ? 'bg-amber-500 text-white'
            : 'bg-gray-100 text-gray-800'
        }
      `}>
        <ClockIcon className={warningLevel === 'critical' ? 'animate-bounce' : ''} />
        <span>{formatTime(remainingSeconds)}</span>
      </div>

      {/* Warning banner */}
      {showWarningBanner && warningLevel && (
        <WarningBanner 
          level={warningLevel} 
          seconds={remainingSeconds} 
        />
      )}
    </div>
  );
}

/**
 * Warning Banner Component
 */
function WarningBanner({ level, seconds }) {
  const [isVisible, setIsVisible] = useState(true);
  const [isDismissed, setIsDismissed] = useState(false);

  // Auto-dismiss after 10 seconds for warning, but not for critical
  useEffect(() => {
    if (level === 'warning' && !isDismissed) {
      const timer = setTimeout(() => {
        setIsVisible(false);
      }, 10000);
      return () => clearTimeout(timer);
    }
  }, [level, isDismissed]);

  // Always show critical warnings
  useEffect(() => {
    if (level === 'critical') {
      setIsVisible(true);
      setIsDismissed(false);
    }
  }, [level]);

  if (!isVisible) return null;

  const handleDismiss = () => {
    if (level !== 'critical') {
      setIsDismissed(true);
      setIsVisible(false);
    }
  };

  const minutes = Math.ceil(seconds / 60);

  return (
    <div className={`
      fixed top-0 left-0 right-0 z-50 p-4 shadow-lg
      ${level === 'critical' 
        ? 'bg-red-600 text-white' 
        : 'bg-amber-500 text-white'
      }
    `}>
      <div className="max-w-4xl mx-auto flex items-center justify-between">
        <div className="flex items-center gap-3">
          <WarningIcon className="w-6 h-6 flex-shrink-0" />
          <div>
            <p className="font-bold text-lg">
              {level === 'critical' 
                ? '⚠️ LESS THAN 1 MINUTE REMAINING!'
                : `⏱️ ${minutes} minutes remaining`
              }
            </p>
            <p className="text-sm opacity-90">
              {level === 'critical'
                ? 'Your test will be automatically submitted when time runs out.'
                : 'Please start wrapping up your answers.'
              }
            </p>
          </div>
        </div>
        {level !== 'critical' && (
          <button
            onClick={handleDismiss}
            className="px-4 py-1 bg-white/20 hover:bg-white/30 rounded-lg text-sm font-medium transition-colors"
          >
            Dismiss
          </button>
        )}
      </div>
    </div>
  );
}

/**
 * Standalone Timer Hook for use in other components
 */
export function useTestTimer(initialSeconds, onTimeUp) {
  const [remainingSeconds, setRemainingSeconds] = useState(initialSeconds);
  const [isExpired, setIsExpired] = useState(false);

  useEffect(() => {
    if (remainingSeconds <= 0) {
      setIsExpired(true);
      onTimeUp?.();
      return;
    }

    const interval = setInterval(() => {
      setRemainingSeconds(prev => prev - 1);
    }, 1000);

    return () => clearInterval(interval);
  }, [remainingSeconds, onTimeUp]);

  return {
    remainingSeconds,
    isExpired,
    formattedTime: formatTimeUtil(remainingSeconds),
    warningLevel: remainingSeconds <= 60 ? 'critical' : remainingSeconds <= 300 ? 'warning' : null
  };
}

function formatTimeUtil(seconds) {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}

// Icons
function ClockIcon({ className = '' }) {
  return (
    <svg className={`w-5 h-5 ${className}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  );
}

function WarningIcon({ className = '' }) {
  return (
    <svg className={className} fill="currentColor" viewBox="0 0 20 20">
      <path fillRule="evenodd" d="M8.485 2.495c.673-1.167 2.357-1.167 3.03 0l6.28 10.875c.673 1.167-.17 2.625-1.516 2.625H3.72c-1.347 0-2.189-1.458-1.515-2.625L8.485 2.495zM10 5a.75.75 0 01.75.75v3.5a.75.75 0 01-1.5 0v-3.5A.75.75 0 0110 5zm0 9a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
    </svg>
  );
}
