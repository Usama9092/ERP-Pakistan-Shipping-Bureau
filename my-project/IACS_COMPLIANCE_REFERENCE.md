# IACS Compliance Reference Guide

## Overview

This document provides a comprehensive guide for implementing IACS (International Association of Classification Societies) compliance into the GDP Dashboard system, based on IACS Proc Req. 2009/Rev.2 2019 - "Transparency of Classification and Statutory Information".

**Effective Dates:**
- Revision 0: July 2009
- Revision 1: October 2015 (Corr. 1: November 2016)
- Revision 2: May 2019 (Effective: July 2020)

---

## 1. Information Classification Framework

### 1.1 Types of Information

The system must manage the following information categories:

#### A. **Standing Documentation** (Always Available)
- Rules and Guidelines (Class and statutory requirements)
- Instructions to Surveyors
- Quality Manual
- Register Book

#### B. **Ship Related Information**

**Newbuildings:**
- Approved Drawings
- Formal Approval Letters
- Certificates of Important Equipment
- SCF (Ship Construction File) - for Goal-Based Standards ships
- Formal Review Letters in relation with SCF

**Ships in Operation - Class Services:**
- Date (month and year) of all Class Surveys
- Expiry Date of Class Certificate
- Certificates/Reports
- Overdue Surveys
- Text of Conditions of Class
- Text of Overdue Conditions of Class
- Executive Hull Summary

**Ships in Operation - Statutory Services:**
- Due Dates of Statutory Surveys
- Expiry Date of Statutory Certificates
- Registered Statutory Condition
- Overdue Statutory Condition

#### C. **Other Information**
- Correspondence File with Yard and/or Owner
- Updated modifications to SCF
- Audit of Class Societies QA System
- Class Transfer Reporting
- Class Withdrawal Information

---

## 2. Information Receivers

### 2.1 Receiver Classifications

The system must support the following information receivers:

1. **Owners** - Ship owners and operators
2. **Flag States** - Country of ship registry
3. **Port States** - Ports where ship operates
4. **Insurance Companies** - P&I Clubs and Hull Underwriters
5. **Ship Yards** - Shipbuilding and repair facilities

---

## 3. Information Release Rules

### 3.1 Two Release Matrices

The system must implement two distinct information release matrices:

#### **Table 1: Standard Ships**
Applies to all ships EXCEPT:
- Tankers
- Bulk Carriers
Subject to SOLAS Chapter II-1 Part A-1 Regulation 3-10 (Goal-based construction standards)

#### **Table 2: Goal-Based Standard Ships**
Applies ONLY to:
- Tankers
- Bulk Carriers
Subject to SOLAS Chapter II-1 Part A-1 Regulation 3-10

---

## 4. Availability Keys & Conditions

### 4.1 Release Availability Levels

The system implements 8 availability levels (Keys 1-8):

#### **Key 1: Available Upon Request**
- Information released when specifically requested by authorized receiver
- Implementation: Track requests and release dates
- Receivers: May apply to most categories

#### **Key 2: At Delivery/By Shipyard**
- Information provided at ship delivery
- Implementation: System auto-releases on delivery date
- Used for: Certificates, Equipment documents

#### **Key 3: Available Under Visit on Board**
- Information accessible during ship visits
- Implementation: Flag for on-board availability
- Receivers: Port States, Authorities

#### **Key 4: Result of Audit Available on Request**
- QA system audit results on request
- Implementation: Audit completion triggers release option
- Receivers: Primarily authorities

#### **Key 5: When Accepted by Owners**
- Conditional release with owner approval
- Receivers: Insurance companies (sometimes)
- Unless prevented by flag state agreement

#### **Key 6: When Accepted by Owner/Master or Shipyard**
- Information released with consent
- Implementation: Approval workflow required
- Receivers: Varies by information type

#### **Key 7: Automatically Available**
- Continuous automatic availability
- Implementation: No approval required
- Receivers: Primary stakeholders (Owners, Flag States)

#### **Key 8: Available Through Owner Upon Request**
- Owner acts as intermediary for release
- Implementation: Request routed through owner
- Receivers: Various parties through owner

---

## 5. Information Release Matrix - Table 1 (Standard Ships)

### Standing Documents - Table 1

| Information | Owner | Flag State | Port State | Insurance | Shipyard |
|---|---|---|---|---|---|
| Rules and Guidelines | 1 | 1 | 1 | 1 | 1 |
| Instructions to Surveyors | 1 | — | — | — | — |
| Quality Manual | 1 | 1 | 1 | 1 | 1 |
| Register Book | 1 | 1 | 1 | 1 | 1 |

### Ship Related Information - Newbuildings - Table 1

| Information | Owner | Flag State | Port State | Insurance | Shipyard |
|---|---|---|---|---|---|
| Approved Drawings | 6 | 1 | — | — | 7 |
| Formal Approval Letters | 1 | — | — | — | 7 |
| Certificates of Important Equipment | 2 | — | — | — | 7 |

