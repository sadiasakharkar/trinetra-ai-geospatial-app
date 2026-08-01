from __future__ import annotations

try:
    import torch
    from torch import Tensor, nn
except ImportError:  # pragma: no cover
    torch = None
    Tensor = object
    nn = object


if torch is not None:
    class ResidualBlock(nn.Module):
        def __init__(self, in_channels: int, out_channels: int) -> None:
            super().__init__()
            self.conv1 = nn.Conv2d(in_channels, out_channels, 3, padding=1, bias=False)
            self.bn1 = nn.BatchNorm2d(out_channels)
            self.act = nn.SiLU(inplace=True)
            self.conv2 = nn.Conv2d(out_channels, out_channels, 3, padding=1, bias=False)
            self.bn2 = nn.BatchNorm2d(out_channels)
            self.skip = (
                nn.Identity()
                if in_channels == out_channels
                else nn.Conv2d(in_channels, out_channels, 1, bias=False)
            )

        def forward(self, x: Tensor) -> Tensor:
            residual = self.skip(x)
            x = self.act(self.bn1(self.conv1(x)))
            x = self.bn2(self.conv2(x))
            return self.act(x + residual)


    class AttentionGate(nn.Module):
        def __init__(self, gate_channels: int, skip_channels: int, inter_channels: int) -> None:
            super().__init__()
            self.gate_conv = nn.Conv2d(gate_channels, inter_channels, 1, bias=False)
            self.skip_conv = nn.Conv2d(skip_channels, inter_channels, 1, bias=False)
            self.score = nn.Sequential(
                nn.SiLU(inplace=True),
                nn.Conv2d(inter_channels, 1, 1),
                nn.Sigmoid(),
            )

        def forward(self, gate: Tensor, skip: Tensor) -> Tensor:
            score = self.score(self.gate_conv(gate) + self.skip_conv(skip))
            return skip * score


    class DownBlock(nn.Module):
        def __init__(self, in_channels: int, out_channels: int) -> None:
            super().__init__()
            self.pool = nn.MaxPool2d(2)
            self.block = ResidualBlock(in_channels, out_channels)

        def forward(self, x: Tensor) -> Tensor:
            return self.block(self.pool(x))


    class UpBlock(nn.Module):
        def __init__(self, in_channels: int, skip_channels: int, out_channels: int) -> None:
            super().__init__()
            self.up = nn.Upsample(scale_factor=2, mode="bilinear", align_corners=False)
            self.attn = AttentionGate(in_channels, skip_channels, out_channels)
            self.block = ResidualBlock(in_channels + skip_channels, out_channels)

        def forward(self, x: Tensor, skip: Tensor) -> Tensor:
            x = self.up(x)
            skip = self.attn(x, skip)
            if x.shape[-2:] != skip.shape[-2:]:
                x = nn.functional.interpolate(x, size=skip.shape[-2:], mode="bilinear", align_corners=False)
            return self.block(torch.cat([x, skip], dim=1))


    class AttentionResidualUNet(nn.Module):
        def __init__(self, in_channels: int = 8, base_channels: int = 32) -> None:
            super().__init__()
            self.stem = ResidualBlock(in_channels, base_channels)
            self.down1 = DownBlock(base_channels, base_channels * 2)
            self.down2 = DownBlock(base_channels * 2, base_channels * 4)
            self.down3 = DownBlock(base_channels * 4, base_channels * 8)
            self.bridge = ResidualBlock(base_channels * 8, base_channels * 16)
            self.up3 = UpBlock(base_channels * 16, base_channels * 8, base_channels * 8)
            self.up2 = UpBlock(base_channels * 8, base_channels * 4, base_channels * 4)
            self.up1 = UpBlock(base_channels * 4, base_channels * 2, base_channels * 2)
            self.up0 = UpBlock(base_channels * 2, base_channels, base_channels)
            self.rgb_head = nn.Sequential(nn.Conv2d(base_channels, 3, 1), nn.Sigmoid())
            self.conf_head = nn.Sequential(nn.Conv2d(base_channels, 1, 1), nn.Sigmoid())
            self.risk_head = nn.Sequential(nn.Conv2d(base_channels, 1, 1), nn.Sigmoid())
            self.cloud_head = nn.Sequential(nn.Conv2d(base_channels, 1, 1), nn.Sigmoid())

        def forward(self, x: Tensor) -> dict[str, Tensor]:
            s0 = self.stem(x)
            s1 = self.down1(s0)
            s2 = self.down2(s1)
            s3 = self.down3(s2)
            bridge = self.bridge(s3)
            u3 = self.up3(bridge, s3)
            u2 = self.up2(u3, s2)
            u1 = self.up1(u2, s1)
            u0 = self.up0(u1, s0)
            return {
                "reconstruction": self.rgb_head(u0),
                "confidence": self.conf_head(u0),
                "risk": self.risk_head(u0),
                "cloud": self.cloud_head(u0),
            }
else:
    class AttentionResidualUNet:  # pragma: no cover
        def __init__(self, *args, **kwargs) -> None:
            raise RuntimeError("PyTorch is required to instantiate AttentionResidualUNet.")
