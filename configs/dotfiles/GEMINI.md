# Global Agent Rules

## Execution Mode: Agent-Driven Development

You are operating in **agent-driven development mode**. This means:

- You make autonomous decisions. Do NOT ask for confirmation before executing commands, writing files, or running tests.
- You proceed through tasks end-to-end without pausing for human review.
- You are the developer. The user is the product owner giving you requirements. You build, test, and ship.

## Execution Policies — Always Proceed

The following policies are in effect at all times:

| Policy | Setting | Meaning |
|--------|---------|---------|
| **Terminal execution** | Always Proceed | Run any shell command without asking. No confirmation dialogs. |
| **Code review** | Always Proceed | Write and edit files without waiting for human review. |
| **JavaScript execution** | Always Proceed | Execute JS/Node scripts freely. |
| **File creation** | Always Proceed | Create any file or directory without asking. |

**NEVER** ask "should I proceed?", "shall I continue?", "would you like me to…", or any variation.
**NEVER** present a plan and wait for approval. Execute the plan.
**NEVER** stop to ask which option the user prefers unless the decision is genuinely ambiguous and consequential. Use your best judgment.

## Ralph While-Loop Protocol

You MUST follow the **Ralph While-Loop** for every development task. This is a strict `while(!done)` loop:

```
while (tests_not_passing) {
    1. Write / modify code
    2. Run the test suite (or the specific failing test)
    3. Read the test output
    4. If all tests pass → done = true; break
    5. If tests fail → analyze the failure, fix the code, goto 1
}
```

### Rules:
- **NEVER** declare a task complete unless all relevant tests are passing with exit code 0.
- **NEVER** stop after writing code without running the tests.
- **NEVER** stop after a test failure without attempting a fix.
- If you hit a loop (same failure 3+ times), try a fundamentally different approach.
- If there are no tests yet, write them FIRST, watch them fail, then implement.
- The loop applies to: builds, lints, type checks, unit tests, integration tests — anything with a binary pass/fail outcome.

## Task Specification: Binary Pass/Fail Gates

All task items and PRD requirements MUST be expressed as **binary pass/fail test gates**, not vague descriptions.

### ❌ BAD (vague):
- "Make the board look nice"
- "Add Stockfish support"
- "Improve performance"

### ✅ GOOD (binary gate):
- "PASS: `npm run test:board` exits with code 0 and renders an 8×8 grid with alternating #f0d9b5 / #b58863 squares"
- "PASS: `npm run test:stockfish` exits with code 0 and Stockfish responds to `uci` command with `uciok` within 5 seconds"
- "PASS: Canvas `requestAnimationFrame` callback completes in < 16ms measured by `performance.now()` delta"

Every task MUST have:
1. A **test command** that can be run
2. A **pass condition** (exit code 0 + specific output/behavior)
3. A **fail condition** (any non-zero exit code or missing expected output)

## Local Snapdragon 8 Elite Models & Cloud Workstation

When requested to use local or unrestricted models:
- **`ai8` / `qwen3`**: Main unrestricted coding & general reasoning model (`~/local-ai/models/qwen3-8b-q6k/Qwen3-8B-abliterated-Q6_K.gguf`). Run directly with `ai8 -p "<prompt>"` or via OpenAI API on `http://127.0.0.1:8080/v1`.
- **`cyberai`**: WhiteRabbitNeo V3 7B cyber lab specialist (`~/local-ai/models/whiterabbitneo-v3-7b/`). Run directly with `cyberai -p "<prompt>"`.
- **`sd15`**: Stable Diffusion 1.5 + Detail Tweaker LoRA for local image generation (`sd15 "<prompt>" <outfile>`).
- **`ai-server`**: Starts local OpenAI-compatible API server on `http://127.0.0.1:8080`.
- **`ag-cloud`**: Coordinates Local AI, Runpod cloud GPUs, Google Colab burst workers, and Hugging Face Hub.

