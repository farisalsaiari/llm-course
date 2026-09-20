import torch
from torch.utils.data import Dataset

from data_loader import create_language_model_windows


class LanguageModelDataset(Dataset):

    def __init__(
        self,
        encoded_documents,
        sequence_length,
        stride=1
    ):

        self.windows = create_language_model_windows(
            encoded_documents=encoded_documents,
            sequence_length=sequence_length,
            stride=stride
        )

        if not self.windows:
            raise ValueError(
                "No training windows were created. Add more tokens "
                "or reduce sequence_length."
            )


    def __len__(self):

        return len(self.windows)


    def __getitem__(self, index):

        input_ids, target_ids = self.windows[index]

        return (
            torch.tensor(input_ids, dtype=torch.long),
            torch.tensor(target_ids, dtype=torch.long)
        )
