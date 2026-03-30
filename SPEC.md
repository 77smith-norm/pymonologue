# PyMonologue Phase 1

Full idea doc: `/Users/norm/.openclaw/workspace/ideas/monologue-pythonista.md`

## Goal

Build a complete Phase 1 skeleton for device smoke testing on Russell's iPhone 11 Pro Max:

- [ ] Xcode host app + keyboard extension skeleton
- [ ] Objective-C text normalizer
- [ ] Objective-C context tag parser
- [ ] Objective-C speech recognizer stub
- [ ] Objective-C keyboard UI skeleton
- [ ] XCTest coverage for normalizer + tags
- [ ] Pythonista keyboard UI skeleton
- [ ] Pythonista UI components

## Critical Smoke Tests

These cannot be verified on Mac. Run them on iPhone 11 Pro Max in this order.

1. `SFSpeechRecognizer` via `objc_util` inside a Pythonista keyboard
   - Open Pythonista on device.
   - Create a tiny keyboard test script that calls `SFSpeechRecognizer` on a known `.m4a` file.
   - Confirm a transcript comes back from the keyboard context.
   - If this fails, stop. The Phase 1 architecture changes.

2. `sound.Recorder` inside a Pythonista keyboard
   - In the keyboard context, start recording to a temp `.m4a`.
   - Stop recording and verify the file exists and is valid.
   - If this fails, stop. The recording strategy changes.

3. `keyboard.insert_text()` from a Pythonista keyboard
   - Open Telegram or Notes on device.
   - Switch to the PyMonologue keyboard.
   - Insert a known string such as `hello from pymonologue`.
   - Confirm the text appears in the active text field.

## Keyboard Layout

```text
+-----------------------------------------------------------+
| [TAGS]                                         .  ,  ?  ! '| 
|                                                           |
|                    [    TAP TO TALK    ]                  |
|                                                           |
| [ABC]                    [      M      ]          [return]|
+-----------------------------------------------------------+
```
