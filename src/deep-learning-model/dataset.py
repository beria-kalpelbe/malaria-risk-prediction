import torch
from torch.utils.data import Dataset
import numpy as np

class SpatioTemporalDataset(Dataset):
    def __init__(self, data, labels, transform=None):
        """
        Args:
            data (numpy.ndarray): Array of shape (num_samples, seq_len, channels, height, width)
            labels (numpy.ndarray): Array of shape (num_samples,)
            transform (callable, optional): Optional transform to be applied on a sample.
        """
        self.data = data
        self.labels = labels
        self.transform = transform

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()

        sample = {'data': self.data[idx], 'label': self.labels[idx]}

        if self.transform:
            sample = self.transform(sample)

        return sample

# Example usage
if __name__ == "__main__":
    # Example data (num_samples, seq_len, channels, height, width)
    num_samples = 100
    seq_len = 12
    channels = 2
    height = 64
    width = 64

    # Generate random data and labels
    data = np.random.randn(num_samples, seq_len, channels, height, width).astype(np.float32)
    labels = np.random.randint(0, 2, size=(num_samples,)).astype(np.float32)

    # Create dataset
    dataset = SpatioTemporalDataset(data=data, labels=labels)

    # Create data loader
    dataloader = torch.utils.data.DataLoader(dataset, batch_size=8, shuffle=True)

    # Iterate through the data loader
    for batch in dataloader:
        x = batch['data']
        y = batch['label']
        print(f"Data batch shape: {x.shape}")
        print(f"Label batch shape: {y.shape}")

        # Forward pass through the model
        output = model(x)
        print(f"Output shape: {output.shape}")