# VGG19_CA.py
import torch
import torch.nn as nn

class Conv(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size=1, stride=1,
                 padding=None, groups=1, activation=True):
        super(Conv, self).__init__()
        padding = kernel_size // 2 if padding is None else padding
        self.conv = nn.Conv2d(in_channels, out_channels, kernel_size, stride,
                              padding, groups=groups, bias=True)
        self.act = nn.ReLU(inplace=True) if activation else nn.Identity()

    def forward(self, x):
        return self.act(self.conv(x))

class h_sigmoid(nn.Module):
    def __init__(self, inplace=True):
        super(h_sigmoid, self).__init__()
        self.relu = nn.ReLU6(inplace=inplace)

    def forward(self, x):
        return self.relu(x + 3) / 6


class h_swish(nn.Module):
    def __init__(self, inplace=True):
        super(h_swish, self).__init__()
        self.sigmoid = h_sigmoid(inplace=inplace)

    def forward(self, x):
        return x * self.sigmoid(x)


class CoordAttention(nn.Module):
    def __init__(self, in_channels, out_channels, reduction=32):
        super(CoordAttention, self).__init__()
        self.pool_w, self.pool_h = nn.AdaptiveAvgPool2d((1, None)), nn.AdaptiveAvgPool2d((None, 1))
        temp_c = max(8, in_channels // reduction)
        self.conv1 = nn.Conv2d(in_channels, temp_c, kernel_size=1, stride=1, padding=0)

        self.bn1 = nn.BatchNorm2d(temp_c)
        self.act1 = h_swish()

        self.conv2 = nn.Conv2d(temp_c, out_channels, kernel_size=1, stride=1, padding=0)
        self.conv3 = nn.Conv2d(temp_c, out_channels, kernel_size=1, stride=1, padding=0)
    def forward(self, x):
        short = x
        n, c, H, W = x.shape
        x_h, x_w = self.pool_h(x), self.pool_w(x).permute(0, 1, 3, 2)
        x_cat = torch.cat([x_h, x_w], dim=2)
        out = self.act1(self.bn1(self.conv1(x_cat)))
        x_h, x_w = torch.split(out, [H, W], dim=2)
        x_w = x_w.permute(0, 1, 3, 2)
        out_h = torch.sigmoid(self.conv2(x_h))
        out_w = torch.sigmoid(self.conv3(x_w))
        return short * out_w * out_h


class VGG19_CA(nn.Module):
    def __init__(self, num_classes):
        super(VGG19_CA, self).__init__()
        
        self.stages1=self._make_stage(3, 64, num_blocks=2, max_pooling=True)
        self.ca1 = CoordAttention(in_channels=64, out_channels=64)
        self.stages2=self._make_stage(64, 128, num_blocks=2, max_pooling=True)
        self.ca2 = CoordAttention(in_channels=128, out_channels=128)
        self.stages3=self._make_stage(128, 256, num_blocks=4, max_pooling=True)
        self.ca3 = CoordAttention(in_channels=256, out_channels=256)
        self.stages4=self._make_stage(256, 512, num_blocks=4, max_pooling=True)
        self.ca4 = CoordAttention(in_channels=512, out_channels=512)
        self.stages5=self._make_stage(512, 512, num_blocks=4, max_pooling=True)
        self.ca5 = CoordAttention(in_channels=512, out_channels=512)
        self.head = nn.Sequential(*[
            nn.Flatten(start_dim=1, end_dim=-1),
            nn.Linear(512 * 7 * 7, 4096),
            nn.ReLU(inplace=True),
            nn.Linear(4096, 4096),
            nn.ReLU(inplace=True),
            nn.Linear(4096, num_classes)
        ])

    @staticmethod
    def _make_stage(in_channels, out_channels, num_blocks, max_pooling):
        layers = [Conv(in_channels, out_channels, kernel_size=3, stride=1)]
        for _ in range(1, num_blocks):
            layers.append(Conv(out_channels, out_channels, kernel_size=3, stride=1))
        if max_pooling:
            layers.append(nn.MaxPool2d(kernel_size=2, stride=2, padding=0))
        return nn.Sequential(*layers)

    def forward(self, x):
        out=self.stages1(x)
        out=self.ca1(out)
        out=self.stages2(out)
        out=self.ca2(out)
        out=self.stages3(out)
        out=self.ca3(out)
        out=self.stages4(out)
        out=self.ca4(out)
        out=self.stages5(out)
        out=self.ca5(out)
        return self.head(out)

def VGG19CA():
    """ return a VGG19_CA network
    """
    return VGG19_CA(num_classes=2)  