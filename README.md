# Rubin Cue Stimuli

实验交接用刺激库：8 套轮廓 × 30 个条件，共 240 张 PNG。
新增 bird、dog、woman、macaque 四套，与原有四套一起放在 `images/`，
按来源分为 8 套，每套再按背景颜色分黑、灰、白三组，每组 10 张。

| 文件 | 用途 |
| --- | --- |
| `images/<set_name>/background-<color>/*.png` | 每套按背景颜色分组，1024 × 1024，8-bit 灰度，无内置注视点 |
| [stimuli.csv](stimuli.csv) | 图片路径、来源、条件标签、尺寸和 SHA-256，一图一行 |
| [SOURCES.md](SOURCES.md) | 来源、署名与已知许可信息 |

## 清单和条件

`stimulus_id` 是不含扩展名的完整文件名；`image_path` 相对于仓库根目录。
刺激标识不是试次号或硬件事件码。CSV 是索引，不是 MonkeyLogic conditions 文件。
MATLAB 可用 `readtable('stimuli.csv','TextType','string')` 读取。

文件夹使用简短的 `set_name`；文件名和 `source_id` 保留原标识，便于对应来源。

| 文件夹 / set_name | source_id |
| --- | --- |
| face1 | wm-cc0-classic |
| face2 | wm-bysa-classic |
| face3 | wm-bysa-klam |
| face4 | oc-274578-heads |
| bird | user-bird |
| dog | user-dog |
| woman | user-woman |
| macaque | user-macaque |

每套包含 `background-black`、`background-gray`、`background-white` 三个文件夹。
分类遵循实验选组规则：ambiguous 轮廓条件以两侧颜色为背景，face 轮廓条件以
中心颜色为背景；CSV 的 `background_color` 列记录该分类。它不是对被试知觉的断言。
例如黑背景组包含前三类中心图形条件的 pbg/pbw，以及两类两侧图形条件的 pgb/pwb。

文件名：`<source>__o{a|f}-s{n|f}-m{a|v}-p{outer}{center}.png`。

- `o`：ambiguous / face 轮廓；保留历史代码 `face`，在新增图片中指两侧人物或动物。
- `s`：none / figure 阴影。`shading_region` 指明作用区域：无阴影时为 none，
  ambiguous 轮廓条件加阴影时为中心 vase，face 轮廓条件加阴影时为两侧 face。
- `m`：ambiguous / vase 材质。
- `p`：两侧、中心的颜色顺序；b/g/w = black/gray/white。

基础灰度值为 43、154、220；纹理和阴影包含其他灰度。这些值不是物理亮度。
指向两侧图形和中心 vase 的冲突组合已排除。条件名表示设计操作，
不代表已验证的识别率或知觉二义性。

## 接入 MonkeyLogic

NIMH MonkeyLogic 支持直接读取 PNG；任务还需要 **conditions 文件（.txt）或
userloop（.m），以及 timing script（.m）**。可接入实验室已有任务。
参见官方 [Creating a Task](https://monkeylogic.nimh.nih.gov/docs_CreatingTask.html)。

静态图片接口为 `pic(filename,Xdeg,Ydeg)`，也可用
`pic(filename,Xdeg,Ydeg,Wpx,Hpx)` 指定缩放尺寸：位置单位是视角度，尺寸单位是像素。
参见官方 [TaskObjects](https://monkeylogic.nimh.nih.gov/docs_TaskObjects.html)。

实验室接入时还需记录或提供：

- 任务脚本及依赖：注视要求、呈现时长、间隔、响应和奖励规则。
- 条件选择规则：block、随机化、重复次数和错误试次处理。
- 事件码对照：刺激身份、出现/消失、响应和结果，与采集端保持一致。
- 显示和设备配置：MATLAB/ML 版本、刷新率、观察距离、视角校准、图片大小和位置、
  背景/亮度、眼动和 I/O 设置。

本交接包未设定这些实验参数，也未包含可运行任务。上述接口按 NIMH ML 文档说明；
如果使用原版 MonkeyLogic，请对照实验室现有版本和脚本。
显示时保持正方形比例和完整画布，保留已确认的边缘与留边；不要设置 colorkey 透明色，
黑灰白区域均为刺激内容。注视点由任务单独呈现。

240 张图片已检查可解码、尺寸和清单一致，且与本地确认版逐文件相同。
尚未在 MonkeyLogic 或实验硬件上运行；正式采集前需在实验机检查加载、显示、时序和事件码。
本仓库当前仅交付图片、清单与说明，生成代码、SVG 和预览保留在本地维护项目。
