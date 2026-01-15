"""离线评估脚本 - 绕过 Ultralytics 网络检查"""
from __future__ import annotations

import argparse
from pathlib import Path

import torch
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from tqdm import tqdm


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="离线评估 YOLO 分类模型")
    p.add_argument("--data_dir", type=str, required=True, help="数据集目录")
    p.add_argument("--model", type=str, required=True, help="best.pt 路径")
    p.add_argument("--imgsz", type=int, default=224)
    p.add_argument("--batch", type=int, default=64)
    return p


def main() -> None:
    args = build_parser().parse_args()

    # 加载模型
    print(f"加载模型: {args.model}")
    ckpt = torch.load(args.model, map_location="cpu", weights_only=False)
    model = ckpt["model"].float().eval()

    # 获取类别名称
    names = ckpt.get("names", {})
    print(f"类别: {names}")

    # 数据预处理
    transform = transforms.Compose([
        transforms.Resize((args.imgsz, args.imgsz)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    # 加载验证集
    val_dir = Path(args.data_dir) / "val"
    if not val_dir.is_dir():
        raise SystemExit(f"验证集目录不存在: {val_dir}")

    val_dataset = datasets.ImageFolder(str(val_dir), transform=transform)
    val_loader = DataLoader(val_dataset, batch_size=args.batch, shuffle=False, num_workers=0)

    print(f"验证集样本数: {len(val_dataset)}")
    print(f"验证集类别: {val_dataset.classes}")

    # 评估
    correct_top1 = 0
    correct_top5 = 0
    total = 0

    with torch.no_grad():
        for images, labels in tqdm(val_loader, desc="评估中"):
            outputs = model(images)

            # 处理不同的输出格式
            if isinstance(outputs, tuple):
                outputs = outputs[0]
            if hasattr(outputs, 'data'):
                outputs = outputs.data

            # Top-1
            _, pred = outputs.max(1)
            correct_top1 += pred.eq(labels).sum().item()

            # Top-5
            _, pred5 = outputs.topk(min(5, outputs.size(1)), 1, True, True)
            correct_top5 += pred5.eq(labels.view(-1, 1).expand_as(pred5)).any(1).sum().item()

            total += labels.size(0)

    top1_acc = 100.0 * correct_top1 / total
    top5_acc = 100.0 * correct_top5 / total

    print(f"\n{'='*40}")
    print(f"评估结果:")
    print(f"  Top-1 准确率: {top1_acc:.2f}%")
    print(f"  Top-5 准确率: {top5_acc:.2f}%")
    print(f"  总样本数: {total}")
    print(f"{'='*40}")


if __name__ == "__main__":
    main()
