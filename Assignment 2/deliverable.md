# Workshop 2: Security Weakness Identification with Bandit

This is the deliverable for Assignment 2. Also available as `deliverable.txt`.

**Course:** COMP 5710 - Software Quality Assurance
**Date:** February 9, 2026

## Overview

Bandit, a static analysis tool for Python, was run recursively against all Python files extracted from `workshop2.zip`. The scan covered 3,401 lines of code and identified 52 total security issues.

## Three Most Frequent Security Weaknesses

### 1. B101: Use of `assert` (30 occurrences)
- **CWE:** CWE-703 (Improper Check or Handling of Exceptional Conditions)
- **Severity:** Low | **Confidence:** High
- **Description:** The use of `assert` statements was detected throughout the codebase. When Python is run with optimization flags (`-O`), all `assert` statements are stripped from the bytecode. If `assert` is used to enforce security checks or validate important conditions, those checks will silently disappear in production, potentially leaving the application vulnerable.

### 2. B311: Use of `random` Module (7 occurrences)
- **CWE:** CWE-330 (Use of Insufficiently Random Values)
- **Severity:** Low | **Confidence:** High
- **Description:** The standard `random` module was used for pseudo-random number generation. This module is not cryptographically secure and should not be used for security-sensitive purposes such as generating tokens, passwords, or cryptographic keys. The `secrets` module or `os.urandom()` should be used instead for security-critical randomness.

### 3. B614: Unsafe PyTorch Load (5 occurrences)
- **CWE:** CWE-502 (Deserialization of Untrusted Data)
- **Severity:** Medium | **Confidence:** High
- **Description:** The `torch.load()` function uses Python's `pickle` module under the hood to deserialize model files. Loading a maliciously crafted file with `torch.load()` can result in arbitrary code execution. The safer alternative is to use `torch.load()` with `weights_only=True` or use `safetensors` format for model storage.

## Summary Table

| Rank | Weakness ID | Description | Count | Severity |
|------|------------|-------------|-------|----------|
| 1 | B101 | assert_used | 30 | Low |
| 2 | B311 | random (blacklist) | 7 | Low |
| 3 | B614 | pytorch_load | 5 | Medium |
