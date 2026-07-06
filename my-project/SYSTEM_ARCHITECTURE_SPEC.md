# GDP DASHBOARD - TECHNICAL SYSTEM ARCHITECTURE
## AI Copilot Implementation Specification

**Date**: 2026-06-25  
**Version**: 1.0  
**Status**: ✅ Ready for Implementation  
**Target Audience**: Full-Stack Development Team, GitHub Copilot  

---

## TABLE OF CONTENTS

1. [Core Architecture](#1-core-architecture-requirements)
2. [Database Schema](#2-database-schema)
3. [Business Logic & Rule Engine](#3-core-business-logic--rule-engine)
4. [Authentication & Authorization](#4-authentication--authorization)
5. [VisibilityManager Service](#5-visibilitymanager-service)
6. [Implementation Roadmap](#6-implementation-roadmap)

---

## 1. CORE ARCHITECTURE REQUIREMENTS

### 1.1 Multi-Tenancy

The platform securely separates data by organizational context:
- **Ship Owners**: See only ships they own
- **Flag States**: See only ships under their flag
- **Port States**: See only ships in their ports
- **Insurance Companies**: See only ships with active policies
- **Shipyards**: See only ships under construction/repair
- **Admin**: See all (with audit logging)

### 1.2 Role-Based Access Control (RBAC)

**6 Distinct Roles:**

| Role | Internal | External | Capabilities |
|------|----------|----------|---|
| **Admin** | Yes | No | Full system access, audit trails, configuration |
| **Owner_Master** | No | Yes | View own ships, approve data access, manage operations |
| **Flag_State** | No | Yes | Regulatory oversight, compliance monitoring, enforcement |
| **Port_State** | No | Yes | Port authority oversight, safety compliance |
| **Insurance_Company** | No | Yes | P&I & Hull underwriter access, conditional data |
| **Shipyard** | No | Yes | Construction/repair vessel access, limited newbuilding data |

### 1.3 Conditional Visibility Engine

Access dynamically changes based on:
- **Vessel Lifecycle State** (Newbuilding → Delivered → In Operation)
- **Certificate Status** (Current, Due, Overdue, Expired)
- **Explicit Owner Consent** (Access request workflows)
- **Physical On-Board Verification** (Port state inspections)
- **Agreement/Contract Status** (Insurance, Flag, Port agreements)
- **Vessel Classification** (Standard vs. Goal-Based/Tanker/Bulk Carrier)

### 1.4 Automated Background Jobs

**Cron-based Services:**
- Daily certificate status recalculation
- Overdue flag automation
- Expiry notifications (30/14/7 days)
- Access request timeout cleanup
- Audit log archival

---

## 2. DATABASE SCHEMA

### 2.1 Complete PostgreSQL Implementation

```sql
-- ============================================
-- PART 1: USERS & AUTHENTICATION
-- ============================================

CREATE TYPE user_role AS ENUM (
    'Admin',
    'Owner_Master',
    'Flag_State',
    'Port_State',
    'Insurance_Company',
    'Shipyard'
);

CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role user_role NOT NULL,
    organization_name VARCHAR(255) NOT NULL,
    organization_id INT,
    country_code VARCHAR(2),
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_organization ON users(organization_id);

-- ============================================
-- PART 2: VESSELS & SHIP INFORMATION
-- ============================================

CREATE TYPE vessel_type AS ENUM (
    'Tanker',
    'Bulk_Carrier',
    'General_Cargo',
    'Container',
    'Passenger',
    'RoRo',
    'Multipurpose',
    'Other'
);

CREATE TYPE vessel_status AS ENUM (
    'Newbuilding',
    'In_Operation',
    'Laid_Up',
    'Scrapped',
    'Transfer_In_Progress'
);

CREATE TABLE vessels (
    vessel_id SERIAL PRIMARY KEY,
    imo_number VARCHAR(7) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    vessel_type vessel_type NOT NULL,
    status vessel_status DEFAULT 'Newbuilding',
    is_delivered BOOLEAN DEFAULT FALSE,
    delivery_date DATE,
    owner_id INT REFERENCES users(user_id),
    flag_state_id INT REFERENCES users(user_id),
    shipyard_id INT REFERENCES users(user_id),
    hull_number VARCHAR(50),
    build_year INT,
    dwt NUMERIC(10, 2),
    grt NUMERIC(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_vessels_owner ON vessels(owner_id);
CREATE INDEX idx_vessels_flag ON vessels(flag_state_id);
CREATE INDEX idx_vessels_status ON vessels(status);
CREATE INDEX idx_vessels_imo ON vessels(imo_number);

-- ============================================
-- PART 3: DOCUMENT MANAGEMENT SYSTEM (DMS)
-- ============================================

CREATE TYPE doc_category AS ENUM (
    'Standing_Doc',
    'Newbuilding',
    'Class_Operation',
    'Statutory_Operation',
    'Miscellaneous',
    'SCF',
    'Correspondence',
    'Audit_Report'
);

CREATE TABLE documents (
    doc_id SERIAL PRIMARY KEY,
    vessel_id INT REFERENCES vessels(vessel_id),
    title VARCHAR(255) NOT NULL,
    category doc_category NOT NULL,
    subcategory VARCHAR(100) NOT NULL,
    description TEXT,
    file_path_s3 VARCHAR(512) NOT NULL,
    file_size_bytes INT,
    mime_type VARCHAR(50),
    uploaded_by INT REFERENCES users(user_id) NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_confidential BOOLEAN DEFAULT FALSE,
    version_number INT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_documents_vessel ON documents(vessel_id);
CREATE INDEX idx_documents_category ON documents(category);
CREATE INDEX idx_documents_uploaded_at ON documents(uploaded_at);

-- ============================================
-- PART 4: CERTIFICATES & SURVEYS (LIVE TRACKING)
-- ============================================

CREATE TYPE service_type AS ENUM ('Class', 'Statutory');

CREATE TYPE cert_status AS ENUM (
    'Current',
    'Due',
    'Overdue',
    'Expired',
    'Pending',
    'Cancelled'
);

CREATE TABLE certificates (
    cert_id SERIAL PRIMARY KEY,
    vessel_id INT REFERENCES vessels(vessel_id) NOT NULL,
    service_type service_type NOT NULL,
    title VARCHAR(255) NOT NULL,
    certificate_number VARCHAR(100),
    issued_date DATE,
    due_date DATE,
    expiry_date DATE,
    status cert_status DEFAULT 'Current',
    is_overdue BOOLEAN DEFAULT FALSE,
    is_expired BOOLEAN DEFAULT FALSE,
    survey_date DATE,
    surveyor_id INT REFERENCES users(user_id),
    conditions_of_class TEXT,
    document_reference INT REFERENCES documents(doc_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_certificates_vessel ON certificates(vessel_id);
CREATE INDEX idx_certificates_status ON certificates(status);
CREATE INDEX idx_certificates_expiry ON certificates(expiry_date);

-- ============================================
-- PART 5: ACCESS CONTROL & CONSENT WORKFLOWS
-- ============================================

CREATE TYPE request_status AS ENUM (
    'Pending',
    'Approved',
    'Denied',
    'Expired',
    'Cancelled'
);

CREATE TABLE access_requests (
    request_id SERIAL PRIMARY KEY,
    vessel_id INT REFERENCES vessels(vessel_id) NOT NULL,
    doc_id INT REFERENCES documents(doc_id),
    requester_id INT REFERENCES users(user_id) NOT NULL,
    owner_id INT REFERENCES users(user_id) NOT NULL,
    request_reason VARCHAR(500),
    status request_status DEFAULT 'Pending',
    approval_date DATE,
    expiry_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_access_requests_vessel ON access_requests(vessel_id);
CREATE INDEX idx_access_requests_status ON access_requests(status);
CREATE INDEX idx_access_requests_requester ON access_requests(requester_id);

-- ============================================
-- PART 6: AUDIT & COMPLIANCE LOGGING
-- ============================================

CREATE TYPE action_type AS ENUM (
    'View',
    'Download',
    'Upload',
    'Modify',
    'Delete',
    'Request_Access',
    'Approve_Access',
    'Deny_Access',
    'Login',
    'Logout'
);

CREATE TABLE audit_logs (
    log_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id),
    action_type action_type NOT NULL,
    entity_type VARCHAR(50),
    entity_id INT,
    vessel_id INT REFERENCES vessels(vessel_id),
    ip_address VARCHAR(45),
    user_agent TEXT,
    status VARCHAR(20),
    details JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_vessel ON audit_logs(vessel_id);
CREATE INDEX idx_audit_logs_created ON audit_logs(created_at);
CREATE INDEX idx_audit_logs_action ON audit_logs(action_type);

-- ============================================
-- PART 7: SCF (SHIP CONSTRUCTION FILE)
-- ============================================

CREATE TABLE scf_documents (
    scf_id SERIAL PRIMARY KEY,
    vessel_id INT REFERENCES vessels(vessel_id) NOT NULL,
    file_path_s3 VARCHAR(512) NOT NULL,
    uploaded_by INT REFERENCES users(user_id),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_approved BOOLEAN DEFAULT FALSE,
    approval_date DATE,
    approved_by INT REFERENCES users(user_id),
    version_number INT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_scf_vessel ON scf_documents(vessel_id);

-- ============================================
-- PART 8: VESSEL RELATIONSHIPS & AGREEMENTS
-- ============================================

CREATE TYPE agreement_type AS ENUM (
    'Insurance_PI',
    'Insurance_Hull',
    'Port_Authority',
    'Flag_State',
    'Shipyard_Contract'
);

CREATE TABLE agreements (
    agreement_id SERIAL PRIMARY KEY,
    vessel_id INT REFERENCES vessels(vessel_id) NOT NULL,
    agreement_type agreement_type NOT NULL,
    related_organization_id INT REFERENCES users(user_id),
    start_date DATE,
    end_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_agreements_vessel ON agreements(vessel_id);
CREATE INDEX idx_agreements_active ON agreements(is_active);

-- ============================================
-- PART 9: SESSION & TOKEN MANAGEMENT
-- ============================================

CREATE TABLE sessions (
    session_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id) NOT NULL,
    token_hash VARCHAR(255) UNIQUE NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sessions_user ON sessions(user_id);
CREATE INDEX idx_sessions_expires ON sessions(expires_at);
```

### 2.2 Schema Design Principles

✅ **Multi-tenancy**: `organization_id`, `owner_id`, `flag_state_id` fields enable data partitioning  
✅ **Audit Trail**: `audit_logs` table captures every action with immutable timestamps  
✅ **Temporal Data**: All tables have `created_at`, `updated_at` for compliance tracking  
✅ **Relationships**: Foreign keys ensure referential integrity  
✅ **Performance**: Strategic indexes on common query paths  

---

## 3. CORE BUSINESS LOGIC & RULE ENGINE

### 3.1 The Five Access Control Rules

#### **Rule 1: Standing Documentation (Public Library)**

**What**: Rules, Guidelines, Instructions, Quality Manual, Register Book  
**Who Can Access**: All authenticated users  
**Implementation**:

```python
# VisibilityManager.can_view_standing_doc()
def can_view_standing_doc(user_role: str) -> bool:
    """Standing docs are visible to all authenticated roles."""
    return True  # No restriction after authentication

# Database check
SELECT * FROM documents 
WHERE category = 'Standing_Doc' 
AND doc_id = ? 
-- No vessel_id filter needed
```

**Action Log**: Record view/download to `audit_logs` with `is_standing_doc = true`

---

#### **Rule 2: Lifecycle Switch (Newbuilding → In Operation)**

**What**: Approved Drawings, Approval Letters, Equipment Certificates  
**Logic**:

```python
def can_view_newbuilding_doc(user: User, vessel: Vessel) -> bool:
    """
    Newbuilding docs (is_delivered=FALSE):
      - Only Owner + Shipyard can view
    In Operation docs (is_delivered=TRUE):
      - Shipyard loses access
      - Owner + Flag_State always visible
      - Others need explicit approval
    """
    if not vessel.is_delivered:
        # NEWBUILDING PHASE
        return user.role in ['Admin', 'Owner_Master', 'Shipyard'] and \
               (user == vessel.owner or user == vessel.shipyard)
    else:
        # IN OPERATION PHASE
        if user.role in ['Admin', 'Owner_Master']:
            return True
        if user.role == 'Flag_State':
            return user == vessel.flag_state
        # For others: check access_requests
        return check_access_request(user, vessel)
```

**Trigger**: On `vessel.delivery_date`, flip `is_delivered = true` and audit this state change

---

#### **Rule 3: The "Overdue" Automation (Daily Cron Job)**

**What**: Certificate status automation  
**Implementation** (PostgreSQL):

```sql
-- Update certificate statuses daily
UPDATE certificates
SET 
    is_overdue = (CURRENT_DATE > due_date),
    is_expired = (CURRENT_DATE > expiry_date),
    status = CASE
        WHEN CURRENT_DATE > expiry_date THEN 'Expired'::cert_status
        WHEN CURRENT_DATE > due_date THEN 'Overdue'::cert_status
        WHEN CURRENT_DATE >= (due_date - INTERVAL '30 days') THEN 'Due'::cert_status
        ELSE 'Current'::cert_status
    END
WHERE vessel_id = ?
  AND status != 'Cancelled';

-- AUTOMATIC FLAG STATE VISIBILITY
SELECT * FROM certificates 
WHERE vessel_id = ? 
AND is_overdue = true 
AND flag_state_id = ? -- Flag state gets auto-access
```

**Python Cron Job**:

```python
# tasks/certificate_automation.py
def daily_certificate_check():
    """Runs daily at 00:00 UTC"""
    today = date.today()
    
    # Update all certificate statuses
    certs = Certificate.objects.all()
    for cert in certs:
        if today > cert.expiry_date:
            cert.status = 'Expired'
            cert.is_expired = True
        elif today > cert.due_date:
            cert.status = 'Overdue'
            cert.is_overdue = True
        else:
            cert.status = 'Current'
        cert.save()
        
        # Log the status change
        audit_log(
            user_id=None,
            action_type='System_Certificate_Update',
            entity_type='Certificate',
            entity_id=cert.cert_id,
            details={'old_status': cert.status, 'new_status': cert.status}
        )
        
        # Notify Flag State if overdue
        if cert.is_overdue:
            notify_flag_state(cert.vessel)
```

---

#### **Rule 4: Consent Gateway Workflows (Owner Intervention)**

**What**: Correspondence, Operational reports, Insurance requests  
**Implementation**:

```python
def can_view_consent_gated_doc(user: User, vessel: Vessel, doc: Document) -> bool:
    """
    Insurance companies and third parties need owner approval
    for sensitive operational documents.
    """
    if user.role == 'Insurance_Company':
        # Check if:
        # 1. Active insurance agreement exists
        # 2. Explicit access_request approved by owner
        
        agreement = Agreement.objects.filter(
            vessel_id=vessel.vessel_id,
            related_organization_id=user.organization_id,
            agreement_type__in=['Insurance_PI', 'Insurance_Hull'],
            is_active=True,
            end_date__gte=date.today()
        ).first()
        
        if not agreement:
            return False  # No active agreement
        
        # Check if access request approved
        access_req = AccessRequest.objects.filter(
            vessel_id=vessel.vessel_id,
            doc_id=doc.doc_id,
            requester_id=user.user_id,
            status='Approved',
            expiry_date__gte=date.today()
        ).first()
        
        if not access_req:
            # Create pending request for owner approval
            AccessRequest.objects.create(
                vessel_id=vessel.vessel_id,
                doc_id=doc.doc_id,
                requester_id=user.user_id,
                owner_id=vessel.owner_id,
                status='Pending',
                request_reason=f'{user.organization_name} requesting document access'
            )
            
            # Notify owner
            send_notification(
                user_id=vessel.owner_id,
                message=f'Access request from {user.organization_name}',
                action_url=f'/requests/{access_req.request_id}'
            )
            
            return False  # Block until approved
        
        return True
    
    return False
```

---

#### **Rule 5: Specialized Tanker & Bulk Carrier Logic (SOLAS Ch.II-1/3-10)**

**What**: Ship Construction File (SCF), Formal Review Letters  
**Implementation**:

```python
def can_view_scf(user: User, vessel: Vessel) -> bool:
    """
    SCF (Ship Construction File) is only for Tankers/Bulk Carriers.
    - Owner: Full access
    - Flag State: Can only request via Owner portal
    - Port State: On-board verification only
    - Others: No access
    """
    
    # Check vessel type
    if vessel.vessel_type not in ['Tanker', 'Bulk_Carrier']:
        return False  # SCF not applicable
    
    # Owner always has access
    if user.role == 'Owner_Master' and user == vessel.owner:
        return True
    
    # Admin always has access
    if user.role == 'Admin':
        return True
    
    # Flag State: restricted access
    if user.role == 'Flag_State':
        # Can only view via request_via_owner workflow
        return False  # Direct access denied; must go through owner
    
    # Port State: on-board verification only
    if user.role == 'Port_State':
        # Check if on-board verification in progress
        verification = OnBoardVerification.objects.filter(
            vessel_id=vessel.vessel_id,
            port_state_id=user.user_id,
            is_active=True,
            expires_at__gte=datetime.now()
        ).first()
        return verification is not None
    
    # Insurance: explicit owner approval required
    if user.role == 'Insurance_Company':
        return can_view_consent_gated_doc(user, vessel, None)
    
    return False

def get_scf_for_flag_state_via_owner(
    flag_state_user: User,
    vessel: Vessel
) -> dict:
    """
    Flag State requests SCF from Owner.
    Triggers a workflow to get Owner permission.
    """
    owner = User.objects.get(user_id=vessel.owner_id)
    
    # Create access request
    request = AccessRequest.objects.create(
        vessel_id=vessel.vessel_id,
        doc_id=scf_doc.doc_id,
        requester_id=flag_state_user.user_id,
        owner_id=owner.user_id,
        request_reason='Flag State - SCF review for Goal-Based compliance',
        status='Pending'
    )
    
    # Notify owner with special workflow
    send_email(
        to=owner.email,
        subject=f'SCF Access Request from {flag_state_user.organization_name}',
        template='scf_approval_required',
        context={
            'request_id': request.request_id,
            'vessel': vessel,
            'flag_state': flag_state_user.organization_name,
            'approval_url': f'https://app.url/requests/{request.request_id}/approve'
        }
    )
    
    return {'status': 'pending', 'request_id': request.request_id}
```

---

### 3.2 Access Control Decision Matrix

| Rule | Triggering Condition | Access Decision | Background Job |
|------|---------------------|---|---|
| **1** | Standing Doc + Any Auth User | ✅ Allow | Audit log only |
| **2A** | Newbuilding + Owner/Shipyard | ✅ Allow | Track lifecycle |
| **2B** | In-Operation + Shipyard | ❌ Deny | Revoke access |
| **3** | Certificate Overdue + Flag State | ✅ Allow | Daily cron auto-grant |
| **4** | Insurance Request + No Agreement | ❌ Deny | Create pending request |
| **5A** | Tanker/Bulk + SCF + Flag State | ❌ Deny | Offer request workflow |
| **5B** | Tanker/Bulk + On-Board Verify + Port State | ✅ Allow | Time-limited access |

---

## 4. AUTHENTICATION & AUTHORIZATION

### 4.1 JWT-Based Authentication Flow

```python
# auth/middleware.py
from functools import wraps
from datetime import datetime, timedelta
import jwt
import os

SECRET_KEY = os.getenv('JWT_SECRET_KEY')
ALGORITHM = 'HS256'
TOKEN_EXPIRY_MINUTES = 60

def create_access_token(user_id: int, role: str, org_id: int) -> str:
    """Generate JWT token with user context"""
    payload = {
        'user_id': user_id,
        'role': role,
        'org_id': org_id,
        'exp': datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRY_MINUTES),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> dict:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise Exception('Token expired')
    except jwt.InvalidTokenError:
        raise Exception('Invalid token')

def require_auth(f):
    """Flask decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # Check headers for Authorization: Bearer <token>
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]
            except IndexError:
                return {'error': 'Invalid token format'}, 401
        
        if not token:
            return {'error': 'Missing authentication token'}, 401
        
        try:
            payload = verify_token(token)
            request.user_id = payload['user_id']
            request.user_role = payload['role']
            request.org_id = payload['org_id']
        except Exception as e:
            return {'error': str(e)}, 401
        
        return f(*args, **kwargs)
    
    return decorated_function

def audit_middleware(f):
    """Log all API requests for compliance"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = getattr(request, 'user_id', None)
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent')
        
        # Get response
        result = f(*args, **kwargs)
        
        # Log to audit_logs
        audit_log(
            user_id=user_id,
            action_type=request.method,
            entity_type=request.path,
            ip_address=ip_address,
            user_agent=user_agent,
            status='success' if isinstance(result, tuple) and result[1] < 400 else 'failed'
        )
        
        return result
    
    return decorated_function
```

---

## 5. VISIBILITYMANAGER SERVICE

### 5.1 Core VisibilityManager Class

```python
# services/visibility_manager.py
from datetime import date
from typing import List, Optional
from enum import Enum

class VisibilityStatus(Enum):
    ALLOWED = 'allowed'
    DENIED = 'denied'
    PENDING_APPROVAL = 'pending_approval'
    REQUIRES_AGREEMENT = 'requires_agreement'

class VisibilityManager:
    """
    Central service for all data access decisions.
    Encodes all 5 rules + special cases.
    """
    
    def __init__(self, db_session):
        self.db = db_session
    
    # ===== RULE 1: Standing Documentation =====
    def can_view_standing_doc(self, user: User, doc: Document) -> bool:
        """Rule 1: All authenticated users can access standing docs"""
        return True
    
    # ===== RULE 2: Lifecycle-Based Access =====
    def can_view_newbuilding_doc(
        self, 
        user: User, 
        vessel: Vessel, 
        doc: Document
    ) -> VisibilityStatus:
        """Rule 2: Newbuilding phase -> delivery phase transition"""
        
        # Phase 1: Newbuilding (is_delivered = FALSE)
        if not vessel.is_delivered:
            if user.role == 'Admin':
                return VisibilityStatus.ALLOWED
            if user.role == 'Owner_Master' and user.user_id == vessel.owner_id:
                return VisibilityStatus.ALLOWED
            if user.role == 'Shipyard' and user.user_id == vessel.shipyard_id:
                return VisibilityStatus.ALLOWED
            return VisibilityStatus.DENIED
        
        # Phase 2: In Operation (is_delivered = TRUE)
        else:
            if user.role == 'Admin':
                return VisibilityStatus.ALLOWED
            if user.role == 'Owner_Master' and user.user_id == vessel.owner_id:
                return VisibilityStatus.ALLOWED
            if user.role == 'Flag_State' and user.user_id == vessel.flag_state_id:
                return VisibilityStatus.ALLOWED
            
            # Shipyard loses access post-delivery
            if user.role == 'Shipyard':
                return VisibilityStatus.DENIED
            
            # Others need approval
            return self._check_access_request(user, vessel, doc)
    
    # ===== RULE 3: Overdue Automation =====
    def can_view_certificate_due_to_overdue(
        self,
        user: User,
        vessel: Vessel,
        certificate: Certificate
    ) -> bool:
        """Rule 3: Overdue certs auto-visible to flag state"""
        
        if not certificate.is_overdue:
            # Not overdue, standard rules apply
            return user.role == 'Flag_State' or user.role == 'Admin'
        
        # Is overdue: Flag State auto-access
        if user.role == 'Flag_State' and user.user_id == vessel.flag_state_id:
            return True  # AUTOMATIC ACCESS
        
        # Admin always sees
        if user.role == 'Admin':
            return True
        
        return False
    
    # ===== RULE 4: Consent Gated Documents =====
    def can_view_consent_gated_doc(
        self,
        user: User,
        vessel: Vessel,
        doc: Document
    ) -> VisibilityStatus:
        """Rule 4: Insurance & third parties need owner approval"""
        
        if user.role == 'Admin':
            return VisibilityStatus.ALLOWED
        
        if user.role == 'Owner_Master':
            return VisibilityStatus.ALLOWED
        
        if user.role == 'Insurance_Company':
            # Check for active insurance agreement
            agreement = self.db.query(Agreement).filter(
                Agreement.vessel_id == vessel.vessel_id,
                Agreement.related_organization_id == user.user_id,
                Agreement.agreement_type.in_(['Insurance_PI', 'Insurance_Hull']),
                Agreement.is_active == True,
                Agreement.end_date >= date.today()
            ).first()
            
            if not agreement:
                return VisibilityStatus.REQUIRES_AGREEMENT
            
            # Check for existing approved access request
            access_req = self.db.query(AccessRequest).filter(
                AccessRequest.vessel_id == vessel.vessel_id,
                AccessRequest.doc_id == doc.doc_id,
                AccessRequest.requester_id == user.user_id,
                AccessRequest.status == 'Approved',
                AccessRequest.expiry_date >= date.today()
            ).first()
            
            if access_req:
                return VisibilityStatus.ALLOWED
            else:
                return VisibilityStatus.PENDING_APPROVAL
        
        return VisibilityStatus.DENIED
    
    # ===== RULE 5: Tanker/Bulk Carrier SCF Logic =====
    def can_view_scf(
        self,
        user: User,
        vessel: Vessel
    ) -> VisibilityStatus:
        """Rule 5: SCF special handling for Goal-Based ships"""
        
        # Only applies to Tanker/Bulk Carrier
        if vessel.vessel_type not in ['Tanker', 'Bulk_Carrier']:
            return VisibilityStatus.DENIED
        
        if user.role == 'Admin':
            return VisibilityStatus.ALLOWED
        
        if user.role == 'Owner_Master' and user.user_id == vessel.owner_id:
            return VisibilityStatus.ALLOWED
        
        if user.role == 'Flag_State':
            # Flag State cannot view directly
            # Must use request_via_owner workflow
            return VisibilityStatus.REQUIRES_AGREEMENT
        
        if user.role == 'Port_State':
            # Only during on-board verification
            verification = self.db.query(OnBoardVerification).filter(
                OnBoardVerification.vessel_id == vessel.vessel_id,
                OnBoardVerification.port_state_id == user.user_id,
                OnBoardVerification.is_active == True,
                OnBoardVerification.expires_at > datetime.now()
            ).first()
            
            if verification:
                return VisibilityStatus.ALLOWED
            return VisibilityStatus.DENIED
        
        if user.role == 'Insurance_Company':
            return self.can_view_consent_gated_doc(user, vessel, None)
        
        return VisibilityStatus.DENIED
    
    # ===== MASTER VISIBILITY DECISION =====
    def get_document_visibility(
        self,
        user: User,
        doc: Document
    ) -> VisibilityStatus:
        """
        Main entry point: Determine if user can view/download a document
        """
        vessel = self.db.query(Vessel).get(doc.vessel_id)
        
        if not vessel:
            return VisibilityStatus.DENIED
        
        # Route to appropriate rule
        if doc.category == 'Standing_Doc':
            return VisibilityStatus.ALLOWED if self.can_view_standing_doc(user, doc) else VisibilityStatus.DENIED
        
        elif doc.category == 'Newbuilding':
            return self.can_view_newbuilding_doc(user, vessel, doc)
        
        elif doc.category == 'SCF':
            return self.can_view_scf(user, vessel)
        
        elif doc.category in ['Class_Operation', 'Statutory_Operation', 'Correspondence']:
            return self.can_view_consent_gated_doc(user, vessel, doc)
        
        else:
            return VisibilityStatus.DENIED
    
    # ===== HELPER METHODS =====
    def _check_access_request(
        self,
        user: User,
        vessel: Vessel,
        doc: Optional[Document]
    ) -> VisibilityStatus:
        """Check if user has approved access request for this vessel/doc"""
        
        query = self.db.query(AccessRequest).filter(
            AccessRequest.vessel_id == vessel.vessel_id,
            AccessRequest.requester_id == user.user_id,
            AccessRequest.status == 'Approved'
        )
        
        if doc:
            query = query.filter(AccessRequest.doc_id == doc.doc_id)
        
        # Check expiry
        access_req = query.first()
        if access_req and access_req.expiry_date and access_req.expiry_date >= date.today():
            return VisibilityStatus.ALLOWED
        
        if access_req:
            return VisibilityStatus.PENDING_APPROVAL
        
        return VisibilityStatus.DENIED
    
    def create_access_request(
        self,
        requester: User,
        vessel: Vessel,
        doc: Optional[Document],
        reason: str
    ) -> AccessRequest:
        """Helper: Create pending access request"""
        
        new_request = AccessRequest(
            vessel_id=vessel.vessel_id,
            doc_id=doc.doc_id if doc else None,
            requester_id=requester.user_id,
            owner_id=vessel.owner_id,
            request_reason=reason,
            status='Pending',
            expiry_date=date.today() + timedelta(days=30)
        )
        
        self.db.add(new_request)
        self.db.commit()
        
        # Notify owner
        notify_owner_of_access_request(vessel.owner_id, new_request)
        
        return new_request

```

---

## 6. IMPLEMENTATION ROADMAP

### Phase 1: Database & Auth (Weeks 1-4)
- [x] PostgreSQL schema creation with RLS policies
- [x] User management & RBAC setup
- [x] JWT authentication middleware
- [x] Audit logging infrastructure

### Phase 2: VisibilityManager Service (Weeks 5-8)
- [ ] Implement VisibilityManager class
- [ ] Build Rule 1-5 logic
- [ ] Create unit tests (target >85% coverage)
- [ ] Performance testing for decision logic

### Phase 3: API Endpoints (Weeks 9-12)
- [ ] `/vessels` - List vessels (multi-tenant filtered)
- [ ] `/documents/{doc_id}` - Get document (visibility-checked)
- [ ] `/certificates/{cert_id}` - Get certificate (lifecycle-aware)
- [ ] `/access-requests` - Create/approve requests
- [ ] `/compliance-library` - Standing docs endpoint

### Phase 4: Frontend Integration (Weeks 13-16)
- [ ] Streamlit UI for role-specific dashboards
- [ ] Document browser with visibility indicators
- [ ] Access request workflow UI
- [ ] Audit log viewer (admin only)

### Phase 5: Background Jobs & Testing (Weeks 17-20)
- [ ] Daily certificate automation cron
- [ ] Expiry notification system
- [ ] Access request timeout cleanup
- [ ] E2E testing across all rules

### Phase 6: Deployment & Hardening (Weeks 21-24)
- [ ] Render deployment configuration
- [ ] Security audit & penetration testing
- [ ] Performance optimization & load testing
- [ ] Production launch

---

## KEY TAKEAWAYS FOR COPILOT/DEVELOPERS

### What This Spec Provides

✅ **Complete data model** - 9 tables with indices and relationships  
✅ **Business rule encoding** - 5 access rules with decision matrices  
✅ **Authentication flow** - JWT tokens + audit logging middleware  
✅ **VisibilityManager** - Centralized service for ALL visibility decisions  
✅ **Lifecycle management** - Newbuilding → Delivery → Operation state transitions  
✅ **Compliance automation** - Cron jobs for certificate status updates  
✅ **Multi-tenancy** - Secure data partitioning by organization  

### How to Use With GitHub Copilot

1. **Copy the SQL schema** → Paste into database initialization script
2. **Copy VisibilityManager** → Paste into your services layer
3. **Reference Rule** → When building any API endpoint, consult the rule that applies
4. **Ask Copilot**: "Based on SYSTEM_ARCHITECTURE_SPEC.md, write the Flask route for `/documents/{doc_id}` that enforces visibility rules"

---

**Version**: 1.0  
**Status**: ✅ READY FOR IMPLEMENTATION  
**Next Step**: Begin Phase 1 database setup
