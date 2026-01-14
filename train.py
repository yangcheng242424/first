from __future__ import annotations

import argparse
from pathlib import Path

from ultralytics import YOLO


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="YOLO 图像分类训练（5 类/多类均可）")
    p.add_argument("--data_dir", type=str, required=True, help="数据集目录，包含 train/ 与 val/ 子目录")
    p.add_argument("--model", type=str, default="yolo11n-cls.pt", help="分类模型权重或模型名")
    p.add_argument("--epochs", type=int, default=30)
    p.add_argument("--imgsz", type=int, default=224)
    p.add_argument("--batch", type=int, default=64)
    p.add_argument("--device", type=str, default="0", help="例如 0 / 0,1 / cpu")
    p.add_argument("--workers", type=int, default=8)
    p.add_argument("--project", type=str, default="runs/classify")
    p.add_argument("--name", type=str, default="train")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--patience", type=int, default=20)
    return p


def main() -> None:
    args = build_parser().parse_args()

    data_dir = Path(args.data_dir)
    train_dir = data_dir / "train"
    val_dir = data_dir / "val"
    if not train_dir.is_dir() or not val_dir.is_dir():
        raise SystemExit(f"data_dir 必须包含 train/ 与 val/：{data_dir}")

    model = YOLO(args.model)
    model.train(
        data=str(data_dir),
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        device=args.device,
        workers=args.workers,
        project=args.project,
        name=args.name,
        seed=args.seed,
        patience=args.patience,
        verbose=True,
    )


if __name__ == "__main__":
    main()
