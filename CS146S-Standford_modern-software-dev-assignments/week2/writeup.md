# Week 2 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## INSTRUCTIONS

Fill out all of the `TODO`s in this file.

## SUBMISSION DETAILS

Name: **TODO** \
SUNet ID: **TODO** \
Citations: **TODO**

This assignment took me about **TODO** hours to do. 


## YOUR RESPONSES
For each exercise, please include what prompts you used to generate the answer, in addition to the location of the generated response. Make sure to clearly add comments in your code documenting which parts are generated.

### Exercise 1: Scaffold a New Feature
Prompt: 
Implement an Ollama-based `extract_action_items_llm(text)` in `week2/app/services/extract.py`.
Requirements:
- Structured output parsing (JSON array of strings) with validation
- Model information from `ollama list` with local fallback model
- Return clean, deduplicated action items
- Raise a clear service-layer exception when Ollama fails or returns malformed output
- Obey Single Responsibility Principle
- No test 
- List all modified code files with the relevant line numbers in brief summary

Generated Code Snippets:
```
List all modified code files with the relevant line numbers.
```
week2/app/services/extract.py

- Imports updated: lines 3-10
- New exception + Ollama/model helpers: lines 93-170
- Ollama HTTP generation: lines 173-205
- JSON candidate extraction + validation: lines 208-240
- Normalization + dedupe: lines 243-267
- extract_action_items_llm(text): lines 270-298


### Exercise 2: Add Unit Tests
Prompt: 
Add unit tests for `extract_action_items_llm()` in `week2/tests/test_extract.py`, and put test files in appropriate folder
Cover:
- bullet-list style notes
- keyword-prefixed lines
- empty input behavior
- malformed LLM JSON response path
- List all modified code files with the relevant line numbers in brief summary
Use monkeypatch/mocks so tests do not depend on a running Ollama daemon.

Generated Code Snippets:
week2/tests/test_extract.py
- Updated imports to include ActionItemExtractionError + extract_action_items_llm: lines 1-5
- Added bullet-list style notes test: lines 23-41
- Added keyword-prefixed lines test: lines 43-63
- Added empty input behavior test: lines 65-68
- Added malformed LLM JSON response path test (expects ActionItemExtractionError): lines 70-78

### Exercise 3: Refactor Existing Code for Clarity
Prompt: 
Refactor week2 backend for clarity:
- define explicit request/response Pydantic schemas
- clean up DB layer and lifecycle initialization
- improve route-level error handling
- keep existing endpoint behavior backward-compatible where possible
- List all modified code files with the relevant line numbers in brief summary


Generated/Modified Code Snippets:
week2/app/main.py: lifespan + startup init
Lines 3-22 (added lifespan, removed import-time init_db()), rest unchanged.
week2/app/db.py: DB lifecycle + connection setup
Lines 17-23 (enable PRAGMA foreign_keys = ON in get_connection())
Lines 26-51 (DB schema init with foreign keys)
(Also removed ensure_data_directory_exists() call inside init_db().)
week2/app/routers/action_items.py: schema usage + route error handling
Lines 1-77 (new typed request/response models, try/except for service/DB errors)
week2/app/routers/notes.py: schema usage + route error handling
Lines 1-44 (new typed request/response models, try/except for DB errors)
week2/app/schemas/__init__.py
Lines 1-2
week2/app/schemas/action_items.py
Lines 8-50 (all request/response schemas for action-items)
week2/app/schemas/notes.py
Lines 8-20 (request/response schemas for notes)
week2/app/services/extract.py (LLM implementation previously added)
Lines 93-298 (service-layer ActionItemExtractionError + Ollama model selection + JSON validation + extract_action_items_llm)
week2/tests/test_extract.py (LLM unit tests previously added)
Lines 1-78 (tests using monkeypatch to mock Ollama)


### Exercise 4: Use Agentic Mode to Automate a Small Task
Prompt: 
Add:
1) a new endpoint `POST /action-items/extract-llm` and wire it to the frontend as an `Extract LLM` button.
2) a notes list endpoint `GET /notes` and wire it to the frontend as a `List Notes` button.
3) List all modified code files with the relevant line numbers in brief summary
Keep UI feedback clear for success and error cases.

Generated Code Snippets:
```
TODO: List all modified code files with the relevant line numbers.
```


### Exercise 5: Generate a README from the Codebase
Prompt: 
```
TODO
```

Generated Code Snippets:
```
TODO: List all modified code files with the relevant line numbers.
```


## SUBMISSION INSTRUCTIONS
1. Hit a `Command (⌘) + F` (or `Ctrl + F`) to find any remaining `TODO`s in this file. If no results are found, congratulations – you've completed all required fields. 
2. Make sure you have all changes pushed to your remote repository for grading.
3. Submit via Gradescope. 