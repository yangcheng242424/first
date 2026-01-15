"""离线推理脚本 - 绕过 Ultralytics 网络检查"""
from __future__ import annotations

import argparse
from pathlib import Path

import torch
from torchvision import transforms
from PIL import Image


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="离线推理 YOLO 分类模型")
    p.add_argument("--model", type=str, required=True, help="best.pt 路径")
    p.add_argument("--source", type=str, required=True, help="图片路径或目录")
    p.add_argument("--imgsz", type=int, default=224)
    return p


# CIFAR-10 类别名称
CIFAR10_CLASSES = ['airplane', 'automobile', 'bird', 'cat', 'deer',
                   'dog', 'frog', 'horse', 'ship', 'truck']


def predict_image(model, image_path: Path, transform, names: list) -> tuple:
    """预测单张图片"""
    img = Image.open(image_path).convert('RGB')
    img_tensor = transform(img).unsqueeze(0)

    with torch.no_grad():
        outputs = model(img_tensor)
        if isinstance(outputs, tuple):
            outputs = outputs[0]

        probs = torch.softmax(outputs, dim=1)
        confidence, pred_idx = probs.max(1)

    return names[pred_idx.item()], confidence.item()


def main() -> None:
    args = build_parser().parse_args()

    # 加载模型
    print(f"加载模型: {args.model}")
    ckpt = torch.load(args.model, map_location="cpu", weights_only=False)
    model = ckpt["model"].float().eval()

    # 获取类别名称
    names = ckpt.get("names", {})
    if isinstance(names, dict) and len(names) > 0:
        names = [names[i] for i in range(len(names))]
    else:
        names = CIFAR10_CLASSES
    print(f"类别: {names}")

    # 数据预处理
    transform = transforms.Compose([
        transforms.Resize((args.imgsz, args.imgsz)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    source = Path(args.source)
    if not source.exists():
        raise SystemExit(f"路径不存在: {source}")

    # 收集图片
    if source.is_file():
        images = [source]
    else:
        images = list(source.glob("*.jpg")) + list(source.glob("*.png")) + list(source.glob("*.jpeg"))

    if not images:
        raise SystemExit(f"未找到图片: {source}")

    print(f"\n{'='*50}")
    print(f"预测结果:")
    print(f"{'='*50}")

    for img_path in images:
        label, conf = predict_image(model, img_path, transform, names)
        print(f"{img_path.name}: {label} (置信度: {conf:.2%})")

    print(f"{'='*50}")
    print(f"共预测 {len(images)} 张图片")


if __name__ == "__main__":
    main()
