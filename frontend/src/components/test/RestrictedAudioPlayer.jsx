import { useState, useRef, useEffect } from 'react';

export default function RestrictedAudioPlayer({ src }) {
  const audioRef = useRef(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [hasPlayed, setHasPlayed] = useState(false);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const updateProgress = () => {
      if (audio.duration) {
        setProgress((audio.currentTime / audio.duration) * 100);
      }
    };

    const handleEnded = () => {
      setIsPlaying(false);
      setHasPlayed(true);
      setProgress(100);
    };

    // Prevent pausing by user interaction if possible (though hiding controls is the main way)
    const handlePause = (e) => {
      if (!audio.ended && !audio.seeking) {
        // Force resume if paused not by ending
        audio.play().catch(() => {});
      }
    };

    audio.addEventListener('timeupdate', updateProgress);
    audio.addEventListener('ended', handleEnded);
    audio.addEventListener('pause', handlePause);

    return () => {
      audio.removeEventListener('timeupdate', updateProgress);
      audio.removeEventListener('ended', handleEnded);
      audio.removeEventListener('pause', handlePause);
    };
  }, []);

  const handleStart = () => {
    if (audioRef.current) {
      audioRef.current.play().catch(err => {
        console.error("Audio play failed:", err);
        alert("Could not play audio. Please check your permissions.");
      });
      setIsPlaying(true);
    }
  };

  return (
    <div className="w-full bg-white rounded-lg border border-gray-200 p-4 shadow-sm">
      <audio 
        ref={audioRef} 
        src={src} 
        className="hidden" 
        preload="auto"
      />

      {!hasPlayed && !isPlaying && (
        <div className="text-center py-4">
          <p className="text-gray-600 mb-4 font-medium">
            ⚠️ Warning: The audio can only be played ONCE. You cannot pause or replay it.
          </p>
          <button
            onClick={handleStart}
            className="px-6 py-3 bg-primary-600 hover:bg-primary-700 text-white rounded-full font-bold shadow-md transition-transform transform hover:scale-105 flex items-center gap-2 mx-auto"
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-6 h-6">
              <path fillRule="evenodd" d="M4.5 5.653c0-1.426 1.529-2.33 2.779-1.643l11.54 6.348c1.295.712 1.295 2.573 0 3.285L7.28 19.991c-1.25.687-2.779-.217-2.779-1.643V5.653z" clipRule="evenodd" />
            </svg>
            Start Audio
          </button>
        </div>
      )}

      {isPlaying && (
        <div className="py-2">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
            <span className="text-primary-700 font-semibold">Audio Playing...</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2.5 overflow-hidden">
            <div 
              className="bg-primary-600 h-2.5 rounded-full transition-all duration-300 ease-linear" 
              style={{ width: `${progress}%` }}
            ></div>
          </div>
          <p className="text-xs text-gray-500 mt-2 text-center">Do not refresh the page.</p>
        </div>
      )}

      {hasPlayed && (
        <div className="text-center py-2 flex items-center justify-center gap-2 text-gray-500">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
            <path fillRule="evenodd" d="M2.25 12c0-5.385 4.365-9.75 9.75-9.75s9.75 4.365 9.75 9.75-4.365 9.75-9.75 9.75S2.25 17.385 2.25 12zm13.36-1.814a.75.75 0 10-1.22-.872l-3.236 4.53L9.53 12.22a.75.75 0 00-1.06 1.06l2.25 2.25a.75.75 0 001.14-.094l3.75-5.25z" clipRule="evenodd" />
          </svg>
          <span className="font-medium">Audio playback completed</span>
        </div>
      )}
    </div>
  );
}
