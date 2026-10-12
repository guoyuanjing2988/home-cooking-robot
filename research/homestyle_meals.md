# The user's reference cook: three home-style 四菜一汤 meals

The user said (2026-10-12): "你参考这位，他做的挺家常的". This file analyses three videos the user downloaded. The structured data is in `homestyle_meals.json`.

The three videos:
- 今日食谱：干锅土豆，桂花糖芋头，炒西兰花，蒜蓉蒸丝瓜，蛤蜊排骨盅
- 今日食谱：红烧肉，番茄炒蛋，白灼秋葵娃娃菜，清蒸海鲈鱼，鲜笋排骨汤
- 今日食谱：芋头蒸排骨，酸辣土豆丝，青椒炒鱿鱼，清炒荷兰豆，青瓜肉片汤

## Method
- **Frames:** taken every 2 s and read with their on-screen captions.
- **Speech:** transcribed with Whisper medium. Obvious mistakes were corrected only where the caption shows the right word (文革 → 文蛤, 炖盅).
- **Times:** marked "stated" when he says them, and "est" when I read them from the footage. The videos are edited, so "est" times are rough.

## How he cooks: a whole meal, planned around the slow items
- **One video = one meal:** 4 dishes, 1 soup and rice for a family. He says 四个人吃的话下了 400 克 (rice).
- **Order:** the longest unattended item goes on first. Then he prepares the rest while it cooks, and the quick wok dishes come last so everything is hot together.
  - 这鲜笋排骨汤比较慢，要先做
  - 等待的时间不要浪费，来做点别的事情
  - 排骨比较慢，优先安排
- **Sharing appliances:** several items share one steamer: 刚好可以跟这个炖盅一起来蒸，节约时间也节约资源; 一锅出两菜.
- **The slow part is the knife work:** 做菜其实并不难，就是前面的切配比较费时间.

## What the 15 dishes need (compared with Wang Gang)
| | This cook (15 dishes) | Wang Gang (42 recipes) |
|---|---|---|
| Steamed | **5**: 蛤蜊排骨盅, 桂花糖芋头, 蒜蓉蒸丝瓜, 清蒸鲈鱼, 芋头蒸排骨 | 3 |
| Soups | **3**: clay pot 1 h, quick soup in the wok, steamed cups | 1–2 |
| Blanched (白灼 / 焯水) | 白灼秋葵娃娃菜; also 土豆丝, 排骨, 五花肉, 鱿鱼 blanched or scalded before cooking | a few |
| Wok stir-fry / braise | **7**: 干锅土豆, 蚝油西兰花, 红烧肉, 番茄炒蛋, 青椒炒鱿鱼, 酸辣土豆丝, 清炒荷兰豆 | 34 |
| Lid | steamer, clay pot, 40 min braise, and 30 s high-heat 焖 in 2 stir-fries | 2 stated |
| Hot oil poured over | 4 (fish, 白灼汁, luffa sauce, steamed ribs) | 5 泼油 |
| Deep-fry | 1 (potato slices 3 min at 六成) | 8 in deep oil |
| Tossing | once, for show; otherwise spatula stirring | none stated in zh |
| Heat | flat induction cooktop, flat-bottom woks; 2 zones used at once | gas (his own) |

**Equipment in his kitchen:**
- a flat induction cooktop, with steamer and wok in use at the same time;
- flat-bottom honeycomb woks with glass lids;
- a 3-tier steamer pot;
- a clay soup pot;
- a rice cooker;
- ceramic stew cups (炖盅) covered with cling film;
- a spider strainer (漏勺), a ladle, sauce bowls.

## Times per dish (stated by him)
- **Long, unattended:**
  - clay-pot soup 60 min;
  - 红烧肉 braise 40 min (lid, medium heat);
  - steaming 30 min (soup cups + taro; taro-and-rib plate);
  - steamed sea bass 6 min after the water boils;
  - luffa 3 min from full steam.
- **Short, at the wok:**
  - lid 焖 30 s on high heat (番茄炒蛋, 西兰花);
  - baby cabbage blanched 1 min, okra 30 s;
  - potato fried about 3 min.

## What this means for the robot
1. **More steaming and soup, less 爆炒.** These are easier for a robot: load the vessel, start it, and take it out when done. Only 7 of 15 dishes need the wok and spatula, and they are short (≤ about 2 min of stirring).
2. **At least two heat sources at once,** plus the rice cooker:
   - the wok, and a steamer or soup pot running at the same time;
   - meal B also needs the soup (1 h) and the braise (40 min) to overlap.
3. **New handling:**
   - lids (wok, steamer, pot);
   - plates of food going into and out of the steamer, at about 100 °C;
   - stew cups;
   - a spider strainer for blanching;
   - a ladle for soup;
   - hot oil poured over a bowl or plate (the R15 lift-and-tip motion);
   - rinsing the wok between dishes.
4. **Knife work is heavy:**
   - fish split along the back;
   - squid scored 麦穗花刀;
   - hand julienne;
   - peeled tomatoes;
   - taro.

   Most of this is beyond the R11 prep machines. Practical route: buy the fish and squid already cleaned and cut, use the slicer's julienne disc, and skip peeling tomatoes.
5. **Timing with one arm** (`sim/r10/claude/meal16.py`, results below): the cooking part of each meal fits in 40–80 minutes. Because the wok dishes are done one after another, the first quick dish waits 8–15 minutes. He has the same problem, and the dishes are served covered.
