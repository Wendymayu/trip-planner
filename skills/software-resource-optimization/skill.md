---
name: software-resource-optimization
description: 分析软件CPU和内存使用情况，关闭并重启占用资源过大的软件
user-invocable: true
license: MIT
metadata:
  version: 1.0.0
  author: System Optimizer Team
  tags: [system, performance, resource, optimization]
---

# Software Resource Optimization Skill

分析系统资源使用情况，关闭并重启占用资源过大的软件。

---

## When to use

- 用户询问系统资源使用情况
- 系统运行缓慢，需要优化性能
- 用户想要关闭占用资源过大的程序并重启

## When NOT to use

- 用户只是想查看任务列表
- 涉及系统关键进程（system、kernel、svchost等）

---

## Steps

### Step 1: 查询资源使用情况

根据操作系统执行命令：

- **Windows**: `wmic process get name,processid,workingsetsize | sort -k3 -n -r | head -20`
- **macOS/Linux**: `ps aux --sort=-%mem | head -20`

### Step 2: 识别异常软件

筛选内存占用 > 500MB 或 CPU > 50% 的软件。排除系统关键进程。

### Step 3: 确认并关闭

向用户展示异常软件列表，确认后关闭：

- Windows: `taskkill /pid <PID>`（失败则 `taskkill /f /pid <PID>`）
- macOS/Linux: `kill <PID>`（失败则 `kill -9 <PID>`）

### Step 4: 重启软件

根据软件类型重启：

- 桌面应用: Windows用`start`，macOS用`open -a`
- 浏览器: 启动时使用恢复标签页参数

### Step 5: 验证结果

重启后再次查询资源，对比前后占用情况。

---

## Example

**用户输入**：
> Chrome占用太大了，帮我重启一下

**执行过程**：
1. 查询进程，发现Chrome占用800MB
2. 确认关闭Chrome
3. 执行 `taskkill /pid 1234`
4. 重启Chrome
5. 验证内存降至400MB

---

## Notes

- 关闭前提醒用户保存数据
- 优先温和关闭，给软件保存数据的机会
- 系统关键进程不建议关闭
- 浏览器重启建议恢复标签页