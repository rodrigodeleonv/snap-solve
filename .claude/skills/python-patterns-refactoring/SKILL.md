---
description: >
  Apply when writing, reviewing, or refactoring Python code that involves
  interfaces, design patterns, or class hierarchies. Triggers on keywords
  such as: refactor, design pattern, Protocol, ABC, interface, Strategy,
  Factory, Registry, clean up, simplify, restructure, class hierarchy.
---

# Python Patterns & Refactoring Conventions

## Interfaces: Protocol vs ABC

Prefer `Protocol` (structural typing) over `ABC` (nominal typing) as the
default choice for defining interfaces. Always have concrete classes
**explicitly inherit** from the Protocol to keep IDE navigation and intent
clear.

Use `ABC` when it is genuinely a better fit:
- The interface carries **shared implementation** (concrete methods on the base)
- **Runtime `isinstance()` checks** are required without `@runtime_checkable`
- The hierarchy is intentionally **nominal** (an `Animal` truly *is-a* `Animal`,
  not just something that happens to have the same methods)
- A **framework or library** expects ABC subclasses explicitly

When in doubt, ask: *does the base class add behaviour, or only define a
contract?* If only a contract → `Protocol`. If behaviour → `ABC`.

### Pattern

```python
from typing import Protocol

class MyProtocol(Protocol):
    def my_method(self, arg: SomeType) -> ReturnType:
        ...

# Explicit inheritance kept for IDE support and readability
class ConcreteImpl(MyProtocol):
    def my_method(self, arg: SomeType) -> ReturnType:
        ...
```

## Design Patterns in use

### Strategy + Registry
Used in `src/ai_client.py` for AI providers. Add a new provider by:
1. Implementing `Provider` protocol
2. Adding one entry to `_REGISTRY`

```python
_REGISTRY: dict[str, type[Provider]] = {
    "claude": ClaudeProvider,
    "openai": OpenAIProvider,
    "groq":   GroqProvider,
}
```
