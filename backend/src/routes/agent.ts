import { Router } from 'express';
import { validateBody } from '../utils/zod';
import { z } from 'zod';

const router = Router();

// Zod schema for agent creation
const agentSchema = z.object({
  name: z.string().min(1, 'Name is required'),
  status: z.enum(['IDLE', 'BUSY', 'OFFLINE']),
  vendorId: z.string().uuid('vendorId must be a valid UUID'),
});

// GET /agents - Return all agents
router.get('/', async (_req, res) => {
  try {
    // In this example we don't have an Agent model in Prisma yet.
    // Since the original code used in-memory agents, we can return a placeholder
    // or we can create a simple Agent model later. For now, return empty array.
    // TODO: Replace with actual Prisma query once Agent model is defined.
    res.json({ success: true, data: [] });
  } catch (error) {
    res.status(500).json({ success: false, error: 'Internal server error' });
  }
});

// POST /agents - Create a new agent
router.post('/', validateBody(agentSchema), async (req, res) => {
  try {
    const { name, status, vendorId } = req.body;
    // Placeholder: In a real app you would save to DB.
    // For now, just return the created agent.
    res.status(201).json({
      success: true,
      data: { name, status, vendorId, id: crypto.randomUUID() },
    });
  } catch (error) {
    res.status(500).json({ success: false, error: 'Internal server error' });
  }
});

export default router;