import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F

# CNN to extract spatial features
class SpatialCNN(nn.Module):
    def __init__(self, in_channels, out_channels):
        super(SpatialCNN, self).__init__()
        self.conv1 = nn.Conv2d(in_channels, 64, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(128, out_channels, kernel_size=3, padding=1)
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)

    def forward(self, x):
        # Apply CNN layers with ReLU and MaxPooling
        x = F.relu(self.conv1(x))
        x = self.pool(x)
        x = F.relu(self.conv2(x))
        x = self.pool(x)
        x = F.relu(self.conv3(x))
        x = self.pool(x)
        return x

# Transformer for temporal dependencies
class TemporalTransformer(nn.Module):
    def __init__(self, d_model, nhead, num_encoder_layers, dim_feedforward, dropout):
        super(TemporalTransformer, self).__init__()
        self.encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=nhead, dim_feedforward=dim_feedforward, dropout=dropout
        )
        self.transformer_encoder = nn.TransformerEncoder(self.encoder_layer, num_layers=num_encoder_layers)
        self.pos_embedding = nn.Parameter(torch.zeros(1, 100, d_model))  # Positional embeddings for sequence data

    def forward(self, x):
        # Add positional encoding to spatial features
        x = x + self.pos_embedding[:, :x.size(1)]
        x = self.transformer_encoder(x)
        return x

# Complete model combining CNN + Transformer + Prediction layer
class SpatioTemporalTransformer(nn.Module):
    def __init__(self, cnn_out_channels, d_model, nhead, num_encoder_layers, dim_feedforward, dropout, img_size):
        super(SpatioTemporalTransformer, self).__init__()
        self.spatial_cnn = SpatialCNN(in_channels=6, out_channels=cnn_out_channels)  # Assuming 2 channels: temp, precip
        self.temporal_transformer = TemporalTransformer(
            d_model=d_model, nhead=nhead, num_encoder_layers=num_encoder_layers,
            dim_feedforward=dim_feedforward, dropout=dropout
        )
        self.fc = nn.Linear(d_model, img_size * img_size * 3)  # Predict RGB image with img_size x img_size

    def forward(self, x):
        batch_size, seq_len, c, h, w = x.size()
        
        # Extract spatial features for each time step
        cnn_features = []
        for t in range(seq_len):
            spatial_features = self.spatial_cnn(x[:, t, :, :, :])  # Apply CNN on each time step
            cnn_features.append(spatial_features.view(batch_size, -1))  # Flatten spatial features
        
        # Stack CNN features into a sequence for Transformer
        cnn_features = torch.stack(cnn_features, dim=1)
        
        # Pass through the temporal transformer
        transformer_out = self.temporal_transformer(cnn_features)
        
        # Predict RGB image for each sequence step
        output = self.fc(transformer_out[:, -1, :])  # Predict based on the last output of the Transformer
        
        # Reshape to (batch_size, 3, img_size, img_size) for RGB image
        img_size = int(output.size(1)**0.5 / 3)  # Assuming img_size is known or inferred
        output = output.view(batch_size, 3, img_size, img_size)
        
        return output

# Example of how to use the model
if __name__ == "__main__":
    # Hyperparameters
    cnn_out_channels = 256
    d_model = 256
    nhead = 4
    num_encoder_layers = 3
    dim_feedforward = 512
    dropout = 0.1
    img_size = 64  # Define the size of the output RGB image

    # Model initialization
    model = SpatioTemporalTransformer(
        cnn_out_channels=cnn_out_channels, d_model=d_model, nhead=nhead,
        num_encoder_layers=num_encoder_layers, dim_feedforward=dim_feedforward,
        dropout=dropout, img_size=img_size
    )

    # Example input (batch_size, seq_len, channels, height, width)
    x = torch.randn(8, 12, 6, 64, 64)  # 8 samples, 12 months (time steps), 2 channels (temp, precip), 64x64 map

    # Forward pass
    output = model(x)
    print(output.shape)  # Should output (batch_size, 3, img_size, img_size) for RGB images

    # Define loss and optimizer
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    # Example target (RGB images for each batch)
    y = torch.randn(8, 3, img_size, img_size)

    # Loss and backpropagation
    loss = criterion(output, y)
    loss.backward()
    optimizer.step()

    print(f"Loss: {loss.item()}")
