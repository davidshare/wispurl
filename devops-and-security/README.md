## Source control & repository hygiene

- Adopt a branching model (trunk-based or GitHub Flow) with protected main, required PR reviews, and required status checks before merge
- Enforce signed commits and signed tags (GPG/sigstore) and a linear history or squash-merge policy
- Add CODEOWNERS so service/frontend areas require the right reviewers
- Add .gitignore/.dockerignore discipline and a pre-commit secret scan (gitleaks/trufflehog) to keep credentials out of history
- Scan existing git history for already-committed secrets and rotate anything found