import { Requirements } from "../schemas/requirements";
export function parseRequirements(input: any): { parsed: Requirements; sources: string[]; confidence: number } {
  return { parsed: {}, sources: Object.keys(input).filter(k => input[k]), confidence: 0.75 };
}
