/**
 * OpenClaw Expert Bundle - Main Entry Point
 *
 * Bundles 4 integrated skills for complete OpenClaw expertise
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

/**
 * Initialize the bundle
 * Loads all 4 skills and sets up routing
 */
export async function initialize(config = {}) {
  const defaultConfig = {
    autoRoute: true,
    enableWebSearch: true,
    pseudocodeLanguages: ['python', 'typescript', 'go'],
    detailLevel: 'professional',
  };

  const finalConfig = { ...defaultConfig, ...config };

  // Load all skills from skills/ directory
  const skillsPath = path.join(__dirname, 'skills');
  const skills = {};

  const skillDirs = fs.readdirSync(skillsPath);

  for (const skillDir of skillDirs) {
    const skillPath = path.join(skillsPath, skillDir);
    const skillMdPath = path.join(skillPath, 'SKILL.md');

    if (fs.existsSync(skillMdPath)) {
      const content = fs.readFileSync(skillMdPath, 'utf-8');
      skills[skillDir] = {
        name: skillDir,
        content: content,
        path: skillPath,
      };
    }
  }

  return {
    // Bundle metadata
    metadata: {
      id: 'openclaw-expert-bundle',
      name: 'OpenClaw Expert Bundle',
      version: '1.0.0',
      description: 'Complete expertise system for OpenClaw',
      skills: Object.keys(skills),
    },

    // Configuration
    config: finalConfig,

    // Load skill by ID
    getSkill: (skillId) => skills[skillId] || null,

    // List all skills
    listSkills: () => Object.keys(skills),

    // Route query to appropriate skill
    routeQuery: (query) => {
      const lowerQuery = query.toLowerCase();

      // Keywords for routing
      const routes = {
        'openclaw-expert': [
          'agent loop', 'context', 'session', 'memory', 'compaction',
          'how does', 'explain', 'understand', 'concept', 'fundamentals',
          'architecture', 'flow', 'process'
        ],
        'openclaw-plugin-builder': [
          'plugin', 'build plugin', 'create plugin', 'integrate',
          'tool', 'hook', 'manifest', 'implementation', 'custom'
        ],
        'openclaw-agent-patterns': [
          'multi-agent', 'supervisor', 'pattern', 'delegate',
          'specialist', 'routing', 'orchestrat', 'design', 'topology'
        ],
        'openclaw-automation-troubleshooting': [
          'webhook', 'hook', 'cron', 'automat', 'debug', 'trouble',
          'not work', 'error', 'fail', 'log', 'monitor'
        ],
      };

      // Score each skill based on keyword matches
      const scores = {};
      for (const [skillId, keywords] of Object.entries(routes)) {
        scores[skillId] = keywords.filter(kw => lowerQuery.includes(kw)).length;
      }

      // Return skill with highest score
      const bestSkill = Object.entries(scores).sort((a, b) => b[1] - a[1])[0];
      return bestSkill[1] > 0 ? bestSkill[0] : 'openclaw-expert';
    },

    // Execute skill (returns skill content + config)
    executeSkill: (skillId, context = {}) => {
      const skill = skills[skillId];
      if (!skill) {
        return {
          error: `Skill not found: ${skillId}`,
          available: Object.keys(skills),
        };
      }

      return {
        skillId: skillId,
        skillName: skill.name,
        content: skill.content,
        config: finalConfig,
        context: context,
        timestamp: new Date().toISOString(),
      };
    },

    // Health check
    health: () => ({
      status: 'healthy',
      skillsLoaded: Object.keys(skills).length,
      skills: Object.keys(skills),
      config: finalConfig,
    }),
  };
}

/**
 * Export for direct usage
 */
export default {
  initialize,
  name: 'openclaw-expert-bundle',
  version: '1.0.0',
};
