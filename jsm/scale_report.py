from scale_configs import SCALE_CONFIGS


for config in SCALE_CONFIGS:
    status = "local" if config.executable_locally else "conceptual only"
    print(
        f"{config.name:18} "
        f"parameters={config.parameter_estimate():,} "
        f"context={config.max_seq_len:,} "
        f"width={config.embedding_dim:,} "
        f"layers={config.num_layers} "
        f"heads={config.num_heads} "
        f"[{status}]"
    )
