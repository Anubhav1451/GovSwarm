import { Router } from 'express';
import { prisma } from '../prisma/client';

const router = Router();

// GET /metrics - Return aggregated metrics
router.get('/', async (_req, res) => {
  try {
    // Placeholder metrics - replace with actual Prisma queries once models are defined
    const metrics = {
      totalOrganizations: 0,
      totalAgents: 0,
      highRiskAlerts: 0,
      busyAgents: 0,
      queuedTasksCount: 0,
    };

    // Example: try to get counts from Prisma if tables exist
    try {
      // const [orgCount, agentCount] = await Promise.all([
      //   prisma.organization.count(),
      //   prisma.agent.count(),
      // ]);
      // metrics.totalOrganizations = orgCount;
      // metrics.totalAgents = agentCount;
    } catch (e) {
      // Tables may not exist yet; keep placeholders
    }

    res.json({ success: true, data: metrics });
  } catch (error) {
    res.status(500).json({ success: false, error: 'Internal server error' });
  }
});

export default router;