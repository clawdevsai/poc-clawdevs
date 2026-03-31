# dev_mobile Implementation Skill

**Version:** 2.0.0
**Maturity:** Production
**Scope:** Mobile app architecture, platform selection, technology stack guidance, and scalable mobile patterns

## Overview

Mobile application architecture analysis and technology selection for iOS, Android, and cross-platform mobile development. The before_execution hook analyzes project requirements and recommends optimal mobile architecture patterns with complete technology stack guidance.

## Architectural Patterns

### 1. Native Development (Swift/Kotlin)
Best for: Premium apps, performance-critical features, full platform access
- Single platform focus (iOS or Android)
- Highest performance
- Full access to native features
- Cost: High | Scalability: Limited per platform

### 2. Cross-Platform (React Native/Flutter)
Best for: MVP, feature parity across platforms, quick launch
- Single codebase for iOS and Android
- Good performance for most use cases
- Large community and libraries
- Cost: Moderate | Scalability: Good

### 3. Progressive Web App (PWA)
Best for: Web-first mobile, offline functionality, no app store dependency
- Web-based, installable
- Zero app store friction
- Works across all devices
- Cost: Low | Scalability: Excellent

### 4. Hybrid (Ionic/Cordova)
Best for: Legacy systems, rapid prototyping
- Single codebase HTML/CSS/JS
- Easy to learn
- Limited native feature access
- Cost: Low-Moderate | Scalability: Limited

### 5. Backend-Driven (Mobile-optimized API)
Best for: Lightweight UI, server-centric architecture
- Minimal client logic
- Server controls experience
- Easier updates and monitoring
- Cost: Moderate | Scalability: Very Good

### 6. Full Native (SwiftUI/Jetpack Compose)
Best for: Modern apps, latest platform features
- Modern frameworks
- Cutting-edge performance
- Maximum platform integration
- Cost: High | Scalability: Good

## Design Principles

- **SOLID** - Clean, maintainable architecture
- **KISS** - Keep It Simple, Stupid
- **YAGNI** - Don't build unnecessary features
- **DRY** - Reusable code and patterns
- **Mobile-First** - Design for constrained environments
- **Offline-First** - Assume connectivity is unreliable
- **Performance** - Every byte and millisecond matters

## Core Requirements Dimensions

- **Platform** - iOS, Android, both, or web
- **Performance** - Frame rate targets, load time
- **Offline Capability** - Full offline, partial, or online-only
- **Device Support** - Latest only, broad support
- **Distribution** - App Store, Play Store, Web, Enterprise
- **Team Size** - Solo developer to large team

## Usage Examples

### MVP Mobile App
```typescript
// Quick to market, minimal resources
const result = await beforeExecutionHook({
  conversation: "MVP app in 4 weeks, one developer, need both iOS and Android"
});
// Recommendation: React Native or Flutter
```

### Enterprise Mobile Solution
```typescript
// Large team, complex requirements, long-term
const result = await beforeExecutionHook({
  conversation: "Mission-critical app, 10+ developers, premium experience required"
});
// Recommendation: Native (separate iOS + Android teams)
```

### Offline-First Application
```typescript
// Offline functionality critical
const result = await beforeExecutionHook({
  conversation: "App must work offline, users in areas with poor connectivity"
});
// Recommendation: PWA or Native with local storage
```

---

**Last Updated:** 2026-03-31
**Status:** Production Ready
