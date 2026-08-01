"""SpA-GAN generator for RGB satellite cloud removal.

Architecture and weights from Penn000/SpA-GAN_for_cloud_removal (MIT License),
pretrained on the RICE1 dataset.
"""

from __future__ import annotations

from collections import OrderedDict

try:
    import torch
    import torch.nn.functional as F
    from torch import nn
except ImportError:  # pragma: no cover
    torch = None
    F = None
    nn = object


if torch is not None:

    def conv1x1(in_channels: int, out_channels: int, stride: int = 1) -> nn.Conv2d:
        return nn.Conv2d(in_channels, out_channels, kernel_size=1, stride=stride, padding=0, bias=False)

    def conv3x3(in_channels: int, out_channels: int, stride: int = 1) -> nn.Conv2d:
        return nn.Conv2d(in_channels, out_channels, kernel_size=3, stride=stride, padding=1, bias=False)

    class Bottleneck(nn.Module):
        def __init__(self, in_channels: int, out_channels: int) -> None:
            super().__init__()
            self.group1 = nn.Sequential(
                OrderedDict(
                    [
                        ("conv1", nn.Conv2d(in_channels, out_channels, kernel_size=1, bias=False)),
                        ("relu1", nn.ReLU(True)),
                        (
                            "conv2",
                            nn.Conv2d(
                                out_channels,
                                out_channels,
                                kernel_size=3,
                                stride=1,
                                padding=2,
                                bias=False,
                                dilation=2,
                            ),
                        ),
                        ("relu2", nn.ReLU(True)),
                        ("conv3", nn.Conv2d(out_channels, out_channels, kernel_size=1, bias=False)),
                    ]
                )
            )

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            return self.group1(x)

    class irnn_layer(nn.Module):
        def __init__(self, in_channels: int) -> None:
            super().__init__()
            self.left_weight = nn.Conv2d(in_channels, in_channels, kernel_size=1, stride=1, groups=in_channels, padding=0)
            self.right_weight = nn.Conv2d(in_channels, in_channels, kernel_size=1, stride=1, groups=in_channels, padding=0)
            self.up_weight = nn.Conv2d(in_channels, in_channels, kernel_size=1, stride=1, groups=in_channels, padding=0)
            self.down_weight = nn.Conv2d(in_channels, in_channels, kernel_size=1, stride=1, groups=in_channels, padding=0)

        def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
            _, _, height, width = x.shape
            top_left = x.clone()
            top_right = x.clone()
            top_up = x.clone()
            top_down = x.clone()
            top_left[:, :, :, 1:] = F.relu(self.left_weight(x)[:, :, :, : width - 1] + x[:, :, :, 1:], inplace=False)
            top_right[:, :, :, :-1] = F.relu(self.right_weight(x)[:, :, :, 1:] + x[:, :, :, : width - 1], inplace=False)
            top_up[:, :, 1:, :] = F.relu(self.up_weight(x)[:, :, : height - 1, :] + x[:, :, 1:, :], inplace=False)
            top_down[:, :, :-1, :] = F.relu(self.down_weight(x)[:, :, 1:, :] + x[:, :, : height - 1, :], inplace=False)
            return top_up, top_right, top_down, top_left

    class Attention(nn.Module):
        def __init__(self, in_channels: int) -> None:
            super().__init__()
            self.out_channels = int(in_channels / 2)
            self.conv1 = nn.Conv2d(in_channels, self.out_channels, kernel_size=3, padding=1, stride=1)
            self.relu1 = nn.ReLU()
            self.conv2 = nn.Conv2d(self.out_channels, self.out_channels, kernel_size=3, padding=1, stride=1)
            self.relu2 = nn.ReLU()
            self.conv3 = nn.Conv2d(self.out_channels, 4, kernel_size=1, padding=0, stride=1)
            self.sigmod = nn.Sigmoid()

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            out = self.relu1(self.conv1(x))
            out = self.relu2(self.conv2(out))
            return self.sigmod(self.conv3(out))

    class SAM(nn.Module):
        def __init__(self, in_channels: int, out_channels: int, attention: int = 1) -> None:
            super().__init__()
            self.out_channels = out_channels
            self.irnn1 = irnn_layer(self.out_channels)
            self.irnn2 = irnn_layer(self.out_channels)
            self.conv_in = conv3x3(in_channels, self.out_channels)
            self.relu1 = nn.ReLU(True)
            self.conv1 = nn.Conv2d(self.out_channels, self.out_channels, kernel_size=1, stride=1, padding=0)
            self.conv2 = nn.Conv2d(self.out_channels * 4, self.out_channels, kernel_size=1, stride=1, padding=0)
            self.conv3 = nn.Conv2d(self.out_channels * 4, self.out_channels, kernel_size=1, stride=1, padding=0)
            self.relu2 = nn.ReLU(True)
            self.attention = attention
            if self.attention:
                self.attention_layer = Attention(in_channels)
            self.conv_out = conv1x1(self.out_channels, 1)
            self.sigmod = nn.Sigmoid()

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            weight = self.attention_layer(x) if self.attention else None
            out = self.conv1(x)
            top_up, top_right, top_down, top_left = self.irnn1(out)
            if self.attention and weight is not None:
                top_up.mul(weight[:, 0:1, :, :])
                top_right.mul(weight[:, 1:2, :, :])
                top_down.mul(weight[:, 2:3, :, :])
                top_left.mul(weight[:, 3:4, :, :])
            out = torch.cat([top_up, top_right, top_down, top_left], dim=1)
            out = self.conv2(out)
            top_up, top_right, top_down, top_left = self.irnn2(out)
            if self.attention and weight is not None:
                top_up.mul(weight[:, 0:1, :, :])
                top_right.mul(weight[:, 1:2, :, :])
                top_down.mul(weight[:, 2:3, :, :])
                top_left.mul(weight[:, 3:4, :, :])
            out = torch.cat([top_up, top_right, top_down, top_left], dim=1)
            out = self.conv3(out)
            out = self.relu2(out)
            return self.sigmod(self.conv_out(out))

    class SPANet(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.conv_in = nn.Sequential(conv3x3(3, 32), nn.ReLU(True))
            self.SAM1 = SAM(32, 32, 1)
            self.res_block1 = Bottleneck(32, 32)
            self.res_block2 = Bottleneck(32, 32)
            self.res_block3 = Bottleneck(32, 32)
            self.res_block4 = Bottleneck(32, 32)
            self.res_block5 = Bottleneck(32, 32)
            self.res_block6 = Bottleneck(32, 32)
            self.res_block7 = Bottleneck(32, 32)
            self.res_block8 = Bottleneck(32, 32)
            self.res_block9 = Bottleneck(32, 32)
            self.res_block10 = Bottleneck(32, 32)
            self.res_block11 = Bottleneck(32, 32)
            self.res_block12 = Bottleneck(32, 32)
            self.res_block13 = Bottleneck(32, 32)
            self.res_block14 = Bottleneck(32, 32)
            self.res_block15 = Bottleneck(32, 32)
            self.res_block16 = Bottleneck(32, 32)
            self.res_block17 = Bottleneck(32, 32)
            self.conv_out = nn.Sequential(conv3x3(32, 3))

        def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
            out = self.conv_in(x)
            out = F.relu(self.res_block1(out) + out)
            out = F.relu(self.res_block2(out) + out)
            out = F.relu(self.res_block3(out) + out)
            attention1 = self.SAM1(out)
            out = F.relu(self.res_block4(out) * attention1 + out)
            out = F.relu(self.res_block5(out) * attention1 + out)
            out = F.relu(self.res_block6(out) * attention1 + out)
            attention2 = self.SAM1(out)
            out = F.relu(self.res_block7(out) * attention2 + out)
            out = F.relu(self.res_block8(out) * attention2 + out)
            out = F.relu(self.res_block9(out) * attention2 + out)
            attention3 = self.SAM1(out)
            out = F.relu(self.res_block10(out) * attention3 + out)
            out = F.relu(self.res_block11(out) * attention3 + out)
            out = F.relu(self.res_block12(out) * attention3 + out)
            attention4 = self.SAM1(out)
            out = F.relu(self.res_block13(out) * attention4 + out)
            out = F.relu(self.res_block14(out) * attention4 + out)
            out = F.relu(self.res_block15(out) * attention4 + out)
            out = F.relu(self.res_block16(out) + out)
            out = F.relu(self.res_block17(out) + out)
            return attention4, self.conv_out(out)

    class SpAGANGenerator(nn.Module):
        """Original SpA-GAN generator wrapper matching the RICE1 checkpoint keys."""

        def __init__(self) -> None:
            super().__init__()
            self.gen = nn.Sequential(OrderedDict([("gen", SPANet())]))

        def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
            return self.gen(x)

    class SpAGANInference(nn.Module):
        """Export-friendly wrapper returning reconstruction and cloud attention."""

        def __init__(self) -> None:
            super().__init__()
            self.generator = SpAGANGenerator()

        def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
            attention, reconstruction = self.generator(x)
            return reconstruction, attention

    DEFAULT_WEIGHTS_URL = (
        "https://raw.githubusercontent.com/Penn000/SpA-GAN_for_cloud_removal/master/"
        "pretrained_models/RICE1/gen_model_epoch_200.pth"
    )
