import React, { useState, useEffect, useRef } from 'react';
import { ShieldAlert, Search, Bell, Cpu, AlertTriangle, Activity, Download, Terminal, Network, Shield, Mic, Upload } from 'lucide-react';
import SwarmGraph from './features/investigations/SwarmGraph';
import HolographicOrb from './components/ui/HolographicOrb';

const AnimationStyles = () => (
  <style>{`
    @keyframes spinCW { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    @keyframes spinCCW { 0% { transform: rotate(0deg); } 100% { transform: rotate(-360deg); } }
    @keyframes pulseNeon { 0%, 100% { opacity: 0.6; transform: scale(1); } 50% { opacity: 1; transform: scale(1.05); } }
    @keyframes slideInRight {
      0% { transform: translateX(100%); opacity: 0; }
      100% { transform: translateX(0); opacity: 1; }
    }
    @keyframes blink {
      0%, 50% { opacity: 1; }
      51%, 100% { opacity: 0; }
    }
  `}</style>
);

// Unified Backend Base Endpoint
const API_BASE = "http://localhost:8000/api/v1";

const vendorDatabase = {
  "Vardhaman Infra Solutions": {
    riskScore: 68,
    activeNodes: 12847,
    highRiskAlerts: 184,
    complianceShield: "92.4%",
    pendingReviews: 73
  },
  "SecureLogix Labs": {
    riskScore: 12,
    activeNodes: 15000,
    highRiskAlerts: 5,
    complianceShield: "99.5%",
    pendingReviews: 2
  }
};

interface LiveMetrics {
  nodes?: string;
  alerts?: number;
  shield?: string;
  pending?: string;
  riskScore?: number;
  riskLabel?: string;
  riskColor?: string;
  mcaStatus?: string;
  gstStatus?: string;
  panStatus?: string;
  escalationText?: string;
  frozen?: boolean;
}

