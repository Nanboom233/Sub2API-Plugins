# Research: Embedded JavaScript Runtime

- Query: Verify a minimal pure-Go JavaScript runtime and API for API-key quota scripts in the Linux CGO-disabled server build.
- Scope: external primary source with local toolchain comparison
- Date: 2026-10-26

## Findings

### Recommendation

Use `github.com/dop251/goja`. Do not add `goja_nodejs`. Create a new `goja.Runtime` for each query. Pass account data with `Runtime.Set` or `Runtime.ToValue`. Expose one synchronous Go HTTP function. JavaScript calls `queryQuota(ctx)`. The `ctx` object holds account data only. The Go callback captures the Go request context. Do not expose Go's `context.Context` to JavaScript. Do not insert credentials into script source.

This design stays in the existing Go executable and does not require CGO or a separate Node process. The upstream quota plugin already owns HTTP transport, URL policy, proxy, TLS, response bounds, and timeouts. A Go callback can reuse those owners.

### Version and build fit

The Go module proxy reports Goja pseudo-version `v0.0.0-20261024144015-2a9269b6b6de`, from commit `2a9269b6b6de531323ed60aa88e6c318ddb0ebed`, dated 2026-10-24. The pinned module declares `go 1.26.0`. The Sub2API source used by the existing build declares `go 1.27.3`, so this pin fits the target toolchain. Goja implements JavaScript in pure Go, so it supports the existing `CGO_ENABLED=0` build. It has no semantic-version tags; pin the pseudo-version rather than `@latest`.

The module declares an MIT license. Its original license includes copyright notices for Dmitry Panov (2016) and Robert Krimen (2012). The plugin must carry that original text in `licenses/`. The pinned `go.mod` also declares `regexp2/v2`, `x/text`, and other modules. Include the original license texts for dependencies present in the built dependency inventory. Do not treat Goja's MIT license as covering its dependencies.

