# Installer terminal component

## Decision and scope

Use `github.com/pterm/pterm` at the observed stable release `v0.12.84`.
It supplies inline selection, text input, confirmation, and timed spinners without an application model or full-screen view.
Keep the installation transaction and its existing error owner.
Keep the existing text reader for plain interaction.
Use one small Go message catalog for Simplified Chinese and English.

The review date is 2026-11-04.
The latest-release APIs identified PTerm `v0.12.84` and Huh `v2.0.3` as stable releases. [S1–S2]
Their pinned module files require Go 1.26.0 and Go 1.25.8, respectively. [S3–S4]
The existing build workflow selects Go 1.27.3, which satisfies both requirements.
No build, terminal session, dependency installation, or runtime test ran during this review.

## Two suitable directions

| Need | PTerm v0.12.84 | Huh v2.0.3 with its Bubble Tea runtime |
| --- | --- | --- |
| Select, input, confirm | `DefaultInteractiveSelect`, `DefaultInteractiveTextInput`, `DefaultInteractiveConfirm` | `NewSelect`, `NewInput`, `NewConfirm`, within `NewForm` |
| Unknown-duration progress | `DefaultSpinner`, `WithShowTimer`, `UpdateText`, `Stop` | `spinner.New`, `ActionWithErr`, `Context`, `Run` |
| Inline rendering | Independent printers. No application model needed | Standalone forms and spinner work without a custom full-screen model |
| Cancellation | Set every prompt's `WithOnInterruptFunc`. Return cancellation through the existing transaction | Forms expose `RunWithContext` and `ErrUserAborted` |
| Plain streams | Caller must retain the text path and avoid interactive printers | Caller must retain the text path. Accessible spinner output still uses cursor escapes |
| Chinese width | Uses `go-runewidth.StringWidth` for display-width calculations | Uses Lip Gloss and ANSI width/wrapping helpers |
| Windows | Keyboard dependency has Windows console input. Color code enables virtual terminal processing | Bubble Tea runtime and its Windows dependencies provide platform handling |

PTerm fits the existing sequential installer with less integration work.
Huh has a cleaner context-aware form API, but the installer does not need its grouped-form model.
Its spinner also lacks PTerm's ready-made elapsed timer.
Neither library's generic fallback replaces the existing plain interaction contract. [S5–S10]

## Concrete PTerm use

Use `DefaultInteractiveSelect.WithOptions(...).WithFilter(false)` for the installation form and target.
Include each existing numeric identifier in its option label.
Keep the number-to-target mapping in the installer. Enter confirms the highlighted entry.
Use `DefaultInteractiveTextInput.WithDefaultValue(...)` for the native path and application address.
Supply all prompt text and validation explanations from the Go catalog. [S5–S6]

For dynamic version confirmation, use `DefaultInteractiveConfirm.WithDefaultValue(false)`.
Its source accepts the first character of `ConfirmText` or `RejectText` and treats Enter as the default value.
Localized labels can start with literal `Y` and `N`, such as `Y 继续` and `N 取消`.
This retains explicit acceptance and default refusal without another confirmation screen. [S7]

Plain confirmation must retain the existing complete-line parser.
Only trimmed, case-insensitive `y` or `yes` continues.
Blank input, refusal, EOF, and interruption cancel.
PTerm's one-key confirmation API does not implement that complete-line contract.
Do not route plain confirmation through it.

Use `DefaultSpinner.WithShowTimer(true).WithWriter(os.Stdout).Start(stage)` during a long operation.
Update its short stage text through `UpdateText` when actual state changes.
Call `Stop` before any question, manual stop/start instruction, stable result, or raw diagnostic.
`Stop` signals the animation goroutine and waits for it to finish. [S8]
Then print the durable status through the existing output owner.
Do not print an error through both `spinner.Fail(err)` and the transaction error path.
The spinner does not own command execution, cancellation, rollback, or readiness decisions.

## Ctrl-C must return to recovery

PTerm's default prompt interrupt path calls `Exit(1)`, which defaults to `os.Exit`. [S11]
Therefore, set `WithOnInterruptFunc` on every interactive select, input, and confirm instance.
The callback must record or request cancellation in the existing installation context.
It must not print the transaction error, call `os.Exit`, or run rollback itself.

On Ctrl-C, the prompt stops the keyboard listener and completes its deferred terminal cleanup before the callback returns control. [S5–S7, S12]
After `Show` returns, check cancellation before its result or ordinary error.
Discard the result on cancellation. A select can still return its highlighted value with a nil error.
Return cancellation to the existing transaction so its separate restoration context remains responsible for rollback.
During spinner-only operations, retain the existing signal/context handling and stop the spinner before recovery output.

PTerm does not expose a prompt `RunWithContext` API.
The callback solves keyboard Ctrl-C. Do not claim that it supplies arbitrary asynchronous context cancellation inside a prompt.
Its select printer also prints a keyboard-listener startup error before returning it.
Avoid replaying that same detail through another error owner. [S5]
Captured external command diagnostics remain unchanged and print once after dynamic rendering stops.

