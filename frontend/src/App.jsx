/**
 * Haupt-App-Komponente für SolarPilot.
 */

import React from 'react';
import { useLiveData } from './hooks/useLiveData';
import StatusBar from './components/StatusBar';
import EnergyFlowDiagram from './components/EnergyFlowDiagram';

function App() {
  const { data, loading, error, lastUpdate } = useLiveData(30000);  // 30 Sekunden Polling

  return (
    <div className="min-h-screen bg-gray-50">
      {/* StatusBar (Header) */}
      <StatusBar lastUpdate={lastUpdate} error={error} />

      {/* Haupt-Content */}
      <main className="container mx-auto p-6">
        {/* Loading-State */}
        {loading && !data && (
          <div className="text-center py-20">
            <div className="text-6xl mb-4 animate-pulse">⏳</div>
            <p className="text-xl text-gray-600">Lade Daten...</p>
            <p className="text-sm text-gray-500 mt-2">
              Verbinde mit dem Solplanet-Dongle...
            </p>
          </div>
        )}

        {/* Energiefluss-Diagramm */}
        {data && <EnergyFlowDiagram data={data} />}

        {/* Error-State */}
        {error && !data && (
          <div className="max-w-2xl mx-auto mt-12">
            <div className="bg-red-100 border border-red-400 text-red-700 px-6 py-4 rounded-lg shadow-md">
              <div className="flex items-start">
                <div className="text-2xl mr-4">⚠️</div>
                <div>
                  <strong className="font-bold block mb-2">Verbindungsfehler</strong>
                  <span className="block">{error}</span>
                  <p className="text-sm mt-3 text-red-600">
                    Bitte prüfen Sie:
                  </p>
                  <ul className="list-disc list-inside text-sm mt-2 text-red-600">
                    <li>Ist der Backend-Container gestartet?</li>
                    <li>Ist der Solplanet-Dongle erreichbar (192.168.10.113)?</li>
                    <li>Sind die Umgebungsvariablen korrekt konfiguriert?</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="text-center py-6 text-gray-500 text-sm">
        <p>
          SolarPilot v1.0.0 | Phase 1 - Fundament | 15,575 kWp (Ost: 6,23 kWp, West: 9,345 kWp)
        </p>
        <p className="mt-1">
          Trina Solar Vertex S+ TSM-NEG9RC.27 (445W × 35 Module)
        </p>
      </footer>
    </div>
  );
}

export default App;
