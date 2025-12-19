import { useState } from 'react';

export default function BandScoreSlider({ label, value, onChange }) {
  return (
    <div className="space-y-2">
      <div className="flex justify-between items-center">
        <label className="text-sm font-semibold text-gray-700">{label}</label>
        <span className="text-lg font-bold text-primary-600">{value.toFixed(1)}</span>
      </div>
      <input
        type="range"
        min="0"
        max="9"
        step="0.5"
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
        className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-primary-600"
      />
      <div className="flex justify-between text-xs text-gray-500">
        <span>0</span>
        <span>3</span>
        <span>6</span>
        <span>9</span>
      </div>
    </div>
  );
}