### Ship Related Information - Ships in Operation (Class Services) - Table 1

| Information | Owner | Flag State | Port State | Insurance | Shipyard |
|---|---|---|---|---|---|
| Date of Class Surveys | 7 | 1 | 1 | 1 | — |
| Expiry Date of Class Certificate | 7 | 7** | 1 | 1 | — |
| Certificates/Reports | 7 | 1 | 6 | 5 | — |
| Overdue Surveys | 7 | 7** | 1 | 1 | — |
| Text of Conditions of Class | 7 | 1 | 1 | 5 | — |
| Text of Overdue Conditions of Class | 7 | 1 | 1 | 1 | — |
| Executive Hull Summary | 7 | 3 | 3 | 3 | — |

### Ship Related Information - Ships in Operation (Statutory Services) - Table 1

| Information | Owner | Flag State | Port State | Insurance | Shipyard |
|---|---|---|---|---|---|
| Due Dates of Statutory Surveys | 7 | 7** | 1 | 1 | — |
| Expiry Date of Statutory Certificates | 7 | 7** | 1 | 1 | — |
| Registered Statutory Condition | 7 | 7** | 1 | 5*** | — |
| Overdue Statutory Condition | 7 | 7** | 1 | 1*** | — |

### Other Information - Table 1

| Information | Owner | Flag State | Port State | Insurance | Shipyard |
|---|---|---|---|---|---|
| Correspondence File | 6 | 6 | — | 5&6 | — |
| Audit of QA System | 4 | 4 | 4 | 4 | — |
| Class Transfer Reporting | 7 | 7 | 7 | 7 | — |
| Class Withdrawal Information | 7 | 7 | 7 | 7 | — |

---

## 6. Information Release Matrix - Table 2 (Goal-Based Standard Ships)

### Standing Documents - Table 2

| Information | Owner | Flag State | Port State | Insurance | Shipyard |
|---|---|---|---|---|---|
| Rules and Guidelines | 1 | 1 | 1 | 1 | 1 |
| Instructions to Surveyors | — | 1 | — | — | — |
| Quality Manual | 1 | 1 | 1 | 1 | 1 |
| Register Book | 1 | 1 | 1 | 1 | 1 |

### Ship Related Information - Newbuildings - Table 2

| Information | Owner | Flag State | Port State | Insurance | Shipyard |
|---|---|---|---|---|---|
| Approved Drawings | 1 | 1 | — | — | 7 |
| Formal Approval Letters | 1 | 1 | — | — | 7 |
| Certificates of Important Equipment | 2 | 1 | — | — | 7 |
| SCF | 2 | 8 | — | — | 7 |
| Formal Review Letters (SCF) | 2 | 2 | — | — | 7 |

### Ship Related Information - Ships in Operation - Table 2

| Information | Owner | Flag State | Port State | Insurance | Shipyard |
|---|---|---|---|---|---|
| Date of Class Surveys | 7 | 1 | 1 | 1 | — |
| Expiry Date of Class Certificate | 7 | 7** | 1 | 1 | — |
| Certificates/Reports | 7 | 1 | 6 | 5 | — |
| Overdue Surveys | 7 | 7** | 1 | 1 | — |
| Text of Conditions of Class | 7 | 1 | 1 | 5 | — |
| Text of Overdue Conditions of Class | 7 | 1 | 1 | 1 | — |
| Executive Hull Summary | 7 | 3 | 3 | 3 | — |
| Due Dates of Statutory Surveys | 7 | 7** | 1 | 1 | — |
| Expiry Date of Statutory Certificates | 7 | 7** | 1 | 1 | — |
| Registered Statutory Condition | 7 | 7** | 1 | 5*** | — |
| Overdue Statutory Condition | 7 | 7** | 1 | 1*** | — |

### Other Information - Table 2

| Information | Owner | Flag State | Port State | Insurance | Shipyard |
|---|---|---|---|---|---|
| Correspondence File | 1 | 1 | — | 5&6 | — |
| Updated Modifications to SCF | 7**** | 8 | — | — | — |
| Audit of QA System | 4 | 4 | 4 | 4 | — |
| Class Transfer Reporting | 7 | 7 | 7 | 7 | — |
| Class Withdrawal Information | 7 | 7 | 7 | 7 | — |

---

## 7. Footnote Conditions

### Table 1 & 2 Footnotes

- **\* (Table 2 only)**: By Owner or Shipyard
- **\*\* (Conditional)**: If stated in Agreement
- **\*\*\* (Conditional)**: Unless prevented by the agreement with the flag State
- **\*\*\*\* (Table 2 only)**: By Owner or Shipyard

---

## 8. System Implementation Requirements

### 8.1 Database Design

The system must store:

