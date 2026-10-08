/**
 * AgriGCS Unified Navigation & Interactive Controller (v2.4 Production Baseline)
 * - Clean semantic routing (/home/, /monitoring/, /sensors/, /alerts/, /inspector/, /academy/, /sim-lab/)
 * - Two-way binding with AgriGCS_State engine
 * - Dynamic Alerts navbar badge counter syncing with acknowledged incidents
 * - Interactive Solenoid Valve #04 actuation triage
 * - Interactive Live ⇄ Simulation toggle
 * - Hardware Bridge Modal & Sector 04 Operator Profile Dropdown
 * - Mobile responsive drawer (< xl)
 * - ⌘K Telemetry Command Palette with quick jump
 */
(function() {
  const CLEAN_ROUTES = {
    'home': '/home/',
    'sensors': '/sensors/',
    'field-setup': '/field-setup/',
    'how-it-works': '/how-it-works/',
    'monitoring': '/monitoring/',
    'telemetry': '/telemetry/',
    'packet-inspector': '/inspector/',
    'inspector': '/inspector/',
    'alerts': '/alerts/',
    'learning': '/academy/',
    'academy': '/academy/',
    'simulation-lab': '/sim-lab/',
    'sim-lab': '/sim-lab/',
    'presentation': '/deck/',
    'deck': '/deck/',
    'wiring': '/wiring/',
    'orbit': '/orbit/',
    'webgl': '/webgl/',
    'motion': '/motion/'
  };

  const ALL_MODULES = [
    { id: 'home', title: 'Home Landing Hub', group: 'Core Platform', icon: 'home', path: '/home/', desc: 'Main telemetry command overview & miniature diorama' },
    { id: 'monitoring', title: 'Live Field Monitoring', group: 'Core Platform', icon: 'monitoring', path: '/monitoring/', desc: 'Sector 04 real-time sensor array & sub-mesh telemetry' },
    { id: 'telemetry', title: 'Live Telemetry Stream', group: 'Diagnostics', icon: 'vital_signs', path: '/telemetry/', desc: '1Hz raw binary packet bus, CRC-16 inspector & RF waterfall' },
    { id: 'sensors', title: 'Sensor Ecosystem', group: 'Hardware & Nodes', icon: 'sensors', path: '/sensors/', desc: 'Capacitive probes, LoRaWAN SX1262, solar masts & RTK' },
    { id: 'field-setup', title: '3D Field Setup & SOP Guide', group: 'Operations', icon: 'layers', path: '/field-setup/', desc: 'Multi-depth probe placement and GPS RTK alignment' },
    { id: 'inspector', title: 'Telemetry Packet Inspector', group: 'Diagnostics', icon: 'terminal', path: '/inspector/', desc: 'CRC-16 verification, 32-byte hex streams, RF signal RSSI' },
    { id: 'alerts', title: 'Alert Center & Triage Support', group: 'Operations', icon: 'warning', path: '/alerts/', desc: 'Automated solenoid valve triggering & moisture deficit' },
    { id: 'how-it-works', title: 'How It Works & Architecture', group: 'Core Platform', icon: 'account_tree', path: '/how-it-works/', desc: 'Sub-canopy 915MHz RF mesh to Tokio packet broker' },
    { id: 'academy', title: 'AgriGCS Academy', group: 'Documentation', icon: 'school', path: '/academy/', desc: 'Field engineering best practices and agronomy guides' },
    { id: 'sim-lab', title: 'Simulation Lab & Stress Tester', group: 'Simulations', icon: 'science', path: '/sim-lab/', desc: 'Flash flood, severe drought & RF packet loss tester' },
    { id: 'wiring', title: 'Interactive Wiring Simulator', group: 'Hardware & Nodes', icon: 'cable', path: '/wiring/', desc: 'ESP32-S3 pinout, I2C/SPI bus & solar wire-up' },
    { id: 'deck', title: '10-Stage Executive Deck', group: 'Presentations', icon: 'slideshow', path: '/deck/', desc: 'Complete architectural walkthrough presentation' },
    { id: 'orbit', title: '3D Three.js Orbit Visualizer', group: '3D & Graphics', icon: '3d_rotation', path: '/orbit/', desc: 'Interactive 360° field crop canopy inspection' },
    { id: 'webgl', title: 'Interactive WebGL Telemetry', group: '3D & Graphics', icon: 'view_in_ar', path: '/webgl/', desc: 'Volumetric soil moisture heatmaps in WebGL' },
    { id: 'motion', title: 'Dynamic Motion Effects', group: '3D & Graphics', icon: 'motion_photos_on', path: '/motion/', desc: 'Real-time telemetry pulse wave animations' }
  ];

  function navigateTo(targetPath) {
    window.location.href = targetPath;
  }

  // Toast System
  function showToast(message, type = 'info') {
    let toastContainer = document.getElementById('agrigcs-toast-container');
    if (!toastContainer) {
      toastContainer = document.createElement('div');
      toastContainer.id = 'agrigcs-toast-container';
      toastContainer.style.cssText = 'position:fixed;top:76px;right:24px;z-index:99998;display:flex;flex-direction:column;gap:8px;pointer-events:none;';
      document.body.appendChild(toastContainer);
    }

    const toast = document.createElement('div');
    const colorClass = type === 'success' ? '#10b981' : type === 'warn' ? '#f59e0b' : '#00d2aa';
    const bgClass = '#151c23';
    toast.style.cssText = `
      background:${bgClass};
      color:#dce3ed;
      border:1px solid ${colorClass}80;
      border-left:4px solid ${colorClass};
      box-shadow:0 10px 30px rgba(0,0,0,0.7), 0 0 15px ${colorClass}30;
      padding:10px 16px;
      border-radius:10px;
      font-family:'JetBrains Mono', monospace;
      font-size:12px;
      display:flex;
      align-items:center;
      gap:10px;
      animation:agrigcsToastIn 0.3s ease-out;
      pointer-events:auto;
    `;
    toast.innerHTML = `
      <span class="material-symbols-outlined" style="color:${colorClass};font-size:18px;">
        ${type === 'success' ? 'check_circle' : type === 'warn' ? 'warning' : 'sensors'}
      </span>
      <span>${message}</span>
    `;
    toastContainer.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(-10px)';
      toast.style.transition = 'all 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 3500);
  }

  window.AgriGCS_UI = { showToast };

  // Sync with AgriGCS_State
  function syncHeaderWithState(state) {
    if (!state) return;

    // Update Alerts Badge in Navbar
    const alertBadges = document.querySelectorAll('.agrigcs-alert-badge');
    const activeCount = state.alerts.filter(a => !a.acknowledged && !a.resolved).length;
    alertBadges.forEach(b => {
      if (activeCount > 0) {
        b.textContent = activeCount;
        b.style.display = 'inline-block';
      } else {
        b.style.display = 'none';
      }
    });

    // Update LIVE Toggle Button
    const liveBtns = document.querySelectorAll('.agrigcs-live-btn');
    liveBtns.forEach(btn => {
      const ping = btn.querySelector('.agrigcs-live-ping');
      const dot = btn.querySelector('.agrigcs-live-dot');
      const label = btn.querySelector('.agrigcs-live-label');
      if (state.isLive) {
        if (ping) ping.style.display = 'inline-flex';
        if (dot) {
          dot.className = 'agrigcs-live-dot relative inline-flex rounded-full h-2 w-2 bg-primary';
          dot.style.background = '#00d2aa';
        }
        if (label) {
          label.textContent = 'Live';
          label.className = 'agrigcs-live-label font-label-caps text-label-caps uppercase tracking-wider text-on-surface';
          label.style.color = '#fff';
        }
      } else {
        if (ping) ping.style.display = 'none';
        if (dot) {
          dot.className = 'agrigcs-live-dot relative inline-flex rounded-full h-2 w-2 bg-amber-400';
          dot.style.background = '#f59e0b';
        }
        if (label) {
          label.textContent = 'Sim';
          label.className = 'agrigcs-live-label font-label-caps text-label-caps uppercase tracking-wider text-amber-400 font-bold';
          label.style.color = '#f59e0b';
        }
      }
    });

    // Update Live Telemetry Metrics on views if present
    const vwcEls = document.querySelectorAll('[data-bind="zoneB.vwc"]');
    vwcEls.forEach(el => { el.textContent = `${state.zoneB.vwc}%`; });

    const statusEls = document.querySelectorAll('[data-bind="zoneB.status"]');
    statusEls.forEach(el => { el.textContent = state.zoneB.status; });

    const pktEls = document.querySelectorAll('[data-bind="packetCount"]');
    pktEls.forEach(el => { el.textContent = state.packetCount; });

    const crcEls = document.querySelectorAll('[data-bind="crcRate"]');
    crcEls.forEach(el => { el.textContent = `${state.crcRate}%`; });
  }

  if (window.AgriGCS_State) {
    window.AgriGCS_State.subscribe(syncHeaderWithState);
  }

  // Connect Hardware Modal
  function openHardwareModal() {
    let modal = document.getElementById('agrigcs-hardware-modal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'agrigcs-hardware-modal';
      modal.style.cssText = 'position:fixed;inset:0;z-index:99999;background:rgba(8,15,22,0.85);backdrop-filter:blur(12px);display:none;align-items:center;justify-content:center;padding:1.5rem;box-sizing:border-box;';
      modal.innerHTML = `
        <div style="background:#151c23;border:1px solid rgba(0,210,170,0.35);border-radius:16px;box-shadow:0 25px 60px -15px rgba(0,0,0,0.9),0 0 30px rgba(0,210,170,0.25);width:100%;max-width:640px;overflow:hidden;color:#dce3ed;font-family:'Inter',system-ui,sans-serif;">
          <div style="padding:18px 24px;background:#192028;border-bottom:1px solid rgba(255,255,255,0.08);display:flex;align-items:center;justify-content:space-between;">
            <div style="display:flex;align-items:center;gap:12px;">
              <span class="material-symbols-outlined" style="color:#00d2aa;font-size:24px;">memory</span>
              <div>
                <div style="font-weight:700;color:#fff;font-size:16px;">AgriGCS Physical Hardware Integration Bridge</div>
                <div style="font-size:11px;font-family:'JetBrains Mono',monospace;color:#00d2aa;">Sector 04 Sub-Canopy Bus (115200 Baud)</div>
              </div>
            </div>
            <button id="agrigcs-close-hw-btn" style="background:transparent;border:none;color:#85948d;cursor:pointer;display:flex;padding:4px;border-radius:6px;">
              <span class="material-symbols-outlined">close</span>
            </button>
          </div>
          <div style="padding:20px;display:flex;flex-direction:column;gap:12px;">
            <!-- Node Card 1 -->
            <div style="display:flex;align-items:center;justify-content:space-between;background:#1e2630;padding:12px 16px;border-radius:10px;border:1px solid rgba(255,255,255,0.05);">
              <div style="display:flex;align-items:center;gap:12px;">
                <div style="width:36px;height:36px;border-radius:8px;background:rgba(0,210,170,0.15);color:#00d2aa;display:flex;align-items:center;justify-content:center;">
                  <span class="material-symbols-outlined" style="font-size:20px;">developer_board</span>
                </div>
                <div>
                  <div style="font-weight:600;font-size:13px;color:#fff;">ESP32-S3 Sub-Canopy Node #04</div>
                  <div style="font-size:11px;font-family:'JetBrains Mono',monospace;color:#85948d;">I2C 0x36 Soil FDR • 3.3V Logic Safe • LiFePO4 94%</div>
                </div>
              </div>
              <span style="font-size:10px;font-family:'JetBrains Mono',monospace;background:rgba(16,185,129,0.2);color:#10b981;border:1px solid rgba(16,185,129,0.3);padding:3px 8px;border-radius:999px;font-weight:700;">SYNCED</span>
            </div>
            <!-- Node Card 2 -->
            <div style="display:flex;align-items:center;justify-content:space-between;background:#1e2630;padding:12px 16px;border-radius:10px;border:1px solid rgba(255,255,255,0.05);">
              <div style="display:flex;align-items:center;gap:12px;">
                <div style="width:36px;height:36px;border-radius:8px;background:rgba(56,189,248,0.15);color:#38bdf8;display:flex;align-items:center;justify-content:center;">
                  <span class="material-symbols-outlined" style="font-size:20px;">cell_tower</span>
                </div>
                <div>
                  <div style="font-weight:600;font-size:13px;color:#fff;">SX1262 LoRaWAN Gateway Master #01</div>
                  <div style="font-size:11px;font-family:'JetBrains Mono',monospace;color:#85948d;">915.2 MHz (SF7 / BW 125kHz) • RSSI -118 dBm</div>
                </div>
              </div>
              <span style="font-size:10px;font-family:'JetBrains Mono',monospace;background:rgba(16,185,129,0.2);color:#10b981;border:1px solid rgba(16,185,129,0.3);padding:3px 8px;border-radius:999px;font-weight:700;">LIVE</span>
            </div>
            <!-- Node Card 3 -->
            <div style="display:flex;align-items:center;justify-content:space-between;background:#1e2630;padding:12px 16px;border-radius:10px;border:1px solid rgba(255,255,255,0.05);">
              <div style="display:flex;align-items:center;gap:12px;">
                <div style="width:36px;height:36px;border-radius:8px;background:rgba(245,158,11,0.15);color:#f59e0b;display:flex;align-items:center;justify-content:center;">
                  <span class="material-symbols-outlined" style="font-size:20px;">gps_fixed</span>
                </div>
                <div>
                  <div style="font-weight:600;font-size:13px;color:#fff;">U-Blox ZED-F9P RTK Base Station</div>
                  <div style="font-size:11px;font-family:'JetBrains Mono',monospace;color:#85948d;">Carrier Phase RTK Fixed • ±1.2cm Spatial Precision</div>
                </div>
              </div>
              <span style="font-size:10px;font-family:'JetBrains Mono',monospace;background:rgba(16,185,129,0.2);color:#10b981;border:1px solid rgba(16,185,129,0.3);padding:3px 8px;border-radius:999px;font-weight:700;">RTK FIXED</span>
            </div>
          </div>
          <div style="padding:16px 20px;background:#192028;border-top:1px solid rgba(255,255,255,0.08);display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:10px;">
            <button id="agrigcs-hw-sim-btn" style="padding:8px 16px;border-radius:9999px;background:rgba(0,210,170,0.15);border:1px solid rgba(0,210,170,0.3);color:#00d2aa;font-weight:600;font-size:12px;cursor:pointer;display:flex;align-items:center;gap:6px;">
              <span class="material-symbols-outlined" style="font-size:16px;">cable</span>
              <span>Open Interactive Wiring Simulator →</span>
            </button>
            <button id="agrigcs-hw-ping-btn" style="padding:8px 20px;border-radius:9999px;background:#00d2aa;color:#00382b;font-weight:700;font-size:12px;border:none;cursor:pointer;box-shadow:0 0 15px rgba(0,210,170,0.4);display:flex;align-items:center;gap:6px;">
              <span class="material-symbols-outlined" style="font-size:16px;">bolt</span>
              <span>Send Test Pulse</span>
            </button>
          </div>
        </div>
      `;
      document.body.appendChild(modal);

      modal.querySelector('#agrigcs-close-hw-btn').addEventListener('click', () => { modal.style.display = 'none'; });
      modal.addEventListener('click', (e) => { if (e.target === modal) modal.style.display = 'none'; });
      modal.querySelector('#agrigcs-hw-sim-btn').addEventListener('click', () => {
        modal.style.display = 'none';
        navigateTo('/wiring/');
      });
      modal.querySelector('#agrigcs-hw-ping-btn').addEventListener('click', () => {
        showToast('Ping Ack: Node #04 roundtrip latency 38ms (CRC-16 Passed)', 'success');
      });
    }
    modal.style.display = 'flex';
  }

  // Operator Profile Dropdown
  function openProfileDropdown(anchorBtn) {
    let dropdown = document.getElementById('agrigcs-profile-dropdown');
    if (!dropdown) {
      dropdown = document.createElement('div');
      dropdown.id = 'agrigcs-profile-dropdown';
      dropdown.style.cssText = 'position:fixed;top:68px;right:20px;z-index:99998;width:320px;background:#151c23;border:1px solid rgba(0,210,170,0.35);border-radius:16px;box-shadow:0 20px 50px rgba(0,0,0,0.85),0 0 25px rgba(0,210,170,0.2);display:none;flex-direction:column;overflow:hidden;color:#dce3ed;font-family:\'Inter\',system-ui,sans-serif;';
      dropdown.innerHTML = `
        <div style="padding:16px;background:#192028;border-bottom:1px solid rgba(255,255,255,0.08);display:flex;align-items:center;gap:12px;">
          <div style="width:40px;height:40px;border-radius:50%;background:#00d2aa;display:flex;align-items:center;justify-content:center;color:#00382b;font-weight:bold;">
            <span class="material-symbols-outlined" style="font-size:22px;">person</span>
          </div>
          <div>
            <div style="font-weight:700;color:#fff;font-size:14px;">Sector 04 Ground Control</div>
            <div style="font-size:11px;font-family:'JetBrains Mono',monospace;color:#00d2aa;">Operator: AGRON-OPS #1092</div>
          </div>
        </div>
        <div style="padding:14px 16px;display:flex;flex-direction:column;gap:8px;font-size:12px;font-family:'JetBrains Mono',monospace;">
          <div style="display:flex;justify-content:space-between;color:#85948d;">
            <span>Sector Area:</span>
            <span style="color:#fff;">160 Acres</span>
          </div>
          <div style="display:flex;justify-content:space-between;color:#85948d;">
            <span>Active Mesh:</span>
            <span style="color:#10b981;">12 / 12 Nodes Synced</span>
          </div>
          <div style="display:flex;justify-content:space-between;color:#85948d;">
            <span>RF Telemetry:</span>
            <span style="color:#fff;">915.2 MHz (SF7)</span>
          </div>
          <div style="display:flex;justify-content:space-between;color:#85948d;">
            <span>Spatial Fix:</span>
            <span style="color:#00d2aa;">RTK FIXED (±1.2cm)</span>
          </div>
          <div style="display:flex;justify-content:space-between;color:#85948d;">
            <span>Zone B Soil:</span>
            <span style="color:#f59e0b;" data-bind="zoneB.vwc">28.0% VWC (Low)</span>
          </div>
        </div>
        <div style="padding:10px 14px;background:#192028;border-top:1px solid rgba(255,255,255,0.08);display:flex;flex-direction:column;gap:6px;">
          <button id="agrigcs-prof-inspect" style="padding:8px 12px;border-radius:8px;background:rgba(255,255,255,0.04);border:none;color:#dce3ed;text-align:left;font-size:12px;cursor:pointer;display:flex;align-items:center;gap:8px;">
            <span class="material-symbols-outlined" style="font-size:16px;color:#00d2aa;">terminal</span>
            <span>Packet Inspector & Diagnostics</span>
          </button>
          <button id="agrigcs-prof-alerts" style="padding:8px 12px;border-radius:8px;background:rgba(255,255,255,0.04);border:none;color:#dce3ed;text-align:left;font-size:12px;cursor:pointer;display:flex;align-items:center;gap:8px;">
            <span class="material-symbols-outlined" style="font-size:16px;color:#ef4444;">warning</span>
            <span>View Active Incidents (3)</span>
          </button>
        </div>
      `;
      document.body.appendChild(dropdown);

      dropdown.querySelector('#agrigcs-prof-inspect').addEventListener('click', () => {
        dropdown.style.display = 'none';
        navigateTo('/inspector/');
      });
      dropdown.querySelector('#agrigcs-prof-alerts').addEventListener('click', () => {
        dropdown.style.display = 'none';
        navigateTo('/alerts/');
      });

      document.addEventListener('click', (e) => {
        if (dropdown.style.display === 'flex' && !dropdown.contains(e.target) && !anchorBtn.contains(e.target)) {
          dropdown.style.display = 'none';
        }
      });
    }

    dropdown.style.display = dropdown.style.display === 'flex' ? 'none' : 'flex';
  }

  // More Dropdown Handler
  function toggleMoreMenu() {
    const menu = document.getElementById('agrigcs-more-menu');
    const btn = document.getElementById('agrigcs-more-btn');
    if (!menu) return;
    const isOpen = menu.style.display === 'flex';
    menu.style.display = isOpen ? 'none' : 'flex';
    if (btn) {
      const arrow = btn.querySelector('.agrigcs-more-arrow');
      if (arrow) arrow.style.transform = isOpen ? 'rotate(0deg)' : 'rotate(180deg)';
    }
  }

  // Mobile Menu Drawer
  function toggleMobileMenu() {
    let menu = document.getElementById('agrigcs-mobile-menu-drawer');
    if (!menu) {
      menu = document.createElement('div');
      menu.id = 'agrigcs-mobile-menu-drawer';
      menu.style.cssText = 'position:fixed;top:64px;left:0;right:0;background:#151c23;border-bottom:1px solid rgba(0,210,170,0.3);box-shadow:0 20px 40px rgba(0,0,0,0.8);z-index:99997;padding:16px;display:none;flex-direction:column;gap:12px;max-height:calc(100vh-80px);overflow-y:auto;';

      const groups = [
        {
          name: 'Core Platform',
          links: [
            { label: 'Home', path: '/home/', icon: 'home' },
            { label: 'Monitoring', path: '/monitoring/', icon: 'monitoring' },
            { label: 'How It Works', path: '/how-it-works/', icon: 'account_tree' }
          ]
        },
        {
          name: 'Hardware & Setup',
          links: [
            { label: 'Sensors', path: '/sensors/', icon: 'sensors' },
            { label: 'Field Setup', path: '/field-setup/', icon: 'layers' },
            { label: 'Wiring Simulator', path: '/wiring/', icon: 'cable' }
          ]
        },
        {
          name: 'Operations & Triage',
          links: [
            { label: 'Inspector', path: '/inspector/', icon: 'terminal' },
            { label: 'Alerts', path: '/alerts/', icon: 'warning', badge: '3' }
          ]
        },
        {
          name: 'Labs & Learning',
          links: [
            { label: 'Academy', path: '/academy/', icon: 'school' },
            { label: 'Sim Lab', path: '/sim-lab/', icon: 'science' }
          ]
        },
        {
          name: 'Presentations & 3D',
          links: [
            { label: '10-Stage Deck', path: '/deck/', icon: 'slideshow' },
            { label: '3D Orbit Visualizer', path: '/orbit/', icon: '3d_rotation' },
            { label: 'WebGL Telemetry', path: '/webgl/', icon: 'view_in_ar' },
            { label: 'Motion Wave Effects', path: '/motion/', icon: 'motion_photos_on' }
          ]
        }
      ];

      const currentPath = window.location.pathname;

      groups.forEach(g => {
        const groupHeader = document.createElement('div');
        groupHeader.style.cssText = 'font-size:11px;font-family:\'JetBrains Mono\',monospace;text-transform:uppercase;color:#85948d;letter-spacing:0.05em;padding:4px 8px 0;';
        groupHeader.textContent = g.name;
        menu.appendChild(groupHeader);

        g.links.forEach(l => {
          const item = document.createElement('a');
          item.href = l.path;
          const isActive = currentPath.includes(l.path);
          item.style.cssText = `
            display:flex;
            align-items:center;
            justify-content:space-between;
            padding:10px 14px;
            border-radius:10px;
            color:${isActive ? '#00382b' : '#dce3ed'};
            background:${isActive ? '#00d2aa' : 'rgba(255,255,255,0.04)'};
            font-weight:${isActive ? '700' : '500'};
            font-size:13px;
            text-decoration:none;
            transition:all 0.15s ease;
          `;
          item.innerHTML = `
            <div style="display:flex;align-items:center;gap:10px;">
              <span class="material-symbols-outlined" style="font-size:18px;color:${isActive ? '#00382b' : '#00d2aa'};">${l.icon}</span>
              <span>${l.label}</span>
            </div>
            ${l.badge ? `<span class="agrigcs-alert-badge" style="background:#ef4444;color:#fff;font-size:10px;padding:2px 7px;border-radius:999px;font-family:'JetBrains Mono',monospace;">${l.badge}</span>` : ''}
          `;
          item.addEventListener('click', (e) => {
            e.preventDefault();
            menu.style.display = 'none';
            navigateTo(l.path);
          });
          menu.appendChild(item);
        });
      });

      document.body.appendChild(menu);
    }

    menu.style.display = menu.style.display === 'flex' ? 'none' : 'flex';
  }

  // Intercept click on data-path, global buttons, and triage triggers
  document.addEventListener('click', function(e) {
    // More button click
    const moreBtn = e.target.closest('#agrigcs-more-btn, .agrigcs-more-btn');
    if (moreBtn) {
      e.preventDefault();
      toggleMoreMenu();
      return;
    }

    // Close more dropdown if clicking outside
    const moreWrapper = document.querySelector('.agrigcs-more-dropdown-wrapper');
    const moreMenu = document.getElementById('agrigcs-more-menu');
    if (moreMenu && moreMenu.style.display === 'flex') {
      if (!moreWrapper || !moreWrapper.contains(e.target)) {
        moreMenu.style.display = 'none';
        const arrow = document.querySelector('.agrigcs-more-arrow');
        if (arrow) arrow.style.transform = 'rotate(0deg)';
      }
    }

    const navLink = e.target.closest('[data-path]');
    if (navLink) {
      const p = navLink.getAttribute('data-path');
      if (CLEAN_ROUTES[p]) {
        e.preventDefault();
        navigateTo(CLEAN_ROUTES[p]);
        return;
      }
    }

    // Live toggle button
    const liveBtn = e.target.closest('.agrigcs-live-btn');
    if (liveBtn) {
      e.preventDefault();
      if (window.AgriGCS_State) {
        const live = window.AgriGCS_State.toggleLive();
        showToast(live ? 'Telemetry Link Active (115200 Baud Live Stream)' : 'Simulation Mode Paused', live ? 'success' : 'warn');
      }
      return;
    }

    // Connect Hardware CTA
    const connectBtn = e.target.closest('.agrigcs-connect-btn');
    if (connectBtn) {
      e.preventDefault();
      openHardwareModal();
      return;
    }

    // Profile button
    const profileBtn = e.target.closest('.agrigcs-profile-btn');
    if (profileBtn) {
      e.preventDefault();
      openProfileDropdown(profileBtn);
      return;
    }

    // Mobile menu toggle
    const mobBtn = e.target.closest('#agrigcs-mobile-menu-btn');
    if (mobBtn) {
      e.preventDefault();
      toggleMobileMenu();
      return;
    }

    // Solenoid Valve Triage Actuation Trigger
    const valveBtn = e.target.closest('#btn-actuate-valve, .btn-actuate-valve, [data-action="actuate-valve"]');
    if (valveBtn) {
      e.preventDefault();
      if (window.AgriGCS_State) {
        window.AgriGCS_State.triggerValveActuation('Zone B (Kale)', 45);
        valveBtn.innerHTML = `
          <span class="material-symbols-outlined text-[16px] animate-spin">refresh</span>
          <span>Actuating Valve #04 (45m pulse active)...</span>
        `;
        valveBtn.disabled = true;
        valveBtn.style.opacity = '0.85';
      }
      return;
    }

    // Incident Acknowledge Button
    const ackBtn = e.target.closest('#btn-ack-alert, .btn-ack, [data-action="acknowledge-alert"]');
    if (ackBtn) {
      e.preventDefault();
      const alertId = ackBtn.getAttribute('data-alert-id') || 'alt-01';
      if (window.AgriGCS_State) {
        window.AgriGCS_State.acknowledgeAlert(alertId);
        ackBtn.textContent = 'Acknowledged ✓';
        ackBtn.disabled = true;
        ackBtn.style.opacity = '0.6';
      }
      return;
    }

    // Sim Lab Scenario triggers
    const scenarioBtn = e.target.closest('[data-scenario]');
    if (scenarioBtn) {
      const scen = scenarioBtn.getAttribute('data-scenario');
      if (window.AgriGCS_State) {
        window.AgriGCS_State.setScenario(scen);
      }
      return;
    }

    // Generic Hero CTAs
    const btn = e.target.closest('button, a');
    if (btn) {
      const txt = btn.textContent.toLowerCase();
      if (txt.includes('launch dashboard') || txt.includes('open dashboard')) {
        e.preventDefault();
        navigateTo('/monitoring/');
        return;
      }
      if (txt.includes('explore sensors')) {
        e.preventDefault();
        navigateTo('/sensors/');
        return;
      }
      if (txt.includes('simulation lab') || txt.includes('sim lab')) {
        e.preventDefault();
        navigateTo('/sim-lab/');
        return;
      }
      if (txt.includes('read hardware schematics')) {
        e.preventDefault();
        navigateTo('/wiring/');
        return;
      }
    }
  });

  // Keyboard shortcut: ⌘K or Ctrl+K
  document.addEventListener('keydown', function(e) {
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
      e.preventDefault();
      toggleCommandPalette();
    } else if (e.key === 'Escape') {
      closeCommandPalette();
      const hwModal = document.getElementById('agrigcs-hardware-modal');
      if (hwModal) hwModal.style.display = 'none';
      const profMenu = document.getElementById('agrigcs-profile-dropdown');
      if (profMenu) profMenu.style.display = 'none';
      const mobMenu = document.getElementById('agrigcs-mobile-menu-drawer');
      if (mobMenu) mobMenu.style.display = 'none';
      const moreMenu = document.getElementById('agrigcs-more-menu');
      if (moreMenu) {
        moreMenu.style.display = 'none';
        const arrow = document.querySelector('.agrigcs-more-arrow');
        if (arrow) arrow.style.transform = 'rotate(0deg)';
      }
    }
  });

  // ⌘K Command Palette & Floating Pill
  function injectPaletteUI() {
    const style = document.createElement('style');
    style.textContent = `
      @keyframes agrigcsToastIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
      }
      #agrigcs-palette-overlay {
        position: fixed;
        inset: 0;
        z-index: 99999;
        background: rgba(8, 15, 22, 0.85);
        backdrop-filter: blur(12px);
        display: none;
        align-items: flex-start;
        justify-content: center;
        padding: 5rem 1rem 2rem;
        box-sizing: border-box;
      }
      #agrigcs-palette-overlay.open {
        display: flex;
      }
      .agrigcs-modal {
        width: 100%;
        max-width: 680px;
        background: #151c23;
        border: 1px solid rgba(0, 210, 170, 0.35);
        box-shadow: 0 25px 60px -15px rgba(0,0,0,0.9), 0 0 30px rgba(0, 210, 170, 0.25);
        border-radius: 16px;
        overflow: hidden;
        color: #dce3ed;
        font-family: 'Inter', system-ui, sans-serif;
      }
      .agrigcs-modal-header {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 16px 20px;
        border-bottom: 1px solid rgba(255,255,255,0.08);
        background: #192028;
      }
      .agrigcs-modal-search {
        flex: 1;
        background: transparent;
        border: none;
        outline: none;
        color: #fff;
        font-size: 16px;
        font-family: 'Inter', system-ui, sans-serif;
      }
      .agrigcs-modal-search::placeholder {
        color: #85948d;
      }
      .agrigcs-kbd {
        background: #242b32;
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 6px;
        padding: 3px 8px;
        font-size: 11px;
        font-family: 'JetBrains Mono', monospace;
        color: #00d2aa;
      }
      .agrigcs-modal-list {
        max-height: 480px;
        overflow-y: auto;
        padding: 12px;
        box-sizing: border-box;
      }
      .agrigcs-item {
        display: flex;
        align-items: center;
        gap: 14px;
        padding: 10px 14px;
        border-radius: 10px;
        cursor: pointer;
        transition: all 0.15s ease;
        text-decoration: none;
        color: inherit;
      }
      .agrigcs-item:hover, .agrigcs-item.selected {
        background: rgba(0, 210, 170, 0.12);
        border-left: 3px solid #00d2aa;
      }
      .agrigcs-item-icon {
        width: 36px;
        height: 36px;
        border-radius: 8px;
        background: #1e2630;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #00d2aa;
        flex-shrink: 0;
      }
      .agrigcs-item:hover .agrigcs-item-icon {
        background: #00d2aa;
        color: #00382b;
      }
      .agrigcs-item-title {
        font-weight: 600;
        font-size: 14px;
        color: #fff;
        display: flex;
        align-items: center;
        gap: 8px;
      }
      .agrigcs-item-group {
        font-size: 10px;
        font-family: 'JetBrains Mono', monospace;
        color: #00d2aa;
        background: rgba(0, 210, 170, 0.12);
        padding: 2px 6px;
        border-radius: 4px;
        text-transform: uppercase;
      }
      .agrigcs-item-desc {
        font-size: 12px;
        color: #85948d;
        margin-top: 2px;
      }
      #agrigcs-dock-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(18, 26, 33, 0.92);
        border: 1px solid rgba(0, 210, 170, 0.35);
        border-radius: 9999px;
        padding: 5px 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.6), 0 0 12px rgba(0, 210, 170, 0.2);
        backdrop-filter: blur(12px);
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        color: #dce3ed;
        cursor: pointer;
        transition: all 0.2s ease;
        user-select: none;
        white-space: nowrap;
        margin-left: 6px;
      }
      #agrigcs-dock-pill:hover {
        background: rgba(28, 38, 48, 0.98);
        border-color: #00d2aa;
        box-shadow: 0 6px 20px rgba(0,0,0,0.8), 0 0 20px rgba(0, 210, 170, 0.4);
        transform: translateY(-1px);
      }
      #agrigcs-dock-pill .pulse-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #00d2aa;
        box-shadow: 0 0 8px #00d2aa;
        animation: agyPulse 2s infinite;
      }
      @media (max-width: 640px) {
        #agrigcs-dock-pill .pill-brand,
        #agrigcs-dock-pill .pill-dot {
          display: none;
        }
      }
      @keyframes agyPulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.4; transform: scale(0.85); }
      }
    `;
    document.head.appendChild(style);

    const overlay = document.createElement('div');
    overlay.id = 'agrigcs-palette-overlay';
    overlay.innerHTML = `
      <div class="agrigcs-modal" role="dialog" aria-modal="true">
        <div class="agrigcs-modal-header">
          <span class="material-symbols-outlined" style="color:#00d2aa;font-size:22px;">terminal</span>
          <input type="text" id="agrigcs-palette-input" class="agrigcs-modal-search" placeholder="Search AgriGCS Telemetry modules (type to filter)..." autocomplete="off" />
          <span class="agrigcs-kbd">ESC</span>
        </div>
        <div class="agrigcs-modal-list" id="agrigcs-palette-list"></div>
      </div>
    `;
    document.body.appendChild(overlay);

    const dock = document.createElement('div');
    dock.id = 'agrigcs-dock-pill';
    dock.title = 'Open AgriGCS Telemetry Command Palette (⌘K)';
    dock.innerHTML = `
      <div class="pulse-dot"></div>
      <span class="pill-brand" style="font-weight:600;color:#00d2aa;">AgriGCS</span>
      <span class="pill-dot" style="color:#85948d;">•</span>
      <span style="font-weight:600;">Modules</span>
      <span class="agrigcs-kbd" style="margin-left:4px;">⌘K</span>
    `;
    dock.addEventListener('click', openCommandPalette);

    // Mount in top-left corner right next to the brand logo
    const brandContainer = document.querySelector('.agrigcs-unified-header .shrink-0, header .shrink-0, .agrigcs-brand-container');
    if (brandContainer) {
      brandContainer.appendChild(dock);
    } else {
      dock.style.position = 'fixed';
      dock.style.top = '14px';
      dock.style.left = '260px';
      dock.style.zIndex = '99990';
      document.body.appendChild(dock);
    }

    const input = document.getElementById('agrigcs-palette-input');
    const list = document.getElementById('agrigcs-palette-list');

    function renderList(query = '') {
      list.innerHTML = '';
      const q = query.toLowerCase().trim();
      const filtered = ALL_MODULES.filter(m =>
        m.title.toLowerCase().includes(q) ||
        m.group.toLowerCase().includes(q) ||
        m.desc.toLowerCase().includes(q)
      );

      if (filtered.length === 0) {
        list.innerHTML = '<div style="padding:24px;text-align:center;color:#85948d;font-size:13px;">No matching modules found</div>';
        return;
      }

      filtered.forEach((m, idx) => {
        const item = document.createElement('div');
        item.className = 'agrigcs-item' + (idx === 0 ? ' selected' : '');
        item.innerHTML = `
          <div class="agrigcs-item-icon">
            <span class="material-symbols-outlined" style="font-size:20px;">${m.icon}</span>
          </div>
          <div style="flex:1;">
            <div class="agrigcs-item-title">
              <span>${m.title}</span>
              <span class="agrigcs-item-group">${m.group}</span>
            </div>
            <div class="agrigcs-item-desc">${m.desc}</div>
          </div>
          <span class="material-symbols-outlined" style="color:#85948d;font-size:18px;">chevron_right</span>
        `;
        item.addEventListener('click', () => {
          navigateTo(m.path);
        });
        list.appendChild(item);
      });
    }

    input.addEventListener('input', (e) => {
      renderList(e.target.value);
    });

    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) closeCommandPalette();
    });

    renderList();
  }

  function openCommandPalette() {
    const overlay = document.getElementById('agrigcs-palette-overlay');
    if (!overlay) return;
    overlay.classList.add('open');
    const input = document.getElementById('agrigcs-palette-input');
    if (input) {
      input.value = '';
      input.focus();
      input.dispatchEvent(new Event('input'));
    }
  }

  function closeCommandPalette() {
    const overlay = document.getElementById('agrigcs-palette-overlay');
    if (overlay) overlay.classList.remove('open');
  }

  function toggleCommandPalette() {
    const overlay = document.getElementById('agrigcs-palette-overlay');
    if (overlay && overlay.classList.contains('open')) {
      closeCommandPalette();
    } else {
      openCommandPalette();
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', injectPaletteUI);
  } else {
    injectPaletteUI();
  }
})();
