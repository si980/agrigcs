/**
 * AgriGCS Unified Real-Time Telemetry & Agronomic State Engine (v2.4)
 * Synchronizes sensor telemetry, alert triage, solenoid valve actuation,
 * and stress scenarios across all open tabs via localStorage & BroadcastChannel.
 */
(function(global) {
  const STORAGE_KEY = 'agrigcs_telemetry_state_v2';
  const CHANNEL_NAME = 'agrigcs_telemetry_bus';

  const DEFAULT_STATE = {
    isLive: true,
    scenario: 'normal',
    packetCount: 524,
    baudRate: 115200,
    rfFrequency: '915.2 MHz',
    spreadingFactor: 'SF7 / BW 125kHz',
    rssi: -118,
    snr: 9.2,
    crcRate: 99.88,
    activeNodes: 12,
    totalNodes: 12,
    rtkStatus: 'RTK FIXED',
    rtkAccuracyCm: 1.2,
    sectorName: 'Sector 04',
    sectorAcres: 160,
    lastSync: Date.now(),
    godMode: false,
    godModeActuators: {
      allValvesOpen: false,
      pumpDuty: 100,
      eStop: false,
      roverTurbo: false
    },
    // Shared Agronomic Data Model (Baseline Spec)
    zoneA: {
      name: 'Zone A (Sweet Corn)',
      crop: 'Sweet Corn',
      vwc: 42.1,
      temp: 23.1,
      ec: 1.42,
      status: 'Healthy',
      probeId: '#10551'
    },
    zoneB: {
      name: 'Zone B (Organic Kale - Incident Target)',
      crop: 'Organic Kale',
      vwc: 28.0,
      temp: 19.5,
      ec: 0.88,
      status: 'Warning',
      probeId: '#10555',
      backupProbeId: '#10554',
      backupVwc: 29.2,
      valveActive: false,
      valveRemainingSec: 0,
      valveId: 'SOLENOID_VALVE_04'
    },
    zoneC: {
      name: 'Zone C (Soybeans)',
      crop: 'Soybeans',
      vwc: 36.8,
      temp: 21.4,
      ec: 1.25,
      status: 'Nominal',
      probeId: '#10559'
    },
    // Priority Incident Queue (Spec: 3 Active)
    alerts: [
      {
        id: 'alt-01',
        type: 'critical',
        zone: 'Zone B (Organic Kale)',
        title: 'Moisture Threshold Breach (<30.0% VWC)',
        desc: 'Sub-canopy FDR sensor #10555 reading 28.0% VWC in upper 15cm root horizon.',
        time: '3m ago',
        probe: '#10555',
        recommendedTriage: 'Actuate Micro-drip solenoid valve #04 for 45-min pulse.',
        acknowledged: false,
        resolved: false
      },
      {
        id: 'alt-02',
        type: 'warning',
        zone: 'Zone B Backup Divergence',
        title: 'Secondary Probe #10554 Discrepancy (+1.2% Drift)',
        desc: 'Differential across redundant capacitive blades exceeding 1.0% tolerance band.',
        time: '7m ago',
        probe: '#10554',
        recommendedTriage: 'Verify soil contact impedance or run dielectric frequency sweep.',
        acknowledged: false,
        resolved: false
      },
      {
        id: 'alt-03',
        type: 'system',
        zone: 'Gateway Master #01',
        title: 'LiFePO4 Array Thermal Gradient (38.4°C Peak)',
        desc: 'Solar MPPT controller heat sink thermal delta elevated during noon absorption cycle.',
        time: '14m ago',
        probe: 'GW-01',
        recommendedTriage: 'Nominal under direct sun; monitor passive convective airflow.',
        acknowledged: false,
        resolved: false
      }
    ],
    // Recent Triage Events Log
    triageLog: []
  };

  let state = loadInitialState();
  const listeners = new Set();
  let channel = null;

  try {
    if (typeof BroadcastChannel !== 'undefined') {
      channel = new BroadcastChannel(CHANNEL_NAME);
      channel.onmessage = function(event) {
        if (event.data && event.data.type === 'SYNC') {
          state = event.data.payload;
          notifyListeners();
        }
      };
    }
  } catch (e) {
    console.warn('AgriGCS: BroadcastChannel not supported; falling back to storage listener');
  }

  window.addEventListener('storage', function(e) {
    if (e.key === STORAGE_KEY && e.newValue) {
      try {
        state = JSON.parse(e.newValue);
        notifyListeners();
      } catch (err) {}
    }
  });

  function loadInitialState() {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        return { ...DEFAULT_STATE, ...parsed };
      }
    } catch (e) {}
    return { ...DEFAULT_STATE };
  }

  function saveState() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
      if (channel) {
        channel.postMessage({ type: 'SYNC', payload: state });
      }
    } catch (e) {}
  }

  function notifyListeners() {
    listeners.forEach(fn => {
      try { fn(state); } catch (err) { console.error(err); }
    });
  }

  // Active Alert Count Helper
  function getActiveAlertCount() {
    return state.alerts.filter(a => !a.acknowledged && !a.resolved).length;
  }

  // Actuate Solenoid Valve Triage
  function triggerValveActuation(zone = 'Zone B', durationMinutes = 45) {
    state.zoneB.valveActive = true;
    state.zoneB.valveRemainingSec = durationMinutes * 60;
    
    const event = {
      timestamp: new Date().toLocaleTimeString(),
      zone: zone,
      valve: state.zoneB.valveId,
      action: `Actuated 45-min pulse cycle (${durationMinutes}m)`,
      status: 'IN_PROGRESS'
    };
    state.triageLog.unshift(event);
    saveState();
    notifyListeners();

    // Trigger visual toast
    if (global.AgriGCS_UI && global.AgriGCS_UI.showToast) {
      global.AgriGCS_UI.showToast(`Actuating ${state.zoneB.valveId}: 45-min pulse irrigation active`, 'success');
    }

    return true;
  }

  // Acknowledge Incident
  function acknowledgeAlert(alertId) {
    const alert = state.alerts.find(a => a.id === alertId);
    if (alert) {
      alert.acknowledged = true;
      saveState();
      notifyListeners();
      if (global.AgriGCS_UI && global.AgriGCS_UI.showToast) {
        global.AgriGCS_UI.showToast(`Incident [${alert.id}] acknowledged by Operator`, 'info');
      }
    }
  }

  // Resolve Alert (e.g. after irrigation cycle completes)
  function resolveAlert(alertId) {
    const alert = state.alerts.find(a => a.id === alertId);
    if (alert) {
      alert.resolved = true;
      alert.acknowledged = true;
      saveState();
      notifyListeners();
    }
  }

  // Scenario Injection
  function setScenario(scenarioName) {
    state.scenario = scenarioName;
    if (scenarioName === 'drought') {
      state.zoneA.vwc = 34.2;
      state.zoneB.vwc = 22.4;
      state.zoneB.status = 'Critical Hazard';
      state.zoneC.vwc = 29.1;
      state.rssi = -122;
    } else if (scenarioName === 'flood') {
      state.zoneA.vwc = 58.5;
      state.zoneB.vwc = 64.2;
      state.zoneB.status = 'Saturation Flood';
      state.zoneC.vwc = 52.0;
    } else if (scenarioName === 'packet_loss') {
      state.crcRate = 84.5;
      state.activeNodes = 9;
    } else if (scenarioName === 'normal') {
      state.zoneA.vwc = 42.1;
      state.zoneB.vwc = state.zoneB.valveActive ? 35.2 : 28.0;
      state.zoneB.status = state.zoneB.valveActive ? 'Recovering' : 'Warning';
      state.zoneC.vwc = 36.8;
      state.crcRate = 99.88;
      state.activeNodes = 12;
      state.rssi = -118;
    }
    saveState();
    notifyListeners();
    if (global.AgriGCS_UI && global.AgriGCS_UI.showToast) {
      global.AgriGCS_UI.showToast(`Simulation Scenario Applied: ${scenarioName.toUpperCase()}`, 'warn');
    }
  }

  // Toggle LIVE stream / PAUSE simulation
  function toggleLive() {
    state.isLive = !state.isLive;
    saveState();
    notifyListeners();
    return state.isLive;
  }

  // Periodic Telemetry Simulator Ticker
  setInterval(function() {
    if (!state.isLive) return;

    // Increment packet count
    state.packetCount += 1;

    // Subtle natural sensor jitter (±0.05%)
    const jitterA = (Math.random() - 0.5) * 0.08;
    const jitterC = (Math.random() - 0.5) * 0.08;
    state.zoneA.vwc = parseFloat((state.zoneA.vwc + jitterA).toFixed(1));
    state.zoneC.vwc = parseFloat((state.zoneC.vwc + jitterC).toFixed(1));

    // If valve is active, simulate progressive soil re-hydration in Zone B
    if (state.zoneB.valveActive) {
      state.zoneB.valveRemainingSec = Math.max(0, state.zoneB.valveRemainingSec - 15);
      if (state.zoneB.vwc < 36.5) {
        state.zoneB.vwc = parseFloat((state.zoneB.vwc + 0.3).toFixed(1));
        state.zoneB.backupVwc = parseFloat((state.zoneB.backupVwc + 0.3).toFixed(1));
      } else {
        state.zoneB.status = 'Healthy (Nominal)';
        resolveAlert('alt-01');
      }
      if (state.zoneB.valveRemainingSec === 0) {
        state.zoneB.valveActive = false;
      }
    } else {
      // Nominal slight evaporation jitter
      if (state.zoneB.vwc > 27.5 && state.scenario === 'normal') {
        const jitterB = (Math.random() - 0.5) * 0.05;
        state.zoneB.vwc = parseFloat((state.zoneB.vwc + jitterB).toFixed(1));
      }
    }

    // Keep packet success rate high
    state.crcRate = parseFloat((99.85 + Math.random() * 0.05).toFixed(2));
    state.lastSync = Date.now();

    saveState();
    notifyListeners();
  }, 3500);

  // God Mode Super-Admin Telemetry & Actuator Override Engine
  function toggleGodMode(forcedVal) {
    state.godMode = typeof forcedVal === 'boolean' ? forcedVal : !state.godMode;
    saveState();
    notifyListeners();
    if (global.AgriGCS_UI && global.AgriGCS_UI.showToast) {
      if (state.godMode) {
        global.AgriGCS_UI.showToast('⚡ GOD MODE ACTIVE: Master Telemetry & Hardware Override Unlocked', 'warn');
      } else {
        global.AgriGCS_UI.showToast('God Mode Disengaged: Nominal Operator Locks Restored', 'info');
      }
    }
    return state.godMode;
  }

  function forceTelemetry(updates) {
    if (!state.godMode) state.godMode = true;
    if (updates.vwc !== undefined) {
      state.zoneB.vwc = parseFloat(updates.vwc);
      state.zoneB.status = updates.vwc < 24 ? 'Severe Drought' : updates.vwc > 50 ? 'Flooded' : 'Optimal';
    }
    if (updates.zoneA_vwc !== undefined) state.zoneA.vwc = parseFloat(updates.zoneA_vwc);
    if (updates.zoneC_vwc !== undefined) state.zoneC.vwc = parseFloat(updates.zoneC_vwc);
    if (updates.rssi !== undefined) state.rssi = parseInt(updates.rssi, 10);
    if (updates.activeNodes !== undefined) state.activeNodes = parseInt(updates.activeNodes, 10);
    saveState();
    notifyListeners();
  }

  function setGodModeActuator(key, val) {
    if (!state.godMode) state.godMode = true;
    if (!state.godModeActuators) state.godModeActuators = {};
    state.godModeActuators[key] = val;
    if (key === 'allValvesOpen') {
      state.zoneB.valveActive = val;
      if (val) state.zoneB.valveRemainingSec = 3600;
    }
    saveState();
    notifyListeners();
  }

  // Export Global API
  global.AgriGCS_State = {
    get: () => ({ ...state }),
    set: (updates) => {
      state = { ...state, ...updates };
      saveState();
      notifyListeners();
    },
    subscribe: (fn) => {
      listeners.add(fn);
      fn(state);
      return () => listeners.delete(fn);
    },
    triggerValveActuation,
    acknowledgeAlert,
    resolveAlert,
    setScenario,
    toggleLive,
    toggleGodMode,
    forceTelemetry,
    setGodModeActuator,
    getActiveAlertCount,
    resetToBaseline: () => {
      state = { ...DEFAULT_STATE };
      saveState();
      notifyListeners();
    }
  };
})(window);
