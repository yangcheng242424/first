from __future__ import annotations

import argparse
from pathlib import Path

from ultralytics import YOLO


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="YOLO 图像分类评估（val 集）")
    p.add_argument("--data_dir", type=str, required=True, help="数据集目录，包含 train/ 与 val/ 子目录")
    p.add_argument("--model", type=str, required=True, help="训练得到的 best.pt 或分类模型权重")
    p.add_argument("--imgsz", type=int, default=224)
    p.add_argument("--batch", type=int, default=64)
    p.add_argument("--device", type=str, default="0")
    p.add_argument("--workers", type=int, default=8)
    return p


def main() -> None:
    args = build_parser().parse_args()
    data_dir = Path(args.data_dir)
    if not (data_dir / "val").is_dir():
        raise SystemExit(f"data_dir 必须包含 val/：{data_dir}")

    model = YOLO(args.model)
    metrics = model.val(
        data=str(data_dir),
        imgsz=args.imgsz,
        batch=args.batch,
        device=args.device,
        workers=args.workers,
        verbose=True,
    )

    # 关键指标打印（ultralytics 不同版本字段略有差异，尽量兼容）
    top1 = getattr(metrics, "top1", None)
    top5 = getattr(metrics, "top5", None)
    if top1 is not None:
        print(f"top1: {top1}")
    if top5 is not None:
        print(f"top5: {top5}")


if __name__ == "__main__":
    main()
