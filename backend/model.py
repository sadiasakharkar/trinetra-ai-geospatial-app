import torch
import torch.nn as nn

class DoubleConv(nn.Module):
    """(convolution => [BN] => ReLU) * 2"""
    def __init__(self, in_channels, out_channels):
        super().__init__()
        self.double_conv = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True)
        )

    def forward(self, x):
        return self.double_conv(x)

class Down(nn.Module):
    """Downscaling with maxpool then double conv"""
    def __init__(self, in_channels, out_channels):
        super().__init__()
        self.maxpool_conv = nn.Sequential(
            nn.MaxPool2d(2),
            DoubleConv(in_channels, out_channels)
        )

    def forward(self, x):
        return self.maxpool_conv(x)

class Up(nn.Module):
    """Upscaling then double conv"""
    def __init__(self, in_channels, out_channels, bilinear=True):
        super().__init__()
        if bilinear:
            self.up = nn.Upsample(scale_factor=2, mode='bilinear', align_corners=True)
            self.conv = DoubleConv(in_channels, out_channels)
        else:
            self.up = nn.ConvTranspose2d(in_channels, in_channels // 2, kernel_size=2, stride=2)
            self.conv = DoubleConv(in_channels, out_channels)

    def forward(self, x1, x2):
        x1 = self.up(x1)
        # Input is CHW
        diffY = x2.size()[2] - x1.size()[2]
        diffX = x2.size()[3] - x1.size()[3]

        x1 = nn.functional.pad(x1, [diffX // 2, diffX - diffX // 2,
                                    diffY // 2, diffY - diffY // 2])
        x = torch.cat([x2, x1], dim=1)
        return self.conv(x)

class OutConv(nn.Module):
    def __init__(self, in_channels, out_channels):
        super(OutConv, self).__init__()
        self.conv = nn.Conv2d(in_channels, out_channels, kernel_size=1)

    def forward(self, x):
        return self.conv(x)

class TrinetraUNet(nn.Module):
    """
    TRINETRA-AI Multi-modal Fusion Reconstruction Model.
    
    Inputs:
        - Current Cloudy LISS-IV (3 channels: R, G, B)
        - Sentinel-1 SAR (1 channel: Backscatter Intensity)
        - Terrain DEM (1 channel: Elevation Prior)
        - Historical LISS-IV (3 channels: R, G, B)
        Total input channels = 8.
        
    Outputs:
        - Reconstructed Cloud-free Scene (3 channels: RGB, values in [0, 1])
        - Per-pixel Confidence Map (1 channel, values in [0, 1])
        - Hallucination Risk Map (1 channel, values in [0, 1])
    """
    def __init__(self, n_channels=8, bilinear=True):
        super().__init__()
        self.n_channels = n_channels
        self.bilinear = bilinear

        # Encoder
        self.inc = DoubleConv(n_channels, 32)
        self.down1 = Down(32, 64)
        self.down2 = Down(64, 128)
        self.down3 = Down(128, 256)
        factor = 2 if bilinear else 1
        self.down4 = Down(256, 512 // factor)

        # Decoder
        self.up1 = Up(512, 256 // factor, bilinear)
        self.up2 = Up(256, 128 // factor, bilinear)
        self.up3 = Up(128, 64 // factor, bilinear)
        self.up4 = Up(64, 32, bilinear)

        # Output branches
        self.out_rgb = nn.Sequential(
            OutConv(32, 3),
            nn.Sigmoid()
        )
        self.out_confidence = nn.Sequential(
            OutConv(32, 1),
            nn.Sigmoid()
        )
        self.out_risk = nn.Sequential(
            OutConv(32, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        """
        x: Tensor of shape (B, 8, H, W)
        Returns:
            rgb: (B, 3, H, W)
            confidence: (B, 1, H, W)
            risk: (B, 1, H, W)
        """
        x1 = self.inc(x)
        x2 = self.down1(x1)
        x3 = self.down2(x2)
        x4 = self.down3(x3)
        x5 = self.down4(x4)
        
        x = self.up1(x5, x4)
        x = self.up2(x, x3)
        x = self.up3(x, x2)
        x = self.up4(x, x1)
        
        rgb = self.out_rgb(x)
        confidence = self.out_confidence(x)
        risk = self.out_risk(x)
        
        return rgb, confidence, risk
