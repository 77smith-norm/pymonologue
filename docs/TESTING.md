# TESTING.md — PyMonologue

## Testing Philosophy

> Unit test everything that CAN be unit tested. Reserve device testing for pieces that genuinely require it.

---

## What Can Be Tested on Mac

### Text Normalizer (`text_normalizer.py`)

Pure Python. No iOS APIs. No network. 100% testable on Mac.

```bash
cd ~/Developer/pymonologue/Pythonista
pytest normalizer_tests.py -v
```

**Test cases:**
- Strip URLs
- Strip phone numbers
- Collapse whitespace
- Collapse repeated filler words (um um um → um)
- Capitalize first letter
- Add period if missing
- Preserve already-capitalized text
- Handle empty string
- Handle single word
- Handle Unicode characters

### Context Tag Parser (`context_tags.py`)

Pure Python. No iOS APIs.

```bash
pytest context_tags_tests.py -v
```

**Test cases:**
- Parse valid tags: `[project:cgmclaw]`, `[task:debug]`, `[priority:urgent]`
- Parse multiple tags: `[project:x][task:y]`
- Reject invalid tags
- Serialize tags to JSON
- Deserialize tags from JSON
- Prepend tag to transcribed text

### Auto Dictionary (`auto_dictionary.py`)

Pure Python.

```bash
pytest auto_dictionary_tests.py -v
```

**Test cases:**
- Suggest new words (capitalized mid-sentence, not in known list)
- Don't suggest known words
- Don't suggest acronyms (all caps)
- Store pending words
- Approve pending words

### UI Layout (Objective-C / Xcode)

Keyboard UI layout can be prototyped in Xcode using `UIInputViewController` in the iOS Simulator. No microphone, no speech recognition — just layout and button interactions.

---

## What Requires On-Device Testing

These three are the **gate** for the entire project. If any fails, development plan changes significantly.

### 1. Does `SFSpeechRecognizer` work via `objc_util` in a Pythonista keyboard?

**How to test:**
1. In Pythonista on iPhone 11 Pro Max, create a test script
2. Use `objc_util` to call `SFSpeechRecognizer`
3. Create a short `.m4a` file (record something via Voice Memos)
4. Call recognizer on the file
5. Check if transcript is returned

**Expected result:** Text transcript of the audio.

**If it fails:** The entire Phase 1 architecture changes. Alternative: investigate using a different transcription approach, or fall back to Approach B (AVAudioEngine streaming).

### 2. Does `sound.Recorder` work in a Pythonista keyboard extension?

**How to test:**
1. Create a minimal Pythonista keyboard script
2. Tap a button → call `sound.Recorder.start()`
3. Tap again → call `sound.Recorder.stop()`
4. Check if a valid `.m4a` file was created

**Expected result:** Valid `.m4a` file at the temp path.

**If it fails:** Keyboard extensions may not have microphone access. Alternative: use `AVAudioEngine` via `objc_util` directly.

### 3. Does `keyboard.insert_text()` work from a Pythonista keyboard?

**How to test:**
1. Open Telegram
2. Switch to PyMonologue keyboard
3. Run `keyboard.insert_text('hello from pymonologue')`
4. Check if text appears in the Telegram text field

**Expected result:** Text appears in the active text field.

**If it fails:** Investigate Pythonista keyboard API limitations. Check if `Full Access` is enabled in iOS Settings.

---

## On-Device Smoke Test Protocol

**Before Phase 1 development continues**, run this sequence on iPhone 11 Pro Max:

```
Day 1: Smoke tests
├── Test 1: SFSpeechRecognizer via objc_util
├── Test 2: sound.Recorder in keyboard context
└── Test 3: keyboard.insert_text()

Day 2: If smoke tests pass
├── Test 4: Full voice → insert loop
└── Test 5: Text appears in Telegram
```

Document all results. If any smoke test fails, stop and reassess before writing more code.

---

## Continuous Integration

### Mac (CI)

```bash
cd ~/Developer/pymonologue/Pythonista
pytest normalizer_tests.py context_tags_tests.py auto_dictionary_tests.py -v
```

### Xcode (ObjC)

Xcode scheme runs XCTest on the Mac (simulator for UI tests, logic tests for normalizer/parser).

---

## Device Testing Checklist

Before each development phase review:

- [ ] SFSpeechRecognizer returns transcript on device
- [ ] sound.Recorder produces valid .m4a on device
- [ ] keyboard.insert_text() works in Telegram
- [ ] Full voice → text → insert loop works end-to-end
- [ ] Context tags are prepended correctly
- [ ] Normalizer output is readable
