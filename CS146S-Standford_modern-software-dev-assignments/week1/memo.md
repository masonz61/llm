# K-shot prompting
## limitations of small/mid-sized LLM:
struggle with character-level transformations (like exact reversal). They operate primarily on tokens, not characters, so they sometimes:
- Drop letters
- Duplicate letters
- Swap chunks instead of reversing precisely
- Hallucinate near-patterns (tsoptht, sttusporth, etc.)

The solution founed in the blog[https://medium.com/@sami93sami93/how-prompting-techniques-transformed-the-llms-we-use-today-2bf2134c39b0] made a lot of restritions and limits on possible characters or character-combinations occurred in the target word. That made the prompt work for the target word and did not have generalization ability.

