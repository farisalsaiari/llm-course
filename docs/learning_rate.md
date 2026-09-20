# Learning-Rate Schedule

A constant learning rate applies the same update scale throughout training. Warmup starts smaller while optimizer statistics and activations settle. Decay then reduces update size as training converges.

This project uses linear warmup followed by cosine decay:

```text
small LR -> peak LR -> smooth cosine decay -> 10% of peak
```

The schedule advances once per optimizer update, not once per token or printed epoch. The short local run uses five warmup steps. Large training runs usually define warmup and total duration in optimizer steps and choose them from validation behavior and effective batch size.
