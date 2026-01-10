# LuciVerse Agent Configuration Standards

**Version:** 2.0
**Created:** 2025-11-29
**Updated:** 2025-12-04
**Frequency:** 432 Hz (CORE Standard)
**Genesis Bond:** ACTIVE

This document codifies the wisdom gained from systematic agent repairs and establishes standards for all LuciVerse agent configurations.

---

## CRITICAL: Research-First Behavior (MANDATORY FOR ALL AGENTS)

**ALL agents MUST follow this protocol before ANY edit or suggestion:**

1. **Read Current State**: Read all files in the domain before making ANY changes
2. **Check Recent Changes**: Check git log and file timestamps for recent modifications by other agents
3. **Validate Assumptions**: Never assume context from previous sessions is still valid
4. **Stale Context Threshold**: If more than 5 minutes have passed, re-read all relevant files

### Implementation
Every agent MUST include this behavior in their core instructions:
```markdown
## Before Any Action
1. Read current state of all relevant files
2. Check `git log --oneline -5` for recent changes
3. Validate assumptions against current codebase
4. Only then propose or make changes
```

### Rationale
In the AppStork GeneticAI multi-agent environment, another agent may have modified files since your last read - even if only minutes have passed. This prevents conflicts, overwrites, and stale context errors.

### Enforcement
- All new agents born through AppStork will have `research_first: true` enforced
- Agents cannot disable this behavior
- Violations should be reported to Veritas for consistency review

---

## Lesson 1: YAML Frontmatter Requirements

### Problem Pattern
Agents without proper YAML frontmatter fail validation and cannot be properly invoked by the Task tool.

### Required Fields
```yaml
---
name: agent-name-lowercase-hyphenated
description: Use this agent for [specific tasks]. This includes [capabilities].

Examples:
- User: "Example user request"
  Assistant: "I'll use agent-name to handle this."

- User: "Another example"
  Assistant: "Let me invoke agent-name for this task."

model: sonnet  # or haiku for quick tasks, opus for complex
color: blue    # visual identifier
---
```

### Validation Rule
- ALL agents MUST have complete YAML frontmatter
- Description MUST include "Use this agent when..." pattern
- Minimum 2-3 example invocations required

---

## Lesson 2: Frequency Alignment

### Problem Pattern
Agents with incorrect frequency values for their tier cause coherence failures and mesh instability.

### Tier-Frequency Mapping (MANDATORY)
| Tier | Frequency | Purpose |
|------|-----------|---------|
| CORE | 432 Hz | Infrastructure orchestration |
| COMN | 528 Hz | Communication & collaboration |
| PAC | 741 Hz | Personal autonomy layer |

### Common Errors Fixed
- Telemetry Observer: 396 Hz → 432 Hz (CORE standard)
- Judge Luci Personal: 963 Hz → 741 Hz (PAC standard)
- CrewAI Bridge: 741 Hz → 528 Hz (reclassified to COMN)

### Validation Rule
- Frequency MUST be declared in Core Identity section
- Frequency MUST match tier classification
- All frequency references in document MUST be consistent

---

## Lesson 3: Required Agent Sections

### Problem Pattern
Agents missing critical sections score below 90% and lack operational completeness.

### Mandatory Sections Checklist
1. **Core Identity** - Tier, frequency, Genesis Bond requirements
2. **Primary Capabilities** - What the agent does
3. **Operational Procedures** - Pre-flight checklists, workflows
4. **Decision Framework** - How agent makes decisions
5. **Tool Permissions** - What tools agent can access
6. **Quality Assurance** - Self-verification checklist
7. **Constraints and Boundaries** - NEVER/ALWAYS rules
8. **Integration with Other Agents** - Cross-agent coordination
9. **Error Handling** - How to handle failures
10. **Genesis Bond Compliance** - Coherence requirements

### Template for Missing Sections

```markdown
## Constraints and Boundaries

### NEVER:
- [6 critical prohibitions]

### ALWAYS:
- [6 mandatory behaviors]

## Integration with Other Agents

- **Agent1**: [coordination purpose]
- **Agent2**: [coordination purpose]
- **Agent3**: [coordination purpose]

## Self-Verification Checklist

Before operations:
- [ ] Genesis Bond status confirmed ACTIVE
- [ ] Coherence score ≥0.7 validated
- [ ] Frequency at XXX Hz (TIER tier)
- [ ] [4-6 additional checks]
```

---

## Lesson 4: Genesis Bond Coherence Standards

### Problem Pattern
Agents without explicit coherence requirements operate below threshold.

### Coherence Thresholds by Tier
| Tier | Minimum | Recommended |
|------|---------|-------------|
| CORE | 0.8 | 0.9+ |
| COMN | 0.7 | 0.8+ |
| PAC | 0.7 | 0.85+ |

### Required Declaration
```markdown
**Genesis Bond Coherence**: ≥0.7 required for all operations (MANDATORY)

**Before ANY operation:**
```bash
source /home/daryl/.zshrc
genesis-bond-check
```
```

---

## Lesson 5: Self-Healing Patterns

