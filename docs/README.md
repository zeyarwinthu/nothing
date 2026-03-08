# Duolingo-Style Learning Platform — Backend Documentation

## Table of Contents

### 1. [API Specification](./01-api-specification.md)
- 1.1 Overview & Versioning Strategy
- 1.2 Authentication & Authorization
- 1.3 User Management Endpoints
- 1.4 Course & Language Endpoints
- 1.5 Lesson & Exercise Endpoints
- 1.6 Progress & XP Endpoints
- 1.7 Streak Endpoints
- 1.8 Leaderboard Endpoints
- 1.9 Shop & In-App Purchase Endpoints
- 1.10 Notification Endpoints
- 1.11 Achievement & Badge Endpoints
- 1.12 Friend & Social Endpoints
- 1.13 Settings & Preferences Endpoints
- 1.14 Admin Endpoints
- 1.15 Error Codes & Error Response Schema
- 1.16 Rate Limiting Headers
- 1.17 Pagination Convention
- 1.18 Example Payloads

### 2. [Backend Technical Specification](./02-backend-technical-specification.md)
- 2.1 System Overview
- 2.2 Technology Stack
- 2.3 Backend Modules & Microservices
- 2.4 Data Flow Diagrams
- 2.5 Background Jobs
- 2.6 Notification System
- 2.7 Caching Strategy
- 2.8 Rate Limiting
- 2.9 Logging & Monitoring
- 2.10 Health Checks

### 3. [System Design Document](./03-system-design-document.md)
- 3.1 High-Level Architecture
- 3.2 Sequence Diagrams
- 3.3 Component Responsibilities
- 3.4 Scaling Strategy
- 3.5 Load Handling
- 3.6 Queueing System
- 3.7 CDN Usage
- 3.8 Deployment Architecture
- 3.9 Disaster Recovery

### 4. [Functional Specification Document](./04-functional-specification-document.md)
- 4.1 Features & User Flows
- 4.2 Business Rules
- 4.3 Acceptance Criteria
- 4.4 Edge Cases
- 4.5 User Stories

### 5. [Entity & Database Schema Documentation](./05-database-schema-documentation.md)
- 5.1 Entity-Relationship Diagram
- 5.2 Table Definitions & Field Descriptions
- 5.3 Relationships
- 5.4 Indexing Strategy
- 5.5 Data Retention Rules
- 5.6 Migration Strategy

### 6. [Business Logic Documentation](./06-business-logic-documentation.md)
- 6.1 Lesson Progression Logic
- 6.2 XP System
- 6.3 Streak Logic
- 6.4 Leaderboards
- 6.5 Skill Tree Logic
- 6.6 Gamification Rules
- 6.7 Reward System
- 6.8 Leveling System
- 6.9 Hearts / Lives System
- 6.10 Monetization Logic

### 7. [Additional Documents](./07-additional-documents.md)
- 7.1 Background Job Documentation
- 7.2 Notification & Email Flow
- 7.3 Security Considerations
- 7.4 API Rate Limits
- 7.5 Localization Strategy
- 7.6 A/B Testing Framework
- 7.7 Feature Flag System
- 7.8 Data Privacy & GDPR Compliance

---

## Technology Stack Summary

| Layer           | Technology       |
|-----------------|------------------|
| Backend         | ASP.NET Core 8   |
| Database        | MySQL 8.0        |
| Cache           | Redis 7          |
| Message Queue   | RabbitMQ 3.12    |
| Authentication  | JWT (RS256)      |
| API Gateway     | YARP / Ocelot    |
| Containerization| Docker + K8s     |
| CI/CD           | GitHub Actions   |
| Monitoring      | Prometheus + Grafana |
| Logging         | Serilog + ELK    |
| CDN             | CloudFront / Cloudflare |

---

## Document Conventions

- All API examples use JSON
- All timestamps are ISO 8601 in UTC
- All IDs are UUIDs unless otherwise noted
- Diagrams are text-based (ASCII / Mermaid notation)
- Status codes follow RFC 7231
- Field names use `camelCase` in JSON, `snake_case` in database schemas
