import { useState, useRef } from 'react';

export default function SpeakingSection({ part, question }) {
  const [isRecording, setIsRecording] = useState(false);
  const [recordedBlob, setRecordedBlob] = useState(null);
  const [preparationTime, setPreparationTime] = useState(part === 2 ? 60 : 0);
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);
  
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      chunksRef.current = [];
      
      mediaRecorderRef.current.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data);
        }
      };
      
      mediaRecorderRef.current.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
        setRecordedBlob(blob);
        stream.getTracks().forEach(track => track.stop());
      };
      
      mediaRecorderRef.current.start();
      setIsRecording(true);
    } catch (error) {
      alert('Microphone access denied. Please allow microphone access to record.');
    }
  };
  
  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };
  
  const playRecording = () => {
    if (recordedBlob) {
      const audio = new Audio(URL.createObjectURL(recordedBlob));
      audio.play();
    }
  };
  
  return (
    <div className="space-y-6">
      {/* Part Header */}
      <div className="bg-purple-50 border border-purple-200 rounded-lg p-6">
        <h3 className="font-bold text-gray-900 mb-2">
          Speaking Part {part}
        </h3>
        <p className="text-gray-700">
          {question}
        </p>
      </div>
      
      {/* Preparation Timer (Part 2 only) */}
      {part === 2 && preparationTime > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-center">
          <p className="font-semibold text-yellow-800">
            Preparation Time: {preparationTime}s
          </p>
          <p className="text-sm text-yellow-700 mt-1">
            You have 1 minute to prepare your response
          </p>
        </div>
      )}
      
      {/* Recording Interface */}
      <div className="bg-white border-2 border-dashed border-gray-300 rounded-lg p-8">
        <div className="text-center">
          {!isRecording && !recordedBlob && (
            <>
              <div className="text-6xl mb-4">🎤</div>
              <button
                onClick={startRecording}
                className="bg-red-600 hover:bg-red-700 text-white px-8 py-4 rounded-lg font-bold text-lg transition"
              >
                Start Recording
              </button>
              <p className="text-sm text-gray-600 mt-3">
                Click to start recording your response
              </p>
            </>
          )}
          
          {isRecording && (
            <>
              <div className="text-6xl mb-4 animate-pulse">🔴</div>
              <p className="text-lg font-bold text-red-600 mb-4">Recording...</p>
              <button
                onClick={stopRecording}
                className="bg-gray-600 hover:bg-gray-700 text-white px-8 py-4 rounded-lg font-bold text-lg transition"
              >
                Stop Recording
              </button>
            </>
          )}
          
          {recordedBlob && !isRecording && (
            <>
              <div className="text-6xl mb-4">✅</div>
              <p className="text-lg font-bold text-green-600 mb-4">Recording Complete!</p>
              <div className="flex justify-center space-x-3">
                <button
                  onClick={playRecording}
                  className="bg-primary-600 hover:bg-primary-700 text-white px-6 py-3 rounded-lg font-semibold transition"
                >
                  🔊 Play Recording
                </button>
                <button
                  onClick={() => {
                    setRecordedBlob(null);
                    chunksRef.current = [];
                  }}
                  className="bg-gray-200 hover:bg-gray-300 text-gray-700 px-6 py-3 rounded-lg font-semibold transition"
                >
                  Re-record
                </button>
              </div>
            </>
          )}
        </div>
      </div>
      
      {/* Instructions */}
      <div className="text-sm text-gray-600 bg-gray-50 rounded-lg p-4">
        <p className="font-semibold mb-2">Recording Tips:</p>
        <ul className="list-disc list-inside space-y-1">
          <li>Find a quiet place</li>
          <li>Speak clearly and at a normal pace</li>
          <li>Take your time to think before answering</li>
          <li>You can listen to your recording before submitting</li>
        </ul>
      </div>
    </div>
  );
}
