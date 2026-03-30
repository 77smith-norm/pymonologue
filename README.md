# PyMonologue

A voice-first custom keyboard for iOS, built in Pythonista 3. Tap to talk — transcribed text appears in any app. Primary use case: talking to Norm via Telegram.

**Reference app:** [Monologue](https://www.monologue.to/)

## Architecture

Two voice input approaches:

- **Phase 1 (Approach A):** File-based recording → `sound.Recorder` → `.m4a` → `SFSpeechRecognizer` → `keyboard.insert_text()`
- **Phase 4 (Approach B):** True streaming → `AVAudioEngine` → `SFSpeechAudioBufferRecognitionRequest` → real-time partial results

See [SPEC.md](./SPEC.md) for the full specification.

## Project Structure

```
pymonologue/
├── ObjC/                    # Xcode project (Mac unit testing)
│   ├── PyMonologue/         # iOS framework / ObjC wrappers
│   └── PyMonologueTests/    # XCTest unit tests
├── Pythonista/              # Pythonista keyboard scripts
│   ├── pymonologue_keyboard.py  # Main entry point
│   ├── speech_recognizer.py     # SFSpeechRecognizer (file-based)
│   ├── text_normalizer.py        # Regex cleanup
│   ├── context_tags.py            # Tag system
│   ├── auto_dictionary.py        # Custom vocabulary
│   └── ui/                       # ui.View components
├── docs/
│   └── TESTING.md
├── SPEC.md                 # Full specification
├── LICENSE                 # MIT, Russell Dillin 2026
└── AGENTS.md               # For coding agents
```

## Development Phases

| Phase | Goal |
|---|---|
| Phase 1 | Core loop: voice → transcript → insert. File-based. |
| Phase 2 | Context tags + auto dictionary |
| Phase 3 | Slash commands + Monologue-style UI polish |
| Phase 4 | Streaming (Approach B) for lower latency |

## Key Smoke Tests (Device Required)

These must be tested on iPhone 11 Pro Max before any other development:

1. Does `SFSpeechRecognizer` work via `objc_util` in a Pythonista keyboard?
2. Does `sound.Recorder` capture usable audio?
3. Does `keyboard.insert_text()` insert text into Telegram?

Everything else is assembly once those three are confirmed.

## Setup

1. Install Pythonista 3 on iPhone 11 Pro Max
2. Add PyMonologue keyboard in iOS Settings → Keyboards → Add New Keyboard → Pythonista
3. Enable Full Access (required for file I/O)
4. Copy `Pythonista/` scripts to Pythonista's scripts directory
5. Switch to PyMonologue keyboard in any app using the Globe key

## License

MIT — Russell Dillin, 2026.
