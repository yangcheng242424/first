from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from tqdm import tqdm


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="下载 CIFAR 并转换为 YOLO classification 目录结构 (train/val/<class>/...)"
    )
    p.add_argument(
        "--dataset",
        type=str,
        default="cifar10",
        choices=["cifar10", "cifar100"],
        help="选择 CIFAR-10 或 CIFAR-100",
    )
    p.add_argument(
        "--out_dir",
        type=str,
        default="data/cifar",
        help="输出目录，将生成 train/ 与 val/ 子目录",
    )
    p.add_argument(
        "--download_dir",
        type=str,
        default="data/_downloads",
        help="torchvision 下载缓存目录（可重复使用）",
    )
    p.add_argument("--clear", action="store_true", help="清空 out_dir 后再生成")
    return p


def _ensure_torchvision() -> None:
    try:
        import torchvision  # noqa: F401
    except Exception as e:  # pragma: no cover
        raise SystemExit(
            "缺少 torchvision。请先安装依赖：pip install -r requirements.txt"
        ) from e


def _save_split(dataset_name: str, split: str, root: Path, out_root: Path) -> None:
    from torchvision.datasets import CIFAR10, CIFAR100

    ds_cls = CIFAR10 if dataset_name == "cifar10" else CIFAR100
    is_train = split == "train"
    ds = ds_cls(root=str(root), train=is_train, download=True)

    # 类别名
    class_names = list(ds.classes)
    for cn in class_names:
        (out_root / split / cn).mkdir(parents=True, exist_ok=True)

    # 保存图片到对应类别文件夹
    for idx in tqdm(range(len(ds)), desc=f"{dataset_name}:{split}", unit="img"):
        img, label = ds[idx]  # PIL.Image
        cls_name = class_names[int(label)]
        # CIFAR 原始分辨率 32x32；直接保存为 png 即可
        img_path = out_root / split / cls_name / f"{idx:05d}.png"
        img.save(img_path)


def main() -> None:
    args = build_parser().parse_args()
    _ensure_torchvision()

    out_dir = Path(args.out_dir)
    download_dir = Path(args.download_dir)

    if args.clear and out_dir.exists():
        shutil.rmtree(out_dir)

    (out_dir / "train").mkdir(parents=True, exist_ok=True)
    (out_dir / "val").mkdir(parents=True, exist_ok=True)
    download_dir.mkdir(parents=True, exist_ok=True)

    # CIFAR 的 test split 更适合作为 val，这里用 train/test -> train/val
    _save_split(args.dataset, "train", download_dir, out_dir)
    _save_split(args.dataset, "val", download_dir, out_dir)

    print(f"Done. YOLO classification dataset ready at: {out_dir}")
    print("You can train with: python3 train.py --data_dir <out_dir>")


if __name__ == "__main__":
    main()
