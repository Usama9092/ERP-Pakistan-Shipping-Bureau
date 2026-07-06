# DEVELOPER QUICK-START: Using This Spec with GitHub Copilot

**For**: Full-stack developers implementing GDP Dashboard  
**Using**: GitHub Copilot, Cursor, or Claude Dev  
**Time to First Implementation**: ~30 minutes

---

## WHAT YOU HAVE

You now have a **complete, copy-pasteable technical specification** for a maritime classification platform:

✅ **PostgreSQL database schema** (9 tables, fully typed)  
✅ **5 business logic rules** (with decision matrices)  
✅ **Authentication middleware** (JWT + audit logging)  
✅ **VisibilityManager service** (centralized access control)  
✅ **Production-ready Python code** (Flask-compatible)  

---

## HOW TO USE WITH COPILOT

### Step 1: Set Up Your Project Structure

```bash
# Create backend structure
mkdir -p backend/{models,services,routes,migrations}
touch backend/__init__.py
touch backend/config.py
touch backend/database.py
```

### Step 2: Copy the Database Schema

1. Open `/workspaces/gdp-dashboard/my-project/SYSTEM_ARCHITECTURE_SPEC.md`
2. Find the "## 2. DATABASE SCHEMA" section
3. Copy the entire SQL block
4. Create `backend/migrations/001_initial_schema.sql`
5. Paste the SQL there

**Or use with Alembic** (recommended for production):

```bash
# In your project root:
alembic init alembic
```

Then tell Copilot:

```
I have the PostgreSQL schema from SYSTEM_ARCHITECTURE_SPEC.md.
Create an Alembic migration that:
1. Creates all 9 tables (users, vessels, documents, certificates, etc.)
2. Adds proper indexes on foreign keys and common query columns
3. Sets up Row-Level Security (RLS) policies for multi-tenancy

Reference the schema in /workspaces/gdp-dashboard/my-project/SYSTEM_ARCHITECTURE_SPEC.md Part 2.
```

### Step 3: Copy the Authentication Service

1. Copy **entire** `AUTH_VISIBILITY_SERVICE.py` file to your project
2. Save as `backend/services/auth_and_visibility.py`
3. Update imports based on your models

**Copilot prompt**:

```
I've copied the authentication and visibility service from AUTH_VISIBILITY_SERVICE.py.
Now create the following Flask routes that use these decorators and classes:

1. POST /auth/login
   - Takes email + password
   - Returns access_token + refresh_token

2. POST /auth/refresh
   - Takes refresh_token
   - Returns new access_token

3. GET /auth/me
   - Returns current user info (using @require_auth)

Reference: SYSTEM_ARCHITECTURE_SPEC.md Section 4
```

### Step 4: Build Your API Endpoints

**For each route, use this template**:

```python
# Copilot prompt template:
"""
Based on SYSTEM_ARCHITECTURE_SPEC.md Section 3 (Business Logic),
write a Flask route that:

1. Name: GET /api/vessels/{vessel_id}/documents
2. Auth: @require_auth decorator
3. Access Control: Use VisibilityManager.get_document_visibility()
4. Response:
   - If ALLOWED: Return list of documents with presigned S3 URLs
   - If PENDING_APPROVAL: Return { status: 'pending', request_id: X }
   - If DENIED: Return 403 Forbidden

5. Audit: Log all access attempts via @audit_middleware

See Rule 2 and Rule 4 in Section 3 for decision logic.
"""
```

---

## QUICK REFERENCE: WHICH FILE IMPLEMENTS WHAT?

| Feature | File | Section |
|---------|------|---------|
| **Database schema** | SYSTEM_ARCHITECTURE_SPEC.md | Part 2 |
| **Business rules** | SYSTEM_ARCHITECTURE_SPEC.md | Part 3 |
| **Auth middleware** | AUTH_VISIBILITY_SERVICE.py | PART 1 |
| **Access control** | AUTH_VISIBILITY_SERVICE.py | PART 2 |
| **JWT tokens** | AUTH_VISIBILITY_SERVICE.py | AuthenticationService class |
| **Rule 1 (Standing Docs)** | AUTH_VISIBILITY_SERVICE.py | `can_view_standing_doc()` |
| **Rule 2 (Lifecycle)** | AUTH_VISIBILITY_SERVICE.py | `can_view_newbuilding_doc()` |
| **Rule 3 (Overdue Auto)** | AUTH_VISIBILITY_SERVICE.py | `can_view_certificate_respecting_overdue()` |
| **Rule 4 (Consent Gateway)** | AUTH_VISIBILITY_SERVICE.py | `can_view_consent_gated_document()` |
| **Rule 5 (SCF/Tanker)** | AUTH_VISIBILITY_SERVICE.py | `can_view_scf()` |

---

## TYPICAL IMPLEMENTATION WORKFLOW

### Week 1: Database & Auth

