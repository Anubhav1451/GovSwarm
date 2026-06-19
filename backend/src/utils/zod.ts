import { type ZodType, ZodError } from 'zod';

export const validateBody = <T extends ZodType>(schema: T) => {
  return (req: any, res: any, next: any) => {
    try {
      req.body = schema.parse(req.body);
      next();
    } catch (e: any) {
      if (e instanceof ZodError) {
        return res.status(400).json({ errors: e.format() });
      }
      next(e);
    }
  };
};