import os
import logging
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict
import comfy.utils
import folder_paths
from .utils import convert_frames_to_mp4, check_dependencies, setup_output_directory, tensor_to_image_sequence


class WebpToMp4Converter:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", {
                    "tooltip": "输入图像序列（来自VAEDecode等节点）"
                }),
                "frame_rate": ("INT", {
                    "default": 20,
                    "min": 1,
                    "max": 60,
                    "step": 1,
                    "display": "slider",
                    "tooltip": "视频帧率"
                }),
            },
            "optional": {
                "filename_prefix": ("STRING", {
                    "default": "video",
                    "placeholder": "输出文件名前缀"
                })
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("video_paths",)
    FUNCTION = "convert_images_to_mp4"
    CATEGORY = "video/conversion"
    DESCRIPTION = "将图像序列转换为MP4视频"
    
    def convert_images_to_mp4(self, images, frame_rate, filename_prefix="video"):
        logging.info("开始图像序列到MP4转换")
        
        try:
            check_dependencies()
            
            # 验证输入图像tensor
            if not hasattr(images, 'shape') or len(images.shape) != 4:
                raise ValueError(f"输入不是有效的图像tensor，期望形状 [B, H, W, C]，实际: {getattr(images, 'shape', 'unknown')}")
            
            batch_size = images.shape[0]
            if batch_size == 0:
                raise ValueError("输入图像序列为空")
            
            logging.info(f"处理图像序列，批量大小: {batch_size}, 图像尺寸: {images.shape[1:3]}")
            
            # 设置输出目录
            output_dir = setup_output_directory("")
            
            # 创建临时目录
            temp_dir = tempfile.mkdtemp()
            
            try:
                # 将IMAGE tensor转换为图像序列文件
                frame_paths = tensor_to_image_sequence(images, temp_dir, "frame")
                
                if not frame_paths:
                    raise RuntimeError("无法从输入图像生成帧序列")
                
                # 生成输出文件路径
                import time
                timestamp = int(time.time())
                video_filename = f"{filename_prefix}_{timestamp}.mp4"
                
                # 转换为MP4视频
                output_path = convert_frames_to_mp4(
                    frames=frame_paths, 
                    frame_rate=frame_rate, 
                    output_dir=output_dir, 
                    source_path=video_filename
                )
                
                logging.info(f"转换完成: {output_path}")
                return (output_path,)
                
            finally:
                # 清理临时文件
                shutil.rmtree(temp_dir, ignore_errors=True)
                
        except Exception as e:
            logging.error(f"图像序列转MP4过程出错: {e}")
            raise RuntimeError(f"转换过程出错: {e}")