export default function App() {
  const [selectedVendorName, setSelectedVendorName] = useState<string>("Vardhaman Infra Solutions");
  const [activeTab, setActiveTab] = useState<string>("directors");
  const [logs, setLogs] = useState<string[]>([]);
  const [metrics, setMetrics] = useState<LiveMetrics>({});
  const [isScanning, setIsScanning] = useState<boolean>(true);
  const [escalationBanner, setEscalationBanner] = useState<string | null>(null);
  const [cmdInput, setCmdInput] = useState<string>("");
  const logContainerRef = useRef<HTMLDivElement>(null);
  const vendor = selectedVendorName;

  // Speech recognition state
  const [speechRecognition, setSpeechRecognition] = useState<SpeechRecognition | null>(null);
  const [isListening, setIsListening] = useState<boolean>(false);
  // Compliance mask state
  const [complianceMask, setComplianceMask] = useState(false);
  // Critical alert toast state
  const [showCriticalToast, setShowCriticalToast] = useState(false);
  const [opHubHeaderTiltX, setOpHubHeaderTiltX] = useState(0);
  const [opHubHeaderTiltY, setOpHubHeaderTiltY] = useState(0);
  const [targetCaseTiltX, setTargetCaseTiltX] = useState(0);
  const [targetCaseTiltY, setTargetCaseTiltY] = useState(0);
  const [threatScoreTiltX, setThreatScoreTiltX] = useState(0);
  const [threatScoreTiltY, setThreatScoreTiltY] = useState(0);
  const [escalationMandateTiltX, setEscalationMandateTiltX] = useState(0);
  const [escalationMandateTiltY, setEscalationMandateTiltY] = useState(0);
  const [documentVaultTiltX, setDocumentVaultTiltX] = useState(0);
  const [documentVaultTiltY, setDocumentVaultTiltY] = useState(0);
  const [matrixTiltX, setMatrixTiltX] = useState(0);
  const [matrixTiltY, setMatrixTiltY] = useState(0);
  const [logsTiltX, setLogsTiltX] = useState(0);
  const [logsTiltY, setLogsTiltY] = useState(0);
  // Add Organization Modal state
  const [showAddOrgModal, setShowAddOrgModal] = useState(false);
  const [newOrgName, setNewOrgName] = useState('');
  const [newOrgRiskScore, setNewOrgRiskScore] = useState('');
  const [newOrgComplianceStatus, setNewOrgComplianceStatus] = useState('');

  // 1. FETCH LIVE TELEMETRY LOG FEED FROM BACKEND
  const fetchLiveLogs = async () => {
    try {
      // Direct state call with safe fallback query parameter
      const response = await fetch(`http://localhost:8000/metrics?vendor=${encodeURIComponent(selectedVendorName)}`);

      if (!response.ok) {
        setLogs([
          `❌ [SYSTEM ERROR] -> Backend metrics route responded with status ${response.status}`,
          `⚙️ [SYSTEM KERNEL] -> Falling back to secure simulated local stream.`
        ]);
        return;
      }

      // Safe update without relying on missing vendor nested arrays
      setLogs([
        `⚙️ [SYSTEM KERNEL] -> Hooking active tactical stream for entity: ${selectedVendorName}`,
        `📡 [MESH GATEWAY] -> Secure data sync initialized successfully.`
      ]);

    } catch (error) {
      setLogs([
        `⚙️ [SYSTEM KERNEL] -> Hooking active tactical stream for entity: ${selectedVendorName}`,
        `⚠️ [STREAM WARNING] -> Connection failed, using resilient local telemetry cache.`
      ]);
    }
  };

  // 2. FETCH REAL-TIME SYSTEM METRICS FOR SELECTED ENTITY
  const fetchMetrics = async () => {
    try {
      // Passing vendor parameter context to backend endpoint
      const res = await fetch(`http://localhost:8000/metrics?vendor=${encodeURIComponent(selectedVendorName)}`);
      if (res.ok) {
        const data = await res.json();
        setMetrics(data);
      } else {
        // Safe structural fallback if backend data mapping is initializing
        fallbackMockMetrics();
      }
    } catch (err) {
      fallbackMockMetrics();
    }
  };

  const fallbackMockMetrics = () => {
    // Dynamic generation matching vendor context to prevent interface breakage
    const isMatrix = selectedVendorName.includes("Matrix");
    const isApex = selectedVendorName.includes("Apex");
    const isSecureLogix = selectedVendorName.includes("SecureLogix");
    const frozen = selectedVendorName.toLowerCase().includes('vardhaman');

    let nodes, alerts, shield, pending, riskScore, riskLabel, riskColor, mcaStatus, gstStatus, panStatus, escalationText;

    // Mock IDs for GSTIN and PAN
    const mockGST = isMatrix ? "27AABCU9603R1Z5"
      : isApex ? "29AABCU9603R2Z6"
      : isSecureLogix ? "30AABCU9603R3Z7"
      : "27AABCU9603R1Z5"; // Vardhaman default

    const mockPAN = isMatrix ? "AABCU9603R"
      : isApex ? "AABCU9603R2"
      : isSecureLogix ? "AABCU9603R3"
      : "AABCU9603R1";

    if (isMatrix) {
      nodes = "8,912";
      alerts = 412;
      shield = "41.2%";
      pending = "195";
      riskScore = 94;
      riskLabel = "CRITICAL THREAT";
      riskColor = "#EF4444";
      mcaStatus = "🚨 MCA ROSTER: FICTITIOUS DIRECTORS";
      gstStatus = `${mockGST} SUSPENDED (❌)`;
      panStatus = `${mockPAN} FAILED RE-VERIFICATION (❌)`;
      escalationText = "IMMEDIATE ASSET FREEZE: Intelligence indicates laundering loops.";
    } else if (isApex) {
      nodes = "14,102";
      alerts = 14;
      shield = "99.1%";
      pending = "12";
      riskScore = 12;
      riskLabel = "OPTIMAL SECURITY";
      riskColor = "#22C55E";
      mcaStatus = "✅ MCA ROSTER: CLEARANCE";
      gstStatus = `${mockGST} ACTIVE (✓)`;
      panStatus = `${mockPAN} VERIFIED (✓)`;
      escalationText = "Continuous baseline polling recommended status tracker.";
    } else if (isSecureLogix) {
      nodes = "15000";
      alerts = 5;
      shield = "99.5%";
      pending = "2";
      riskScore = 12;
      riskLabel = "OPTIMAL SECURITY";
      riskColor = "#22C55E";
      mcaStatus = "✅ MCA ROSTER: CLEARANCE";
      gstStatus = `${mockGST} ACTIVE (✓)`;
      panStatus = `${mockPAN} VERIFIED (✓)`;
      escalationText = "Continuous baseline polling recommended status tracker.";
    } else {
      // Default to Vardhaman Infra Solutions
      nodes = "12,847";
      alerts = 184;
      shield = "92.4%";
      pending = "73";
      riskScore = 68;
      riskLabel = "ELEVATED THREAT";
      riskColor = "#EF4444";
      mcaStatus = "⚠️ MCA ROSTER: IDENTITY BREACH";
      gstStatus = `${mockGST} ACTIVE (✓)`;
      panStatus = `${mockPAN} VERIFIED (✓)`;
      escalationText = "Continuous baseline polling recommended status tracker.";
    }

    setMetrics({
      nodes,
      alerts,
      shield,
      pending,
      riskScore,
      riskLabel,
      riskColor,
      mcaStatus,
      gstStatus,
      panStatus,
      escalationText,
      frozen
    });
  };

  useEffect(() => {
    fetchMetrics();
    fetchLiveLogs();
  }, [selectedVendorName]);

  useEffect(() => {
    if (logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
    }
  }, [logs]);

  // Dynamic telemetry engine (simulated live updates)
  useEffect(() => {
    const intervalId = setInterval(() => {
      // Add a random log entry
      const randomLog = `📡 [TELEMETRY] -> Random packet ${Math.floor(Math.random() * 1000)} received at ${new Date().toLocaleTimeString()}`;
      setLogs(prev => {
        const newLogs = [...prev, randomLog];
        if (newLogs.length > 500) newLogs = newLogs.slice(-500);
        return newLogs;
      });
      // Slightly vary riskScore for realism
      setMetrics(prev => {
        if (!prev || prev.riskScore === undefined) return prev;
        const change = (Math.random() - 0.5) * 2; // -1 to 1
        const newScore = Math.max(0, Math.min(100, prev.riskScore + change));
        return { ...prev, riskScore: newScore };
      });
    }, 3500);
    return () => clearInterval(intervalId);
  }, []); // run once on mount

  // Show critical toast when riskScore > 70
  useEffect(() => {
    if (metrics.riskScore !== undefined && metrics.riskScore !== null && metrics.riskScore > 70) {
      setShowCriticalToast(true);
    } else {
      setShowCriticalToast(false);
    }
  }, [metrics.riskScore]);

  // Initialize speech recognition
  useEffect(() => {
    // Check if SpeechRecognition is available in the browser
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = 'en-US';

      recognition.onresult = (event: SpeechRecognitionEvent) => {
        const transcript = event.results[0][0].transcript.trim();

        // Match against known vendor names
        const vendorNames = ["Vardhaman Infra Solutions", "Apex Cyber Defense", "Matrix Shell Logistics", "SecureLogix Labs"];
        const matchedVendor = vendorNames.find(name =>
          name.toLowerCase().includes(transcript.toLowerCase()) ||
          transcript.toLowerCase().includes(name.toLowerCase())
        );

        if (matchedVendor) {
          setSelectedVendorName(matchedVendor);
          // Note: fetchLiveLogs will be called automatically via the selectedVendorName useEffect
        }

        // Stop listening after getting a result
        recognition.stop();
        setIsListening(false);
      };

      recognition.onerror = (event: SpeechRecognitionError) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
      };

      recognition.onend = () => {
        setIsListening(false);
      };

      setSpeechRecognition(recognition);
    } else {
      console.warn('SpeechRecognition API not available in this browser');
    }

    // Cleanup
    return () => {
      if (speechRecognition) {
        speechRecognition.stop();
      }
    };
  }, []); // Empty deps array means run once on mount

  // 3. CLI INTEGRATION TERMINAL ACTION & COPILOT INTERROGATION
  const handleCommandSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!cmdInput.trim()) return;

    const cmd = cmdInput.trim();
    const timestamp = new Date().toLocaleTimeString();
    setLogs(prev => [...prev, `> ${cmd}`]);

    if (cmd === "help") {
      setLogs(prev => [...prev, `🤖 [CLI] Options:\n -> 'clear'\n -> '/scan Apex Cyber Defense'\n -> '/scan Matrix Shell Logistics'\n -> '/scan Vardhaman Infra Solutions'`]);
    } else if (cmd === "clear") {
      setLogs([`🧹 [CONSOLE] Stream log storage purged at ${timestamp}`]);
    } else if (cmd.startsWith("/scan ")) {
      const target = cmd.replace("/scan ", "").trim();
      setSelectedVendorName(target);
      setLogs(prev => [...prev, `📡 [CLI] Context vector re-routed -> ${target}`]);
    } else {
      // TRACE AND INTERROGATE VIA LIVE AI COPILOT ENDPOINT
      try {
        const res = await fetch(`${API_BASE}/copilot/interrogate`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query: cmd, context: { selectedVendorName } })
        });
        if (res.ok) {
          const data = await res.json();
          setLogs(prev => [...prev, `🤖 [COPILOT RESP]: ${data.response || data.output}`]);
        } else {
          setLogs(prev => [...prev, `⚠️ Error mapping AI kernel pipeline integration response.`]);
        }
      } catch (err) {
        setLogs(prev => [...prev, `⚠️ Connection to Copilot Interrogation API lost.`]);
      }
    }
    setCmdInput("");
  };

  const triggerDownloadLog = () => {
    const blob = new Blob([logs.join('\n')], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `GOVSWARM_FORENSIC_LOG.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Helper variables for risk progress bar
  const riskPercent = metrics?.riskScore ?? 68;
  let riskBarColor = '#EF4444'; // default critical
  if (riskPercent < 50) riskBarColor = '#22C55E';
  else if (riskPercent < 80) riskBarColor = '#F59E0B';

  const steps = ["Data Ingestion", "Entity Extraction", "Registry Match", "Compliance Audit", "Risk Profiling", "Intel Report"];

  return (
    <div style={{
      height: '100vh',
      display: 'grid',
      gridTemplateRows: 'auto 1fr auto',
      gap: '24px',
      padding: '24px',
      boxSizing: 'border-box',
      backgroundColor: '#050816',
      color: '#F8FAFC',
      fontFamily: 'monospace',
      letterSpacing: '0.5px'
    }}>
      <AnimationStyles />

      {/* SYSTEM CRITICAL NOTIFICATION MODAL BANNER */}
      {escalationBanner && (
        <div style={{ position: 'fixed', top: '20px', left: '50%', transform: 'translateX(-50%)', zIndex: 9999, width: '90%', maxWidth: '800px', padding: '16px 24px', borderRadius: '8px', background: '#EF4444', color: '#FFF', fontWeight: 'bold', display: 'flex', alignItems: 'center', justifyContent: 'space-between', border: '2px solid #FFF', boxShadow: '0 0 30px rgba(239,68,68,0.8)' }}>
          <div>{escalationBanner}</div>
          <button onClick={() => setEscalationBanner(null)} style={{ background: 'none', border: 'none', color: '#FFF', cursor: 'pointer', fontWeight: '900' }}>[ DISMISS ]</button>
        </div>
      )}

      {/* MAIN TOP HUD */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', maxWidth: '1700px', margin: '0 auto 0 auto', borderBottom: '1px solid rgba(0,229,255,0.15)', paddingBottom: '16px' }}>
        <div>
          <h1 style={{ margin: 0, fontSize: '24px', fontWeight: '900', color: '#FFF', letterSpacing: '2px' }}>
            GOV<span style={{ color: '#00E5FF' }}>SWARM</span> LIVE HUD CORE
          </h1>
          <div style={{ margin: '4px 0 0 0', color: '#64748B', fontSize: '11px' }}>
            SWARM RUNTIME: SEC_ROOT_SYS_01 // ENDPOINTS CONNECTED: API_V1 ACTIVE
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', background: '#0F172A', border: '1px solid rgba(0,229,255,0.3)', borderRadius: '8px', padding: '6px 14px' }}>
            <Search size={14} color="#00E5FF" />
            <select
              value={selectedVendorName}
              onChange={(e) => setSelectedVendorName(e.target.value)}
              style={{ background: 'none', border: 'none', color: '#FFF', fontSize: '12px', outline: 'none', width: '240px', fontFamily: 'monospace', cursor: 'pointer', transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)' }}
            >
              <option value="Vardhaman Infra Solutions" style={{ background: '#0F172A' }}>Vardhaman Infra Solutions</option>
              <option value="Apex Cyber Defense" style={{ background: '#0F172A' }}>Apex Cyber Defense</option>
              <option value="Matrix Shell Logistics" style={{ background: '#0F172A' }}>Matrix Shell Logistics</option>
            </select>
            {!isListening && (
              <Mic
                size={20}
                color="#00E5FF"
                onClick={() => {
                  if (speechRecognition) {
                    speechRecognition.start();
                    setIsListening(true);
                  }
                }}
                style={{ cursor: 'pointer', padding: '4px', background: 'rgba(0,229,255,0.1)', borderRadius: '50%', transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)' }}
              />
            )}
            {isListening && (
              <Mic
                size={20}
                color="#EF4444"
                onClick={() => {
                  if (speechRecognition) {
                    speechRecognition.stop();
                    setIsListening(false);
                  }
                }}
                style={{ cursor: 'pointer', padding: '4px', background: 'rgba(239,68,68,0.1)', borderRadius: '50%', transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)' }}
              />
            )}
          </div>
          <button
            onClick={() => setShowAddOrgModal(true)}
            style={{
              background: 'rgba(0,229,255,0.1)',
              border: '1px solid #00E5FF',
              color: '#00E5FF',
              borderRadius: '4px',
              fontSize: '9px',
              padding: '2px 6px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '2px',
              transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)'
            }}
          >
            <Shield size={16} color="#00E5FF" /> ADD ORG
          </button>
          <Bell size={18} color="#00E5FF" />
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#22C55E', boxShadow: '0 0 8px #22C55E' }} />
            SECURE_MESH_GATEWAY
          </div>
        </div>
      </div>

      {/* LEFT COLUMN: LIVE RUNTIME STATISTICS */}
      <div style={{ display: 'flex', height: '100%' }}>
        <div style={{ flex: '1 1 360px', display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <div
            style={{
              background: 'rgba(15, 23, 42, 0.6)',
              backdropFilter: 'blur(10px)',
              WebkitBackdropFilter: 'blur(10px)',
              boxShadow: '0 0 20px rgba(0,229,255,0.15), 0 0 40px rgba(0,229,255,0.1)',
              borderRadius: '16px',
              padding: '16px',
              transform: `rotateX(${matrixTiltY}deg) rotateY(${matrixTiltX}deg)`,
              transition: 'transform 0.2s ease'
            }}
            onMouseMove={(e) => {
              const { clientX, clientY } = e;
              const { width, height, left, top } = e.currentTarget.getBoundingClientRect();
              const x = clientX - (left + width / 2);
              const y = clientY - (top + height / 2);
              const tiltX = (y / (height / 2)) * 5; // max 5 degrees
              const tiltY = (x / (width / 2)) * 5;
              setMatrixTiltX(tiltX);
              setMatrixTiltY(tiltY);
            }}
            onMouseLeave={() => {
              setMatrixTiltX(0);
              setMatrixTiltY(0);
            }}
          >
            <div style={{ fontSize: '11px', color: '#64748B', marginBottom: '12px' }}>// GLOBAL TELEMETRY MATRIX (API SYNCED)</div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', width: '100%' }}>
              <div style={{ background: '#050816', border: '1px solid rgba(255,255,255,0.02)', borderRadius: '8px', padding: '12px' }}>
                <div style={{ fontSize: '9px', color: '#64748B', marginBottom: '4px' }}>ACTIVE SWARM NODES</div>
                <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#FFF' }}>{metrics.nodes || "..."}</div>
                <div style={{ fontSize: '9px', color: '#00E5FF', marginTop: '4px' }}>LIVE STREAM</div>
              </div>
              <div style={{ background: '#050816', border: '1px solid rgba(255,255,255,0.02)', borderRadius: '8px', padding: '12px' }}>
                <div style={{ fontSize: '9px', color: '#64748B', marginBottom: '4px' }}>HIGH RISK ALERTS</div>
                <div style={{ fontSize: '18px', fontWeight: 'bold', color: metrics.riskColor || '#FFF' }}>{metrics.alerts ?? "..."}</div>
                <div style={{ fontSize: '9px', color: '#64748B', marginTop: '4px' }}>BUFFER FEED</div>
              </div>
              <div style={{ background: '#050816', border: '1px solid rgba(255,255,255,0.02)', borderRadius: '8px', padding: '12px' }}>
                <div style={{ fontSize: '9px', color: '#64748B', marginBottom: '4px' }}>COMPLIANCE SHIELD</div>
                <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#22C55E' }}>{metrics.shield || "..."}</div>
                <div style={{ fontSize: '9px', color: '#64748B', marginTop: '4px' }}>SYSTEM COMPLIANT</div>
              </div>
              <div style={{ background: '#050816', border: '1px solid rgba(255,255,255,0.02)', borderRadius: '8px', padding: '12px' }}>
                <div style={{ fontSize: '9px', color: '#64748B', marginBottom: '4px' }}>PENDING REVIEWS</div>
                <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#F59E0B' }}>{metrics.pending || "..."}</div>
                <div style={{ fontSize: '9px', color: '#64748B', marginTop: '4px' }}>TASK QUEUE</div>
              </div>
            </div>
          </div>

          {/* TELEMETRY FEED CONSOLE CONTAINER */}
          <div
            style={{
              background: 'rgba(15, 23, 42, 0.6)',
              backdropFilter: 'blur(10px)',
              WebkitBackdropFilter: 'blur(10px)',
              boxShadow: '0 0 20px rgba(0,229,255,0.15), 0 0 40px rgba(0,229,255,0.1)',
              borderRadius: '16px',
              padding: '16px',
              transform: `rotateX(${logsTiltY}deg) rotateY(${logsTiltX}deg)`,
              transition: 'transform 0.2s ease'
            }}
            onMouseMove={(e) => {
              const { clientX, clientY } = e;
              const { width, height, left, top } = e.currentTarget.getBoundingClientRect();
              const x = clientX - (left + width / 2);
              const y = clientY - (top + height / 2);
              const tiltX = (y / (height / 2)) * 5; // max 5 degrees
              const tiltY = (x / (width / 2)) * 5;
              setLogsTiltX(tiltX);
              setLogsTiltY(tiltY);
            }}
            onMouseLeave={() => {
              setLogsTiltX(0);
              setLogsTiltY(0);
            }}
          >
            <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: '100%', background: 'linear-gradient(to bottom, transparent 45%, rgba(0,229,255,0.02) 50%, transparent 55%)', animation: 'scanline 6s linear infinite', pointerEvents: 'none' }} />

            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '12px', borderBottom: '1px solid rgba(255,255,255,0.05)', paddingBottom: '8px', zIndex: 5 }}>
              <span style={{ fontSize: '11px', fontWeight: 'bold', color: '#00E5FF' }}>📡 SWARM LIVE ENDPOINT STREAM LOGS</span>
              <div style={{ display: 'flex', gap: '8px', marginLeft: 'auto' }}>
                <button onClick={() => setIsScanning(!isScanning)} style={{ background: 'rgba(0,229,255,0.1)', border: '1px solid #00E5FF', color: '#00E5FF', borderRadius: '4px', fontSize: '9px', padding: '2px 6px', cursor: 'pointer', transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)' }}>
                  {isScanning ? "PAUSE" : "RESUME"}
                </button>
                <button onClick={triggerDownloadLog} style={{ background: 'rgba(34,197,94,0.1)', border: '1px solid #22C55E', color: '#22C55E', borderRadius: '4px', fontSize: '9px', padding: '2px 6px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '2px', transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)' }}>
                  <Download size={8} /> EXTRACT
                </button>
              </div>
            </div>

            <div ref={logContainerRef} style={{ background: '#050816', borderRadius: '8px', padding: '12px', height: '190px', overflowY: 'auto', fontSize: '10px', color: '#38BDF8', scrollBehavior: 'smooth', zIndex: 5 }}>
              {logs.length === 0 ? (
                <div style={{ color: '#64748B' }}>Awaiting live agent heartbeat stream array...</div>
              ) : (
                logs.map((log, idx) => (
                  <div key={idx} style={{ marginBottom: '6px', color: log.includes('🚨') || log.includes('BREACH') || log.includes('CRITICAL') ? '#EF4444' : log.includes('⚠️') ? '#F59E0B' : '#38BDF8' }}>
                    {log}
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* MIDDLE LAYER CENTER: DYNAMIC FORENSIC ORB */}
        <div style={{ flex: '1.8 1 500px', display: 'flex', flexDirection: 'column', gap: '20px', height: '100%' }}>
          <HolographicOrb vendor={vendor} metrics={metrics} />

          {/* ACTIVE DETAILS NAVIGATION LAYERS */}
          <div style={{ background: '#0F172A', borderRadius: '16px', border: '1px solid rgba(255,255,255,0.05)', padding: '16px' }}>
            <div style={{ display: 'flex', gap: '4px', borderBottom: '1px solid rgba(255,255,255,0.08)', paddingBottom: '10px', marginBottom: '12px' }}>
              {["directors", "taxation", "sanctions"].map((tName) => (
                <button key={tName} onClick={() => setActiveTab(tName)} style={{ background: activeTab === tName ? 'rgba(0,229,255,0.15)' : 'none', border: 'none', borderBottom: activeTab === tName ? '2px solid #00E5FF' : 'none', color: activeTab === tName ? '#00E5FF' : '#64748B', fontSize: '11px', padding: '6px 12px', cursor: 'pointer', fontWeight: 'bold', textTransform: 'uppercase' }}>
                  {tName === "directors" ? "DIRECTOR NETWORK MESH" : tName === "taxation" ? "TAXATION HISTORY" : "SANCTIONS LIST"}
                </button>
              ))}
            </div>

            <div style={{ minHeight: '60px', fontSize: '11px', color: '#CBD5E1', lineHeight: '1.5' }}>
              {activeTab === "directors" && (
                <div>
                  <div style={{ color: '#00E5FF', fontWeight: 'bold', marginBottom: '6px' }}>Active Linked Corporate Director Logs:</div>
                  • Structural mapping targets tracked continuously through active database queues.
                </div>
              )}
              {activeTab === "taxation" && (
                <div>
                  <div style={{ color: '#22C55E', fontWeight: 'bold', marginBottom: '6px' }}>GSTIN Telemetry Audit Records:</div>
                  • Registration filing state condition: <span style={{ color: '#FFF' }}>{metrics.gstStatus}</span>
                </div>
              )}
              {activeTab === "sanctions" && (
                <div>
                  <div style={{ color: '#EF4444', fontWeight: 'bold', marginBottom: '6px' }}>Global Entity Screening Core Flags:</div>
                  • Current status: <span style={{ color: '#FFF' }}>{metrics.mcaStatus}</span>
                </div>
              )}
            </div>
          </div>

          <SwarmGraph />
        </div>

        {/* RIGHT PANEL CONTROL LAYER */}
        <div style={{ flex: '1.2 1 400px', height: '100%', display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <div style={{ background: '#0F172A', border: '1px solid rgba(239,68,68,0.25)', borderRadius: '24px', padding: '20px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px', borderBottom: '1px solid rgba(255,255,255,0.08)', paddingBottom: '12px' }}>
              <ShieldAlert size={16} color="#EF4444" />
              <span style={{ fontSize: '12px', fontWeight: 'bold', color: '#FFF' }}>DECISION INTELLIGENCE OPERATOR HUB</span>
            </div>

            <div
              style={{
                background: 'rgba(15, 23, 42, 0.6)',
                backdropFilter: 'blur(10px)',
                WebkitBackdropFilter: 'blur(10px)',
                boxShadow: '0 0 20px rgba(0,229,255,0.15), 0 0 40px rgba(0,229,255,0.1)',
                borderRadius: '12px',
                padding: '14px',
                marginBottom: '16px',
                transform: `rotateX(${targetCaseTiltY}deg) rotateY(${targetCaseTiltX}deg)`,
                transition: 'transform 0.2s ease'
              }}
              onMouseMove={(e) => {
                const { clientX, clientY } = e;
                const { width, height, left, top } = e.currentTarget.getBoundingClientRect();
                const x = clientX - (left + width / 2);
                const y = clientY - (top + height / 2);
                const tiltX = (y / (height / 2)) * 5; // max 5 degrees
                const tiltY = (x / (width / 2)) * 5;
                setTargetCaseTiltX(tiltX);
                setTargetCaseTiltY(tiltY);
              }}
              onMouseLeave={() => {
                setTargetCaseTiltX(0);
                setTargetCaseTiltY(0);
              }}
            >
              <div style={{ fontSize: '10px', color: '#64748B' }}>TARGET CASE ENTITY</div>
              <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#00E5FF', marginTop: '2px' }}>{selectedVendorName}</div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginTop: '12px', fontSize: '11px' }}>
                <div>GSTIN: <span style={{ color: '#38BDF8', fontWeight: 'bold' }}>{metrics.gstStatus || (() => {
  const map = {
    "Vardhaman Infra Solutions": "27AABCU9603R1Z5 ACTIVE",
    "Apex Cyber Defense": "29AABCU9603R2Z6 ACTIVE",
    "Matrix Shell Logistics": "27AABCU9603R1Z5 SUSPENDED",
    "SecureLogix Labs": "30AABCU9603R3Z7 ACTIVE"
  };
  return map[selectedVendorName] || "27AABCU9603R1Z5 ACTIVE";
})()}</span></div>
                <div>PAN STATUS: <span style={{ color: '#38BDF8', fontWeight: 'bold' }}>{metrics.panStatus || (() => {
  const map = {
    "Vardhaman Infra Solutions": "AABCU9603R1 VERIFIED",
    "Apex Cyber Defense": "AABCU9603R2 VERIFIED",
    "Matrix Shell Logistics": "AABCU9603R FAILED",
    "SecureLogix Labs": "AABCU9603R3 VERIFIED"
  };
  return map[selectedVendorName] || "AABCU9603R1 VERIFIED";
})()}</span></div>
                <div style={{ gridColumn: 'span 2', color: '#EF4444', fontWeight: 'bold' }}>{metrics.mcaStatus || "Verifying structural roster..."}</div>
              </div>
            </div>

            <div style={{ marginBottom: '16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', marginBottom: '4px' }}>
                <span style={{ color: '#64748B' }}>COMPOSITE THREAT SCORE INDEX</span>
                <span style={{ color: metrics.riskColor || '#EF4444', fontWeight: 'bold' }}>{metrics.riskScore ?? 0} / 100 ({metrics.riskLabel})</span>
              </div>
              <div style={{ width: '100%', height: '6px', background: '#050816', borderRadius: '4px', overflow: 'hidden' }}>
    <div
      style={{
        width: `${riskPercent}%`,
        height: '100%',
        backgroundColor: riskBarColor,
        transition: 'width 0.5s ease-in-out'
      }}
    />
              </div>
            </div>

            <div style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.05)', borderRadius: '12px', padding: '12px', fontSize: '11px' }}>
              <span style={{ color: '#F59E0B', fontWeight: 'bold' }}>SARKARI PROTOCOL ESCALATION MANDATE:</span>
              <p style={{ margin: '4px 0 12px 0', color: '#CBD5E1', lineHeight: '1.4' }}>{metrics.escalationText}</p>

              <button
                onClick={() => setEscalationBanner(`🚨 ENFORCEMENT ACTION FORENSICS RECORD DISPATCHED FOR ENTITY -> ${selectedVendorName.toUpperCase()}`)}
                style={{ width: '100%', background: '#EF4444', color: '#FFF', border: 'none', padding: '10px', borderRadius: '6px', fontWeight: 'bold', cursor: 'pointer', fontFamily: 'monospace', letterSpacing: '1px', transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)' }}
              >
                TRIGGER ENFORCEMENT REPORT DISPATCH
              </button>
            </div>

            <div style={{ background: '#0F172A', border: '1px solid rgba(0,229,255,0.15)', borderRadius: '16px', padding: '16px' }}>
              <div style={{ fontSize: '11px', color: '#64748B', marginBottom: '12px' }}>// COMPLIANCE DOCUMENT VAULT</div>
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(120px, 1fr))',
                gap: '12px'
              }}>
                {/* Document cards */}
                <div style={{
                  background: '#050816',
                  border: '1px solid rgba(255,255,255,0.02)',
                  borderRadius: '8px',
                  padding: '12px',
                  textAlign: 'center'
                }}>
                  <div style={{ fontSize: '10px', color: '#64748B', marginBottom: '4px' }}>Audit_Report.pdf</div>
                  <div style={{
                    width: '32px',
                    height: '32px',
                    background: 'rgba(0,229,255,0.1)',
                    borderRadius: '50%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    margin: '0 auto 8px'
                  }}>
                    <Activity size={16} color="#00E5FF" />
                  </div>
                </div>
                <div style={{
                  background: '#050816',
                  border: '1px solid rgba(255,255,255,0.02)',
                  borderRadius: '8px',
                  padding: '12px',
                  textAlign: 'center'
                }}>
                  <div style={{ fontSize: '10px', color: '#64748B', marginBottom: '4px' }}>Tax_Clearance.json</div>
                  <div style={{
                    width: '32px',
                    height: '32px',
                    background: 'rgba(0,229,255,0.1)',
                    borderRadius: '50%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    margin: '0 auto 8px'
                  }}>
                    <Activity size={16} color="#00E5FF" />
                  </div>
                </div>
                {/* Placeholder for uploading new document */}
                <div style={{
                  background: '#050816',
                  border: '1px dashed rgba(0,229,255,0.3)',
                  borderRadius: '8px',
                  padding: '16px',
                  textAlign: 'center',
                  cursor: 'pointer'
                }}
                onClick={() => {
                  // Simulate upload
                  alert('Upload document functionality triggered! (simulated)');
                }}
                >
                  <div style={{ fontSize: '10px', color: '#64748B', marginBottom: '8px' }}>+ Upload New Document</div>
                  <div style={{
                    width: '48px',
                    height: '48px',
                    background: 'rgba(0,229,255,0.1)',
                    borderRadius: '50%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}>
                    <Upload size={24} color="#00E5FF" />
                  </div>
                  <div style={{ fontSize: '9px', color: '#00E5FF', marginTop: '8px' }}>Click to upload</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* FOOTER INTERACTIVE AI LOG INJECTION LINE */}
      <div style={{ maxWidth: '1700px', margin: '0 auto 0 auto', background: '#0A0F24', border: '1px solid rgba(0,229,255,0.2)', borderRadius: '12px', padding: '14px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '11px', color: '#00E5FF', fontWeight: 'bold', marginBottom: '8px' }}>
          <Terminal size={14} /> Enter command [help, clear, /scan [vendorName]] // INJECT SYSTEM INQUIRY TO LIVE AI COPILOT
        </div>
        <form onSubmit={handleCommandSubmit} style={{ display: 'flex', width: '100%' }}>
          <span style={{ color: '#00E5FF', marginRight: '8px', fontSize: '14px', fontWeight: 'bold' }}>&gt;</span>
          <input
            type="text"
            value={cmdInput}
            onChange={(e) => setCmdInput(e.target.value)}
            placeholder="Interrogate active agents or route system contexts here..."
            style={{ flex: 1, background: 'none', border: 'none', outline: 'none', color: '#38BDF8', fontFamily: 'monospace', fontSize: '13px' }}
          />
        </form>
      </div>

      {/* CRITICAL ALERT TOAST */}
      {showCriticalToast && (
        <div style={{
          position: 'fixed',
          top: '20px',
          right: '20px',
          background: 'rgba(239, 68, 68, 0.9)',
          color: 'white',
          padding: '12px 20px',
          borderRadius: '8px',
          fontSize: '14px',
          fontWeight: 'bold',
          boxShadow: '0 0 20px rgba(239, 68, 68, 0.7)',
          zIndex: '1000',
          animation: 'slideInRight 0.3s ease-out'
        }}>
          [CRITICAL THREAT DETECTED]: High Risk Entity Loaded
        </div>
      )}
      {showAddOrgModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <div style={{
            background: '#0F172A',
            border: '1px solid rgba(0,229,255,0.3)',
            borderRadius: '16px',
            padding: '24px',
            width: '400px',
            maxWidth: '90%',
            color: '#F8FAFC'
          }}>
            <h2 style={{ marginTop: 0, color: '#00E5FF' }}>Add New Organization</h2>
            <form
              onSubmit={(e) => {
                e.preventDefault();
                setShowAddOrgModal(false);
                setNewOrgName('');
                setNewOrgRiskScore('');
                setNewOrgComplianceStatus('');
                alert('Organization added successfully! (simulated)');
              }}
            >
              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', marginBottom: '4px', fontSize: '11px', color: '#64748B' }}>Organization Name</label>
                <input
                  type="text"
                  value={newOrgName}
                  onChange={(e) => setNewOrgName(e.target.value)}
                  placeholder="Enter organization name"
                  style={{
                    width: '100%',
                    padding: '8px',
                    background: 'none',
                    border: '1px solid rgba(0,229,255,0.3)',
                    borderRadius: '4px',
                    color: '#F8FAFC',
                    fontFamily: 'monospace',
                    fontSize: '13px'
                  }}
                />
              </div>
              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', marginBottom: '4px', fontSize: '11px', color: '#64748B' }}>Initial Risk Score (0-100)</label>
                <input
                  type="number"
                  value={newOrgRiskScore}
                  onChange={(e) => setNewOrgRiskScore(e.target.value)}
                  min="0"
                  max="100"
                  placeholder="Enter risk score"
                  style={{
                    width: '100%',
                    padding: '8px',
                    background: 'none',
                    border: '1px solid rgba(0,229,255,0.3)',
                    borderRadius: '4px',
                    color: '#F8FAFC',
                    fontFamily: 'monospace',
                    fontSize: '13px'
                  }}
                />
              </div>
              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', marginBottom: '4px', fontSize: '11px', color: '#64748B' }}>Compliance Status</label>
                <select
                  value={newOrgComplianceStatus}
                  onChange={(e) => setNewOrgComplianceStatus(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '8px',
                    background: 'none',
                    border: '1px solid rgba(0,229,255,0.3)',
                    borderRadius: '4px',
                    color: '#000000',
                    fontFamily: 'monospace',
                    fontSize: '13px'
                  }}
                >
                  <option value="" style={{ color: '#000000' }}>Select status</option>
                  <option value="Compliant" style={{ color: '#000000' }}>Compliant</option>
                  <option value="Non-Compliant" style={{ color: '#000000' }}>Non-Compliant</option>
                  <option value="Under Review" style={{ color: '#000000' }}>Under Review</option>
                </select>
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px', marginTop: '24px' }}>
                <button
                  type="button"
                  onClick={() => {
                    setShowAddOrgModal(false);
                    setNewOrgName('');
                    setNewOrgRiskScore('');
                    setNewOrgComplianceStatus('');
                  }}
                  style={{
                    background: 'rgba(34,197,94,0.1)',
                    border: '1px solid #22C55E',
                    color: '#22C55E',
                    borderRadius: '4px',
                    fontSize: '9px',
                    padding: '2px 6px',
                    cursor: 'pointer',
                    transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)'
                  }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  style={{
                    background: '#00E5FF',
                    color: '#050816',
                    border: 'none',
                    borderRadius: '4px',
                    fontSize: '9px',
                    padding: '2px 6px',
                    cursor: 'pointer',
                    fontWeight: 'bold',
                    transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)'
                  }}
                >
                  Add Organization
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}