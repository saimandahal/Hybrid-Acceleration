## SpaceTxAx: Hybrid Acceleration of Lower-Parameter Spatio-Temporal Attention Models

Transformer architecture has emerged as a prominent deep neural network and is widely applied in several sequence transduction tasks. With attention mechanisms at their center, transformers have demonstrated excellent performance in large
language models (LLMs). In addition to their success with LLMs, attention mechanisms are effectively applied in spatio-temporal
analysis. However, their application is often constrained as they are highly complex and require bulk computation resources.
While numerous efforts have been made to mitigate the complexity and memory footprints, particularly for inference tasks,
optimizing training remains a significant challenge to address. Consequently, enhancing time and energy becomes critical for
maintaining feasible training and deployment. Accelerating the training using near-data processing can be a novel approach,
but the frequent write overhead is another pivotal issue. Only a hardware-level solution is not sufficient to tackle this issue.
Here, we present SpaceTxAx, a pioneer composite approach that integrates adaptive methods to train the transformer model with
reduced parameters, significantly cutting down the training complexity and computational demands. SpaceTxAx is a hardware-
software-based codesign that implements lightweight training for self-attention mechanisms on various spatiotemporal datasets and
accelerates it using heterogeneous architecture. Our parameter-efficient training approach incorporates intrinsic dimensionality
to reduce the trainable parameters, achieving efficiency in training without significant loss in accuracy. 
