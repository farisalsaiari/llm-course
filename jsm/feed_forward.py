import torch.nn as nn


# -----------------------------------
# Feed-Forward Network
# -----------------------------------

class FeedForward(nn.Module):

    def __init__(
        self,
        embedding_dim,
        ffn_multiplier=4,
        dropout=0.0
    ):

        super().__init__()


        # -----------------------------------
        # Expand
        #
        # 3 → 12
        # -----------------------------------

        self.linear1 = nn.Linear(
            embedding_dim,
            embedding_dim * ffn_multiplier
        )


        # -----------------------------------
        # Activation
        # -----------------------------------

        self.activation = nn.GELU()

        self.dropout = nn.Dropout(dropout)


        # -----------------------------------
        # Contract
        #
        # 12 → 3
        # -----------------------------------

        self.linear2 = nn.Linear(
            embedding_dim * ffn_multiplier,
            embedding_dim
        )


    # -----------------------------------
    # Forward
    # -----------------------------------

    def forward(self, vectors):

        expanded = self.linear1(
            vectors
        )

        activated = self.activation(
            expanded
        )

        activated = self.dropout(activated)

        output = self.linear2(
            activated
        )

        output = self.dropout(output)

        return output
