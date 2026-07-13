# Frieren Pixel for Codex

一只可爱、Q 版、像素风的芙莉莲主题 Codex v2 动画宠物。包含 9 组状态动画和 16 个环视方向。

![Frieren Pixel 动画联系表](qa/contact-sheet.png)

## 动作与触发方式

![修复后的鼠标悬浮动画](qa/hover-preview.gif)

| 动作 | Codex 中的触发方式 |
| --- | --- |
| 待机、眨眼 | 没有任务通知时自动播放 |
| 向右跑 / 向左跑 | 按住宠物并向右 / 向左拖动 |
| 挥手 | 宠物首次唤醒或出现问候提示时 |
| 轻微魔法漂浮 | 鼠标移入宠物时；Codex 会自动连续播放 3 次 |
| 沮丧 | 任务失败、阻塞或出现危险级提示时 |
| 等待 | Codex 需要输入、确认或授权时 |
| 托腮思考 | 任务运行、思考或处理中 |
| 检查成果 | 任务成功完成、结果等待查看时 |
| 16 向注视 | 鼠标在宠物周围移动时，脸和视线会跟随指针方向 |

这些动作由 Codex 的界面状态自动触发，不能在宠物包里单独绑定快捷键。非待机状态通常会短暂播放数轮，然后回到待机。悬浮动作已改为保持直立、最高上浮约 5 像素并眨眼，不再下蹲或落地回弹。

### 思考动画优化

![平滑后的思考动画](qa/thinking-preview.gif)

Codex v2 的 `running` 状态固定使用 6 帧，前 5 帧各显示 120ms，最后一帧显示 220ms。旧版在不到一秒内依次切换站立、托腮、抱臂、施法、合掌和举手，连续播放时容易显得抽搐。

新版统一使用托腮姿势，只加入 1 像素的呼吸位移和一帧轻微眨眼；首尾帧逐像素一致，因此循环边界不会跳变。除 `running` 所在的第 8 行外，其余图集行保持不变。详细验证结果见 [`qa/thinking-repair.json`](qa/thinking-repair.json)。

维护者可使用以下命令重新生成图集、动画预览和验证报告（需要 Pillow）：

```sh
python scripts/refine_thinking_animation.py \
  --input pet/frieren-pixel/spritesheet.webp \
  --output pet/frieren-pixel/spritesheet.webp \
  --preview qa/thinking-preview.gif \
  --report qa/thinking-repair.json
```

## 一键安装

macOS 或 Linux：

```sh
./install.sh
```

脚本会：

- 将宠物安装到 `${CODEX_HOME:-$HOME/.codex}/pets/frieren-pixel`
- 备份已有的同名宠物和 `config.toml`
- 将 `desktop.selected-avatar-id` 设为 `custom:frieren-pixel`
- 保留重复执行的安全性

安装后重启 Codex。

## 两台电脑同步

本项目已发布到私有仓库：<https://github.com/zc-xu/frieren-codex-pet>。另一台电脑需要先登录有权访问该仓库的 GitHub 账号。

第二台电脑首次执行：

```sh
git clone https://github.com/zc-xu/frieren-codex-pet.git
cd frieren-codex-pet
./install.sh
```

之后更新只需：

```sh
git pull && ./install.sh
```

## 卸载

```sh
./uninstall.sh
```

宠物图集使用 Codex `spriteVersionNumber: 2`，尺寸为 `1536x2288`。

这是供个人使用的非官方同人宠物包。
