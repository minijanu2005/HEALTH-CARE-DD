# Security and limitations

## Implemented (prototype)

- Argon2 password hashing
- Server-side role checks in services
- Session expiration (`SESSION_TIMEOUT_MINUTES`)
- Sync API key header (`X-Sync-Api-Key`)
- Audit logging (no passwords or tokens)
- Input validation on backend
- Environment-based secrets (`.env`)

## Not claimed

- HIPAA / regulatory compliance
- Production hardening
- HTTPS termination (use reverse proxy in real deployments)
- CSRF tokens (Streamlit has its own session model; full CSRF analysis needed for custom APIs)

## Real healthcare deployment would also need

- Encryption at rest and in transit
- Access reviews and break-glass procedures
- Monitoring, alerting, and incident response
- Formal penetration testing
- Data retention and privacy policies
- Qualified clinical workflows and human oversight

Use **fictional data only** in this college project.
