def estimate_training_memory(
    parameter_count,
    batch_size,
    sequence_length,
    embedding_dim,
    num_heads,
    num_layers,
    bytes_per_value=4
):

    parameters = parameter_count * bytes_per_value
    gradients = parameter_count * bytes_per_value
    adamw_states = parameter_count * 2 * 4
    hidden_activations = (
        batch_size
        * sequence_length
        * embedding_dim
        * num_layers
        * bytes_per_value
    )
    attention_scores = (
        batch_size
        * num_heads
        * sequence_length
        * sequence_length
        * num_layers
        * bytes_per_value
    )

    components = {
        "parameters": parameters,
        "gradients": gradients,
        "adamw_states": adamw_states,
        "hidden_activations_lower_bound": hidden_activations,
        "attention_scores_lower_bound": attention_scores
    }
    components["estimated_total_lower_bound"] = sum(
        components.values()
    )

    return components
