import os
import logging
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict
import comfy.utils
import folder_paths
from .utils import ImageAnalyzer, FrameExtractor, convert_frames_to_mp4, check_dependencies, parse_file_paths, setup_output_directory


class WebpToMp4Converter:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "webp_files": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "placeholder": "输入WEBP文件路径，每行一个"
                }),
                "frame_rate": ("INT", {
                    "default": 20,
                    "min": 1,
                    "max": 60,
                    "step": 1,
                    "display": "slider"
                }),
            },
            "optional": {
                "output_directory": ("STRING", {
                    "default": "",
                    "placeholder": "输出目录（可选，默认使用ComfyUI输出目录）"
                })
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("video_paths",)
    FUNCTION = "convert_webp_to_mp4"
    CATEGORY = "video/conversion"
    DESCRIPTION = "将WEBP动画文件转换为MP4视频"
    
    def convert_webp_to_mp4(self, webp_files, frame_rate, output_directory=""):
        logging.info("开始WEBP到MP4转换")
        
        try:
            check_dependencies()
            
            file_paths = parse_file_paths(webp_files)
            if not file_paths:
                raise ValueError("未找到有效的WEBP文件路径")
            
            output_dir = setup_output_directory(output_directory)
            
            video_paths = []
            progress_bar = comfy.utils.ProgressBar(len(file_paths))
            
            for i, webp_path in enumerate(file_paths):
                try:
                    logging.info(f"处理文件: {webp_path}")
                    
                    image_info = ImageAnalyzer.analyze_image(webp_path)
                    if image_info['frame_count'] <= 1:
                        logging.warning(f"文件 {webp_path} 不是动画或只有一帧")
                        continue
                    
                    temp_dir = tempfile.mkdtemp()
                    try:
                        frames = FrameExtractor.extract_frames(webp_path, temp_dir)
                        if frames:
                            output_path = convert_frames_to_mp4(frames, frame_rate, output_dir, webp_path)
                            video_paths.append(output_path)
                            logging.info(f"转换完成: {output_path}")
                    finally:
                        shutil.rmtree(temp_dir, ignore_errors=True)
                    
                    progress_bar.update_absolute(i + 1, len(file_paths))
                    
                except Exception as e:
                    logging.error(f"转换失败 {webp_path}: {e}")
                    raise RuntimeError(f"WEBP转换失败 {webp_path}: {e}")
            
            if not video_paths:
                raise RuntimeError("没有文件被成功转换")
                
            logging.info(f"转换完成，共生成 {len(video_paths)} 个视频文件")
            return ("\n".join(video_paths),)
            
        except Exception as e:
            logging.error(f"WEBP转MP4转换过程出错: {e}")
            raise RuntimeError(f"转换过程出错: {e}")