/**
 * EnergyFlowDiagram: Visualisiert den Energiefluss (PV, Batterie, Haus, Netz).
 */

import React from 'react';

const EnergyFlowDiagram = ({ data }) => {
  if (!data) return null;

  // Hilfsfunktionen für Formatierung
  const formatPower = (value) => {
    return Math.abs(value).toFixed(2) + ' kW';
  };

  const formatPercent = (value) => {
    return Math.round(value) + '%';
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold mb-6 text-gray-800">Energiefluss</h2>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* PV-Anlage */}
        <div className="col-span-1">
          <div className="bg-yellow-50 border-4 border-solar-yellow rounded-lg p-6 text-center transition-all hover:shadow-xl">
            <div className="text-5xl mb-3">☀️</div>
            <h3 className="font-bold text-lg mb-2 text-gray-800">PV-Anlage</h3>
            <div className="text-4xl font-bold text-solar-yellow mb-3">
              {formatPower(data.pv_total_power)}
            </div>
            <div className="text-sm text-gray-600 space-y-1">
              <div className="flex justify-between">
                <span>Ost:</span>
                <span className="font-semibold">{formatPower(data.pv_east_power)}</span>
              </div>
              <div className="flex justify-between">
                <span>West:</span>
                <span className="font-semibold">{formatPower(data.pv_west_power)}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Batterie */}
        <div className="col-span-1">
          <div className="bg-green-50 border-4 border-battery-green rounded-lg p-6 text-center transition-all hover:shadow-xl">
            <div className="text-5xl mb-3">🔋</div>
            <h3 className="font-bold text-lg mb-2 text-gray-800">Batterie</h3>
            <div className="text-4xl font-bold text-battery-green mb-3">
              {formatPercent(data.battery_soc)}
            </div>
            <div className="text-sm text-gray-600">
              <div className="flex items-center justify-center gap-2">
                {data.battery_power > 0.1 ? (
                  <>
                    <span>⬆️ Laden</span>
                    <span className="font-semibold">{formatPower(data.battery_power)}</span>
                  </>
                ) : data.battery_power < -0.1 ? (
                  <>
                    <span>⬇️ Entladen</span>
                    <span className="font-semibold">{formatPower(Math.abs(data.battery_power))}</span>
                  </>
                ) : (
                  <span>➡️ Keine Aktivität</span>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Hausverbrauch */}
        <div className="col-span-1">
          <div className="bg-gray-100 border-4 border-house-gray rounded-lg p-6 text-center transition-all hover:shadow-xl">
            <div className="text-5xl mb-3">🏠</div>
            <h3 className="font-bold text-lg mb-2 text-gray-800">Hausverbrauch</h3>
            <div className="text-4xl font-bold text-house-gray mb-3">
              {formatPower(data.house_consumption)}
            </div>
            <div className="text-sm text-gray-500">
              Aktueller Verbrauch
            </div>
          </div>
        </div>
      </div>

      {/* Netz (volle Breite unten) */}
      <div className="mt-6">
        <div className="bg-blue-50 border-4 border-grid-blue rounded-lg p-6 text-center transition-all hover:shadow-xl">
          <div className="flex items-center justify-center gap-8">
            <div className="text-5xl">⚡</div>
            <div className="text-left">
              <h3 className="font-bold text-lg mb-1 text-gray-800">Stromnetz</h3>
              <div className="flex items-center gap-4">
                <div className="text-3xl font-bold text-grid-blue">
                  {formatPower(data.grid_power)}
                </div>
                <div className="text-sm text-gray-600">
                  {data.grid_power > 0.1 ? (
                    <span className="bg-blue-200 px-3 py-1 rounded">⬇️ Bezug</span>
                  ) : data.grid_power < -0.1 ? (
                    <span className="bg-green-200 px-3 py-1 rounded">⬆️ Einspeisung</span>
                  ) : (
                    <span className="bg-gray-200 px-3 py-1 rounded">➡️ Ausgeglichen</span>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Zeitstempel */}
      <div className="mt-6 text-sm text-gray-500 text-center">
        Letzte Aktualisierung: {new Date(data.timestamp).toLocaleString('de-DE')}
      </div>
    </div>
  );
};

export default EnergyFlowDiagram;
