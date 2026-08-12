# Authorized Red Team — Rules of Engagement (Template)

Use only against systems you **own** or are **written-authorized** to test.

## 1. Authorization

- Client / owner: ______________________
- Authorization document ID / ticket: ______________________
- Approved by (name, role, date): ______________________
- Emergency contact: ______________________

## 2. Scope

**In scope**
- Hosts / apps / repos: ______________________
- Environments (e.g. staging only): ______________________
- Accounts / test identities provided: ______________________

**Out of scope**
- Production data exfiltration beyond agreed samples
- Third-party systems not listed above
- Denial-of-service above agreed limits
- Social engineering of non-consenting individuals (unless explicitly approved)
- Physical access (unless explicitly approved)

## 3. Time window

- Start (UTC): __________
- End (UTC): __________
- Allowed hours: __________

## 4. Allowed techniques (check those approved)

- [ ] Reconnaissance on in-scope public surfaces
- [ ] Authenticated application testing with provided credentials
- [ ] Configuration review of in-scope repos/infrastructure-as-code
- [ ] Controlled exploit proof-of-concept on staging
- [ ] Other: ______________________

## 5. Prohibited actions

- Accessing systems outside written scope
- Destroying data or leaving persistent backdoors
- Using findings against third parties
- Sharing credentials or personal data outside the engagement channel

## 6. Stop conditions

Stop and notify emergency contact if:
- Unintended production impact
- Discovery of active exploitation by others
- Exposure of highly sensitive personal data beyond agreed handling

## 7. Data handling

- Evidence stored at: ______________________
- Retention period: ______________________
- Encryption / access control: ______________________

## 8. Reporting

- Format: findings with severity, reproduction steps, impact, remediation
- Draft due: __________
- Final due: __________

## 9. Sign-off

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Authorizing official | | | |
| Red team lead | | | |
