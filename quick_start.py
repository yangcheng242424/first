"""
YOLO快速入门示例
这个文件展示了最简单的YOLO使用方式
"""

from ultralytics import YOLO

# ============================================
# 示例1: 最简单的图片检测 (3行代码)
# ============================================
def simple_image_detection():
    """最简单的图片检测示例"""
    # 1. 加载模型 (首次运行会自动下载)
    model = YOLO('yolov8n.pt')

    # 2. 执行检测 (可以是URL或本地路径)
    results = model('https://ultralytics.com/images/bus.jpg')

    # 3. 显示结果
    results[0].show()


# ============================================
# 示例2: 获取检测结果详细信息
# ============================================
def get_detection_details():
    """获取检测结果的详细信息"""
    model = YOLO('yolov8n.pt')
    results = model('https://ultralytics.com/images/bus.jpg')

    # 遍历每个检测结果
    for result in results:
        # 获取边界框
        boxes = result.boxes

        print(f"检测到 {len(boxes)} 个目标\n")

        for box in boxes:
            # 类别ID和名称
            cls_id = int(box.cls[0])
            cls_name = model.names[cls_id]

            # 置信度
            confidence = float(box.conf[0])

            # 边界框坐标 (x1, y1, x2, y2)
            x1, y1, x2, y2 = box.xyxy[0].tolist()

            print(f"目标: {cls_name}")
            print(f"  置信度: {confidence:.2%}")
            print(f"  位置: ({x1:.0f}, {y1:.0f}) -> ({x2:.0f}, {y2:.0f})")
            print()


# ============================================
# 示例3: 检测并保存结果
# ============================================
def detect_and_save():
    """检测图片并保存结果"""
    model = YOLO('yolov8n.pt')

    # 检测图片
    results = model('https://ultralytics.com/images/zidane.jpg')

    # 保存带标注的图片
    for result in results:
        result.save('detected_result.jpg')
        print("结果已保存为 detected_result.jpg")


# ============================================
# 示例4: 使用不同大小的模型
# ============================================
def compare_models():
    """比较不同大小模型的区别"""
    # 模型大小: n < s < m < l < x
    # 速度:    快 > > > > 慢
    # 精度:    低 < < < < 高

    models = ['yolov8n', 'yolov8s', 'yolov8m']
    image_url = 'https://ultralytics.com/images/bus.jpg'

    for model_name in models:
        print(f"\n使用模型: {model_name}")
        model = YOLO(f'{model_name}.pt')
        results = model(image_url, verbose=False)
        print(f"检测到 {len(results[0].boxes)} 个目标")


# ============================================
# 示例5: 调整置信度阈值
# ============================================
def adjust_confidence():
    """演示置信度阈值的影响"""
    model = YOLO('yolov8n.pt')
    image_url = 'https://ultralytics.com/images/bus.jpg'

    thresholds = [0.25, 0.5, 0.75]

    for conf in thresholds:
        results = model(image_url, conf=conf, verbose=False)
        num_detections = len(results[0].boxes)
        print(f"置信度阈值 {conf}: 检测到 {num_detections} 个目标")


# ============================================
# 示例6: 实时摄像头检测
# ============================================
def realtime_camera():
    """使用摄像头进行实时检测"""
    import cv2

    model = YOLO('yolov8n.pt')

    # 打开摄像头
    cap = cv2.VideoCapture(0)

    print("按 'q' 退出")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 检测当前帧
        results = model(frame, verbose=False)

        # 绘制检测结果
        annotated_frame = results[0].plot()

        # 显示
        cv2.imshow('YOLO Detection', annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


# ============================================
# 主程序
# ============================================
if __name__ == '__main__':
    print("YOLO快速入门示例")
    print("=" * 50)
    print("\n可运行的示例函数:")
    print("1. simple_image_detection() - 最简单的图片检测")
    print("2. get_detection_details()  - 获取检测结果详情")
    print("3. detect_and_save()        - 检测并保存结果")
    print("4. compare_models()         - 比较不同模型")
    print("5. adjust_confidence()      - 调整置信度阈值")
    print("6. realtime_camera()        - 实时摄像头检测")
    print("\n" + "=" * 50)

    # 运行示例2展示检测详情
    print("\n运行示例: 获取检测结果详情\n")
    get_detection_details()
