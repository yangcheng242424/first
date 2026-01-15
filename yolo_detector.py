"""
YOLO目标检测探索脚本
使用ultralytics库实现YOLOv8目标检测

功能:
1. 图片检测 - 检测单张或多张图片中的目标
2. 视频检测 - 检测视频文件中的目标
3. 实时摄像头检测 - 使用摄像头进行实时目标检测
4. 结果保存 - 保存检测结果图片和标注信息
"""

import os
import cv2
import argparse
from pathlib import Path
from ultralytics import YOLO


class YOLODetector:
    """YOLO目标检测器类"""

    # 可用的预训练模型
    AVAILABLE_MODELS = {
        'yolov8n': 'yolov8n.pt',  # Nano - 最快，精度较低
        'yolov8s': 'yolov8s.pt',  # Small - 快速，精度适中
        'yolov8m': 'yolov8m.pt',  # Medium - 平衡速度和精度
        'yolov8l': 'yolov8l.pt',  # Large - 较慢，精度较高
        'yolov8x': 'yolov8x.pt',  # Extra Large - 最慢，精度最高
    }

    def __init__(self, model_name='yolov8n', confidence=0.5):
        """
        初始化YOLO检测器

        Args:
            model_name: 模型名称，可选 yolov8n/s/m/l/x
            confidence: 置信度阈值，默认0.5
        """
        self.model_name = model_name
        self.confidence = confidence

        # 加载模型
        model_file = self.AVAILABLE_MODELS.get(model_name, 'yolov8n.pt')
        print(f"正在加载模型: {model_file}")
        self.model = YOLO(model_file)
        print(f"模型加载完成! 共有 {len(self.model.names)} 个类别")

    def get_class_names(self):
        """获取所有可检测的类别名称"""
        return self.model.names

    def detect_image(self, image_path, save_dir='results', show=True):
        """
        检测单张图片

        Args:
            image_path: 图片路径
            save_dir: 结果保存目录
            show: 是否显示结果

        Returns:
            检测结果列表
        """
        print(f"\n正在检测图片: {image_path}")

        # 执行检测
        results = self.model(image_path, conf=self.confidence)

        # 处理结果
        for result in results:
            # 获取检测到的目标信息
            boxes = result.boxes
            if len(boxes) > 0:
                print(f"\n检测到 {len(boxes)} 个目标:")
                for i, box in enumerate(boxes):
                    cls_id = int(box.cls[0])
                    cls_name = self.model.names[cls_id]
                    conf = float(box.conf[0])
                    xyxy = box.xyxy[0].tolist()
                    print(f"  [{i+1}] {cls_name}: 置信度 {conf:.2%}, 位置 {xyxy}")
            else:
                print("未检测到目标")

            # 保存结果
            os.makedirs(save_dir, exist_ok=True)
            save_path = os.path.join(save_dir, Path(image_path).name)
            result.save(save_path)
            print(f"结果已保存至: {save_path}")

            # 显示结果
            if show:
                result.show()

        return results

    def detect_images(self, image_dir, save_dir='results', show=False):
        """
        批量检测目录下的所有图片

        Args:
            image_dir: 图片目录
            save_dir: 结果保存目录
            show: 是否显示结果

        Returns:
            所有检测结果
        """
        # 支持的图片格式
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp'}

        # 获取所有图片
        image_paths = []
        for ext in image_extensions:
            image_paths.extend(Path(image_dir).glob(f'*{ext}'))
            image_paths.extend(Path(image_dir).glob(f'*{ext.upper()}'))

        print(f"\n找到 {len(image_paths)} 张图片")

        all_results = []
        for img_path in image_paths:
            results = self.detect_image(str(img_path), save_dir, show)
            all_results.extend(results)

        return all_results

    def detect_video(self, video_path, save_dir='results', show=True):
        """
        检测视频文件

        Args:
            video_path: 视频路径
            save_dir: 结果保存目录
            show: 是否实时显示
        """
        print(f"\n正在检测视频: {video_path}")

        # 打开视频
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"无法打开视频: {video_path}")
            return

        # 获取视频信息
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        print(f"视频信息: {width}x{height}, {fps}fps, 共{total_frames}帧")

        # 设置输出视频
        os.makedirs(save_dir, exist_ok=True)
        output_path = os.path.join(save_dir, f"detected_{Path(video_path).name}")
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        frame_count = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1

            # 检测当前帧
            results = self.model(frame, conf=self.confidence, verbose=False)

            # 绘制结果
            annotated_frame = results[0].plot()

            # 写入输出视频
            out.write(annotated_frame)

            # 显示进度
            if frame_count % 30 == 0:
                print(f"处理进度: {frame_count}/{total_frames} ({frame_count/total_frames*100:.1f}%)")

            # 显示结果
            if show:
                cv2.imshow('YOLO Detection', annotated_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("用户中断")
                    break

        cap.release()
        out.release()
        cv2.destroyAllWindows()

        print(f"\n视频检测完成! 结果已保存至: {output_path}")

    def detect_camera(self, camera_id=0, save_video=False, save_dir='results'):
        """
        实时摄像头检测

        Args:
            camera_id: 摄像头ID，默认0
            save_video: 是否保存检测视频
            save_dir: 保存目录
        """
        print(f"\n启动摄像头 {camera_id} 进行实时检测...")
        print("按 'q' 退出, 按 's' 截图保存")

        cap = cv2.VideoCapture(camera_id)
        if not cap.isOpened():
            print(f"无法打开摄像头 {camera_id}")
            return

        # 设置摄像头参数
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30

        print(f"摄像头分辨率: {width}x{height}, {fps}fps")

        # 视频写入器
        out = None
        if save_video:
            os.makedirs(save_dir, exist_ok=True)
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(save_dir, f"camera_{timestamp}.mp4")
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            print(f"录制视频至: {output_path}")

        screenshot_count = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                print("无法读取摄像头帧")
                break

            # 检测
            results = self.model(frame, conf=self.confidence, verbose=False)

            # 绘制结果
            annotated_frame = results[0].plot()

            # 添加FPS显示
            # (可选) 计算并显示实时FPS

            # 保存视频
            if out:
                out.write(annotated_frame)

            # 显示
            cv2.imshow('YOLO Real-time Detection (Press q to quit)', annotated_frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                # 截图保存
                os.makedirs(save_dir, exist_ok=True)
                screenshot_count += 1
                screenshot_path = os.path.join(save_dir, f"screenshot_{screenshot_count}.jpg")
                cv2.imwrite(screenshot_path, annotated_frame)
                print(f"截图已保存: {screenshot_path}")

        cap.release()
        if out:
            out.release()
        cv2.destroyAllWindows()
        print("摄像头检测已停止")

    def export_model(self, format='onnx'):
        """
        导出模型到其他格式

        Args:
            format: 目标格式，支持 onnx, torchscript, openvino, engine 等
        """
        print(f"\n正在导出模型为 {format} 格式...")
        self.model.export(format=format)
        print("模型导出完成!")


def demo_detection():
    """
    演示检测功能 - 使用示例图片
    """
    print("=" * 60)
    print("YOLO目标检测演示")
    print("=" * 60)

    # 初始化检测器
    detector = YOLODetector(model_name='yolov8n', confidence=0.5)

    # 显示可检测的类别
    print("\n可检测的目标类别:")
    names = detector.get_class_names()
    for i, name in names.items():
        print(f"  {i}: {name}")

    # 检测示例
    print("\n" + "=" * 60)
    print("演示功能:")
    print("1. 图片检测: detector.detect_image('path/to/image.jpg')")
    print("2. 批量检测: detector.detect_images('path/to/image_dir/')")
    print("3. 视频检测: detector.detect_video('path/to/video.mp4')")
    print("4. 实时检测: detector.detect_camera()")
    print("=" * 60)

    return detector


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description='YOLO目标检测工具')
    parser.add_argument('--mode', type=str, default='demo',
                        choices=['demo', 'image', 'images', 'video', 'camera'],
                        help='检测模式: demo/image/images/video/camera')
    parser.add_argument('--source', type=str, default=None,
                        help='输入源: 图片路径/目录/视频路径/摄像头ID')
    parser.add_argument('--model', type=str, default='yolov8n',
                        choices=['yolov8n', 'yolov8s', 'yolov8m', 'yolov8l', 'yolov8x'],
                        help='模型大小')
    parser.add_argument('--conf', type=float, default=0.5,
                        help='置信度阈值 (0-1)')
    parser.add_argument('--save-dir', type=str, default='results',
                        help='结果保存目录')
    parser.add_argument('--no-show', action='store_true',
                        help='不显示检测结果')
    parser.add_argument('--save-video', action='store_true',
                        help='摄像头模式下保存视频')

    args = parser.parse_args()

    # 初始化检测器
    detector = YOLODetector(model_name=args.model, confidence=args.conf)

    if args.mode == 'demo':
        demo_detection()
    elif args.mode == 'image':
        if args.source is None:
            print("请指定图片路径: --source path/to/image.jpg")
            return
        detector.detect_image(args.source, args.save_dir, show=not args.no_show)
    elif args.mode == 'images':
        if args.source is None:
            print("请指定图片目录: --source path/to/images/")
            return
        detector.detect_images(args.source, args.save_dir, show=not args.no_show)
    elif args.mode == 'video':
        if args.source is None:
            print("请指定视频路径: --source path/to/video.mp4")
            return
        detector.detect_video(args.source, args.save_dir, show=not args.no_show)
    elif args.mode == 'camera':
        camera_id = int(args.source) if args.source else 0
        detector.detect_camera(camera_id, save_video=args.save_video, save_dir=args.save_dir)


if __name__ == '__main__':
    main()