```
Monday:
- Ask Copilot to create Alembic migrations from schema
- Run migrations locally

Tuesday-Wednesday:
- Ask Copilot to implement POST /auth/login
- Ask Copilot to implement POST /auth/refresh
- Test with curl/Postman

Thursday-Friday:
- Ask Copilot to add @require_auth to test routes
- Verify JWT token validation works
- Test audit_middleware logging
```

### Week 2: Access Control

```
Monday-Tuesday:
- Ask Copilot to implement VisibilityManager in your codebase
- Copy Rule 1-5 logic implementations

Wednesday:
- Ask Copilot to create GET /api/documents/{doc_id}
- Reference SYSTEM_ARCHITECTURE_SPEC.md Section 3 for all 5 rules
- Implement visibility check + response routing

Thursday-Friday:
- Add access request workflow endpoints
- Test all 5 rules with different user roles
- Verify audit logging
```

### Week 3-4: Frontend & Testing

```
- Build Streamlit dashboards using API endpoints
- Write unit tests for VisibilityManager (target >85% coverage)
- Load testing for multi-tenant scenarios
- Security testing for rule enforcement
```

---

## EXACT COPILOT PROMPTS TO USE

### Prompt 1: Create Database Models

```
I have a PostgreSQL schema in /workspaces/gdp-dashboard/my-project/
SYSTEM_ARCHITECTURE_SPEC.md (Part 2).

Create SQLAlchemy ORM models for:
- users (user_id, email, username, role, organization_id)
- vessels (vessel_id, imo_number, name, vessel_type, is_delivered, owner_id, flag_state_id)
- documents (doc_id, vessel_id, title, category, subcategory, file_path_s3)
- certificates (cert_id, vessel_id, title, is_overdue, status)
- access_requests (request_id, vessel_id, requester_id, status)
- audit_logs (log_id, user_id, action_type, entity_type, status)
- agreements (agreement_id, vessel_id, agreement_type, is_active)

File location: backend/models.py

Include:
- Relationship definitions (foreign keys)
- Enum types for roles, statuses, categories
- Index hints as comments
- Timestamps (created_at, updated_at)
```

### Prompt 2: Create Document Access Route

```
Using the VisibilityManager from AUTH_VISIBILITY_SERVICE.py,
write a Flask route that implements document access control:

Route: GET /api/documents/{doc_id}
Decorators: @require_auth, @audit_middleware

Logic (from SYSTEM_ARCHITECTURE_SPEC.md Section 3):
1. Load document from database
2. Call visibility_mgr.get_document_visibility()
3. If ALLOWED:
   - Generate presigned S3 URL (15 min expiry)
   - Return { url, filename, size, category }
4. If PENDING_APPROVAL:
   - Create access request if needed
   - Return { status: 'pending', request_id, created_at }
5. If DENIED or REQUIRES_AGREEMENT:
   - Return 403 with reason

Response logging: Every access attempt via AuditLog
```

### Prompt 3: Create Certificate Status Check Task

```
Create a Celery task that runs daily at 00:00 UTC:

Task name: daily_certificate_status_check

Logic (Rule 3 from SYSTEM_ARCHITECTURE_SPEC.md):
1. Query all certificates
2. For each certificate:
   - If current_date > expiry_date: status = 'Expired'
   - If current_date > due_date: status = 'Overdue'
   - Else: status = 'Current'
3. Log changes to AuditLog table
4. Send notifications to Flag State for overdue certs

File: backend/tasks/certificates.py
```

### Prompt 4: Create Access Request Approval Route

```
Write a Flask route for ship owners to approve data access requests:

Route: POST /api/access-requests/{request_id}/approve
Method: Owner-only (check vessel.owner_id == g.user_id)

Logic:
1. Load AccessRequest from database
2. Validate owner authorization
3. Update: request.status = 'Approved', approval_date = today()
4. Log to AuditLog
5. Send notification to requester
6. Return { status: 'approved', request_id, granted_until }

See Rule 4 (Consent Gateway) in SYSTEM_ARCHITECTURE_SPEC.md Section 3.
```

---

## TESTING CHECKLIST

Create unit tests to verify each rule:

```python
# test_visibility_manager.py

def test_rule_1_standing_docs_visible_to_all():
    """All authenticated users can see standing docs"""
    visibility_mgr = VisibilityManager(db.session)
    assert visibility_mgr.can_view_standing_doc(user_id=1, user_role='Any') == True

def test_rule_2_newbuilding_lifecycle():
    """Shipyard loses access after delivery"""
    # Test BEFORE delivery: shipyard has access
    # Test AFTER delivery: shipyard denied
    
def test_rule_3_overdue_automation():
    """Overdue certs auto-visible to flag state"""
    # Set certificate.is_overdue = True
    # Verify Flag State gets VisibilityStatus.ALLOWED
    
def test_rule_4_insurance_approval_workflow():
    """Insurance needs owner approval"""
    # No agreement: REQUIRES_AGREEMENT
    # Agreement exists, no approval: PENDING_APPROVAL
    # Approved: ALLOWED
    
def test_rule_5_scf_tanker_only():
    """SCF only for Tankers/Bulk Carriers"""
    # Tanker: accessible
    # Container ship: denied
    # Flag state: requires_agreement (workflow)
```

