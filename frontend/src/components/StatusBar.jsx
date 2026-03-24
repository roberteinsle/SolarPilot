/**
 * StatusBar-Komponente: Header mit Online-Status und Timestamp.
 */

import React from 'react';

const StatusBar = ({ lastUpdate, error }) => {
  return (
    <div className="bg-gray-800 text-white p-4 shadow-md">
      <div className="container mx-auto flex justify-between items-center">
        {/* Links: Titel */}
        <div className="flex items-center gap-4">
          <h1 className="text-2xl font-bold">☀️ SolarPilot</h1>
          <span className="text-sm text-gray-400 hidden md:inline">
            Phase 1 - Fundament
          </span>
        </div>

        {/* Rechts: Status */}
        <div className="flex items-center gap-4">
          {/* Fehler-Anzeige */}
          {error && (
            <div className="bg-red-500 px-3 py-1 rounded text-sm">
              ⚠️ {error}
            </div>
          )}

          {/* Letzte Aktualisierung */}
          {lastUpdate && !error && (
            <div className="text-sm text-gray-400 hidden sm:block">
              Aktualisiert: {lastUpdate.toLocaleTimeString('de-DE')}
            </div>
          )}

          {/* Online/Offline-Indikator */}
          <div className="flex items-center gap-2">
            <div
              className={`w-3 h-3 rounded-full ${
                error ? 'bg-red-500 animate-pulse' : 'bg-green-500'
              }`}
            ></div>
            <span className="text-sm">{error ? 'Offline' : 'Online'}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StatusBar;
