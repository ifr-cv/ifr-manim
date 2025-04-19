# ifr-manim

使用 [Manim](https://docs.manim.community/) 制作代码讲解动画的内部工具。  

## 项目结构

```bash
ifr-manim/
├── serial_animation.py    # MultiHeadReader动画
├── ...
```

## Manim 使用说明

本项目基于 [Manim](https://docs.manim.community/)。  
如未安装，请使用如下方式安装：

```bash
pip install manim
```

渲染某个 Scene 的基本命令如下：

```bash
manim -qh 文件名.py 场景名
```

- `-qh` 表示渲染质量为 high（快速）
- `-qm` 为中等质量，`-ql` 为低质量（速度最快）
- 若省略场景名，Manim 会显示文件中的所有可用场景供你选择

## 当前示例

渲染当前项目中的 `MultiHeadReader` 场景：

```bash
manim -qh serial_animation.py MultiHeadReader
```
