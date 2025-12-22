import { useState, useRef, useEffect, useCallback } from 'react';

/**
 * RestrictedAudioPlayer - Audio player with IELTS-style restrictions
 * 
 * Features:
 * - Play count limit (default: 1 play only)
 * - Backward seeking disabled
 * - Visual feedback for remaining plays
 * - Locked state after plays exhausted
 */
export default function RestrictedAudioPlayer({
  src,
  maxPlays = 1,
  onPlayCountChange,
  onEnded,
  disabled = false
}) {
  const audioRef = useRef(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [playCount, setPlayCount] = useState(0);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [lastValidTime, setLastValidTime] = useState(0);
  const [isLocked, setIsLocked] = useState(false);

  // Check if player is exhausted
  const isExhausted = playCount >= maxPlays;

  // Handle play button click
  const handlePlay = useCallback(() => {
    if (isExhausted || disabled || !audioRef.current) return;

    if (isPlaying) {
      // Pause is allowed
      audioRef.current.pause();
      setIsPlaying(false);
    } else {
      // Starting a new play
      if (audioRef.current.ended || audioRef.current.currentTime === 0) {
        setPlayCount(prev => {
          const newCount = prev + 1;
          onPlayCountChange?.(newCount);
          return newCount;
        });
      }
      audioRef.current.play();
      setIsPlaying(true);
    }
  }, [isExhausted, disabled, isPlaying, onPlayCountChange]);

  // Handle time update - prevent backward seeking
  const handleTimeUpdate = useCallback(() => {
    if (!audioRef.current) return;
    
    const current = audioRef.current.currentTime;
    
    // Only allow forward movement or very small backward (to handle normal playback jitter)
    if (current < lastValidTime - 0.5) {
      // Attempted to seek backward - reset to last valid position
      audioRef.current.currentTime = lastValidTime;
    } else {
      setLastValidTime(current);
      setCurrentTime(current);
    }
  }, [lastValidTime]);

  // Handle seeking attempt
  const handleSeeking = useCallback(() => {
    if (!audioRef.current) return;
    
    const seekTime = audioRef.current.currentTime;
    
    // Only allow seeking forward from current position
    if (seekTime < lastValidTime - 0.5) {
      audioRef.current.currentTime = lastValidTime;
    }
  }, [lastValidTime]);

  // Handle audio ended
  const handleEnded = useCallback(() => {
    setIsPlaying(false);
    setLastValidTime(0);
    setCurrentTime(0);
    
    if (audioRef.current) {
      audioRef.current.currentTime = 0;
    }
    
    // Check if all plays are exhausted
    if (playCount >= maxPlays) {
      setIsLocked(true);
    }
    
    onEnded?.();
  }, [playCount, maxPlays, onEnded]);

  // Handle metadata loaded
  const handleLoadedMetadata = useCallback(() => {
    if (audioRef.current) {
      setDuration(audioRef.current.duration);
    }
  }, []);

  // Format time as MM:SS
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Calculate progress percentage
  const progress = duration > 0 ? (currentTime / duration) * 100 : 0;

  return (
    <div className={`rounded-lg border ${isLocked ? 'bg-gray-100 border-gray-300' : 'bg-white border-gray-200'} p-4 shadow-sm`}>
      {/* Hidden audio element */}
      <audio
        ref={audioRef}
        src={src}
        onTimeUpdate={handleTimeUpdate}
        onSeeking={handleSeeking}
        onEnded={handleEnded}
        onLoadedMetadata={handleLoadedMetadata}
        onPlay={() => setIsPlaying(true)}
        onPause={() => setIsPlaying(false)}
      />

      {/* Player controls */}
      <div className="flex items-center gap-4">
        {/* Play/Pause button */}
        <button
          onClick={handlePlay}
          disabled={isExhausted || disabled}
          className={`w-12 h-12 rounded-full flex items-center justify-center transition-all ${
            isExhausted || disabled
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : isPlaying
                ? 'bg-red-500 hover:bg-red-600 text-white'
                : 'bg-primary-600 hover:bg-primary-700 text-white'
          }`}
          title={isExhausted ? 'No plays remaining' : isPlaying ? 'Pause' : 'Play'}
        >
          {isPlaying ? (
            <PauseIcon />
          ) : (
            <PlayIcon />
          )}
        </button>

        {/* Progress bar */}
        <div className="flex-1">
          <div className="relative h-2 bg-gray-200 rounded-full overflow-hidden">
            <div 
              className="absolute left-0 top-0 h-full bg-primary-500 transition-all duration-100"
              style={{ width: `${progress}%` }}
            />
          </div>
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>{formatTime(currentTime)}</span>
            <span>{formatTime(duration)}</span>
          </div>
        </div>

        {/* Play count indicator */}
        <div className={`text-sm font-medium px-3 py-1 rounded-full ${
          isExhausted 
            ? 'bg-red-100 text-red-700' 
            : 'bg-green-100 text-green-700'
        }`}>
          {isExhausted ? (
            <span>No plays left</span>
          ) : (
            <span>{maxPlays - playCount} play{maxPlays - playCount !== 1 ? 's' : ''} left</span>
          )}
        </div>
      </div>

      {/* Warning message when locked */}
      {isLocked && (
        <div className="mt-3 text-sm text-amber-700 bg-amber-50 border border-amber-200 rounded-lg p-3 flex items-center gap-2">
          <WarningIcon />
          <span>You have used all available plays for this audio. You cannot replay it.</span>
        </div>
      )}

      {/* Instructions */}
      {!isLocked && !isExhausted && (
        <div className="mt-2 text-xs text-gray-500">
          ⚠️ You can only play this audio once. Rewinding is disabled.
        </div>
      )}
    </div>
  );
}

// Icon components
function PlayIcon() {
  return (
    <svg className="w-5 h-5 ml-1" fill="currentColor" viewBox="0 0 20 20">
      <path d="M6.3 2.841A1.5 1.5 0 004 4.11V15.89a1.5 1.5 0 002.3 1.269l9.344-5.89a1.5 1.5 0 000-2.538L6.3 2.84z" />
    </svg>
  );
}

function PauseIcon() {
  return (
    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
      <path fillRule="evenodd" d="M6 4a1 1 0 011 1v10a1 1 0 11-2 0V5a1 1 0 011-1zm8 0a1 1 0 011 1v10a1 1 0 11-2 0V5a1 1 0 011-1z" clipRule="evenodd" />
    </svg>
  );
}

function WarningIcon() {
  return (
    <svg className="w-5 h-5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
      <path fillRule="evenodd" d="M8.485 2.495c.673-1.167 2.357-1.167 3.03 0l6.28 10.875c.673 1.167-.17 2.625-1.516 2.625H3.72c-1.347 0-2.189-1.458-1.515-2.625L8.485 2.495zM10 5a.75.75 0 01.75.75v3.5a.75.75 0 01-1.5 0v-3.5A.75.75 0 0110 5zm0 9a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
    </svg>
  );
}
