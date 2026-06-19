import express, { Request, Response } from 'express';
import cors from 'cors';
import helmet from 'helmet';
import rateLimit from 'express-rate-limit';
import routes from './routes';

const app = express();

// Middleware
app.use(cors());
app.use(helmet());
app.use(express.json());

// Rate limiting: max 200 requests per minute per IP
const limiter = rateLimit({
  windowMs: 60 * 1000, // 1 minute
  max: 200, // limit each IP to 200 requests per windowMs
  standardHeaders: true, // Return rate limit info in the `RateLimit-*` headers
  legacyHeaders: false, // Disable the `X-RateLimit-*` headers
});
app.use(limiter);

// Metrics endpoint (matches frontend expectation)
app.get('/metrics', (req: Request, res: Response) => {
  const vendorName = (req.query.vendor || 'Default') as string;
  console.log(`[Metrics Ingest] Polling metrics telemetry data for vendor: ${vendorName}`);

  // Send back valid structure matching what App.tsx expects
  res.json({
    status: 'success',
    timestamp: new Date().toISOString(),
    metrics: {
      riskScore: vendorName.toString().includes('Vardhaman') ? 68 : 12,
      activeNodes: 12847,
      highRiskAlerts: 184,
      complianceShield: "92.4%",
      pendingReviews: 73
    }
  });
});

// Health check endpoint
app.get('/api/v1/health', (_req: Request, res: Response) => {
  res.json({ success: true, message: 'Service is healthy', timestamp: new Date().toISOString() });
});

// API routes
app.use('/api/v1', routes);

// 404 handler
app.use((_req, res) => {
  res.status(404).json({ success: false, error: 'Route not found' });
});

// Global error handler
app.use((err: any, _req: any, res: any, _next: any) => {
  console.error(err);
  res.status(500).json({ success: false, error: 'Internal server error' });
});

export default app;