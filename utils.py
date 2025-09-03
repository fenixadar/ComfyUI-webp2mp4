import os
import logging
import tempfile
from pathlib import Path
from typing import List, Dict
import folder_paths


class ImageAnalyzer:
    """分析动画图像属性和帧提取的处理类"""
    
    @staticmethod
    def analyze_image(image_path: str) -> Dict:
        """
        分析动画图像的属性
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            包含图像属性的字典：
            - size: (宽度, 高度) 元组
            - mode: 'full' 或 'partial' （完整帧 vs 部分更新）
            - frame_count: 总帧数
            - duration: 总持续时间（毫秒）
            - format: 图像格式
        """
        logging.info(f"分析图像: {image_path}")
        
        try:
            from PIL import Image, ImageSequence
        except ImportError:
            raise ImportError("需要安装PIL: pip install Pillow")
        
        with Image.open(image_path) as img:
            image_info = {
                'size': img.size,
                'mode': 'full',
                'frame_count': 1,
                'duration': 0,
                'format': img.format
            }
            
            # 检查图像是否为动画
            if not getattr(img, 'is_animated', False):
                return image_info
                
            image_info['frame_count'] = img.n_frames if hasattr(img, 'n_frames') else 0
            
            try:
                durations = []
                for frame in ImageSequence.Iterator(img):
                    durations.append(frame.info.get('duration', 0))
                    
                    # 检查部分更新
                    if frame.tile:
                        tile = frame.tile[0]
                        if tile[1][2:] != img.size:
                            image_info['mode'] = 'partial'
                            break
                
                image_info['duration'] = sum(durations)
                if image_info['frame_count'] == 0:
                    image_info['frame_count'] = len(durations)
                    
            except Exception as e:
                logging.warning(f"分析图像帧时出错: {e}")
                
        logging.debug(f"图像分析结果: {image_info}")
        return image_info


class FrameExtractor:
    """从动画图像中高效提取帧的处理类"""
    
    @staticmethod
    def extract_frames(image_path: str, output_dir: str) -> List[str]:
        """
        从动画图像中提取所有帧并保存为PNG
        
        Args:
            image_path: 源图像路径
            output_dir: 保存提取帧的目录
            
        Returns:
            提取的帧文件路径列表
        """
        logging.info(f"从以下位置提取帧: {image_path}")
        
        try:
            from PIL import Image, ImageSequence
        except ImportError:
            raise ImportError("需要安装PIL: pip install Pillow")
        
        image_info = ImageAnalyzer.analyze_image(image_path)
        if image_info['frame_count'] <= 1:
            logging.warning("图像不是动画或只包含一帧")
            return []
            
        frame_paths = []
        temp_dir = Path(output_dir)
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            with Image.open(image_path) as img:
                last_frame = img.convert('RGBA')
                
                for frame_index, frame in enumerate(ImageSequence.Iterator(img)):
                    frame_filename = temp_dir / f"{Path(image_path).stem}-{frame_index:04d}.png"
                    
                    # 处理部分帧更新
                    if image_info['mode'] == 'partial':
                        new_frame = last_frame.copy()
                        new_frame.paste(frame, (0, 0), frame.convert('RGBA'))
                    else:
                        new_frame = frame.convert('RGBA')
                    
                    new_frame.save(frame_filename, 'PNG')
                    frame_paths.append(str(frame_filename))
                    last_frame = new_frame
                    
        except Exception as e:
            logging.error(f"提取帧时出错: {e}")
            # 清理部分提取的帧
            for frame in frame_paths:
                try:
                    os.remove(frame)
                except:
                    pass
            return []
            
        logging.info(f"成功提取 {len(frame_paths)} 帧")
        return frame_paths


def convert_frames_to_mp4(frames: List[str], frame_rate: int, output_dir: str, source_path: str) -> str:
    """
    使用moviepy将帧序列转换为MP4视频
    
    Args:
        frames: 帧文件路径列表
        frame_rate: 目标帧率
        output_dir: 输出目录
        source_path: 源WEBP文件路径（用于命名）
        
    Returns:
        生成的MP4文件路径
    """
    try:
        from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
    except ImportError:
        raise ImportError("需要安装moviepy: pip install moviepy")
    
    if not frames:
        raise ValueError("没有可用的帧进行转换")
    
    # 生成输出文件名
    source_name = Path(source_path).stem
    output_path = Path(output_dir) / f"{source_name}.mp4"
    
    logging.info(f"创建视频，包含 {len(frames)} 帧，帧率 {frame_rate} FPS")
    
    try:
        # 创建视频剪辑
        clip = ImageSequenceClip(frames, fps=frame_rate)
        
        # 优化视频编码设置
        clip.write_videofile(
            str(output_path),
            codec="libx264",
            threads=4,
            preset="ultrafast",
            ffmpeg_params=["-crf", "23", "-pix_fmt", "yuv420p"],
            logger=None  # 禁用moviepy进度条
        )
        
        clip.close()
        
    except Exception as e:
        logging.error(f"视频转换失败: {e}")
        raise RuntimeError(f"视频转换失败: {e}")
    
    logging.info(f"视频转换完成: {output_path}")
    return str(output_path)


def check_dependencies():
    """检查PIL和moviepy是否可用"""
    try:
        import PIL
        import moviepy
        logging.info("依赖检查通过: PIL 和 moviepy 都可用")
    except ImportError as e:
        raise ImportError(f"缺少必需依赖: {e}. 请运行: pip install Pillow moviepy")


def parse_file_paths(file_input: str) -> List[str]:
    """解析多行文件路径输入并验证文件存在性"""
    if not file_input.strip():
        return []
    
    paths = []
    for line in file_input.strip().split('\n'):
        path = line.strip()
        if path and os.path.exists(path) and path.lower().endswith('.webp'):
            paths.append(path)
        elif path:
            logging.warning(f"文件不存在或不是WEBP格式: {path}")
    
    return paths


def setup_output_directory(output_dir: str) -> str:
    """设置输出目录，如果为空则使用ComfyUI默认输出目录"""
    if not output_dir.strip():
        output_dir = folder_paths.output_directory
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    return str(output_path)