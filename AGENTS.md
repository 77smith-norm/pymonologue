# AGENTS.md — PyMonologue

**Context:** You are working on PyMonologue, a voice-first custom keyboard for iOS built in Pythonista 3. The primary user is Russell Dillin.

## Key References

- **Full spec:** `SPEC.md` (this directory)
- **Idea doc:** `~/Developer/norman-world/` (Norman's workspace) — actually at `~/.openclaw/workspace/ideas/monologue-pythonista.md`
- **Pythonista keyboard docs:** https://omz-software.com/pythonista/docs-3.4/py3/ios/keyboard.html
- **objc_util docs:** https://omz-software.com/pythonista/docs-3.4/py3/ios/objc_util.html
- **Reference app:** Monologue — https://www.monologue.to/

## Important Constraints

### Voice Input Approach

- **Phase 1:** File-based. `sound.Recorder` → `.m4a` file → `SFSpeechRecognizer` (file URL API). Simple, reliable.
- **Phase 4 (future):** True streaming. `AVAudioEngine` → `SFSpeechAudioBufferRecognitionRequest`. Lower latency. More complex. Do NOT implement streaming in Phase 1 unless specifically asked.

### Platform Limitations

- **Must test on device:** `SFSpeechRecognizer` and `sound.Recorder` cannot be tested in macOS Simulator. Must use iPhone 11 Pro Max.
- **Keyboard sandbox:** Pythonista keyboard runs in a sandboxed extension context. Some APIs may not work as in the main app.
- **Memory limits:** Keyboards have tighter memory budgets. Keep audio buffers small.
- **Simulator testing:** Only UI layout, text processing logic, and keyboard API calls (without mic/audio) can be tested in simulator.

## Voice Keyboard Core Loop (Phase 1)

```
1. User taps 🎤 button
2. sound.Recorder.start() → records to temp .m4a file
3. User taps 🎤 again → sound.Recorder.stop() → returns file path
4. SFSpeechRecognizer (via objc_util) → transcribes .m4a file
5. text_normalizer.normalize() → basic cleanup
6. context_tags.prepend() → add current tag
7. keyboard.insert_text() → type into active app
```

## Text Normalizer Rules (Phase 1)

The normalizer is pure Python — no iOS APIs, no network. Unit testable on any platform.

```
- Strip URLs (https?://\S+)
- Strip phone numbers (\b\d{3}[-.]?\d{3}[-.]?\d{4}\b)
- Collapse whitespace (\s+ → single space)
- Collapse repeated filler words (um um → um)
- Capitalize first letter
- Add period if missing at end
```

## Context Tags

Format: `[project:name]`, `[task:name]`, `[priority:level]`

Storage: JSON in Pythonista documents directory.

## UI Style

Match Monologue:
- Dark background (#000000 to #1a1a1a)
- Teal accent (#00d4aa)
- White text
- Large centered voice button
- Minimal punctuation row: . , ? ! '

## Development Principles

1. **Test what can be tested on Mac.** Text normalizer, tag parser, UI layout — all unit-testable without a device.
2. **Smoke test on device before building further.** If `SFSpeechRecognizer` doesn't work in the keyboard context, the whole project changes.
3. **Keep Phase 1 simple.** Get voice → insert working first. Polish comes later.
4. **No API calls for delivery.** The keyboard types text. It does not POST anywhere.

## Owner

Russell Dillin (rastreus) — norman.dillin@icloud.com
