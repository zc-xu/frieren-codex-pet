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
| 忙碌施法 | 任务运行、思考或处理中 |
| 检查成果 | 任务成功完成、结果等待查看时 |
| 16 向注视 | 鼠标在宠物周围移动时，脸和视线会跟随指针方向 |

这些动作由 Codex 的界面状态自动触发，不能在宠物包里单独绑定快捷键。非待机状态通常会短暂播放数轮，然后回到待机。悬浮动作已改为保持直立、最高上浮约 5 像素并眨眼，不再下蹲或落地回弹。

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

本目录本身就是一个已提交的 Git 仓库。建议先在 GitHub 创建名为 `frieren-codex-pet` 的私有空仓库，然后在本机执行：

```sh
git remote add origin git@github.com:<你的用户名>/frieren-codex-pet.git
git push -u origin main
```

第二台电脑首次执行：

```sh
git clone git@github.com:<你的用户名>/frieren-codex-pet.git
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
