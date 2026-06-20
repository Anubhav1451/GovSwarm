import { useState, useEffect, useRef } from 'react';
import { Terminal, Play, Cpu } from 'lucide-react';

export default function CopilotPanel() {
  const [logs, setLogs] = useState<string[]>([
    "⚙️ [SYSTEM KERNEL] -> Initializing GovSwarm Node SEC_ROOT_SYS_01...",
    "🔑 [AUTH EXECUTED] -> Security clearance level ALPHA established.",
    "🛡️ [ANTI-FRAUD MESH] -> Live connection hooked to MCA, GSTIN, and Central Watchlists."
  ]);
  const [isScanning, setIsScanning] = useState(true);
  const logEndRef = useRef<HTMLDivElement>(null);

  const advancedIntelLogs = [
    "🔍 [MCA AGENT] -> Scanning corporate director roster for 'Vardhaman Infra'...",
    "⚠️ [MCA ROSTER BREACH] -> Director 'Rajesh Vardhaman' matches cross-linkage on 8 sub-shell units.",
    "🤖 [PAN SWARM] -> Verification signal dispatched to NSDL core API...",
    "✅ [PAN AGENT] -> Verification status: VALIDATED // Active match found.",
    "🕵️ [FRAUD ENGINE] -> Running high-frequency layering algorithm graph...",
    "🚨 [ALERT DETECTED] -> Circular transaction pattern matched with overseas blacklisted entity #CN-991.",
    "📊 [RISK INTEGRATOR] -> Recalculating threat composite index... Composite score set to: 68/100.",
    "⚠️ [COMPLIANCE MONITOR] -> Flagging mismatch on Form AOC-4 filing continuity.",
    "🤖 [GST AGENT] -> Multi-year GSTR-3B filing trend evaluated: OPTIMAL (No discrepancy).",
    "⚙️ [SWARM COMPLETED] -> Execution telemetry logs successfully updated in Central HUD."
  ];

  useEffect(() => {
    if (!isScanning) return;

    const interval = setInterval(() => {
      const randomLine = advancedIntelLogs[Math.floor(Math.random() * advancedIntelLogs.length)];
      const timestamp = new Date().toLocaleTimeString();
      setLogs(prev => [...prev, `[${timestamp}] ${randomLine}`]);
    }, 4000);

    return () => clearInterval(interval);
  }, [isScanning]);

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  return (
    <div style={{ background: '#0F172A', border: '1px solid rgba(0,229,255,0.15)', borderRadius: '16px', padding: '16px', textAlign: 'left', height: '100%', display: 'flex', flexDirection: 'column', boxSizing: 'border-box' }}>

      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px', borderBottom: '1px solid rgba(255,255,255,0.05)', paddingBottom: '8px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Terminal size={14} color="#00E5FF" />
          <span style={{ fontSize: '11px', fontWeight: 'bold', color: '#00E5FF', fontFamily: 'monospace', letterSpacing: '1px' }}>GOVSWARM SWARM AGENT STREAM</span>
        </div>
        <button
          onClick={() => setIsScanning(!isScanning)}
          style={{ background: isScanning ? 'rgba(239,68,68,0.1)' : 'rgba(34,197,94,0.1)', border: isScanning ? '1px solid rgba(239,68,68,0.3)' : '1px solid rgba(34,197,94,0.3)', color: isScanning ? '#EF4444' : '#22C55E', borderRadius: '4px', fontSize: '9px', padding: '2px 6px', cursor: 'pointer', fontFamily: 'monospace', display: 'flex', alignItems: 'center', gap: '4px' }}
        >
          {isScanning ? (
            <>
              <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#EF4444', display: 'inline-block' }} />
              PAUSE STREAM
            </>
          ) : (
            <>
              <Play size={8} fill="#22C55E" />
              RESUME AGENTS
            </>
          )}
        </button>
      </div>

      <div style={{ flex: 1, background: '#050816', borderRadius: '8px', padding: '12px', minHeight: '210px', maxHeight: '250px', overflowY: 'auto', fontFamily: 'monospace', fontSize: '10px', color: '#38BDF8', border: '1px solid rgba(255,255,255,0.02)', marginBottom: '12px' }}>
        {logs.map((log, idx) => {
          let logColor = '#38BDF8';
          if (log.includes('🚨') || log.includes('ALERT') || log.includes('BREACH')) logColor = '#EF4444';
          if (log.includes('⚠️') || log.includes('WARNING')) logColor = '#F59E0B';
          if (log.includes('✅') || log.includes('VALIDATED')) logColor = '#22C55E';

          return (
            <div key={idx} style={{ marginBottom: '6px', color: logColor, lineHeight: '1.4' }}>
              {log}
            </div>
          );
        })}
        <div ref={logEndRef} />
      </div>

      <div style={{ display: 'flex', alignItems: 'center', background: 'rgba(255,255,255,0.02)', padding: '6px 10px', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.04)', fontSize: '9px', color: '#64748B' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <Cpu size={10} color="#00E5FF" />
          <span>SWARM_BUFFER: STABLE</span>
        </div>
        <span style={{ marginLeft: 'auto', color: '#00E5FF' }}>THREAT_LEVEL: ELEVATED (68%)</span>
      </div>

    </div>
  );
}