# K-shot prompting
## limitations of small/mid-sized LLM:
struggle with character-level transformations (like exact reversal). They operate primarily on tokens, not characters, so they sometimes:
- Drop letters
- Duplicate letters
- Swap chunks instead of reversing precisely
- Hallucinate near-patterns (tsoptht, sttusporth, etc.)
- LLMs are not deterministic string processors.

The solution founed in the blog[https://medium.com/@sami93sami93/how-prompting-techniques-transformed-the-llms-we-use-today-2bf2134c39b0] made a lot of restritions and limits on possible characters or character-combinations occurred in the target word. That made the prompt work for the target word and did not have generalization ability.


# Why Reversing Words Is Hard for Large Language Models

Reversing a word looks trivial for humans. For example:

```
"stressed" → "desserts"
```

However, this simple task reveals several architectural limitations in Large Language Models (LLMs). This document explains why.

---

## 1. Why Larger Models Perform Better

Larger models generally perform better on tasks like word reversal because they have:

- **More parameters** – allowing them to capture more patterns in training data.
- **Better internal representations** – enabling them to approximate algorithmic behavior.
- **Greater contextual understanding** – which can help them reason about sequences.

However, even very large models **do not truly learn algorithms**. Instead, they approximate patterns seen during training. This means their performance improves statistically rather than algorithmically.

Key reason:
- Larger models can approximate character relationships more accurately.

But:
- They still lack a guaranteed step-by-step symbolic process.

---

## 2. How Tokenization Breaks String Tasks

LLMs do not see text as characters. They see **tokens**.

Example tokenization:

```
"unbelievable" → ["un", "believ", "able"]
```

If a model tries to reverse this tokenized sequence:

```
["un", "believ", "able"] → ["able", "believ", "un"]
```

The output becomes:

```
"ablebelievun"
```

This is not the correct character-level reversal.

Problems caused by tokenization:

- Character boundaries are lost
- Tokens may represent multiple characters
- Some tokens may contain partial words

Therefore, **character-level operations are misaligned with token-level processing**.

---

## 3. Designing Prompts for Algorithmic Reliability

Prompt design can partially mitigate these issues.

### Technique 1: Force character-level reasoning

Example prompt:

```
Reverse the following word character-by-character.
Write each step.

Word: "stressed"
```

Expected reasoning:

```
s t r e s s e d
↓
d e s s e r t s
```

### Technique 2: Use spacing

```
Input: s t r e s s e d
Output: d e s s e r t s
```

Spacing forces the model closer to character-level processing.

### Technique 3: Structured instructions

```
Step 1: List characters
Step 2: Reverse the list
Step 3: Join them
```

Structured prompts increase reliability but **do not guarantee correctness**.

---

## 4. Benchmarking Character-Level Accuracy

To test models reliably, researchers measure **character-level accuracy** rather than token-level output.

Example benchmark procedure:

1. Generate random words
2. Ask the model to reverse them
3. Compare output with ground truth

Metrics:

- **Exact match accuracy**
- **Character edit distance**
- **Error rate by word length**

Typical observation:

Accuracy decreases rapidly as word length increases.

Example trend:

| Word Length | Accuracy |
|-------------|----------|
| 3–5         | High     |
| 6–8         | Medium   |
| 9+          | Low      |

This reflects the model's difficulty with long sequential operations.

---

## 5. Why This Problem Is Fundamentally Hard for Transformers

Transformers are designed for **probabilistic next-token prediction**, not algorithm execution.

Key limitations:

### 1. No explicit memory stack

Algorithms like reversal naturally use:

- stacks
- pointers
- iteration

Transformers do not explicitly implement these.

### 2. Parallel attention instead of sequential execution

Transformers process sequences **in parallel**, whereas algorithms typically require **step-by-step execution**.

### 3. Token prediction objective

The training objective is:

```
Predict the next token given previous tokens
```

This objective does not explicitly train models to perform deterministic algorithms.

### 4. Lack of guaranteed generalization

Even if a model learns to reverse short words, it may fail on longer ones because it has not learned the **underlying algorithm**, only a statistical pattern.

---

## Conclusion

Word reversal highlights a broader insight:

> LLMs are powerful pattern recognition systems but weak algorithmic processors.

While larger models and careful prompting can improve performance, tasks requiring precise character-level manipulation remain challenging due to:

- tokenization
- training objectives
- architectural constraints

Understanding these limitations helps design better prompts, evaluations, and future architectures.


# Self Consistency
While CoT generates a single reasoning path, Self-Consistency generates multiple different reasoning paths and then selects the most frequent answer (the majority vote).

## How it works
Self-consistency prompting is an advanced technique that improves Large Language Model (LLM) accuracy on reasoning tasks by generating multiple, diverse reasoning paths for a single prompt and selecting the most consistent (majority) answer. It enhances Chain-of-Thought (CoT) prompting by mitigating the risk of a single, faulty, or greedy reasoning path.

Instead of a single “greedy” decode (taking the most likely next word once), the model follows these steps:

1. __Prompting__: The model is prompted using Chain of Thought (e.g., “Let’s think step by step”).
2. __Sampling__: The model generates several independent responses (e.g., 5, 10, or even 40 versions) for the same prompt.
3. __Aggregation__: The system look at the final answer in each reasoning path.
4. __Majority Vote__: The final answer provided to the user is the one that appeared most often across all the samples.

Key Aspects of Self-Consistency Prompting:

    + How it Works: The model is prompted multiple times to generate several, diverse reasoning paths for the same question. The final answer is chosen by selecting the most frequent answer (majority vote) among the generated responses.
    + Methodology: It typically uses Few-Shot CoT to generate multiple potential answers and then aggregates them to find the consistent result.
    + Applications: Highly effective for tasks requiring arithmetic, symbolic, or commonsense reasoning.
    + Performance: Significantly improves accuracy over standard CoT, with studies showing gains on benchmarks like GSM8K (+17.9%), SVAMP (+11.0%), and AQuA (+12.2%).
    + Limitations: It is less suited for creative or free-form generation and may have diminishing returns after a certain number of samples.