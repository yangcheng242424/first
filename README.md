## YOLO 五分类图像分类（从 0 到可训练/可推理）

本仓库提供一个**从零搭建**的 YOLO 图像分类（5 类）训练与推理示例，基于 `ultralytics`（YOLOv8/YOLO11 体系，支持 classification 模式）。

### 1) 环境准备

- Python：建议 3.10+
- 系统：Linux / macOS / Windows 均可

安装依赖：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

### 2) 数据集组织（5 类）

把你的图片按如下目录放置（**每个类别一个文件夹**）：

```text
data/
  raw/
    class0/
      xxx.jpg
    class1/
    class2/
    class3/
    class4/
```

然后运行脚本自动划分训练/验证集（默认 8:2）：

```bash
python3 scripts/prepare_dataset.py \
  --raw_dir data/raw \
  --out_dir data/dataset \
  --val_ratio 0.2 \
  --seed 42
```

生成结果：

```text
data/dataset/
  train/
    class0/...
    class1/...
    class2/...
    class3/...
    class4/...
  val/
    class0/...
    class1/...
    class2/...
    class3/...
    class4/...
```

### 3) 训练（5 类分类）

训练命令（会自动下载分类模型权重，推荐从 `yolo11n-cls.pt` 或 `yolov8n-cls.pt` 起步）：

```bash
python3 train.py \
  --data_dir data/dataset \
  --model yolo11n-cls.pt \
  --epochs 30 \
  --imgsz 224 \
  --batch 64 \
  --device 0
```

训练输出默认在 `runs/classify/` 下。

### 4) 评估

```bash
python3 eval.py \
  --data_dir data/dataset \
  --model runs/classify/train/weights/best.pt \
  --imgsz 224 \
  --device 0
```

### 5) 单张图片推理

```bash
python3 predict.py \
  --model runs/classify/train/weights/best.pt \
  --source path/to/your.jpg \
  --imgsz 224 \
  --device 0
```

### 6) 常见问题

- **“从0-1”是什么意思？**：这里按“从零到可训练/可推理的完整闭环”实现；模型输出概率在 0~1。
- **类别数必须是 5 吗？**：不必须。你的 `data/dataset/train/` 下有几个类别文件夹，就会训练成几分类。

### 7) 参考

- Ultralytics YOLO 文档（classification）：`https://docs.ultralytics.com/`
