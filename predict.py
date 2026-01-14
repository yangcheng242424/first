from __future__ import annotations

import argparse
from pathlib import Path

from ultralytics import YOLO


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="YOLO 图像分类推理（单张/文件夹）")
    p.add_argument("--model", type=str, required=True, help="best.pt 或分类模型权重")
    p.add_argument("--source", type=str, required=True, help="图片路径或目录")
    p.add_argument("--imgsz", type=int, default=224)
    p.add_argument("--device", type=str, default="0")
    p.add_argument("--save", action="store_true", help="保存可视化/结果文件到 runs/")
    p.add_argument("--conf", type=float, default=0.0, help="最小置信度阈值（分类可设 0）")
    return p


def main() -> None:
    args = build_parser().parse_args()
    source = Path(args.source)
    if not source.exists():
        raise SystemExit(f"source 不存在：{source}")

    model = YOLO(args.model)
    results = model.predict(
        source=str(source),
        imgsz=args.imgsz,
        device=args.device,
        conf=args.conf,
        save=args.save,
        verbose=False,
    )

    for r in results:
        probs = getattr(r, "probs", None)
        names = getattr(r, "names", None)
        path = getattr(r, "path", None)
        if probs is None:
            print(f"{path}: (no probs)")
            continue

        top1 = int(probs.top1)
        top1conf = float(probs.top1conf)
        label = names[top1] if isinstance(names, dict) and top1 in names else str(top1)
        print(f"{path}: {label}  prob={top1conf:.4f}")


if __name__ == "__main__":
    main()
