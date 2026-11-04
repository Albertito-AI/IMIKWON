# Security and privacy

Use IMIKWON on a trusted local project, preferably a separate Git branch. The model receives the task and explicitly selected source files. The optional self-review sends the first provider response back to that same provider. IMIKWON has no telemetry service and does not receive your key or code through a project-operated server.

Common credential files, private-key patterns, traversal paths, symlinks and hardlinks are blocked. Detection cannot identify every secret, personal record or prompt injection. Review selected files before sending them. Repository content is treated as untrusted task data in the prompt, but that prompt is not a security boundary.

The model can only propose full replacements for the exact selected paths. There is no model shell tool. Applying a downloaded or edited proposal is still an explicit trust decision: inspect the complete diff. Hash checks prevent accidental stale application, not malicious code. Metadata and `.github` writes are excluded in this alpha.

Local checks execute project code with your operating-system permissions. They are not sandboxed. Credential-named environment variables are removed, but tests can still read accessible files, access the network, consume disk space or launch processes. Use an isolated environment for untrusted projects. Windows timeout cleanup does not guarantee termination of descendant processes.

State files are local, use restrictive permissions where supported, and may contain source, absolute paths and test output. Add `.imikwon/` to your project's `.gitignore`. Never commit API keys. Requests use HTTPS and refuse redirects; a custom endpoint receives the supplied key. A timeout can leave a billed request running at the provider.

Application rolls back ordinary I/O failures. Process crashes, power loss and concurrent writers are outside its transaction guarantee. Keep Git history or backups. Do not run overlapping apply operations on the same files.

Report suspected vulnerabilities privately via the contact route on [Albert's website](https://www.alberttansinhon.com/#contact), with a minimal reproduction and no credentials. Public issues should contain only safe, synthetic examples.
