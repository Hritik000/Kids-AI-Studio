"use client";

import React, { useState } from 'react';
import { Sparkles, Rocket, Palette, Volume2, Wand2, Compass } from 'lucide-react';

interface PromptGeneratorProps {
  onGenerate: (prompt: string, ageGroup: string, aspectRatio: string) => void;
  isGenerating: boolean;
}

const PRESET_PROMPTS = [
  { prompt: "Dinosaurs learn colors at a birthday party", icon: "🦖", tag: "Educational" },
  { prompt: "Baby Animals explore the enchanted rainforest", icon: "🦁", tag: "Nature" },
  { prompt: "Little Astronauts discover shapes on Mars", icon: "🚀", tag: "Science" },
  { prompt: "Friendly Monsters practice bedtime routines", icon: "🌙", tag: "Bedtime" },
];

export const PromptGenerator: React.FC<PromptGeneratorProps> = ({ onGenerate, isGenerating }) => {
  const [prompt, setPrompt] = useState("");
  const [ageGroup, setAgeGroup] = useState("3-6 years");
  const [aspectRatio, setAspectRatio] = useState("16:9");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim() || isGenerating) return;
    onGenerate(prompt, ageGroup, aspectRatio);
  };

  return (
    <div className="w-full max-w-4xl mx-auto glass-panel p-8 rounded-3xl border border-white/10 shadow-2xl relative overflow-hidden">
      {/* Background Ambient Glow */}
      <div className="absolute -top-24 -left-24 w-60 h-60 bg-purple-600/20 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute -bottom-24 -right-24 w-60 h-60 bg-blue-600/20 rounded-full blur-3xl pointer-events-none" />

      <div className="relative z-10">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 rounded-xl bg-purple-500/10 border border-purple-500/20 text-purple-400">
            <Wand2 className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-white tracking-tight">Create YouTube Kids Video</h2>
            <p className="text-sm text-gray-400">Enter a simple topic or click a preset to launch the 5 AI agents</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6 mt-6">
          {/* Main Prompt Input */}
          <div className="relative">
            <input
              type="text"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="e.g., Dinosaurs learn colors at the beach..."
              className="w-full px-6 py-4 rounded-2xl bg-black/40 border border-white/15 text-white placeholder-gray-500 text-lg focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 transition-all"
              disabled={isGenerating}
            />
            <button
              type="submit"
              disabled={!prompt.trim() || isGenerating}
              className="absolute right-3 top-3 bottom-3 px-6 rounded-xl gradient-button text-white font-semibold flex items-center gap-2 shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isGenerating ? (
                <>
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  <span>Generating Video...</span>
                </>
              ) : (
                <>
                  <Rocket className="w-5 h-5" />
                  <span>Create Video</span>
                </>
              )}
            </button>
          </div>

          {/* Quick Presets */}
          <div>
            <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3 flex items-center gap-2">
              <Compass className="w-4 h-4 text-purple-400" />
              Popular Inspiration Presets
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {PRESET_PROMPTS.map((preset, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => setPrompt(preset.prompt)}
                  className="p-3.5 rounded-xl glass-panel-interactive text-left flex items-start justify-between gap-3 group"
                >
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">{preset.icon}</span>
                    <span className="text-sm font-medium text-gray-200 group-hover:text-white transition-colors">
                      {preset.prompt}
                    </span>
                  </div>
                  <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-purple-500/10 text-purple-300 border border-purple-500/20">
                    {preset.tag}
                  </span>
                </button>
              ))}
            </div>
          </div>

          {/* Options Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
            {/* Age Group */}
            <div className="p-4 rounded-xl bg-white/5 border border-white/10">
              <label className="block text-xs font-medium text-gray-400 mb-2 flex items-center gap-2">
                <Palette className="w-4 h-4 text-blue-400" />
                Target Audience Age
              </label>
              <select
                value={ageGroup}
                onChange={(e) => setAgeGroup(e.target.value)}
                className="w-full bg-black/60 border border-white/10 rounded-lg px-3 py-2 text-sm text-gray-200 focus:outline-none focus:border-purple-500"
              >
                <option value="2-4 years">Toddlers (2-4 years)</option>
                <option value="3-6 years">Preschool (3-6 years)</option>
                <option value="7-10 years">Early Elementary (7-10 years)</option>
              </select>
            </div>

            {/* Aspect Ratio */}
            <div className="p-4 rounded-xl bg-white/5 border border-white/10">
              <label className="block text-xs font-medium text-gray-400 mb-2 flex items-center gap-2">
                <Volume2 className="w-4 h-4 text-pink-400" />
                Video Aspect Ratio
              </label>
              <select
                value={aspectRatio}
                onChange={(e) => setAspectRatio(e.target.value)}
                className="w-full bg-black/60 border border-white/10 rounded-lg px-3 py-2 text-sm text-gray-200 focus:outline-none focus:border-purple-500"
              >
                <option value="16:9">YouTube Standard (16:9 Landscape)</option>
                <option value="9:16">YouTube Shorts (9:16 Portrait)</option>
              </select>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};
