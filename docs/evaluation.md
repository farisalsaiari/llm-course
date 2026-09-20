# Basic Evaluation

The standalone evaluator reports held-out mean next-token loss, perplexity, token accuracy, evaluated token count, and deterministic generation samples. Validation runs in `model.eval()` and `torch.no_grad()` and never updates parameters.

Token accuracy is strict argmax accuracy and can hide probability quality. Loss and perplexity capture probability assignment but depend on tokenizer/data. Generation samples reveal qualitative failures but are subjective. A useful evaluation uses all of them and later adds task/domain-specific benchmarks.

High accuracy on this tiny corpus means memorization of a tiny distribution. It is not evidence of reasoning, broad language ability, or intelligence.
