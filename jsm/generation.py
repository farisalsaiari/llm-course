import torch

from subword_tokenizer import BOS_TOKEN, EOS_TOKEN


def sample_next_token(
    logits,
    temperature=1.0,
    top_k=None,
    top_p=None,
    generator=None
):

    if temperature < 0:
        raise ValueError("temperature must be non-negative.")

    if temperature == 0:
        return logits.argmax(dim=-1, keepdim=True)

    if top_k is not None and top_k < 1:
        raise ValueError("top_k must be positive.")

    if top_p is not None and not 0 < top_p <= 1:
        raise ValueError("top_p must be in the interval (0, 1].")

    filtered_logits = logits / temperature

    if top_k is not None:
        top_k = min(top_k, filtered_logits.shape[-1])
        threshold = torch.topk(
            filtered_logits,
            top_k,
            dim=-1
        ).values[:, -1:]
        filtered_logits = filtered_logits.masked_fill(
            filtered_logits < threshold,
            float("-inf")
        )

    if top_p is not None:
        sorted_logits, sorted_indices = torch.sort(
            filtered_logits,
            descending=True,
            dim=-1
        )
        sorted_probabilities = torch.softmax(
            sorted_logits,
            dim=-1
        )
        cumulative_probabilities = torch.cumsum(
            sorted_probabilities,
            dim=-1
        )
        remove_mask = (
            cumulative_probabilities - sorted_probabilities
        ) >= top_p
        sorted_logits = sorted_logits.masked_fill(
            remove_mask,
            float("-inf")
        )
        filtered_logits = torch.full_like(
            filtered_logits,
            float("-inf")
        ).scatter(
            dim=-1,
            index=sorted_indices,
            src=sorted_logits
        )

    probabilities = torch.softmax(filtered_logits, dim=-1)

    return torch.multinomial(
        probabilities,
        num_samples=1,
        generator=generator
    )


@torch.no_grad()
def generate(
    model,
    tokenizer,
    prompt,
    max_new_tokens=20,
    temperature=1.0,
    top_k=None,
    top_p=None,
    generator=None,
    use_kv_cache=True
):

    model.eval()

    token_ids = tokenizer.encode(prompt).ids

    if not token_ids:
        token_ids = [tokenizer.token_to_id(BOS_TOKEN)]

    eos_id = tokenizer.token_to_id(EOS_TOKEN)
    device = next(model.parameters()).device

    generated_ids = torch.tensor(
        [token_ids],
        dtype=torch.long,
        device=device
    )
    caches = None

    for _ in range(max_new_tokens):

        if use_kv_cache and caches is not None:
            model_input = generated_ids[:, -1:]
        else:
            model_input = generated_ids[:, -model.max_seq_len:]

        if use_kv_cache:
            logits, caches = model(
                model_input,
                caches=caches,
                use_cache=True
            )
        else:
            logits = model(model_input)
        next_token_id = sample_next_token(
            logits=logits[:, -1, :],
            temperature=temperature,
            top_k=top_k,
            top_p=top_p,
            generator=generator
        )

        generated_ids = torch.cat(
            [generated_ids, next_token_id],
            dim=1
        )

        if next_token_id.item() == eos_id:
            break

        if (
            use_kv_cache
            and caches[0][0].shape[-2] >= model.max_seq_len
        ):
            caches = None

    return tokenizer.decode(
        generated_ids[0].tolist(),
        skip_special_tokens=True
    )
