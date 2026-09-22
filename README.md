# 🌌 ParaGravity (`pgrav`)

> **Native, non-invasive parallel multi-account & sandbox manager for Google Antigravity.**  
> Run multiple Google Gemini Pro accounts side-by-side in independent, isolated windows on macOS.

English | [简体中文](README_zh.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Platform: macOS](https://img.shields.io/badge/Platform-macOS-lightgrey.svg)]()
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8+-yellow.svg)]()
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)]()

---

## ✨ Key Advantages

- 🚀 **True Parallel Concurrency**: Run multiple Google Gemini Pro accounts side-by-side in separate windows simultaneously without restarting or session switching.
- 🛡️ **100% Non-Invasive**: Built strictly on Chromium/Electron's official `--user-data-dir` sandboxing. Zero binary patching, zero internal database modifications, zero account security risks.
- 🔑 **Native Google OAuth**: Complete, untouched Google Cloud authentication flow. Token refresh and sign-in redirects work seamlessly without proxies or interruptions.
- 🔍 **macOS Native Integration**: Automatically generates independent macOS `.app` bundles with app icons. Launch your instances directly via **Spotlight (`Cmd + Space`)** or Dock.
- ⚡ **Zero-Footprint & Ultra-Lightweight**: No background daemon eating RAM (0 MB idle overhead). Powered purely by macOS native Python 3 with zero external pip or npm dependencies.
- 🗂️ **Total Workspace Isolation**: Each instance maintains completely separated extensions, local storage, indexedDB, and chat histories, preventing workspace contamination.

---

## 🚀 Quick Start

### 1. One-Line Install (Recommended)

```bash
curl -fsSL https://raw.githubusercontent.com/edison-land/paragravity/main/install.sh | bash
```

### 2. Homebrew Tap (Coming Soon)

```bash
brew tap edison-land/tap
brew install paragravity
```

---

## 📖 CLI Usage

> 💡 **Tip**: Both `pgrav` (short) and `paragravity` (full) are registered and ready to use!

### 1. Create an Isolated Profile
Create a new sandbox with a single command:
```bash
pgrav create zwe
```
This instantly:
- Provisions an isolated sandbox at `~/.antigravity-profiles/zwe`
- Generates a native macOS application `Antigravity (zwe).app` in `~/Applications`
- Registers it with macOS LaunchServices for **Spotlight (`Cmd + Space`)** indexing

To launch immediately upon creation:
```bash
pgrav create work --launch
```

### 2. List All Profiles & Status
View all your parallel instances, live process status, and bound Google accounts:
```bash
pgrav list
# or simply:
pgrav ls
```

**Example Output:**
```text
PROFILE            STATUS         PID      ACCOUNT (GOOGLE)               SIZE       DESCRIPTION
───────────────────────────────────────────────────────────────────────────────────────────────
zwe                ● Running      49377    zwe.dev@gmail.com              24.5 MB    Development account
work               ○ Stopped      -        work@company.com               18.2 MB    Company projects
```

### 3. Launch an Instance
```bash
pgrav launch zwe
```
*Or simply press `Cmd + Space` anywhere on your Mac and type `Antigravity (zwe)`!*

### 4. Stop a Running Instance
```bash
pgrav stop zwe
```

### 5. Inspect Profile Details
```bash
pgrav info zwe
```

### 6. Delete a Profile
```bash
pgrav delete zwe
```

---

## 🏗️ Technical Architecture

ParaGravity achieves completely clean, isolated execution through three native mechanisms:

```text
┌──────────────────────────────────────────────────────────────┐
│                    macOS Host Environment                    │
│                                                              │
│  [Official App]          [Profile A: zwe]    [Profile B: work]
│  /Applications/          ~/.antigravity-     ~/.antigravity- 
│  Antigravity.app         profiles/zwe        profiles/work   
│  (washingshop account)   (zwe account)       (work account)  
│                                                              │
│  ├── default Library/    ├── data/           ├── data/       
│  └── default Keychain    └── home/           └── home/       
│                              ├── .gemini/        ├── .gemini/
│                              └── isolated        └── isolated
│                                  tokens              tokens  
└──────────────────────────────────────────────────────────────┘
```

1. **Storage Sandboxing (`--user-data-dir`)**: Each profile maintains its own Chromium partition, SQLite databases, IndexedDB, extensions, and workspace state.
2. **Environment & Keychain Isolation (`SSH_CONNECTION=1`)**: Electron/Language Server automatically falls back to file-based token storage within the profile's isolated directory, preventing keychain contention with the host instance.
3. **Native macOS Application Bundles**: Every profile has a dedicated `.app` bundle registered in `~/Applications`, making Antigravity multi-instance a first-class citizen in macOS.

---

## 🤝 Contributing

Contributions are warmly welcomed! Please feel free to submit an Issue or Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

Distributed under the MIT License. See [`LICENSE`](LICENSE) for more information.

---

## ⚠️ Disclaimer

ParaGravity is an open-source utility that leverages standard Chromium command-line options. It is not affiliated with, sponsored by, or endorsed by Google LLC. All trademarks belong to their respective owners.
