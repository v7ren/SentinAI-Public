# Overview

SentinAI v4 is an AI-powered SAST tool with a multi-agent pipeline. Before main scanning, Recon, Pattern, and Threat Model agents build context (call graph, dependencies, sanitizer registry, dead code). Six specialist agents (Injection, Auth, Crypto, Cipher design, Logic, Config) run in parallel, then findings go through deduplication, consensus scoring, and Skeptic adversarial validation.