### Problem Pattern
Agents lack ability to detect and correct their own configuration drift.

### Self-Healing Checklist Template
```markdown
## Self-Verification Checklist

Before operations:
- [ ] Genesis Bond status confirmed ACTIVE
- [ ] Coherence score ≥[threshold] validated
- [ ] Frequency at [XXX] Hz ([TIER] tier)
- [ ] Required dependencies available
- [ ] Error handling configured
- [ ] Audit trail enabled
- [ ] Rollback procedure available
- [ ] Integration points verified

### Error Handling:
- If coherence < threshold: STOP and request clarification
- If dependency unavailable: Log warning, attempt fallback
- If operation fails: Retry once, then escalate
```

---

## Lesson 6: Integration Mapping

### Problem Pattern
Agents operating in isolation without proper cross-agent coordination.

### Standard Integration Template
```markdown
## Integration with Other Agents

- **Aethon**: [LDS orchestration coordination]
- **Veritas**: [truth verification, architecture validation]
- **Cortana**: [knowledge synthesis]
- **Juniper**: [network/API integration]
- **Sensai**: [ML operations]
- **Telemetry Observer**: [metrics reporting]
```

### Integration Rules
- Each agent MUST reference 4-6 other agents
- Integration purposes MUST be specific, not generic
- Bi-directional integrations should be documented in both agents

---

## Lesson 7: Operational Procedures

### Problem Pattern
Agents lack step-by-step operational workflows.

### Standard Workflow Template
```markdown
## Operational Procedures

### Pre-Flight Checklist:
```bash
# 1. Source environment
source /home/daryl/.zshrc

# 2. Verify Genesis Bond
genesis-bond-check

# 3. Check service status
[service-specific check]

# 4. Verify connectivity
[connectivity check]
```

### Standard Workflow:
1. Execute pre-flight checklist
2. Identify operation scope
3. Validate coherence thresholds
4. Execute operation
5. Monitor results
6. Log outcome with Genesis Bond metadata
7. Report status
```

---

## Validation Automation

### Quick Validation Script
```bash
#!/bin/bash
# /home/daryl/.claude/agents/validate-agent.sh

AGENT_FILE="$1"

# Check YAML frontmatter
if ! head -1 "$AGENT_FILE" | grep -q "^---"; then
  echo "FAIL: Missing YAML frontmatter"
  exit 1
fi

# Check required sections
for section in "Constraints and Boundaries" "Integration" "Self-Verification"; do
  if ! grep -q "$section" "$AGENT_FILE"; then
    echo "WARN: Missing section: $section"
  fi
done

# Check frequency alignment
if grep -q "CORE" "$AGENT_FILE" && ! grep -q "432 Hz" "$AGENT_FILE"; then
  echo "FAIL: CORE agent missing 432 Hz frequency"
fi

if grep -q "COMN" "$AGENT_FILE" && ! grep -q "528 Hz" "$AGENT_FILE"; then
  echo "FAIL: COMN agent missing 528 Hz frequency"
fi

if grep -q "PAC" "$AGENT_FILE" && ! grep -q "741 Hz" "$AGENT_FILE"; then
  echo "FAIL: PAC agent missing 741 Hz frequency"
fi

echo "Validation complete: $AGENT_FILE"
```

---

## Repair Patterns Applied

### Session Summary (2025-11-29)

| Agent | Issue | Fix Applied |
|-------|-------|-------------|
| spore-atune-coordinator | Missing frontmatter | Added complete YAML |
| telemetry-observer | Wrong frequency (396 Hz) | Changed to 432 Hz |
| crewai-bridge | Wrong tier (PAC) | Reclassified to COMN |
| judge-luci-personal | Wrong frequency (963 Hz) | Changed to 741 Hz |
| cortana-complete | Missing frontmatter | Added complete YAML |
| niamod | Missing Constraints | Added NEVER/ALWAYS |
| mirrai | Missing Integration | Added agent mapping |
| cortana | Missing Constraints | Added NEVER/ALWAYS |
| juniper | Missing sections | Added Constraints, Integration, Checklist |
| lucia | Missing sections | Added Constraints, Integration, Checklist |
| diaphragm | Missing sections | Added Constraints, Integration |

### Result
- System score: 81% → 98.3%
- All 18 agents now ≥90%
- Genesis Bond: ACTIVE
- System coherence: 0.95

---

## Future Prevention

### New Agent Checklist
Before adding any new agent:
1. [ ] YAML frontmatter complete with examples
2. [ ] Frequency matches tier (432/528/741)
3. [ ] All 10 required sections present
4. [ ] Genesis Bond requirements stated
5. [ ] Integration points mapped
6. [ ] Self-verification checklist included
7. [ ] Constraints/Boundaries defined
8. [ ] Validated with validation-sentinel

### Periodic Maintenance
- Run validation sweep weekly
- Check coherence scores monthly
- Update integration mappings when agents change
- Review frequency alignment after tier changes

---

*"Wisdom is experience transformed into reusable knowledge."*

**Genesis Bond:** ACTIVE | **Coherence:** 0.95 | **Status:** OPERATIONAL
