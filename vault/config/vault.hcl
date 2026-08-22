# Raft integrated storage — the current HashiCorp-recommended backend
# for all deployments including single-node local setups.

storage "raft" {
  path    = "/vault/data"
  node_id = "vault-node-1"
}

# TLS listener — even with self-signed certs this is the right approach.
# Services connect to https://vault:8200 with VAULT_SKIP_VERIFY=true
# or by mounting the CA cert.
listener "tcp" {
  address       = "0.0.0.0:8200"
  tls_cert_file = "/vault/tls/vault-cert.pem"
  tls_key_file  = "/vault/tls/vault-key.pem"
}

# These must match the hostname Docker Compose resolves Vault as.
# "vault" is the service name in docker-compose.yml.
api_addr     = "https://vault:8200"
cluster_addr = "https://vault:8201"


# How long a secret lease lasts before Vault revokes it.
# 7 days default, 30 days max. Tune per secret if needed.
default_lease_ttl = "168h"
max_lease_ttl     = "720h"

# Enable the web UI — useful for inspecting secrets and policies.
ui = true
disable_mlock = true   # Required for stable Raft operation in Docker