## Capability checks and output routing

Use the existing streams to decide the presentation before constructing interactive printers.
Dynamic prompts need actual terminal stdin and stdout, rather than an arbitrary reader or writer.
`golang.org/x/term.IsTerminal` supplies that check and is already a PTerm dependency. [S3, S13]
Use the plain path for redirected streams, synthetic test streams, or `TERM=dumb`.
Do not probe redirected stdin through a keyboard listener or reopen another terminal for plain input.

PTerm's text-input cursor area uses stdout directly.
Its global `SetDefaultOutput` does not redirect every cursor operation. [S6, S14]
Use real stdin/stdout for the dynamic path and the existing injected reader/writer for the plain path.
The spinner supports an explicit writer. Keep it on the same terminal output.
Do not replace process-global `os.Stdin` or `os.Stdout` to adapt a printer.

PTerm's `DisableStyling` is not a substitute for this branch.
Interactive printers still use cursor and keyboard operations.
Keep plain prompts and sequential lines free of animation and cursor controls.
Color support is separate: PTerm honors `NO_COLOR`, `TERM=dumb`, and Windows console support. [S15]
Do not force color back on.

Chinese width uses the library's existing width helper. Do not add a second width calculator. [S9]
Windows input uses `CONIN$`, and color support attempts to enable virtual terminal processing. [S12, S15]
These source paths establish platform support, not a completed runtime test in this repository.
Unsupported terminal capabilities retain the plain path.

## Language and dependency boundary

The latest user decision selects language from terminal locale variables only.
Use the first nonempty value in `LC_ALL`, `LC_MESSAGES`, then `LANG`.
Chinese locale values select Simplified Chinese.
Other values, absent values, `C`, and `POSIX` select English.
A nonempty `LC_ALL=C` therefore overrides `LANG=zh_CN.UTF-8` and selects English.

Keep catalog strings in Go and retain literal commands, paths, identifiers, versions, and external diagnostics.
No language menu, in-session switch, locale helper, Windows system-language lookup, argument, or configuration file is needed.
No translation framework or external translation resource is needed.

Prepare the pinned PTerm dependency in the existing temporary installer module at build time.
The installed binary needs no Go runtime or dependency download on the user's machine.
PTerm is MIT, with the original notice `Copyright (c) 2020 pterm`. [S16]
Retain its original license and relevant dependency license texts through the existing license collection.
Do not change their attribution or create a separate notice manifest.

## Sources

- S1. [Observed PTerm stable release](https://api.github.com/repos/pterm/pterm/releases/latest), published 2026-10-10.
- S2. [Observed Huh stable release](https://api.github.com/repos/charmbracelet/huh/releases/latest), published 2026-03-10.
- S3. [PTerm pinned module](https://github.com/pterm/pterm/blob/v0.12.84/go.mod).
- S4. [Huh pinned module and stable import path](https://github.com/charmbracelet/huh/blob/v2.0.3/go.mod).
- S5. [PTerm select and interrupt hook](https://github.com/pterm/pterm/blob/v0.12.84/interactive_select_printer.go).
- S6. [PTerm text input, defaults, and cursor area](https://github.com/pterm/pterm/blob/v0.12.84/interactive_textinput_printer.go).
- S7. [PTerm confirmation keys, defaults, and interrupt hook](https://github.com/pterm/pterm/blob/v0.12.84/interactive_confirm_printer.go).
- S8. [PTerm spinner timer, text updates, and synchronized stop](https://github.com/pterm/pterm/blob/v0.12.84/spinner_printer.go).
- S9. [PTerm Chinese display-width helper](https://github.com/pterm/pterm/blob/v0.12.84/internal/max_text_width.go).
- S10. Huh [form context and errors](https://github.com/charmbracelet/huh/blob/v2.0.3/form.go), [select width](https://github.com/charmbracelet/huh/blob/v2.0.3/field_select.go), and [spinner behavior](https://github.com/charmbracelet/huh/blob/v2.0.3/spinner/spinner.go).
- S11. PTerm [deferred interruption](https://github.com/pterm/pterm/blob/v0.12.84/internal/cancelation_signal.go) and [default exit](https://github.com/pterm/pterm/blob/v0.12.84/internal/exit.go).
- S12. PTerm's keyboard dependency [listener cleanup](https://github.com/atomicgo/keyboard/blob/v0.2.10/keyboard.go) and [Windows input](https://github.com/atomicgo/keyboard/blob/v0.2.10/tty_windows.go).
- S13. [Go terminal detection API](https://pkg.go.dev/golang.org/x/term#IsTerminal).
- S14. [PTerm default output and printing](https://github.com/pterm/pterm/blob/v0.12.84/print.go).
- S15. PTerm [color decisions](https://github.com/pterm/pterm/blob/v0.12.84/color.go) and [Windows virtual terminal support](https://github.com/pterm/pterm/blob/v0.12.84/internal/color/console_windows.go).
- S16. [Original PTerm license](https://github.com/pterm/pterm/blob/v0.12.84/LICENSE).
