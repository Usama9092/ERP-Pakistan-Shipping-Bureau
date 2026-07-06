# GDP Dashboard - Specification

## 1. System Architecture Overview

### Core Components
- **Frontend**: Streamlit-based role-based dashboards
- **Backend**: Python application with business logic
- **Database**: PostgreSQL (via Supabase) with Row-Level Security
- **Storage**: Supabase file storage with SQLite fallback
- **Deployment**: Render cloud platform with GitHub integration

### Technology Stack
- **Framework**: Streamlit
- **Database**: PostgreSQL / Supabase
- **Authentication**: Role-based access control (RBAC)
- **File Storage**: Supabase Storage + SQLite
- **Deployment**: Render
- **Version Control**: Git/GitHub

## 2. Functional Modules

### 2.1 User Management & RBAC
**Modules**:
- Admin Control Center
- Role-based Dashboard Access
- Technical Authority Structure
- User provisioning and lifecycle management

**Key Features**:
- Multiple role types (Admin, Trainer, Tutor, Trainee, Authority, Auditor)
- Permission-based feature access
- Audit logging for all user actions

### 2.2 Competency Management
**Modules**:
- Competency Levels Framework
- Scope-specific Authorization Matrix
- Competency Review Board (CRB) workflow
- Revalidation/Reauthorization workflow

**Key Features**:
- Define competency levels (1-5 scale or custom)
- Track competency progression
- Automated revalidation scheduling
- Integration with IACS classification standards

### 2.3 Training & Development
**Modules**:
- Theoretical Training Matrix
- Trainer Course Creation
- Development Plans for Trainees/Probationers
- MCQ Generation from Content
- Digital Approval/Signature Flow
- QR Authorization Certificates

**Key Features**:
- Course creation and management
- Automatic MCQ generation from uploaded content
- Development plan tracking
- Digital certificate generation
- QR code based authorization

### 2.4 Assessment & Evaluation
**Modules**:
- Witness Survey Assessment
- Supervised Survey Assessment
- Plan Appraisal (Joint/Independent Review)
- Competency Review Board evaluations

**Key Features**:
- Structured assessment templates
- Multi-level approval workflows
- Assessment history and tracking
- Evidence collection and storage

### 2.5 Field Operations
**Modules**:
- Field Exposure Matrix
- Risk-based Job Assignment Engine
- Witness Survey Management
- Supervised Survey Management

**Key Features**:
- Exposure tracking across different maritime sectors
- Risk assessment for job assignments
- Survey coordination and scheduling
- Evidence documentation

### 2.6 Knowledge & Information Management
**Modules**:
- Technical Knowledge Library
- File Upload System (PDF/PPT/DOC/TXT/Video/Evidence)
- Information Classification per IACS standards
- QMS/CAPA/Audit Trail system

**Key Features**:
- Centralized knowledge repository
- Full-text search capabilities
- Document version control
- Access control per IACS guidelines
- Audit trail for all document access

### 2.7 Monitoring & Analytics
**Modules**:
- KPI Dashboard
- Utilization Tracking
- CPD/Seminar/Refresher Records
- System Health Monitoring

**Key Features**:
- Real-time KPI visualization
- Personnel utilization metrics
- Professional development tracking
- Performance analytics

### 2.8 Data Management
**Modules**:
- Backup/Export System
- Database Management
- SQLite Local Fallback
- Supabase Integration

**Key Features**:
- Automated daily backups
- Export to multiple formats
- Local/cloud synchronization
- Data integrity verification

## 3. Database Schema Highlights

### Key Tables
- `users` - User accounts with roles
- `roles` - Role definitions and permissions
- `competencies` - Competency framework
- `training_courses` - Course management
- `assessments` - Assessment records
- `certificates` - Digital certificates
- `audit_logs` - Complete audit trail
- `documents` - Knowledge library
- `authorizations` - IACS-compliant authorization matrix

### Security
- Row-Level Security (RLS) policies
- Role-based access control at database level
- Encrypted sensitive fields
- Audit triggers on all modifications

## 4. Compliance Requirements

### IACS/SOLAS Standards
- Support for both standard ships and goal-based construction standards
- Information transparency matrix (Table 1 & 2 from IACS Proc Req. 2009/Rev.2)
- Automatic information release based on receiver type (Owner, Flag State, Port State, etc.)
- SCF (Ship Construction File) management
- Formal approval letters and certificate tracking

### Data Classification
- Automatic availability levels (1-8 per IACS standards)
- Role-based information release
- Conditional availability based on agreements
- Audit logging for all information access

## 5. Deployment & DevOps

### Production Environment
- Render deployment platform
- PostgreSQL/Supabase backend
- GitHub Actions CI/CD
- Environment-based configuration

### Local Development
- SQLite for local testing
- Docker support for containerization
- Development environment parity
- Comprehensive logging

## 6. Non-Functional Requirements

### Performance
- API response time < 200ms (p95)
- Page load time < 2 seconds (p95)
- Support for 10,000+ concurrent users
- Database query optimization

### Reliability
- 99.9% system uptime
- Automated failover mechanisms
- Data backup every 6 hours
- Disaster recovery procedures

### Security
- All communications over HTTPS/TLS
- Regular security audits
- Penetration testing quarterly
- Compliance with maritime cybersecurity standards

### Scalability
- Horizontal scaling for compute layer
- Database connection pooling
- File storage scaling with Supabase
- Load balancing across instances

## 7. Integration Points

### External Systems
- IACS classification databases
- Maritime authority platforms
- Email/notification systems
- Document management systems

### APIs
- RESTful API for programmatic access
- WebSocket support for real-time updates
- GraphQL optional layer
- Webhook support for events

