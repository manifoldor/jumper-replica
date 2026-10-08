<!-- tracks: README.md @ sha256:fa8fea72ac60f73541feb08339f9f16218bac3d92d22669a7ab64f6379d3fa08 -->

# 装配与爆炸渲染

[高清海报](Jumper_Exploded_Annotated.png) · [可编辑 SVG](Jumper_Exploded_Annotated.svg) · [Blender 场景](Jumper_Exploded.blend) · [标注名录](LABELS.zh.md)

海报尺寸 6000 × 4800，含 66 组标注、三个局部视图及 HOME 装配参考。场景包含 88 个网格对象和完整 430,915 个源面（包括重复面），属于装配展示，不是经实体验证的制造说明。

`scene_manifest.json` 记录源 HOME 矩阵和各爆炸平移；`scene_meshes/` 为展开后的毫米制 STL。Blender 对象缩放 0.001 转为米。爆炸展开仅增加平移；上壳 / 显示模块横向偏移以露出后部结构，夹持小件竖向拉开以便查看。展示距离不是装配公差。

`annotation_layout.json` 将 66 个唯一标注对应到源 ID 与屏幕位置；几何、渲染和 Blender 回读报告保留核验结果。执行器采用源模型参考，未替换为外部舵机 CAD。红 / 银 / 深色为渲染外观，不是实物材料指定。

原装配参考见 `../geometry/assembly_home.glb`（米）或 `../geometry/assembly_home_mm.stl`（毫米）。坐标与关节约定见[装配指南](../docs/ASSEMBLY.zh.md)。
