# .NET: fast verify with a single-class test filter

**Summary**: To verify a change quickly in a multi-project .NET solution, run one test project with `--filter` targeting a single class instead of the whole suite.

**Type**: experience / verifier

**Stacks**: dotnet, xunit

**Provenance**: ExampleApp @ working tree (main), verified via `dotnet test … --filter "FullyQualifiedName~ExampleUnitTests"` → 21/21 green in 547 ms (2026-06-18).

**Confidence**: high

**Last updated**: 2026-06-18

---

## Context

A large solution's full `dotnet test` restores and builds many projects and runs
all classes — too slow for a tight spec→verify loop. You want the fastest check
that still proves one acceptance criterion.

## Insight / Recipe

- Target the **test project** directly and filter to one class:
  `dotnet test <Tests>.csproj --filter "FullyQualifiedName~<TestClass>"`.
- `~` is "contains", so a class name (or namespace fragment) is enough; no need for
  the fully-qualified name.
- The first run still restores + builds dependencies (unavoidable); subsequent runs
  are fast. Add `--nologo` to trim banner noise.
- Pick a **pure-logic** class for the smoke check (math/parsing), not one needing
  external services — keeps it hermetic and avoids touching live systems.

## Evidence

On ExampleApp, `--filter "FullyQualifiedName~ExampleUnitTests"` built the dependency
chain and ran 21 tests green in 547 ms, vs. building+running all ~20 classes.

## Related pages

- [[appdata-config-local-override]]
