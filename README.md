# 🎮 AI Game Studio (Local Autonomous Pipeline)

A **100% free, local, and self-improving AI Game Studio** engineered to eliminate the blank page in game development. This system orchestrates a multi-agent AI workforce on local Linux hardware to autonomously transform a simple text concept into a fully documented Master Game Design Document (GDD), Unity 6 architecture plan, sprite sheet assets, and clean C# codebase in minutes.

---

## ✨ Key Features

* **100% Local & Data Sovereign:** Powered entirely by local LLMs via [Ollama](https://ollama.com/), ensuring zero cloud API costs and total privacy over your intellectual property.
* **Telegram Interface & Access Control:** Remote control your studio via a custom Telegram bot with built-in user authentication (`/newgame`, `/artfix`, and approval workflows).
* **23-Agent Autonomous Pipeline:** Specialized AI agents handle distinct game dev phases—from systems design and physics loops to code review and art direction.
* **Automated Visual QA:** Integrates local vision models (**LLaVA**) to inspect generated sprite anatomy and automatically strip backgrounds using `rembg` for immediate Unity Sprite Editor slicing.
* **Production-Grade Architecture:** Enforces strict game programming standards, including Component-Based Design, Object Pooling, Finite State Machines (FSM), and frame-rate independent physics (`Time.deltaTime`).

---

## 🏗️ System Architecture

The studio operates on a relay-race state machine across distinct phases:

1. **Phase 1: Game Design Document (GDD)** — Collects title, core gameplay loops, environmental constraints, and win/loss conditions.
2. **Phase 2: Technical Architecture** — Maps out C# script decoupling, centralized Input Managers, and primitive collision hierarchies.
3. **Phase 3: Asset Generation & Inspection** — Generates 16-bit/retro sprite assets on solid magenta backgrounds, validated by visual AI agents and processed for transparency.
4. **Phase 4: C# Code Generation** — Writes Unity 6 compatible scripts with zero "God-Classes" and strict separation between `Update()` (visuals/input) and `FixedUpdate()` (physics).

---

## 🛠️ Tech Stack & Requirements

* **OS:** Pop!_OS / Linux (Systemd background service integration)
* **Language:** Python 3.12+ (`pyTelegramBotAPI`, `python-dotenv`, `requests`, `rembg`)
* **Local AI Engine:** Ollama
  * **Code & Logic:** `qwen2.5-coder` / `mistral`
  * **Vision Inspection:** `llava` (7B parameter model optimized for mid-range VRAM)
* **Game Engine Target:** Unity 6 / 2D Arcade Engine

---

## 🚀 Getting Started

### 1. Prerequisites
Ensure Ollama is installed and running locally with the required models pulled:
```bash
ollama pull qwen2.5-coder
ollama pull llava