---

## ENVIRONMENT VARIABLES TO SET

```bash
# .env file for your Flask app

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-key-change-in-production
TOKEN_EXPIRY_MINUTES=60
REFRESH_TOKEN_EXPIRY_DAYS=7

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/gdp_dashboard
SQLALCHEMY_TRACK_MODIFICATIONS=False

# AWS S3 (for document storage)
AWS_S3_BUCKET=gdp-dashboard-documents
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_REGION=us-east-1

# Celery (for background jobs)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/gdp_dashboard.log
```

---

## COPILOT SYSTEM PROMPT (SAVE THIS)

Save this as `.copilot-prompt.md` in your project root:

```markdown
# GDP Dashboard - GitHub Copilot System Prompt

You are implementing a maritime classification platform for Pakistan Shipping Bureau.

## Key Files
- **SYSTEM_ARCHITECTURE_SPEC.md**: Complete DB schema, 5 business rules, architecture
- **AUTH_VISIBILITY_SERVICE.py**: Authentication + access control implementation
- **PLAN.md**: 24-week implementation roadmap

## The 5 Access Control Rules

1. **Standing Docs**: Public to all authenticated users
2. **Lifecycle**: Access changes at vessel delivery
3. **Overdue Auto**: Overdue certs visible to flag state
4. **Consent Gateway**: Insurance requests require owner approval
5. **SCF/Tanker**: Special rules for goal-based ship construction files

## Reference Pattern
Always reference the specific rule when asked to implement access control:
- "Rule 2 from SYSTEM_ARCHITECTURE_SPEC.md Section 3"
- Check can_view_newbuilding_doc() in AUTH_VISIBILITY_SERVICE.py

## Database
PostgreSQL with Row-Level Security (RLS) for multi-tenancy.
All access decisions logged to audit_logs table.
```

---

## DEPLOYMENT CHECKLIST

Before going to production:

- [ ] Database migrations run successfully
- [ ] All 6 user roles tested with each rule
- [ ] Audit logging captures all access attempts
- [ ] JWT token expiry working correctly
- [ ] Overdue certificate automation runs daily
- [ ] S3 presigned URLs expire after 15 min
- [ ] 85%+ unit test coverage
- [ ] Security audit: penetration testing passed
- [ ] Performance: <2 sec page load, 99.9% uptime SLA
- [ ] IACS compliance: All 50+ requirements mapped to system

---

## WHAT COPILOT DOES BEST WITH THIS SPEC

✅ **Boilerplate code**: Auth middleware, service classes, decorators  
✅ **Database scaffolding**: ORM models, migrations, indexes  
✅ **API endpoints**: Consistent routing patterns, error handling  
✅ **Testing**: Unit test templates matching rule implementations  
✅ **Documentation**: Docstrings, type hints, inline comments  

❌ **Not ideal for**: Architectural decisions (already made!), business logic (already detailed)

---

## FINAL WORKFLOW: 3-STEP PROCESS

### Step 1: Copy & Paste
- Copy SYSTEM_ARCHITECTURE_SPEC.md database schema
- Copy AUTH_VISIBILITY_SERVICE.py authentication code
- Add to your project

### Step 2: Tell Copilot What to Build
```
"Create Flask route GET /api/documents/{doc_id}
that uses VisibilityManager.get_document_visibility()
per Rule 2 and Rule 4 from SYSTEM_ARCHITECTURE_SPEC.md Section 3"
```

### Step 3: Integrate & Test
- Connect to your database
- Run unit tests for each rule
- Deploy to Render

---

**Status**: ✅ **READY FOR COPILOT**

Copy these files into your workspace and start building!

---

## QUICK LINKS TO FILES

| File | Purpose |
|------|---------|
| [SYSTEM_ARCHITECTURE_SPEC.md](SYSTEM_ARCHITECTURE_SPEC.md) | Database + Rules (copy schema) |
| [AUTH_VISIBILITY_SERVICE.py](AUTH_VISIBILITY_SERVICE.py) | Auth + Access Control (copy code) |
| [SPECIFICATION.md](SPECIFICATION.md) | Overall system design |
| [PLAN.md](PLAN.md) | 24-week implementation timeline |
| [IACS_COMPLIANCE_REFERENCE.md](IACS_COMPLIANCE_REFERENCE.md) | Compliance requirements |

---

**Happy building!** 🚀

Use these materials with GitHub Copilot to implement a production-grade maritime platform.

---

**Questions?**
- For database: See SYSTEM_ARCHITECTURE_SPEC.md Part 2
- For auth: See AUTH_VISIBILITY_SERVICE.py Part 1
- For rules: See SYSTEM_ARCHITECTURE_SPEC.md Part 3 + AUTH_VISIBILITY_SERVICE.py Part 2
- For timeline: See PLAN.md
