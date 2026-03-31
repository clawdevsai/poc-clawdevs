import { z } from "zod";
export const requirementsSchema = z.object({
  scale: z.enum(["small", "medium", "large", "xlarge"]).optional(),
  priority: z.enum(["critical", "high", "medium", "low"]).optional(),
});
export type Requirements = z.infer<typeof requirementsSchema>;
