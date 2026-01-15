"""
YOLO实例分割(Instance Segmentation)探索脚本

分割 vs 检测的区别:
- 检测(Detection): 用矩形框标出物体位置
- 分割(Segmentation): 精确标出物体的轮廓/形状

使用方法:
    python yolo_segmentation.py --mode image --source your_image.jpg
    python yolo_segmentation.py --mode video --source your_video.mp4
    python yolo_segmentation.py --mode camera
"""

import os
import cv2
import argparse
import numpy as np
from pathlib import Path
from ultralytics import YOLO


class YOLOSegmenter:
    """YOLO实例分割器类"""

    # 分割模型 (注意是 -seg 后缀)
    AVAILABLE_MODELS = {
        'yolov8n-seg': 'yolov8n-seg.pt',  # Nano - 最快
        'yolov8s-seg': 'yolov8s-seg.pt',  # Small
        'yolov8m-seg': 'yolov8m-seg.pt',  # Medium
        'yolov8l-seg': 'yolov8l-seg.pt',  # Large
        'yolov8x-seg': 'yolov8x-seg.pt',  # Extra Large - 最精确
    }

    def __init__(self, model_name='yolov8n-seg', confidence=0.5):
        """
        初始化YOLO分割器

        Args:
            model_name: 模型名称，可选 yolov8n-seg/s-seg/m-seg/l-seg/x-seg
            confidence: 置信度阈值
        """
        self.model_name = model_name
        self.confidence = confidence

        model_file = self.AVAILABLE_MODELS.get(model_name, 'yolov8n-seg.pt')
        print(f"正在加载分割模型: {model_file}")
        self.model = YOLO(model_file)
        print(f"模型加载完成! 共有 {len(self.model.names)} 个类别")

    def segment_image(self, image_path, save_dir='results_seg', show=True):
        """
        分割单张图片

        Args:
            image_path: 图片路径
            save_dir: 结果保存目录
            show: 是否显示结果
        """
        print(f"\n正在分割图片: {image_path}")

        # 执行分割
        results = self.model(image_path, conf=self.confidence)

        for result in results:
            # 获取分割掩码
            if result.masks is not None:
                masks = result.masks
                boxes = result.boxes

                print(f"\n分割到 {len(masks)} 个目标:")

                for i, (mask, box) in enumerate(zip(masks, boxes)):
                    cls_id = int(box.cls[0])
                    cls_name = self.model.names[cls_id]
                    conf = float(box.conf[0])

                    # 掩码面积 (像素数)
                    mask_area = mask.data.sum().item()

                    print(f"  [{i+1}] {cls_name}: 置信度 {conf:.2%}, 掩码面积 {mask_area:.0f} 像素")
            else:
                print("未分割到目标")

            # 保存结果
            os.makedirs(save_dir, exist_ok=True)
            save_path = os.path.join(save_dir, f"seg_{Path(image_path).name}")
            result.save(save_path)
            print(f"结果已保存至: {save_path}")

            # 显示结果
            if show:
                result.show()

        return results

    def segment_image_custom(self, image_path, save_dir='results_seg',
                             show_masks_only=False, mask_alpha=0.5):
        """
        自定义分割可视化

        Args:
            image_path: 图片路径
            save_dir: 保存目录
            show_masks_only: 只显示掩码(不显示原图)
            mask_alpha: 掩码透明度
        """
        print(f"\n自定义分割: {image_path}")

        # 读取原图
        image = cv2.imread(image_path)
        if image is None:
            print(f"无法读取图片: {image_path}")
            return

        # 执行分割
        results = self.model(image, conf=self.confidence)

        for result in results:
            if result.masks is None:
                print("未检测到目标")
                continue

            # 创建彩色掩码图
            mask_image = np.zeros_like(image)

            # 随机颜色列表
            colors = [
                (255, 0, 0), (0, 255, 0), (0, 0, 255),
                (255, 255, 0), (255, 0, 255), (0, 255, 255),
                (128, 255, 0), (255, 128, 0), (128, 0, 255),
            ]

            masks = result.masks
            boxes = result.boxes

            for i, (mask, box) in enumerate(zip(masks, boxes)):
                # 获取掩码数据
                mask_data = mask.data.cpu().numpy()[0]

                # 调整掩码大小以匹配原图
                mask_resized = cv2.resize(mask_data, (image.shape[1], image.shape[0]))

                # 选择颜色
                color = colors[i % len(colors)]

                # 应用颜色到掩码区域
                mask_image[mask_resized > 0.5] = color

                # 获取类别信息
                cls_id = int(box.cls[0])
                cls_name = self.model.names[cls_id]
                conf = float(box.conf[0])

                # 在掩码上添加标签
                xyxy = box.xyxy[0].cpu().numpy()
                x1, y1 = int(xyxy[0]), int(xyxy[1])
                label = f"{cls_name} {conf:.2f}"
                cv2.putText(mask_image, label, (x1, y1 - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

            # 合成结果
            if show_masks_only:
                output = mask_image
            else:
                output = cv2.addWeighted(image, 1 - mask_alpha, mask_image, mask_alpha, 0)

            # 保存
            os.makedirs(save_dir, exist_ok=True)
            save_path = os.path.join(save_dir, f"custom_seg_{Path(image_path).name}")
            cv2.imwrite(save_path, output)
            print(f"自定义分割结果已保存: {save_path}")

            # 显示
            cv2.imshow('Custom Segmentation', output)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        return results

    def segment_video(self, video_path, save_dir='results_seg', show=True):
        """
        分割视频

        Args:
            video_path: 视频路径
            save_dir: 保存目录
            show: 是否实时显示
        """
        print(f"\n正在分割视频: {video_path}")

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"无法打开视频: {video_path}")
            return

        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        print(f"视频信息: {width}x{height}, {fps}fps, 共{total_frames}帧")

        os.makedirs(save_dir, exist_ok=True)
        output_path = os.path.join(save_dir, f"seg_{Path(video_path).name}")
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        frame_count = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1

            # 分割当前帧
            results = self.model(frame, conf=self.confidence, verbose=False)

            # 绘制结果
            annotated_frame = results[0].plot()

            out.write(annotated_frame)

            if frame_count % 30 == 0:
                print(f"处理进度: {frame_count}/{total_frames} ({frame_count/total_frames*100:.1f}%)")

            if show:
                cv2.imshow('YOLO Segmentation', annotated_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("用户中断")
                    break

        cap.release()
        out.release()
        cv2.destroyAllWindows()

        print(f"\n视频分割完成! 结果已保存至: {output_path}")

    def segment_camera(self, camera_id=0, save_dir='results_seg'):
        """
        实时摄像头分割

        Args:
            camera_id: 摄像头ID
            save_dir: 截图保存目录
        """
        print(f"\n启动摄像头 {camera_id} 进行实时分割...")
        print("按 'q' 退出, 按 's' 截图")

        cap = cv2.VideoCapture(camera_id)
        if not cap.isOpened():
            print(f"无法打开摄像头 {camera_id}")
            return

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        screenshot_count = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # 分割
            results = self.model(frame, conf=self.confidence, verbose=False)

            # 绘制结果
            annotated_frame = results[0].plot()

            cv2.imshow('YOLO Segmentation (Press q to quit)', annotated_frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                os.makedirs(save_dir, exist_ok=True)
                screenshot_count += 1
                path = os.path.join(save_dir, f"seg_screenshot_{screenshot_count}.jpg")
                cv2.imwrite(path, annotated_frame)
                print(f"截图已保存: {path}")

        cap.release()
        cv2.destroyAllWindows()
        print("摄像头分割已停止")

    def extract_masks(self, image_path, save_dir='masks'):
        """
        提取并保存每个目标的单独掩码

        Args:
            image_path: 图片路径
            save_dir: 掩码保存目录
        """
        print(f"\n提取掩码: {image_path}")

        image = cv2.imread(image_path)
        results = self.model(image, conf=self.confidence)

        os.makedirs(save_dir, exist_ok=True)

        for result in results:
            if result.masks is None:
                print("未检测到目标")
                return

            masks = result.masks
            boxes = result.boxes

            print(f"提取到 {len(masks)} 个掩码")

            for i, (mask, box) in enumerate(zip(masks, boxes)):
                cls_id = int(box.cls[0])
                cls_name = self.model.names[cls_id]

                # 获取掩码
                mask_data = mask.data.cpu().numpy()[0]
                mask_resized = cv2.resize(mask_data, (image.shape[1], image.shape[0]))

                # 转为二值图
                binary_mask = (mask_resized > 0.5).astype(np.uint8) * 255

                # 保存掩码
                mask_path = os.path.join(save_dir, f"mask_{i+1}_{cls_name}.png")
                cv2.imwrite(mask_path, binary_mask)

                # 提取目标区域 (带透明背景)
                # 创建4通道图像 (BGRA)
                rgba = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
                rgba[:, :, 3] = binary_mask  # 设置alpha通道

                extracted_path = os.path.join(save_dir, f"extracted_{i+1}_{cls_name}.png")
                cv2.imwrite(extracted_path, rgba)

                print(f"  已保存: {cls_name} -> {mask_path}")

        print(f"\n所有掩码已保存至: {save_dir}")


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description='YOLO实例分割工具')
    parser.add_argument('--mode', type=str, default='image',
                        choices=['image', 'video', 'camera', 'extract'],
                        help='分割模式')
    parser.add_argument('--source', type=str, required=False,
                        help='输入源')
    parser.add_argument('--model', type=str, default='yolov8n-seg',
                        choices=['yolov8n-seg', 'yolov8s-seg', 'yolov8m-seg',
                                'yolov8l-seg', 'yolov8x-seg'],
                        help='模型大小')
    parser.add_argument('--conf', type=float, default=0.5,
                        help='置信度阈值')
    parser.add_argument('--save-dir', type=str, default='results_seg',
                        help='保存目录')
    parser.add_argument('--no-show', action='store_true',
                        help='不显示结果')

    args = parser.parse_args()

    # 初始化分割器
    segmenter = YOLOSegmenter(model_name=args.model, confidence=args.conf)

    if args.mode == 'image':
        if args.source is None:
            print("请指定图片路径: --source path/to/image.jpg")
            return
        segmenter.segment_image(args.source, args.save_dir, show=not args.no_show)

    elif args.mode == 'video':
        if args.source is None:
            print("请指定视频路径: --source path/to/video.mp4")
            return
        segmenter.segment_video(args.source, args.save_dir, show=not args.no_show)

    elif args.mode == 'camera':
        camera_id = int(args.source) if args.source else 0
        segmenter.segment_camera(camera_id, args.save_dir)

    elif args.mode == 'extract':
        if args.source is None:
            print("请指定图片路径: --source path/to/image.jpg")
            return
        segmenter.extract_masks(args.source, args.save_dir)


if __name__ == '__main__':
    main()