External references: [Go module proxy record for the pinned version](https://proxy.golang.org/github.com/dop251/goja/@v/v0.0.0-20261024144015-2a9269b6b6de.info), [pinned go.mod](https://github.com/dop251/goja/blob/2a9269b6b6de531323ed60aa88e6c318ddb0ebed/go.mod), [pinned LICENSE](https://github.com/dop251/goja/blob/2a9269b6b6de531323ed60aa88e6c318ddb0ebed/LICENSE), and [upstream README](https://github.com/dop251/goja/blob/2a9269b6b6de531323ed60aa88e6c318ddb0ebed/README.md#L8-L13).

### Execution API

The public API supports the minimum invocation flow:

1. Create a runtime with `goja.New()`.
2. Expose values and the HTTP callback with `vm.Set(name, value)`. `Runtime.ToValue` converts Go values to JavaScript values.
3. Execute source with `vm.RunString(source)`. It returns parse or execution errors.
4. Load the named function with `goja.AssertFunction(vm.Get("queryQuota"))`.
5. Call it with `callable(goja.Undefined(), vm.ToValue(ctx))`, where `ctx` contains account data only.
6. Read only the plugin's known output fields and validate their types and values.

`Runtime.Set` accepts a Go function. The runtime wraps the function as a JavaScript callable. A Go callback with a trailing `error` return turns failures into JavaScript exceptions. This supports a synchronous `http.request(request)` callback without adding a network API to the JavaScript runtime. `Value.Export()` and `Runtime.ExportTo()` are available, but exporting an arbitrary object is unnecessary when the plugin accepts only named quota fields.

External references: [README value passing, export, and function invocation](https://github.com/dop251/goja/blob/2a9269b6b6de531323ed60aa88e6c318ddb0ebed/README.md#L109-L189), [`Runtime.ToValue`](https://github.com/dop251/goja/blob/2a9269b6b6de531323ed60aa88e6c318ddb0ebed/runtime.go#L1868-L1869), [`Runtime.Set`](https://github.com/dop251/goja/blob/2a9269b6b6de531323ed60aa88e6c318ddb0ebed/runtime.go#L2485-L2493), and [host function conversion](https://github.com/dop251/goja/blob/2a9269b6b6de531323ed60aa88e6c318ddb0ebed/runtime.go#L2124-L2135).

### Limits and cancellation

`Runtime.Interrupt(value)` stops JavaScript execution. It returns an `*InterruptedError` from the active Go call. It does not stop a native Go function. Use the shared ten-second Go request context for both script execution and HTTP. A watchdog can call `Interrupt` when that context ends. The synchronous HTTP callback must use the same context so cancellation also stops I/O.

Therefore the host `http.request` callback must use an HTTP request context with a deadline. It must use the existing upstream transport and URL checks. A VM interrupt cannot abort a blocked callback. Keep the JavaScript evaluation and callback on the same goroutine. Goja runtimes are not goroutine-safe.

`SetMaxCallStackSize(int)` limits call depth. It does not bound overall heap use. Goja has no per-runtime memory limit. Its maintainer says that there is no practical way to add one in Go. A script can allocate enough memory to exhaust the server process. `Interrupt` and a stack limit do not prevent that failure.

The engine supports promises, but core Goja does not provide an event loop to process jobs. `setTimeout` and `setInterval` are not included. A synchronous quota contract avoids adding `goja_nodejs` or an event loop. Require a synchronous `queryQuota` result. Do not use `async`, promises, timers, Node modules, or `require`.

External references: [README runtime concurrency and event-loop behavior](https://github.com/dop251/goja/blob/2a9269b6b6de531323ed60aa88e6c318ddb0ebed/README.md#L69-L81), [README interruption example](https://github.com/dop251/goja/blob/2a9269b6b6de531323ed60aa88e6c318ddb0ebed/README.md#L277-L300), [`Interrupt` native-call limitation](https://github.com/dop251/goja/blob/2a9269b6b6de531323ed60aa88e6c318ddb0ebed/runtime.go#L1570-L1587), [`SetMaxCallStackSize`](https://github.com/dop251/goja/blob/2a9269b6b6de531323ed60aa88e6c318ddb0ebed/runtime.go#L2532-L2538), and [maintainer reply on memory limits](https://github.com/dop251/goja/discussions/646).

## Planning Consequence

Goja is the chosen dependency for synchronous administrator-authored JavaScript in this executable.
Its missing memory cap is the material risk. Scripts can exhaust the server process memory despite the HTTP callback boundary.
Treat script editing as an administrator capability.
Keep the ten-second shared deadline, bounded HTTP response, and native URL/proxy/TLS rules.
The latest user correction requires visible custom-script errors during refresh and testing. Default-query failures remain silent.

## Files Found

- `plugins/sub2api-quota-extension/patches/quota-extension.patch`: Existing upstream quota query, URL validation, transport, and native result mapping.
- `plugins/sub2api-quota-extension/tests/test_upstream_quota_test.go`: Flat Go tests for single and batch quota reads and silent failures.
- `.trellis/spec/backend/api-key-quota.md`: Existing quota fields, transport rules, response bounds, and failure behavior.

## Code Patterns

- `plugins/sub2api-quota-extension/patches/quota-extension.patch:90`: The response parser validates the upstream result before it maps native quota fields.
- `plugins/sub2api-quota-extension/patches/quota-extension.patch:166`: The HTTP query validates the target and reuses the account key, proxy, transport profile, and TLS profile.
- `plugins/sub2api-quota-extension/tests/test_upstream_quota_test.go:82`: One test covers the existing single and batch account usage entry points.

## Related Specs

- `.trellis/spec/backend/api-key-quota.md`
- `.trellis/spec/backend/minimal-linux-delivery.md`
- `.trellis/spec/backend/quality-guidelines.md`
- `.trellis/spec/backend/directory-structure.md`

## Caveats / Not Found

- No per-runtime Goja memory quota exists in the inspected upstream revision.
- `SetMaxCallStackSize` bounds recursive call depth, not all memory allocation.
- No code was installed, compiled, or executed during this research.
