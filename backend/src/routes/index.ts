import { Router } from 'express';
import agentRouter from './agent';
import metricsRouter from './metrics';
import logsRouter from './logs';

const router = Router();

// Mount feature routers
router.use('/agents', agentRouter);
router.use('/metrics', metricsRouter);
router.use('/logs', logsRouter);

export default router;