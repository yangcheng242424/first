from __future__ import annotations

import argparse
import random
import shutil
from pathlib import Path

from tqdm import tqdm


IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def is_image(p: Path) -> bool:
    return p.is_file() and p.suffix.lower() in IMG_EXTS


def copy_files(files: list[Path], dst_dir: Path) -> None:
    dst_dir.mkdir(parents=True, exist_ok=True)
    for f in files:
        shutil.copy2(f, dst_dir / f.name)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="把 raw/ 按类别划分为 train/val（YOLO 分类数据格式）")
    p.add_argument("--raw_dir", type=str, required=True, help="原始数据目录，子目录为各类别")
    p.add_argument("--out_dir", type=str, required=True, help="输出目录，将生成 train/ 和 val/")
    p.add_argument("--val_ratio", type=float, default=0.2, help="验证集比例 (0~1)")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--clear", action="store_true", help="清空 out_dir 后再生成")
    return p


def main() -> None:
    args = build_parser().parse_args()
    raw_dir = Path(args.raw_dir)
    out_dir = Path(args.out_dir)

    if not raw_dir.is_dir():
        raise SystemExit(f"raw_dir 不存在或不是目录：{raw_dir}")
    if not (0.0 < args.val_ratio < 1.0):
        raise SystemExit("--val_ratio 必须在 (0,1) 内")

    if args.clear and out_dir.exists():
        shutil.rmtree(out_dir)

    train_root = out_dir / "train"
    val_root = out_dir / "val"
    train_root.mkdir(parents=True, exist_ok=True)
    val_root.mkdir(parents=True, exist_ok=True)

    class_dirs = [p for p in raw_dir.iterdir() if p.is_dir()]
    class_dirs.sort(key=lambda p: p.name)
    if len(class_dirs) == 0:
        raise SystemExit(f"raw_dir 下未发现任何类别子目录：{raw_dir}")

    random.seed(args.seed)
    for cdir in class_dirs:
        images = [p for p in cdir.rglob("*") if is_image(p)]
        images.sort()
        if len(images) == 0:
            print(f"[WARN] 类别 {cdir.name} 没有图片，跳过")
            continue

        random.shuffle(images)
        n_val = max(1, int(len(images) * args.val_ratio))
        val_files = images[:n_val]
        train_files = images[n_val:]
        if len(train_files) == 0:
            # 极端小样本：保证 train 至少 1 张
            train_files = val_files[:1]
            val_files = val_files[1:] if len(val_files) > 1 else val_files

        print(f"{cdir.name}: train={len(train_files)} val={len(val_files)} total={len(images)}")
        copy_files(train_files, train_root / cdir.name)
        copy_files(val_files, val_root / cdir.name)

    # 简单统计
    total_train = sum(1 for p in train_root.rglob("*") if is_image(p))
    total_val = sum(1 for p in val_root.rglob("*") if is_image(p))
    print(f"Done. train_images={total_train}, val_images={total_val}, out_dir={out_dir}")


if __name__ == "__main__":
    main()
