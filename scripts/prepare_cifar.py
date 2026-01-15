from __future__ import annotations

import argparse
import pickle
import shutil
from pathlib import Path

import numpy as np
from PIL import Image
from tqdm import tqdm


# CIFAR-10 类别名
CIFAR10_CLASSES = [
    "airplane", "automobile", "bird", "cat", "deer",
    "dog", "frog", "horse", "ship", "truck"
]


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="将 CIFAR 数据集转换为 YOLO classification 目录结构 (train/val/<class>/...)"
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
        "--local_cifar_dir",
        type=str,
        default=None,
        help="本地 CIFAR 数据目录（如 data/cifar-10-batches-py），如果提供则从本地加载",
    )
    p.add_argument(
        "--download_dir",
        type=str,
        default="data/_downloads",
        help="torchvision 下载缓存目录（仅当不使用 --local_cifar_dir 时生效）",
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


def _load_cifar10_batch(filepath: Path) -> tuple[np.ndarray, list[int]]:
    """加载单个 CIFAR-10 batch 文件"""
    with open(filepath, "rb") as f:
        batch = pickle.load(f, encoding="bytes")
    # CIFAR-10 数据格式: (N, 3072) -> (N, 3, 32, 32)
    data = batch[b"data"].reshape(-1, 3, 32, 32).transpose(0, 2, 3, 1)
    labels = batch[b"labels"]
    return data, labels


def _save_split_from_local(
    local_dir: Path, split: str, out_root: Path, class_names: list[str]
) -> None:
    """从本地 CIFAR-10 数据加载并保存"""
    # 创建类别目录
    for cn in class_names:
        (out_root / split / cn).mkdir(parents=True, exist_ok=True)

    if split == "train":
        # 训练集：data_batch_1 到 data_batch_5
        batch_files = [local_dir / f"data_batch_{i}" for i in range(1, 6)]
    else:
        # 验证集：test_batch
        batch_files = [local_dir / "test_batch"]

    global_idx = 0
    for batch_file in batch_files:
        if not batch_file.exists():
            raise FileNotFoundError(f"找不到文件: {batch_file}")

        data, labels = _load_cifar10_batch(batch_file)

        for img_data, label in tqdm(
            zip(data, labels),
            desc=f"cifar10:{split}:{batch_file.name}",
            total=len(labels),
            unit="img"
        ):
            cls_name = class_names[label]
            img = Image.fromarray(img_data)
            img_path = out_root / split / cls_name / f"{global_idx:05d}.png"
            img.save(img_path)
            global_idx += 1


def _save_split(dataset_name: str, split: str, root: Path, out_root: Path) -> None:
    """使用 torchvision 下载并保存"""
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

    out_dir = Path(args.out_dir)

    if args.clear and out_dir.exists():
        shutil.rmtree(out_dir)

    (out_dir / "train").mkdir(parents=True, exist_ok=True)
    (out_dir / "val").mkdir(parents=True, exist_ok=True)

    if args.local_cifar_dir:
        # 从本地目录加载 CIFAR 数据
        local_dir = Path(args.local_cifar_dir)
        if not local_dir.exists():
            raise SystemExit(f"本地 CIFAR 目录不存在: {local_dir}")

        if args.dataset == "cifar10":
            class_names = CIFAR10_CLASSES
            print(f"从本地加载 CIFAR-10 数据: {local_dir}")
            _save_split_from_local(local_dir, "train", out_dir, class_names)
            _save_split_from_local(local_dir, "val", out_dir, class_names)
        else:
            raise SystemExit("本地加载暂时只支持 CIFAR-10，CIFAR-100 请使用 torchvision 下载")
    else:
        # 使用 torchvision 下载
        _ensure_torchvision()
        download_dir = Path(args.download_dir)
        download_dir.mkdir(parents=True, exist_ok=True)

        # CIFAR 的 test split 更适合作为 val，这里用 train/test -> train/val
        _save_split(args.dataset, "train", download_dir, out_dir)
        _save_split(args.dataset, "val", download_dir, out_dir)

    print(f"Done. YOLO classification dataset ready at: {out_dir}")
    print("You can train with: python3 train.py --data_dir <out_dir>")


if __name__ == "__main__":
    main()
