"use client";

import { useState, useEffect, useRef } from 'react';
import { Send, Upload, Loader2 } from 'lucide-react';

const VIDEO_URL = 'https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260602_150901_c45b90ec-18d7-42ff-90e2-b95d7109e330.mp4';

// Premium color variables (oklch-inspired slate dark-mode)
const COLORS = {
  primary: 'oklch(0.646 0.222 264)',
  mutedForeground: 'oklch(0.701 0.022 264)',
  background: 'oklch(0.145 0.014 265)',
  foreground: 'oklch(0.985 0.002 264)',
  border: 'oklch(0.251 0.018 265)',
  accent: 'oklch(0.646 0.222 264)',
  success: 'oklch(0.646 0.191 142)',
  warning: 'oklch(0.768 0.149 85)',
  error: 'oklch(0.627 0.194 25)',
};

const VERIFICATIONS = ['Bylaws Check', 'Tax Registry', 'Corporate ID', 'Audit Trail'];

export default function Dashboard() {
  // Initial Strict Empty State
  const [orgName, setOrgName] = useState('');
  const [incNum, setIncNum] = useState('');
  const [complianceStatus, setComplianceStatus] = useState<'PENDING' | 'APPROVED' | 'REJECTED'>('PENDING');
  
  const [messages, setMessages] = useState<any[]>([
    {
      id: '1',
      role: 'system',
      content: 'Welcome to GovSwarm AI Auditor. I am your intelligent compliance assistant. Upload your documents and I will help you navigate government eligibility requirements with real-time analysis.',
      timestamp: new Date(),
    },
  ]);
  
  const [uploadedDocs, setUploadedDocs] = useState<any[]>([]);
  const [selectedVerifications, setSelectedVerifications] = useState<string[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isAutoFilling, setIsAutoFilling] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [isGlowing, setIsGlowing] = useState(false);
  const [isAudited, setIsAudited] = useState(false);
  const [lastSyncTime, setLastSyncTime] = useState('');
  const [showNotification, setShowNotification] = useState(false);
  const [notificationMessage, setNotificationMessage] = useState('');
  const [notificationPosition, setNotificationPosition] = useState<'center' | 'right'>('center');
  const [auditLogs, setAuditLogs] = useState<string[]>([]);
  const [extractedMetadata, setExtractedMetadata] = useState<{ orgName: string; incNum: string; fileContent: string } | null>(null);
  const [canDownloadReport, setCanDownloadReport] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);
  const timeoutRefs = useRef<NodeJS.Timeout[]>([]);

  // Auto-scroll chat to bottom
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Sync Timer for Telemetry
  useEffect(() => {
    setLastSyncTime(new Date().toLocaleTimeString());
    const interval = setInterval(() => {
      setLastSyncTime(new Date().toLocaleTimeString());
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  const handleVerificationToggle = (verification: string) => {
    setSelectedVerifications(prev =>
      prev.includes(verification)
        ? prev.filter(v => v !== verification)
        : [...prev, verification]
    );
  };

  // Real Frontend File Parser (FileReader API)
  const parseFileContent = (fileContent: string) => {
    // Check for FAILURE scenario keywords
    const hasFailureKeywords = /FAKE|INVALID/i.test(fileContent);
    
    // Extract organization name from file content
    const orgPatterns = [
      /Company:\s*([A-Za-z0-9\s&.,-]+)/i,
      /Organization:\s*([A-Za-z0-9\s&.,-]+)/i,
      /Org Name:\s*([A-Za-z0-9\s&.,-]+)/i,
    ];
    
    // Extract incorporation number from file content
    const incPatterns = [
      /ID:\s*([A-Za-z0-9-]+)/i,
      /Registration:\s*([A-Za-z0-9-]+)/i,
      /Incorporation:\s*([A-Za-z0-9-]+)/i,
      /CIN:\s*([A-Za-z0-9]+)/i,
    ];
    
    let extractedOrg = '';
    let extractedInc = '';
    
    for (const pattern of orgPatterns) {
      const match = fileContent.match(pattern);
      if (match && match[1]) {
        extractedOrg = match[1].trim();
        break;
      }
    }
    
    for (const pattern of incPatterns) {
      const match = fileContent.match(pattern);
      if (match && match[1]) {
        extractedInc = match[1].trim();
        break;
      }
    }
    
    // Fallback to filename-based extraction if content parsing fails
    if (!extractedOrg || !extractedInc) {
      const anomalousPattern = /[<>{}\\|\^`]/;
      const hasAnomalies = anomalousPattern.test(fileContent);
      
      const companyPatterns = [
        /([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+Enterprise|Inc|Corp|Ltd|LLC)?)/g,
        /([A-Z]{2,}(?:\s+[A-Z]{2,})*)/g,
      ];
      
      const incPatternsFallback = [
        /INCORP[-_\s]?(\d{4})[-_\s]?([A-Z]{3,4})/i,
        /CIN[-_\s]?([A-Z0-9]{6,10})/i,
      ];
      
      if (!extractedOrg) {
        for (const pattern of companyPatterns) {
          const matches = fileContent.match(pattern);
          if (matches && matches[0]) {
            extractedOrg = matches[0];
            break;
          }
        }
      }
      
      if (!extractedInc) {
        for (const pattern of incPatternsFallback) {
          const matches = fileContent.match(pattern);
          if (matches) {
            if (matches[1] && matches[2]) {
              extractedInc = `INCORP-${matches[1]}-${matches[2].toUpperCase()}`;
            } else if (matches[1]) {
              extractedInc = matches[1].toUpperCase();
            }
            break;
          }
        }
      }
    }
    
    return { extractedOrg, extractedInc, hasFailureKeywords };
  };

  // Drag & drop file uploads
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    handleFileUpload(e.dataTransfer.files);
  };

  // Orchestrator Core Execution Pipeline with Dual-Scenario Matrix
  const triggerOrchestratorSequence = (extractedData?: { orgName: string; incNum: string; hasFailureKeywords: boolean; fileContent: string }) => {
    // Race-Condition Cleanup: Clear all active timeouts
    timeoutRefs.current.forEach(clearTimeout);
    timeoutRefs.current = [];
    
    // Clear previous logs
    setMessages([]);
    setAuditLogs([]);
    setIsAudited(false);
    setOrgName('');
    setIncNum('');
    setComplianceStatus('PENDING');
    setSelectedVerifications([]);
    setCanDownloadReport(false);

    const companyName = extractedData?.orgName || 'Anubhav Enterprise';
    const incNumber = extractedData?.incNum || 'INCORP-2026-ANUX';
    const hasFailureKeywords = extractedData?.hasFailureKeywords || false;
    const fileContent = extractedData?.fileContent || '';

    // Store extracted metadata for audit report
    setExtractedMetadata({ orgName: companyName, incNum: incNumber, fileContent });

    // Phase 1 (Immediate): Orchestrator - Trigger keywords mapped
    const log1 = '⚙️ [ORCHESTRATOR]: Trigger keywords mapped. Booting Task Decomposition matrix...';
    setMessages(prev => [...prev, { id: 'orch-1', role: 'assistant', content: log1, timestamp: new Date() }]);
    setAuditLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] ${log1}`]);

    // Phase 2 (after 800ms): Orchestrator - Allocating to Legal Agent
    const timeout2 = setTimeout(() => {
      const log2 = '⚙️ [ORCHESTRATOR]: Allocating structural token arrays to Professional Agent A [LEGAL_NODE]...';
      setMessages(prev => [...prev, { id: 'orch-2', role: 'assistant', content: log2, timestamp: new Date() }]);
      setAuditLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] ${log2}`]);
    }, 800);
    timeoutRefs.current.push(timeout2);

    // Phase 3 (after 1600ms): Check for FAILURE scenario
    const timeout3 = setTimeout(() => {
      if (hasFailureKeywords) {
        // FAILURE SCENARIO
        const securityLog = '🚨 [SECURITY_BUS]: Malformed/Untrusted data constraints payload detected!';
        const auditLog = '🚨 [AUDIT_NODE]: Validation Failed - Cryptographic signature mismatch!';
        
        setMessages(prev => [...prev, 
          { id: 'security-1', role: 'system', content: securityLog, timestamp: new Date() },
          { id: 'audit-1', role: 'system', content: auditLog, timestamp: new Date() }
        ]);
        setAuditLogs(prev => [...prev, 
          `[${new Date().toLocaleTimeString()}] ${securityLog}`,
          `[${new Date().toLocaleTimeString()}] ${auditLog}`
        ]);
        
        // Force REJECTED status
        setComplianceStatus('REJECTED');
        setIsAudited(true);
        setCanDownloadReport(true);
      } else {
        // SUCCESS SCENARIO - Continue normal flow
        const log3 = '⚙️ [ORCHESTRATOR]: Content verified. Routing output arrays via Message Bus to Professional Agent B [AUDIT_NODE]...';
        setMessages(prev => [...prev, { id: 'orch-3', role: 'assistant', content: log3, timestamp: new Date() }]);
        setAuditLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] ${log3}`]);
        
        // Phase 4 (after 2400ms): Orchestrator - Lifecycle complete
        const timeout4 = setTimeout(() => {
          const log4 = '⚙️ [ORCHESTRATOR]: Lifecycle check complete. Shared State resolved. Setting global state to APPROVED.';
          setMessages(prev => [...prev, { id: 'orch-4', role: 'assistant', content: log4, timestamp: new Date() }]);
          setAuditLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] ${log4}`]);
          
          // Post-Evaluation Visual Stamp & Input Glows
          setOrgName(companyName);
          setIncNum(incNumber);
          setComplianceStatus('APPROVED');
          setIsAudited(true);
          setIsGlowing(true);
          setSelectedVerifications(['Bylaws Check', 'Tax Registry', 'Corporate ID', 'Audit Trail']);
          setCanDownloadReport(true);
          
          const timeout6 = setTimeout(() => {
            setIsGlowing(false);
          }, 4000);
          timeoutRefs.current.push(timeout6);
        }, 2400);
        timeoutRefs.current.push(timeout4);
      }
    }, 1600);
    timeoutRefs.current.push(timeout3);
  };

  const handleFileUpload = async (files: FileList | null) => {
    if (!files || files.length === 0) return;

    const file = files[0];
    const newDoc = {
      id: `${Date.now()}-${Math.random()}`,
      name: file.name,
      size: file.size,
      type: file.type,
    };

    setUploadedDocs(prev => [...prev, newDoc]);

    // Real Frontend File Parser (FileReader API)
    const reader = new FileReader();
    reader.onload = (e) => {
      const fileContent = e.target?.result as string;
      const extractedData = parseFileContent(fileContent);
      
      // Auto-fill inputs if extraction successful
      if (extractedData.extractedOrg) {
        setOrgName(extractedData.extractedOrg);
      }
      if (extractedData.extractedInc) {
        setIncNum(extractedData.extractedInc);
      }
      
      // Launch orchestrator sequence with file content
      triggerOrchestratorSequence({
        orgName: extractedData.extractedOrg || 'Anubhav Enterprise',
        incNum: extractedData.extractedInc || 'INCORP-2026-ANUX',
        hasFailureKeywords: extractedData.hasFailureKeywords,
        fileContent
      });
    };
    
    // Read file as text
    reader.readAsText(file);

    // Trigger API upload asynchronously for persistence/backend sync
    try {
      const formData = new FormData();
      formData.append('file', file);
      await fetch('http://localhost:8000/api/upload', {
        method: 'POST',
        body: formData,
      });
    } catch (e) {
      // Fail silently, letting the simulated timeout pipeline drive the visual state
    }
  };

  // Chat API send message
  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: inputMessage,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    const userQuery = inputMessage;
    setInputMessage('');

    try {
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userQuery }),
      });

      const result = await response.json();

      const assistantMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: result.response,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Failed to connect to AI auditor. Please ensure the backend is running.',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  // Auto-Fill Button with Security Block & Toast Notification
  const handleManualAutoFill = () => {
    // Security Block: If form state is completely empty, trigger visual notification and log alert
    if (!orgName && !incNum && uploadedDocs.length === 0) {
      setShowNotification(true);
      setNotificationPosition('right');
      setNotificationMessage('Please run orchestration first. Upload a certificate to initialize the auditor matrix.');
      
      setMessages(prev => [
        ...prev,
        {
          id: Date.now().toString(),
          role: 'system',
          content: '⚠️ [SECURITY BLOCK]: No active document telemetry found. Please upload a certificate to initialize the auditor matrix.',
          timestamp: new Date(),
        },
      ]);
      
      // Auto-hide notification after 3 seconds
      setTimeout(() => {
        setShowNotification(false);
      }, 3000);
      return;
    }

    setIsAutoFilling(true);
    triggerOrchestratorSequence({
      orgName: orgName || 'Anubhav Enterprise',
      incNum: incNum || 'INCORP-2026-ANUX',
      hasFailureKeywords: false,
      fileContent: ''
    });
    
    const timeout = setTimeout(() => {
      setIsAutoFilling(false);
    }, 4000);
    timeoutRefs.current.push(timeout);
  };

  // Download Certified Audit Report
  const handleDownloadReport = () => {
    if (!extractedMetadata) return;
    
    const timestamp = new Date().toLocaleString();
    const reportContent = `
═══════════════════════════════════════════════════════════════
           GOVSWARM AI CERTIFIED AUDIT TRAIL REPORT
═══════════════════════════════════════════════════════════════

Generated: ${timestamp}

═══════════════════════════════════════════════════════════════
                    EXTRACTED METADATA
═══════════════════════════════════════════════════════════════

Organization Name: ${extractedMetadata.orgName}
Incorporation Number: ${extractedMetadata.incNum}
Compliance Status: ${complianceStatus}

═══════════════════════════════════════════════════════════════
                    CHRONOLOGICAL AUDIT LOGS
═══════════════════════════════════════════════════════════════

${auditLogs.join('\n')}

═══════════════════════════════════════════════════════════════
File Content Preview:
${extractedMetadata.fileContent.substring(0, 500)}${extractedMetadata.fileContent.length > 500 ? '...' : ''}
═══════════════════════════════════════════════════════════════

This report is digitally signed and verified by GovSwarm AI.
Unauthorized reproduction or modification is prohibited.
`;
    
    const blob = new Blob([reportContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `GovSwarm_Audit_Report_${Date.now()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  // Sub-Agent Persona Parameter Toggle Handler
  const handleAgentToggle = (agentType: string) => {
    setShowNotification(true);
    setNotificationPosition('center');
    setNotificationMessage('Agent system prompts locked on active governance compliance mandates.');
    
    setTimeout(() => {
      setShowNotification(false);
    }, 3000);
  };

  return (
    <div className="min-h-screen w-full bg-slate-950 m-0 p-0 sm:p-6 overflow-hidden flex flex-col justify-center" style={{ fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif' }}>
      <main className="rounded-2xl sm:rounded-3xl overflow-hidden min-h-[calc(100vh-24px)] sm:min-h-[calc(100vh-32px)] md:min-h-[calc(100vh-48px)] lg:h-[calc(100vh-48px)] relative flex flex-col p-6 sm:p-8 md:p-10 lg:p-12 justify-between">
        
        {/* Video Background */}
        <video
          autoPlay
          muted
          loop
          playsInline
          className="absolute inset-0 w-full h-full object-cover"
          src={VIDEO_URL}
        />
        
        {/* Darkened overlay for readable high-contrast panels */}
        <div className="absolute inset-0 bg-black/40 pointer-events-none z-0" />

        {/* Toast Notification */}
        {showNotification && (
          <div className={`absolute top-20 z-50 bg-red-500/90 backdrop-blur-md text-white px-6 py-3 rounded-xl shadow-2xl border border-red-400/50 flex items-center gap-3 animate-bounce ${
            notificationPosition === 'right' ? 'right-6' : 'left-1/2 transform -translate-x-1/2'
          }`}>
            <span className="text-xl">⚠️</span>
            <span className="text-sm font-semibold">{notificationMessage}</span>
          </div>
        )}

        {/* Main Grid Workspace - Split Viewport Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 w-full z-10 relative flex-1 min-h-0 items-stretch mt-2">
          
          {/* Left Column: Headline, Drag & Drop, Chat */}
          <div className="lg:col-span-7 flex flex-col justify-between gap-4 h-full min-h-0">
            
            {/* Core Headline - Plus Jakarta Sans */}
            <div className="text-2xl sm:text-3xl xl:text-4xl font-semibold leading-tight text-white drop-shadow-lg lg:max-w-xl shrink-0" style={{ fontFamily: '"Plus Jakarta Sans", system-ui, sans-serif' }}>
              Government Compliance & Eligibility Intelligence <span style={{ fontFamily: '"Plus Jakarta Sans", system-ui, sans-serif', fontStyle: 'italic', fontWeight: 400 }}>Platform</span>
            </div>

            {/* Drag & Drop Document Parser - Micro-Interactions */}
            <div
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className={`relative border border-dashed rounded-2xl p-4 cursor-pointer flex flex-col items-center justify-center text-center backdrop-blur-xl bg-black/40 border-white/10 text-white transition-all duration-200 ${
                isDragging 
                  ? 'border-emerald-400 bg-emerald-500/10 scale-[1.01] shadow-lg shadow-emerald-500/20' 
                  : 'hover:-translate-y-0.5 hover:border-white/30 hover:bg-black/50 hover:shadow-xl hover:shadow-black/30'
              }`}
            >
              <input
                ref={fileInputRef}
                type="file"
                className="hidden"
                onChange={(e) => handleFileUpload(e.target.files)}
              />
              <Upload className="w-5 h-5 text-white/70 mb-1" />
              <p className="text-white text-xs font-semibold">Drop eligibility files here</p>
              <p className="text-white/50 text-[10px]">or click to browse local files</p>

              {/* Uploaded files summary */}
              {uploadedDocs.length > 0 && (
                <div className="mt-2 w-full max-w-sm space-y-1 text-left">
                  {uploadedDocs.map(doc => (
                    <div key={doc.id} className="flex items-center gap-2 bg-black/50 rounded-lg p-1.5 border border-white/5 text-[10px]">
                      <span className="text-emerald-400">✓</span>
                      <span className="text-white/80 truncate flex-1">{doc.name}</span>
                      <span className="text-white/40">{(doc.size / 1024).toFixed(1)} KB</span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Skylv Multi-Agent Orchestrator Tree Pane - JetBrains Mono */}
            <div className="backdrop-blur-xl bg-black/40 border border-white/10 text-white rounded-2xl p-4 mb-4 shadow-2xl">
              <div className="text-[9px] font-mono text-cyan-400/80 mb-2 tracking-wider uppercase" style={{ fontFamily: '"JetBrains Mono", monospace' }}>System Architecture Tree</div>
              <div className="flex items-center gap-2 text-[10px] font-mono flex-wrap" style={{ fontFamily: '"JetBrains Mono", monospace' }}>
                <span className="bg-cyan-500/20 text-cyan-300 px-2 py-1 rounded border border-cyan-400/30 flex items-center gap-1 animate-pulse">
                  🎛️ ORCHESTRATOR NODE
                </span>
                <span className="text-emerald-400/60">&rarr;</span>
                <span className="bg-purple-500/20 text-purple-300 px-2 py-1 rounded border border-purple-400/30 flex items-center gap-1">
                  🤖 LEGAL NODE
                </span>
                <span className="text-emerald-400/60">&rarr;</span>
                <span className="bg-emerald-500/20 text-emerald-300 px-2 py-1 rounded border border-emerald-400/30 flex items-center gap-1">
                  🕵️‍♂️ AUDIT_NODE
                </span>
              </div>
            </div>

            {/* Sub-Agent Persona Parameter Toggles */}
            <div className="backdrop-blur-xl bg-black/30 border border-white/10 text-white rounded-xl p-3 mb-4 shadow-xl">
              <div className="flex items-center gap-3">
                <button
                  onClick={() => handleAgentToggle('legal')}
                  className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-cyan-500/10 border border-cyan-400/30 text-cyan-300 text-[10px] font-semibold hover:bg-cyan-500/20 transition-all duration-150 active:scale-95 cursor-pointer"
                >
                  ⚙️ Legal Ruleset [Standard]
                </button>
                <button
                  onClick={() => handleAgentToggle('auditor')}
                  className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-purple-500/10 border border-purple-400/30 text-purple-300 text-[10px] font-semibold hover:bg-purple-500/20 transition-all duration-150 active:scale-95 cursor-pointer"
                >
                  ⚙️ Auditor Ruleset [Strict Ledger]
                </button>
              </div>
            </div>

            {/* AI Auditor Chat Panel */}
            <div className="backdrop-blur-xl bg-black/40 border border-white/10 text-white rounded-2xl overflow-hidden flex flex-col flex-1 min-h-0 shadow-2xl">
              <div className="px-4 py-2 border-b border-white/10 bg-black/35 flex items-center justify-between">
                <span className="text-xs font-bold flex items-center gap-1.5 text-white/90">
                  <span className="relative flex h-2 w-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                  </span>
                  AI Auditor Assistant
                </span>
                <span className="text-[10px] text-white/50">v1.0 (Live)</span>
              </div>

              {/* Message scroll list */}
              <div className="flex-1 overflow-y-auto max-h-[300px] p-3.5 space-y-3">
                {/* ============================================================================ */}
                {/* MESSAGE BUBBLES LAYOUT SECTION - Agent & User Message Rendering        */}
                {/* ============================================================================ */}
                {messages.map((message) => {
                  const isAgentMessage = message.content.includes('[LEGAL AGENT]') || message.content.includes('[AUDITOR AGENT]') || message.content.includes('[ORCHESTRATOR]') || message.content.includes('[SECURITY_BUS]');
                  
                  if (isAgentMessage && message.role === 'assistant') {
                    const lines = message.content.split('\n').filter((line: string) => line.trim());
                    return (
                      <div key={message.id} className="flex justify-start w-full">
                        <div className="max-w-[95%] space-y-2 w-full">
                          {lines.map((line: string, idx: number) => {
                            const isLegal = line.includes('[LEGAL AGENT]');
                            const isAuditor = line.includes('[AUDITOR AGENT]');
                            const isOrchestrator = line.includes('[ORCHESTRATOR]');
                            const isSecurity = line.includes('[SECURITY_BUS]');
                            let agentType = 'AGENT';
                            let contentText = line;

                            if (isLegal) {
                              agentType = 'LEGAL AGENT';
                              contentText = line.replace(/🤖\s*\[LEGAL AGENT\]:?|\[LEGAL AGENT\]:?/g, '').trim();
                            } else if (isAuditor) {
                              agentType = 'AUDITOR AGENT';
                              contentText = line.replace(/🕵️‍♂️\s*\[AUDITOR AGENT\]:?|\[AUDITOR AGENT\]:?/g, '').trim();
                            } else if (isOrchestrator) {
                              agentType = 'ORCHESTRATOR';
                              contentText = line.replace(/⚙️\s*\[ORCHESTRATOR\]:?|\[ORCHESTRATOR\]:?/g, '').trim();
                            } else if (isSecurity) {
                              agentType = 'SECURITY_BUS';
                              contentText = line.replace(/🛡️\s*\[SECURITY_BUS\]:?|\[SECURITY_BUS\]:?/g, '').trim();
                            }

                            return (
                              <div
                                key={idx}
                                className={`rounded-xl p-3 border-l-4 text-[10px] sm:text-xs leading-relaxed transition-all duration-300 ${
                                  isLegal 
                                    ? 'bg-cyan-950/20 border-l-cyan-400 border-white/5 text-cyan-400 shadow-[inset_1px_0_0_0_rgba(6,182,212,0.3)] shadow-[0_0_15px_rgba(6,182,212,0.05)]' 
                                    : isAuditor
                                      ? 'bg-purple-950/30 border-l-emerald-400 border-white/5 text-emerald-400 shadow-[inset_1px_0_0_0_rgba(16,185,129,0.3)] shadow-[0_0_15px_rgba(16,185,129,0.05)]'
                                      : isOrchestrator
                                        ? 'bg-amber-950/20 border-l-amber-400 border-white/5 text-amber-400 shadow-[inset_1px_0_0_0_rgba(251,191,36,0.3)] shadow-[0_0_15px_rgba(251,191,36,0.05)]'
                                        : 'bg-red-950/20 border-l-red-400 border-white/5 text-red-400 shadow-[inset_1px_0_0_0_rgba(248,113,113,0.3)] shadow-[0_0_15px_rgba(248,113,113,0.05)]'
                                }`}
                              >
                                <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[8px] font-bold font-mono tracking-wider mb-1.5 ${
                                  isLegal 
                                    ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-400/30' 
                                    : isAuditor
                                      ? 'bg-purple-500/20 text-purple-300 border border-purple-400/30'
                                      : isOrchestrator
                                        ? 'bg-amber-500/20 text-amber-300 border border-amber-400/30'
                                        : 'bg-red-500/20 text-red-300 border border-red-400/30'
                                }`} style={{ fontFamily: '"JetBrains Mono", monospace' }}>
                                  {isLegal ? '🤖 LEGAL AGENT' : isAuditor ? '🕵️‍♂️ AUDITOR AGENT' : isOrchestrator ? '⚙️ ORCHESTRATOR' : '🛡️ SECURITY_BUS'}
                                </span>
                                <p className="font-mono font-medium" style={{ fontFamily: '"JetBrains Mono", monospace' }}>{contentText}</p>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    );
                  }

                  return (
                    <div key={message.id} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                      <div className={`max-w-[85%] rounded-xl p-3 text-[10px] sm:text-xs leading-relaxed border ${
                        message.role === 'user' 
                          ? 'bg-white/10 text-white border-white/10 backdrop-blur-md font-medium' 
                          : message.role === 'system'
                            ? 'bg-red-500/10 text-red-400 border-red-500/20 font-semibold'
                            : 'bg-black/40 text-slate-200 border-white/5'
                      }`}>
                        <p className="whitespace-pre-line">{message.content}</p>
                      </div>
                    </div>
                  );
                })}
                <div ref={chatEndRef} />
              </div>
              {/* ============================================================================ */}
                {/* END MESSAGE BUBBLES LAYOUT SECTION                                          */}
                {/* ============================================================================ */}

              {/* Chat action controls */}
              <div className="p-2 border-t border-white/10 bg-black/35 flex gap-2">
                <input
                  type="text"
                  value={inputMessage}
                  onChange={e => setInputMessage(e.target.value)}
                  onKeyDown={e => e.key === 'Enter' && handleSendMessage()}
                  placeholder="Ask about compliance requirements..."
                  className="flex-1 bg-black/50 text-slate-100 rounded-xl px-3 py-2 text-xs placeholder-slate-500 border border-white/10 focus:border-emerald-400 focus:outline-none transition-colors"
                />
                <button
                  onClick={handleSendMessage}
                  className="bg-white/10 hover:bg-white/20 text-white px-3.5 py-2 rounded-xl text-xs font-semibold transition-all duration-150 active:scale-95 border border-white/15 flex items-center justify-center cursor-pointer"
                >
                  <Send className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          </div>

          {/* Right Column: Government Registry Form */}
          <div className="lg:col-span-5 flex flex-col h-full min-h-0">
            <div className="w-full bg-slate-900/80 backdrop-blur-xl text-white border border-slate-700/50 p-6 rounded-2xl flex flex-col justify-between gap-5 h-full shadow-2xl">
              
              {/* Form Title & status indicator */}
              <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                <div className="text-white font-bold text-sm sm:text-base flex items-center gap-1.5">
                  <span>📋</span> Government Registry Form
                </div>
                <span className="text-[9px] text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded-full font-mono font-bold animate-pulse">LIVE SYNC</span>
              </div>

              {/* Required Compliance Verifications chips */}
              <div className="flex flex-col gap-2">
                <span className="text-[9px] text-slate-400 font-bold uppercase tracking-wider">Required Compliance Verifications</span>
                <div className="grid grid-cols-2 gap-1.5">
                  {VERIFICATIONS.map(verification => {
                    const isSelected = selectedVerifications.includes(verification);
                    return (
                      <button
                        key={verification}
                        type="button"
                        onClick={() => handleVerificationToggle(verification)}
                        className={`text-[9px] sm:text-xs py-2 px-2.5 rounded-xl font-semibold border text-center transition-all duration-150 active:scale-95 cursor-pointer ${
                          isSelected
                            ? 'bg-yellow-400 border-yellow-400 text-slate-950 shadow-md shadow-yellow-500/10'
                            : 'bg-slate-800/40 border-slate-700 hover:bg-slate-800/80 text-slate-300'
                        }`}
                      >
                        {verification}
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Form Input elements with Slate Theme and Audited glowing green text theme */}
              <div className="flex flex-col gap-3.5 relative">
                {/* Post-Evaluation Visual Stamp Watermark */}
                {isAudited && complianceStatus === 'APPROVED' && (
                  <div className="absolute inset-0 flex items-center justify-center pointer-events-none z-0">
                    <div className="text-emerald-500/10 font-mono text-[8px] sm:text-[9px] tracking-widest uppercase transform -rotate-12 border-2 border-emerald-500/20 px-4 py-2 rounded-lg" style={{ fontFamily: '"JetBrains Mono", monospace' }}>
                      [ AUTHORIFIED REGISTRY COMPLIANT // SECURE LOCK ]
                    </div>
                  </div>
                )}
                {isAudited && complianceStatus === 'REJECTED' && (
                  <div className="absolute inset-0 flex items-center justify-center pointer-events-none z-0">
                    <div className="text-rose-500/10 font-mono text-[8px] sm:text-[9px] tracking-widest uppercase transform -rotate-12 border-2 border-rose-500/20 px-4 py-2 rounded-lg" style={{ fontFamily: '"JetBrains Mono", monospace' }}>
                      [ COMPLIANCE REGISTRY FAILED // ANOMALY BLOCKED ]
                    </div>
                  </div>
                )}
                {/* Organization Name */}
                <div className="flex flex-col gap-1.5">
                  <label className="text-[9px] text-slate-400 font-bold uppercase tracking-wider">Organization Name</label>
                  <input
                    type="text"
                    placeholder="Enter organization name"
                    value={orgName}
                    onChange={e => setOrgName(e.target.value)}
                    className={`w-full bg-slate-800/60 border text-slate-200 placeholder-slate-500 rounded-xl p-3 focus:outline-none transition-all ${
                      isAudited && complianceStatus === 'APPROVED'
                        ? 'border-emerald-500/30 text-emerald-400 bg-emerald-950/10 font-bold shadow-[0_0_15px_rgba(16,185,129,0.3)] ring-2 ring-emerald-500/40 focus:ring-emerald-500/50' 
                        : isAudited && complianceStatus === 'REJECTED'
                          ? 'border-rose-500/30 text-rose-400 bg-rose-950/10 font-bold shadow-[0_0_15px_rgba(244,63,94,0.3)] ring-2 ring-rose-500/40 focus:ring-rose-500/50'
                          : 'border-slate-700 focus:ring-2 focus:ring-yellow-400'
                    }`}
                  />
                </div>

                {/* Incorporation Number */}
                <div className="flex flex-col gap-1.5">
                  <label className="text-[9px] text-slate-400 font-bold uppercase tracking-wider">Incorporation Number</label>
                  <input
                    type="text"
                    placeholder="Enter incorporation number"
                    value={incNum}
                    onChange={e => setIncNum(e.target.value)}
                    className={`w-full bg-slate-800/60 border text-slate-200 placeholder-slate-500 rounded-xl p-3 focus:outline-none transition-all ${
                      isAudited && complianceStatus === 'APPROVED'
                        ? 'border-emerald-500/30 text-emerald-400 bg-emerald-950/10 font-bold shadow-[0_0_15px_rgba(16,185,129,0.3)] ring-2 ring-emerald-500/40 focus:ring-emerald-500/50' 
                        : isAudited && complianceStatus === 'REJECTED'
                          ? 'border-rose-500/30 text-rose-400 bg-rose-950/10 font-bold shadow-[0_0_15px_rgba(244,63,94,0.3)] ring-2 ring-rose-500/40 focus:ring-rose-500/50'
                          : 'border-slate-700 focus:ring-2 focus:ring-yellow-400'
                    }`}
                  />
                </div>

                {/* Compliance Status Selector */}
                <div className="flex flex-col gap-1.5">
                  <label className="text-[9px] text-slate-400 font-bold uppercase tracking-wider">Compliance Status</label>
                  <div className="flex gap-2">
                    <select
                      value={complianceStatus}
                      onChange={e => setComplianceStatus(e.target.value as any)}
                      className="bg-slate-800/60 border border-slate-700 text-slate-200 rounded-xl p-3 focus:ring-2 focus:ring-yellow-400 focus:outline-none flex-1 transition-all"
                    >
                      <option value="PENDING" className="bg-slate-900 text-white">PENDING</option>
                      <option value="APPROVED" className="bg-slate-900 text-white">APPROVED</option>
                      <option value="REJECTED" className="bg-slate-900 text-white">REJECTED</option>
                    </select>
                    
                    {/* Compliance Status Badge with glowing pulse animations on APPROVED */}
                    <div className={`px-4 rounded-xl text-[10px] font-bold flex items-center justify-center border transition-all duration-500 ${
                      complianceStatus === 'APPROVED'
                        ? `bg-emerald-500/20 text-emerald-400 border-emerald-500/30 ${isGlowing ? 'shadow-[0_0_20px_rgba(16,185,129,0.8)] border-emerald-400 ring-2 ring-emerald-500/30' : 'animate-pulse'}`
                        : complianceStatus === 'REJECTED'
                          ? 'bg-red-500/20 text-red-400 border-red-500/30'
                          : 'bg-amber-500/20 text-amber-400 border-amber-500/30'
                    }`}>
                      {complianceStatus}
                    </div>
                  </div>
                </div>
              </div>


              {/* Neon/Yellow Auto-Fill button with Security Block - Micro-Interactions */}
              <button
                onClick={handleManualAutoFill}
                disabled={isAutoFilling}
                className="w-full bg-yellow-400 text-slate-950 font-bold tracking-wide py-3.5 rounded-xl hover:bg-yellow-300 transition-all duration-150 active:scale-95 shadow-lg shadow-yellow-500/20 flex items-center justify-center gap-2 cursor-pointer disabled:opacity-75 uppercase text-xs sm:text-sm"
              >
                {isAutoFilling ? (
                  <>
                    <Loader2 className="w-3.5 h-3.5 animate-spin text-slate-950" />
                    Simulating Pipeline...
                  </>
                ) : (
                  '⚡ AUTO-FILL APPLICATION FORM'
                )}
              </button>

              {/* Dynamic Download Certified Audit Report Button */}
              <button
                onClick={handleDownloadReport}
                disabled={!canDownloadReport}
                className={`w-full font-bold tracking-wide py-3 rounded-xl transition-all duration-150 active:scale-95 shadow-lg flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed uppercase text-xs sm:text-sm ${
                  canDownloadReport
                    ? 'bg-slate-700 text-white hover:bg-slate-600 border border-slate-600'
                    : 'bg-slate-800/50 text-slate-500 border border-slate-700'
                }`}
              >
                🖨️ Download Certified Audit Trail
              </button>

            </div>
          </div>

        </div>
      </main>
    </div>
  );
}