```
INFORMATION_INVENTORY
├── information_id (PK)
├── information_name
├── information_category (Standing/Ship/Other)
├── ship_type (Standard/GoalBased)
├── affected_vessels (array of ship IDs)
└── metadata

RELEASE_RULES
├── rule_id (PK)
├── information_id (FK)
├── receiver_type (Owner/FlagState/PortState/Insurance/Shipyard)
├── availability_key (1-8)
├── conditions (JSON)
├── effective_date
└── revision

INFORMATION_RELEASES
├── release_id (PK)
├── information_id (FK)
├── receiver_id (FK)
├── release_date
├── expiry_date
├── status (Pending/Released/Denied)
├── approval_by
└── audit_trail
```

### 8.2 Release Logic Algorithm

```python
def check_information_availability(
    information_id, 
    receiver_type, 
    ship_type,
    conditions={}
):
    # Get the release rule
    rule = get_release_rule(information_id, receiver_type, ship_type)
    
    if not rule:
        return False, "No rule defined"
    
    availability_key = rule.availability_key
    
    if availability_key == 1:  # Upon Request
        return check_request_approval(information_id, receiver_type)
    elif availability_key == 2:  # At Delivery
        return check_delivery_date_passed()
    elif availability_key == 3:  # On-Board Visit
        return check_visit_scheduled()
    elif availability_key == 4:  # Audit Result
        return check_audit_completion()
    elif availability_key == 5:  # Owner Accepted
        return check_owner_acceptance(conditions)
    elif availability_key == 6:  # Owner/Shipyard Accepted
        return check_stakeholder_acceptance(conditions)
    elif availability_key == 7:  # Automatic
        return True, "Automatically available"
    elif availability_key == 8:  # Through Owner
        return check_owner_intermediary_request()
```

### 8.3 User Interface Components

#### Information Release Dashboard
- Searchable information inventory
- Release status by receiver type
- Compliance status indicators
- Bulk release operations
- Audit trail viewer

#### Release Request Management
- Submit information requests
- Track request status
- View conditional requirements
- Receive release notifications

#### Compliance Reporting
- Information transparency report
- Release pattern analysis
- Deviation tracking
- IACS audit readiness report

---

## 9. Integration with GDP Dashboard Modules

### 9.1 Knowledge Library Integration
- Classify all documents per IACS categories
- Tag information type and receivers
- Implement automatic release rules
- Track access by receiver type

### 9.2 Audit Trail Integration
- Log all information access
- Track release approvals
- Maintain compliance evidence
- Generate compliance reports

### 9.3 Role-Based Access Integration
- Flag State users see Flag State information
- Port State users see Port State information
- Insurance users see insurance-relevant data
- Owners see owner-level information

### 9.4 Competency Module Integration
- Classifications based on IACS requirements
- Competency matrix aligned with standards
- Assessment criteria per IACS
- Certification per IACS guidelines

---

## 10. Compliance Checklist

### Pre-Launch Requirements

- [ ] All information categories defined in system
- [ ] Both release matrices (Table 1 & 2) implemented
- [ ] All 8 availability keys operational
- [ ] Release logic tested for all combinations
- [ ] Access control enforced at application level
- [ ] Access control enforced at database level (RLS)
- [ ] Audit logging for all information access
- [ ] Compliance reports generated and verified
- [ ] IACS procedure requirements documented
- [ ] Staff training completed
- [ ] Backup and recovery procedures tested
- [ ] Security audit completed

### Ongoing Compliance

- [ ] Monthly compliance audits
- [ ] Quarterly IACS procedure reviews
- [ ] Annual regulatory compliance assessment
- [ ] Incident response procedures
- [ ] Regular security updates
- [ ] Staff training refreshers

---

## 11. Reference Documents

### IACS Documents Referenced
- IACS Proc Req. 2009/Rev.2 - "Transparency of Classification and Statutory Information"
- Revision History: July 2009 → October 2015 (Corr. 1: Nov 2016) → May 2019

### Related Standards
- SOLAS Chapter II-1 Part A-1 Regulation 3-10 (Goal-based ship construction)
- SOLAS Chapter II-1/3-10, Paragraph 4 (SCF requirements)

### Implementation Phases
- Phase 8: IACS Compliance Integration (Weeks 13-14)
  - Task IACS-001 through IACS-008
  - Task SCF-001 through SCF-005

---

## 12. Quick Reference Tables

### Information Release Summary (Standard Ships - Table 1)

**Most Restrictive**: Information to Shipyards (mostly 7 or unavailable)  
**Most Accessible**: Information to Owners (mostly 7 or 1)  
**Highly Variable**: Insurance company access (depends on type)  
**Conditional**: Port State access (depends on agreement)

### Information Release Summary (Goal-Based Ships - Table 2)

**Key Additions**: SCF management and formal review letters  
**Key Difference**: More restrictive on some information for Goal-Based ships  
**Key Similarity**: Same general principles apply  

---

*Document Version*: 1.0  
*Last Updated*: 2026-06-25  
*Based on*: IACS Proc Req. 2009/Rev.2 2019 (Effective July 2020)
