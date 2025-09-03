# WEBP 转 MP4 转换器 - ComfyUI 自定义节点

将图像序列转换为MP4视频的ComfyUI自定义节点，专门设计用于接收VAEDecode等节点的IMAGE输出。

## 功能特性

- 🎬 **图像序列到视频转换** - 将IMAGE tensor批量转换为MP4视频
- 🔗 **无缝集成** - 直接接收VAEDecode、Sampler等节点的IMAGE输出
- ⚡ **高效处理** - 自动tensor到图像转换和临时文件管理
- 🎯 **简单易用** - 仅需设置帧率和输出文件名前缀

## 节点信息

**节点名称**: WEBP转MP4转换器  
**类别**: video/conversion  
**输入类型**: IMAGE tensor  
**输出类型**: STRING (视频文件路径)

### 输入参数

| 参数 | 类型 | 说明 | 默认值 | 范围 |
|------|------|------|--------|------|
| images | IMAGE | 图像序列tensor（来自VAEDecode等节点） | - | 必需 |
| frame_rate | INT | 视频帧率 | 20 | 1-60 |
| filename_prefix | STRING | 输出文件名前缀 | "video" | 可选 |

### 输出

- **video_paths** (STRING): 生成的MP4文件完整路径

## 安装方法

1. 将整个 `webp_to_mp4_converter` 文件夹复制到 ComfyUI 的 `custom_nodes` 目录
2. 安装依赖包：
   ```bash
   pip install Pillow>=9.2.0 moviepy>=2.0.0
   ```
3. 重启 ComfyUI

## 使用方法

1. 在ComfyUI工作流中添加"WEBP转MP4转换器"节点
2. 将VAEDecode（或其他IMAGE输出节点）的输出连接到converter的images输入
3. 设置desired帧率（1-60 FPS）
4. 可选：自定义输出文件名前缀
5. 运行工作流，MP4文件将保存到ComfyUI的output目录

## 工作流示例

```
VAEDecode → WEBP转MP4转换器 → PreviewVideo
    ↓              ↓
  IMAGE         STRING (video_path)
```

## 技术细节

### IMAGE Tensor 格式
- **输入格式**: `[B, H, W, C]` 其中 B=批量大小，H=高度，W=宽度，C=通道数
- **数值范围**: 0.0-1.0 (float32)
- **支持通道**: RGB (3通道) 和 RGBA (4通道，自动转换为RGB)

### 处理流程
1. 验证IMAGE tensor格式和尺寸
2. 将tensor转换为PIL Image并保存为临时PNG文件
3. 使用MoviePy的ImageSequenceClip生成MP4视频
4. 应用H.264编码优化设置
5. 自动清理临时文件

### 视频编码设置
- **编解码器**: libx264
- **像素格式**: yuv420p
- **CRF**: 23 (高质量)
- **预设**: ultrafast（快速编码）

## 文件结构

```
webp_to_mp4_converter/
├── __init__.py          # 节点注册
├── nodes.py             # 主节点实现
├── utils.py             # 工具函数
├── requirements.txt     # 依赖包
└── README.md           # 说明文档
```

## 依赖包

- **Pillow** (≥9.2.0): 图像处理
- **moviepy** (≥2.0.0): 视频生成

## 常见问题

### Q: 支持哪些输入格式？
A: 节点专门设计用于ComfyUI的IMAGE tensor格式，支持来自VAEDecode、KSampler等节点的直接输出。

### Q: 输出视频保存在哪里？
A: 默认保存在ComfyUI的`output`目录，文件名格式为`{prefix}_{timestamp}.mp4`。

### Q: 如何调整视频质量？
A: 当前使用固定的高质量设置（CRF 23）。如需调整，可修改`utils.py`中的编码参数。

### Q: 支持音频吗？
A: 当前版本仅支持视频生成，不包含音频处理功能。

## 版本历史

- **v1.0** - 初始版本，支持IMAGE tensor到MP4转换
- **v1.1** - 优化tensor处理和临时文件管理

## 许可证

本项目遵循与ComfyUI相同的许可证条款。

## 贡献

欢迎提交Issue和Pull Request来改进这个自定义节点。