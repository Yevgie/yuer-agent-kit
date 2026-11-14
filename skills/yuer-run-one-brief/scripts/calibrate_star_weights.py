#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""牌库星级加权模型 = 校准探针（可重复跑）。

用途 = 每次改 `STAR_SHARES` / `SINGLE_CARD_CAP` / 往库里加牌之后，
      跑一次这个探针，量出「星级到底有没有生效」，用数据决定要不要回炉。

    /usr/bin/python3 ~/.hermes/skills/yuer-run-one-brief/scripts/calibrate_star_weights.py
    /usr/bin/python3 ~/.hermes/skills/yuer-run-one-brief/scripts/calibrate_star_weights.py --samples 3000

三条不变量（必须同时成立，缺一条 = 加权模型废）：
  ① 5★ 明显优先      = 5★ 档命中份额 > 3★ 档命中份额
  ② 1★ 几乎不出现    = 1★ 档命中份额 <= 8%
  ③ 单张不霸占        = 任一单张命中份额 <= SINGLE_CARD_CAP + 2%

不变量满足 = 加权模型合格；否则 = 回炉（见 SKILL.md §12.2.3 的三版翻车表）。

🔴 为什么需要这个探针 = 「星级白加」是**静默**的：加完星级、抽卡看起来正常、
   但 5★ 命中率可能只有 0.95%（跟 3★ 没差别）= 主人以为在按偏好抽，
   其实完全没生效。**只靠「抽到一张 5★ 就以为成了」= 假验收。**
   判据 = 数字，不是感觉。
"""
import argparse
import collections
import importlib.util
import os
import sys

PICKER = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "pick_roster_record.py")


def load_picker():
    spec = importlib.util.spec_from_file_location("pr", PICKER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def measure(mod, pool, samples):
    """按当前加权模型抽 samples 次，统计星级分布 + 单张集中度。"""
    star_hit = collections.Counter()
    card_hit = collections.Counter()
    for _ in range(samples):
        rec, d = mod.weighted_pick(pool, 1)[0]
        star_hit[d.get("星级", mod.DEFAULT_STAR)] += 1
        card_hit[rec] += 1
    return star_hit, card_hit


def report(pr, pool, samples, label):
    star_hit, card_hit = measure(pr, pool, samples)
    n = max(1, samples)
    pct = {s: star_hit.get(s, 0) * 100.0 / n for s in range(1, 6)}

    print(f"\n=== {label} ===")
    print(f"池 = {len(pool)} 张 | 抽样 {samples} 次")
    for s in range(5, 0, -1):
        bar = "#" * int(round(pct[s] / 2))
        print(f"  {s}* {pct[s]:5.1f}%  {bar}")
    top_card = card_hit.most_common(1)[0] if card_hit else ("-", 0)
    top_pct = top_card[1] * 100.0 / n
    print(f"  单张最高 = {top_pct:.1f}% (牌 {top_card[0]})  上限 = {pr.SINGLE_CARD_CAP*100:.0f}%")

    # 三条不变量
    fails = []
    if pct[5] <= pct[3]:
        fails.append("① 5* 不比 3* 优先 = 加权没生效")
    if pct[1] > 8:
        fails.append(f"② 1* 命中 {pct[1]:.1f}% > 8% = 「可有可无」变「常常有」")
    if top_pct > pr.SINGLE_CARD_CAP * 100 + 2:
        fails.append(f"③ 单张 {top_pct:.1f}% 超上限 = 抽卡退化成只看那一张")
    if fails:
        for f in fails:
            print(f"  ❌ {f}")
    else:
        print("  ✅ 三条不变量全过 = 加权模型合格")
    return fails


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--samples", type=int, default=2000)
    ap.add_argument("--skip-synthetic", action="store_true",
                    help="只测真实池，不测合成的多档场景")
    args = ap.parse_args()

    pr = load_picker()
    pool = pr.load_valid()
    if not pool:
        print("牌池里没有合格档案", file=sys.stderr)
        return 1

    all_fails = []
    all_fails += report(pr, pool, args.samples, "真实池")

    if not args.skip_synthetic:
        # 场景 A = 库里多几张 5* 时，单张不该霸占
        five = []
        for n, d in list(pool)[:5]:
            d2 = dict(d)
            d2["星级"] = 5
            five.append((n + "F", d2))
        all_fails += report(pr, pool + five, args.samples, "场景 A = 加 5 张 5*")

        # 场景 B = 全 5* 池 = 单张应当均匀
        all5 = []
        for n, d in list(pool)[:20]:
            d2 = dict(d)
            d2["星级"] = 5
            all5.append((n, d2))
        all_fails += report(pr, all5, args.samples, "场景 B = 全 5* 池")

    print()
    if all_fails:
        print("结论 = ❌ 加权模型不合格 = 回炉（见 SKILL.md §12.2.3）")
        return 1
    print("结论 = ✅ 加权模型合格")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
