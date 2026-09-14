
const DATA = {"records": [{"no": "205227027", "booked": "2026/01/30 11:30", "start": "2026-01-30 11:15", "end": "2026-01-30 13:53", "station": "ＭＧＡ金町", "car": "ソリオ", "base": "ソリオ", "brand": "Suzuki", "plate": "葛飾 500 ワ 2334:シルバー）", "minutes": 143, "km": 15, "yen": 2200}, {"no": "205539307", "booked": "2026/02/01 10:30", "start": "2026-02-01 10:39", "end": "2026-02-01 19:42", "station": "ＭＧＡ金町", "car": "ソリオ", "base": "ソリオ", "brand": "Suzuki", "plate": "葛飾 500 ワ 2334:シルバー）", "minutes": 552, "km": 56, "yen": 6220}, {"no": "205731226", "booked": "2026/02/04 08:00", "start": "2026-02-04 08:06", "end": "2026-02-04 13:36", "station": "ＭＧＡ金町", "car": "ソリオ", "base": "ソリオ", "brand": "Suzuki", "plate": "葛飾 500 ワ 2334:シルバー）", "minutes": 336, "km": 63, "yen": 5150}, {"no": "206152829", "booked": "2026/02/07 17:45", "start": "2026-02-07 17:49", "end": "2026-02-07 20:34", "station": "南水元４丁目２５", "car": "ヤリス（ハイブリッド）", "base": "ヤリス", "brand": "Toyota", "plate": "葛飾 500 ワ 2469:シルバー）", "minutes": 169, "km": 23, "yen": 2700}, {"no": "206797847", "booked": "2026/02/14 12:00", "start": "2026-02-14 12:26", "end": "2026-02-14 21:44", "station": "南水元４丁目２５", "car": "アクア（ハイブリッド）", "base": "アクア", "brand": "Toyota", "plate": "葛飾 500 ワ 2497:カーキ）", "minutes": 584, "km": 65, "yen": 6400}, {"no": "207429978", "booked": "2026/02/22 09:15", "start": "2026-02-22 09:05", "end": "2026-02-22 21:26", "station": "東金町２丁目", "car": "アクア（ハイブリッド）", "base": "アクア", "brand": "Toyota", "plate": "葛飾 500 ワ 2118:ベージュ）", "minutes": 731, "km": 132, "yen": 7960}, {"no": "208022973", "booked": "2026/02/27 09:15", "start": "2026-02-27 09:10", "end": "2026-02-27 16:58", "station": "南水元４丁目２５", "car": "ノート e-POWER", "base": "ノート e-POWER", "brand": "Nissan", "plate": "葛飾 500 ワ 2483:シルバー）", "minutes": 463, "km": 71, "yen": 6520}, {"no": "208466561", "booked": "2026/03/03 11:15", "start": "2026-03-03 11:15", "end": "2026-03-03 13:36", "station": "南水元４丁目２５", "car": "ノート e-POWER", "base": "ノート e-POWER", "brand": "Nissan", "plate": "葛飾 500 ワ 2483:シルバー）", "minutes": 141, "km": 14, "yen": 2200}, {"no": "208758144", "booked": "2026/03/06 10:45", "start": "2026-03-06 10:34", "end": "2026-03-06 16:32", "station": "東金町２丁目５", "car": "MAZDA2", "base": "MAZDA2", "brand": "Mazda", "plate": "葛飾 500 ワ 2423:ライトブルー）", "minutes": 347, "km": 77, "yen": 6750}, {"no": "208983365", "booked": "2026/03/08 14:00", "start": "2026-03-08 13:56", "end": "2026-03-08 19:01", "station": "東水元２丁目３２", "car": "ヤリスクロス（ハイブリッド）", "base": "ヤリスクロス", "brand": "Toyota", "plate": "葛飾 300 ワ 998:グレイッシュブルー）", "minutes": 301, "km": 70, "yen": 5290}, {"no": "209152073", "booked": "2026/03/10 09:00", "start": "2026-03-10 08:51", "end": "2026-03-10 19:46", "station": "南水元４丁目２５", "car": "ヤリス（ハイブリッド）", "base": "ヤリス", "brand": "Toyota", "plate": "葛飾 500 ワ 2469:シルバー）", "minutes": 646, "km": 68, "yen": 6460}, {"no": "209481003", "booked": "2026/03/14 10:00", "start": "2026-03-14 10:23", "end": "2026-03-14 20:01", "station": "ＵＲ金町駅前（屋上）", "car": "ヤリスクロス（ハイブリッド）", "base": "ヤリスクロス", "brand": "Toyota", "plate": "葛飾 300 ワ 904:グレー）", "minutes": 601, "km": 84, "yen": 6780}, {"no": "209703436", "booked": "2026/03/15 18:30", "start": "2026-03-15 18:27", "end": "2026-03-15 20:38", "station": "ＵＲ金町駅前（屋上）", "car": "スイフト(ハイブリッド/1200cc)", "base": "スイフト", "brand": "Suzuki", "plate": "葛飾 500 ワ 2132:ベージュ）", "minutes": 128, "km": 20, "yen": 1980}, {"no": "209915022", "booked": "2026/03/18 09:15", "start": "2026-03-18 09:20", "end": "2026-03-18 20:16", "station": "南水元４丁目２５", "car": "ソリオ(ハイブリッド/1200cc)", "base": "ソリオ", "brand": "Suzuki", "plate": "葛飾 500 ワ 2857:ブルー）", "minutes": 661, "km": 68, "yen": 6460}, {"no": "210065254", "booked": "2026/03/19 09:45", "start": "2026-03-19 09:33", "end": "2026-03-19 21:22", "station": "南水元４丁目２５", "car": "ソリオ(ハイブリッド/1200cc)", "base": "ソリオ", "brand": "Suzuki", "plate": "葛飾 500 ワ 2857:ブルー）", "minutes": 697, "km": 96, "yen": 7020}, {"no": "209989377", "booked": "2026/03/20 09:30", "start": "2026-03-20 09:26", "end": "2026-03-20 18:53", "station": "南水元４丁目２５", "car": "ソリオ(ハイブリッド/1200cc)", "base": "ソリオ", "brand": "Suzuki", "plate": "葛飾 500 ワ 2857:ブルー）", "minutes": 563, "km": 72, "yen": 6540}, {"no": "210284121", "booked": "2026/03/21 23:00", "start": "2026-03-21 23:00", "end": "2026-03-21 23:04", "station": "南水元４丁目２５", "car": "ソリオ(ハイブリッド/1200cc)", "base": "ソリオ", "brand": "Suzuki", "plate": "葛飾 500 ワ 2857:ブルー）", "minutes": 4, "km": 0, "yen": 220}, {"no": "210378901", "booked": "2026/03/22 10:45", "start": "2026-03-22 10:35", "end": "2026-03-22 20:17", "station": "南水元４丁目２５", "car": "ソリオ(ハイブリッド/1200cc)", "base": "ソリオ", "brand": "Suzuki", "plate": "葛飾 500 ワ 2857:ブルー）", "minutes": 572, "km": 72, "yen": 6540}, {"no": "211011382", "booked": "2026/03/28 15:15", "start": "2026-03-28 15:18", "end": "2026-03-28 17:24", "station": "タイムズ浦和常盤１０丁目", "car": "スイフト", "base": "スイフト", "brand": "Suzuki", "plate": "大宮 502 ワ 8250:シルバー）", "minutes": 129, "km": 5, "yen": 1980}, {"no": "211024121", "booked": "2026/03/29 09:00", "start": "2026-03-29 09:10", "end": "2026-03-29 22:03", "station": "タイムズ与野新中里第４", "car": "アクア（ハイブリッド）", "base": "アクア", "brand": "Toyota", "plate": "大宮 502 ワ 2441:ブルー）", "minutes": 783, "km": 77, "yen": 7740}, {"no": "211297763", "booked": "2026/03/31 14:00", "start": "2026-03-31 14:02", "end": "2026-03-31 16:57", "station": "常盤第３駐車場", "car": "オーラ e-POWER", "base": "オーラ e-POWER", "brand": "Nissan", "plate": "大宮 300 ワ 8825:レッド）", "minutes": 177, "km": 11, "yen": 2640}, {"no": "211543106", "booked": "2026/04/03 09:30", "start": "2026-04-03 09:21", "end": "2026-04-03 15:44", "station": "常盤９丁目", "car": "フィット（ハイブリッド）", "base": "フィット", "brand": "Honda", "plate": "大宮 502 ワ 6474:シルバー）", "minutes": 374, "km": 54, "yen": 5190}, {"no": "211795114", "booked": "2026/04/05 11:15", "start": "2026-04-05 11:24", "end": "2026-04-05 17:29", "station": "タイムズ北浦和第４", "car": "ヤリスクロス（ハイブリッド）", "base": "ヤリスクロス", "brand": "Toyota", "plate": "大宮 300 ワ 8099:シルバー）", "minutes": 374, "km": 22, "yen": 4550}, {"no": "212703552", "booked": "2026/04/14 12:15", "start": "2026-04-14 12:06", "end": "2026-04-14 14:01", "station": "常盤９丁目", "car": "フィット（ハイブリッド）", "base": "フィット", "brand": "Honda", "plate": "大宮 502 ワ 6474:シルバー）", "minutes": 106, "km": 14, "yen": 1760}, {"no": "213516841", "booked": "2026/04/22 10:45", "start": "2026-04-22 10:47", "end": "2026-04-22 13:04", "station": "常盤９丁目", "car": "フィット（ハイブリッド）", "base": "フィット", "brand": "Honda", "plate": "大宮 502 ワ 6474:シルバー）", "minutes": 139, "km": 14, "yen": 2200}, {"no": "213760726", "booked": "2026/04/25 09:30", "start": "2026-04-25 10:14", "end": "2026-04-25 14:24", "station": "常盤第３駐車場", "car": "ヤリスクロス（ハイブリッド）", "base": "ヤリスクロス", "brand": "Toyota", "plate": "大宮 300 ワ 8129:ブルー）", "minutes": 294, "km": 24, "yen": 4370}, {"no": "214671573", "booked": "2026/05/03 11:00", "start": "2026-05-03 11:11", "end": "2026-05-03 14:51", "station": "針ヶ谷２丁目", "car": "アクア（ハイブリッド）", "base": "アクア", "brand": "Toyota", "plate": "大宮 502 ワ 6584:シルバー）", "minutes": 231, "km": 26, "yen": 3640}, {"no": "214765207", "booked": "2026/05/05 09:00", "start": "2026-05-05 10:31", "end": "2026-05-05 10:47", "station": "北浦和パーキング", "car": "アクア（ハイブリッド）", "base": "アクア", "brand": "Toyota", "plate": "大宮 502 ワ 7729:ベージュ）", "minutes": 107, "km": 0, "yen": 1760}, {"no": "214862062", "booked": "2026/05/06 09:30", "start": "2026-05-06 09:46", "end": "2026-05-06 18:10", "station": "常盤第３駐車場", "car": "フィット（ハイブリッド）", "base": "フィット", "brand": "Honda", "plate": "大宮 502 ワ 8496:シルバー）", "minutes": 520, "km": 77, "yen": 6640}, {"no": "217104201", "booked": "2026/05/30 10:00", "start": "2026-05-30 10:11", "end": "2026-05-30 14:32", "station": "タイムズ浦和常盤１０丁目", "car": "スイフト", "base": "スイフト", "brand": "Suzuki", "plate": "大宮 502 ワ 8250:シルバー）", "minutes": 272, "km": 20, "yen": 4180}, {"no": "217892876", "booked": "2026/06/06 10:00", "start": "2026-06-06 10:18", "end": "2026-06-06 13:32", "station": "常盤９丁目", "car": "フィット（ハイブリッド）", "base": "フィット", "brand": "Honda", "plate": "大宮 502 ワ 6474:シルバー）", "minutes": 212, "km": 17, "yen": 3300}, {"no": "218610941", "booked": "2026/06/12 11:00", "start": "2026-06-12 10:58", "end": "2026-06-12 13:02", "station": "常盤第３駐車場", "car": "フィット（ハイブリッド）", "base": "フィット", "brand": "Honda", "plate": "大宮 502 ワ 8496:シルバー）", "minutes": 122, "km": 13, "yen": 1980}, {"no": "218716759", "booked": "2026/06/14 09:30", "start": "2026-06-14 09:58", "end": "2026-06-14 14:46", "station": "常盤第１", "car": "スイフト(ハイブリッド/1200cc)", "base": "スイフト", "brand": "Suzuki", "plate": "大宮 502 ワ 7294:オレンジ）", "minutes": 316, "km": 22, "yen": 4330}, {"no": "219432076", "booked": "2026/06/20 11:30", "start": "2026-06-20 11:30", "end": "2026-06-20 20:48", "station": "常盤第３駐車場", "car": "ヤリスクロス（ハイブリッド）", "base": "ヤリスクロス", "brand": "Toyota", "plate": "大宮 300 ワ 8129:ブルー）", "minutes": 558, "km": 66, "yen": 6420}, {"no": "219836555", "booked": "2026/06/24 10:30", "start": "2026-06-24 10:40", "end": "2026-06-24 12:58", "station": "常盤第１", "car": "スイフト(ハイブリッド/1200cc)", "base": "スイフト", "brand": "Suzuki", "plate": "大宮 502 ワ 7294:オレンジ）", "minutes": 148, "km": 17, "yen": 2200}, {"no": "220377218", "booked": "2026/06/29 09:00", "start": "2026-06-29 09:00", "end": "2026-06-29 09:02", "station": "常盤第１", "car": "スイフト(ハイブリッド/1200cc)", "base": "スイフト", "brand": "Suzuki", "plate": "大宮 502 ワ 7294:オレンジ）", "minutes": 2, "km": 0, "yen": 220}, {"no": "220486430", "booked": "2026/06/30 10:00", "start": "2026-06-30 10:00", "end": "2026-06-30 14:55", "station": "タイムズ浦和常盤１０丁目", "car": "アクア（ハイブリッド）", "base": "アクア", "brand": "Toyota", "plate": "大宮 502 ワ 8229:カーキ）", "minutes": 295, "km": 45, "yen": 4790}, {"no": "220832136", "booked": "2026/07/04 10:00", "start": "2026-07-04 10:05", "end": "2026-07-04 13:27", "station": "タイムズ浦和常盤１０丁目", "car": "アクア（ハイブリッド）", "base": "アクア", "brand": "Toyota", "plate": "大宮 502 ワ 8229:カーキ）", "minutes": 207, "km": 13, "yen": 3080}, {"no": "221142362", "booked": "2026/07/06 11:30", "start": "2026-07-06 11:26", "end": "2026-07-06 15:49", "station": "常盤第１", "car": "スイフト(ハイブリッド/1200cc)", "base": "スイフト", "brand": "Suzuki", "plate": "大宮 502 ワ 7294:オレンジ）", "minutes": 259, "km": 55, "yen": 4360}, {"no": "221271412", "booked": "2026/07/07 15:30", "start": "2026-07-07 15:25", "end": "2026-07-07 18:38", "station": "常盤第３駐車場", "car": "ヤリスクロス（ハイブリッド）", "base": "ヤリスクロス", "brand": "Toyota", "plate": "大宮 300 ワ 8129:ブルー）", "minutes": 188, "km": 39, "yen": 2940}, {"no": "221450968", "booked": "2026/07/09 11:30", "start": "2026-07-09 11:28", "end": "2026-07-09 17:20", "station": "常盤第３駐車場", "car": "フィット（ハイブリッド）", "base": "フィット", "brand": "Honda", "plate": "大宮 502 ワ 8496:シルバー）", "minutes": 350, "km": 16, "yen": 4290}, {"no": "221789142", "booked": "2026/07/12 11:45", "start": "2026-07-12 11:34", "end": "2026-07-12 18:21", "station": "南与野東口", "car": "ヤリス（ハイブリッド）", "base": "ヤリス", "brand": "Toyota", "plate": "大宮 502 ワ 3174:グレー）", "minutes": 396, "km": 60, "yen": 5450}, {"no": "222455022", "booked": "2026/07/18 11:15", "start": "2026-07-18 11:11", "end": "2026-07-18 15:12", "station": "南与野東口", "car": "ノート e-POWER", "base": "ノート e-POWER", "brand": "Nissan", "plate": "大宮 502 ワ 8900:グレー）", "minutes": 237, "km": 16, "yen": 3520}, {"no": "222670907", "booked": "2026/07/20 09:30", "start": "2026-07-20 09:56", "end": "2026-07-20 19:37", "station": "タイムズ北浦和第４", "car": "スイフト(ハイブリッド/1200cc)", "base": "スイフト", "brand": "Suzuki", "plate": "大宮 502 ワ 7938:ベージュ）", "minutes": 607, "km": 102, "yen": 6840}, {"no": "222941432", "booked": "2026/07/25 10:00", "start": "2026-07-25 09:54", "end": "2026-07-25 16:12", "station": "タイムズ浦和常盤１０丁目", "car": "アクア（ハイブリッド）", "base": "アクア", "brand": "Toyota", "plate": "大宮 502 ワ 8229:カーキ）", "minutes": 372, "km": 36, "yen": 4530}, {"no": "223389613", "booked": "2026/07/26 10:00", "start": "2026-07-26 11:10", "end": "2026-07-26 21:26", "station": "タイムズ浦和常盤１０丁目", "car": "アクア（ハイブリッド）", "base": "アクア", "brand": "Toyota", "plate": "大宮 502 ワ 8229:カーキ）", "minutes": 686, "km": 90, "yen": 6600}, {"no": "223908205", "booked": "2026/08/01 10:00", "start": "2026-08-01 10:29", "end": "2026-08-01 17:36", "station": "常盤第３駐車場", "car": "オーラ e-POWER", "base": "オーラ e-POWER", "brand": "Nissan", "plate": "大宮 300 ワ 8825:レッド）", "minutes": 456, "km": 27, "yen": 5500}, {"no": "225069866", "booked": "2026/08/09 10:30", "start": "2026-08-09 10:30", "end": "2026-08-09 13:14", "station": "常盤第１", "car": "スイフト(ハイブリッド/1200cc)", "base": "スイフト", "brand": "Suzuki", "plate": "大宮 502 ワ 7294:オレンジ）", "minutes": 164, "km": 21, "yen": 2420}, {"no": "225242932", "booked": "2026/08/10 17:30", "start": "2026-08-10 17:35", "end": "2026-08-10 20:22", "station": "常盤第３駐車場", "car": "ヤリスクロス（ハイブリッド）", "base": "ヤリスクロス", "brand": "Toyota", "plate": "大宮 300 ワ 8129:ブルー）", "minutes": 172, "km": 11, "yen": 2640}, {"no": "225311806", "booked": "2026/08/11 10:30", "start": "2026-08-11 10:42", "end": "2026-08-11 17:41", "station": "常盤第１", "car": "スイフト(ハイブリッド/1200cc)", "base": "スイフト", "brand": "Suzuki", "plate": "大宮 502 ワ 7294:オレンジ）", "minutes": 431, "km": 50, "yen": 5690}, {"no": "225686912", "booked": "2026/08/14 18:30", "start": "2026-08-14 18:25", "end": "2026-08-14 20:41", "station": "常盤第１", "car": "スイフト(ハイブリッド/1200cc)", "base": "スイフト", "brand": "Suzuki", "plate": "大宮 502 ワ 7294:オレンジ）", "minutes": 131, "km": 9, "yen": 1980}, {"no": "225540400", "booked": "2026/08/16 10:00", "start": "2026-08-16 11:23", "end": "2026-08-16 11:38", "station": "常盤第１", "car": "スイフト(ハイブリッド/1200cc)", "base": "スイフト", "brand": "Suzuki", "plate": "大宮 502 ワ 7294:オレンジ）", "minutes": 98, "km": 0, "yen": 1540}, {"no": "226776833", "booked": "2026/08/24 11:30", "start": "2026-08-24 11:22", "end": "2026-08-24 15:34", "station": "タイムズ与野新中里第４", "car": "ヤリスクロス（ハイブリッド）", "base": "ヤリスクロス", "brand": "Toyota", "plate": "大宮 301 ワ 1047:ベージュ）", "minutes": 244, "km": 75, "yen": 4540}, {"no": "227264683", "booked": "2026/08/28 18:30", "start": "2026-08-28 18:32", "end": "2026-08-28 19:52", "station": "常盤第１", "car": "スイフト(ハイブリッド/1200cc)", "base": "スイフト", "brand": "Suzuki", "plate": "大宮 502 ワ 7294:オレンジ）", "minutes": 82, "km": 2, "yen": 2680}]};
const R = DATA.records;
const PALETTE = ['#22d3ee','#a855f7','#ff3d81','#facc15','#4ade80','#fb923c','#60a5fa','#f472b6','#34d399','#c084fc','#f87171'];
const MODEL_EN = {
  'アクア':'AQUA','オーラ':'AURA','スイフト':'SWIFT','ソリオ':'SOLIO','ノート':'NOTE',
  'フィット':'FIT','ヤリスクロス':'YARIS CROSS','ヤリス':'YARIS','MAZDA2':'MAZDA2'
};

/* ---------- 车标（内联 SVG；若 web/logos/<brand>.png 存在则优先用图片） ---------- */
const BRAND_COLOR = {Toyota:'#E2111A', Nissan:'#C9CED6', Honda:'#F26522', Suzuki:'#0F62C4', Mazda:'#00AEEF'};
const BRAND_SVG = {
  Toyota:`<svg class="fb" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="3.4">
    <ellipse cx="32" cy="32" rx="29" ry="18"/>
    <ellipse cx="32" cy="27" rx="8.5" ry="19"/>
    <ellipse cx="32" cy="40" rx="20" ry="8.5"/></svg>`,
  Nissan:`<svg class="fb" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="3.4">
    <circle cx="32" cy="32" r="27"/>
    <rect x="5" y="24.5" width="54" height="15" fill="currentColor" stroke="none"/>
    <text x="32" y="35" text-anchor="middle" font-size="10.5" font-weight="800"
      fill="#0b1020" font-family="Arial,sans-serif" letter-spacing="0.5">NISSAN</text></svg>`,
  Suzuki:`<svg class="fb" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="6"
    stroke-linecap="round">
    <path d="M47 19c-2.5-4-7.5-6.5-14-6.5C22 12.5 14.5 17.5 14.5 25.5s4.5 10 14 12l5.5 1
      c5.5 1 8 3 8 6.5s-4.5 7-12 7c-7.5 0-13-3.5-14-9"/></svg>`,
  Honda:`<svg class="fb" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="3.4"
    stroke-linejoin="round">
    <path d="M14 15h36l6 34H8z"/>
    <path d="M21 26v14M43 26v14M21 33h22" stroke-width="5"/></svg>`,
  Mazda:`<svg class="fb" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="3.4"
    stroke-linejoin="round" stroke-linecap="round">
    <circle cx="32" cy="32" r="27"/>
    <path d="M17 43V24l15 13 15-13v19" stroke-width="4.6"/>
    <path d="M32 37v11" stroke-width="3"/></svg>`
};
function logo(b, sm){
  if(!b) return '';
  return `<span class="logo${sm?' sm':''}" data-b="${b}" style="--bc:${BRAND_COLOR[b]||'#22d3ee'}" title="${b}">`
    + (BRAND_SVG[b]||'') + `</span>`;
}

/* web/logos/ 下的真实车标（构建期已读入，file:// 直接打开也能显示） */
const LOGO_FILES = {"honda": {"kind": "svg", "markup": "<svg fill=\"#000000\" version=\"1.1\" id=\"Layer_1\" xmlns=\"http://www.w3.org/2000/svg\" xmlns:xlink=\"http://www.w3.org/1999/xlink\" viewBox=\"0 0 44.6 44.6\" xml:space=\"preserve\" preserveAspectRatio=\"xMidYMid meet\" focusable=\"false\"> <title>honda-logo</title> <g> <path d=\"M32.6,7.2c-1,4.6-1.4,6.7-2.3,10s-1.4,6.1-2.5,7.6c-0.8,1.1-2.1,1.8-3.5,1.9c-1.3,0.1-2.7,0.1-4,0 c-1.4-0.1-2.7-0.8-3.5-1.9c-1.1-1.4-1.7-4.4-2.5-7.6S13,11.8,12,7.2l-1.5,0.1c-0.6,0-1.1,0.1-1.6,0.2c0,0,0.6,9.4,0.9,13.4 c0.3,4.2,0.8,11.2,1.2,16.6c0,0,0.9,0.1,2.3,0.2s2.2,0.1,2.2,0.1c0.6-2.4,1.4-5.6,2.2-7c0.5-0.8,1.4-1.3,2.4-1.3 c0.7-0.1,1.4-0.1,2.2-0.1l0,0c0.7,0,1.4,0,2.2,0.1c1,0,1.9,0.5,2.4,1.3c0.9,1.4,1.6,4.6,2.2,7c0,0,0.7,0,2.2-0.1s2.3-0.2,2.3-0.2 c0.5-5.3,1-12.4,1.2-16.6c0.3-4,0.9-13.4,0.9-13.4c-0.5-0.1-1-0.1-1.6-0.2L32.6,7.2z\"/> <path d=\"M44.4,12.8c-0.6-6-4.6-7.2-8.1-7.8c-2.3-0.3-4.6-0.5-6.9-0.6c-1.8-0.1-5.9-0.2-7.1-0.2s-5.4,0.1-7.1,0.2 C12.8,4.4,10.5,4.6,8.2,5c-3.5,0.6-7.5,1.9-8.1,7.8c-0.2,2-0.2,4-0.2,6c0,2.7,0.2,5.4,0.6,8.1c0.2,2.3,0.7,4.5,1.3,6.8 c0.9,2.6,1.7,3.4,2.6,4.1c1.6,1.1,3.3,1.7,5.2,2c8.4,0.9,16.8,0.9,25.2,0c1.9-0.3,3.6-0.9,5.2-2c1-0.8,1.8-1.5,2.6-4.1 c0.6-2.2,1.1-4.5,1.3-6.8c0.3-2.7,0.5-5.4,0.6-8.1C44.6,16.8,44.5,14.8,44.4,12.8z M42.2,22.8c-0.1,3.3-0.6,6.5-1.4,9.7 c-0.3,1.5-1.1,2.8-2.2,3.9c-1.5,1.2-3.3,1.9-5.1,2c-7.5,0.8-15,0.8-22.5,0c-1.9-0.1-3.6-0.8-5.1-2c-1.1-1.1-1.8-2.4-2.2-3.9 c-0.8-3.2-1.2-6.4-1.4-9.7c-0.2-3.3-0.2-6.7,0.1-10C3,9,4.8,7.2,8.8,6.5c2.2-0.4,4.5-0.6,6.7-0.7c1.9-0.1,5-0.2,6.8-0.2 s4.9,0,6.8,0.2c2.2,0.1,4.5,0.3,6.7,0.7c4,0.7,5.8,2.6,6.3,6.3C42.3,16.1,42.4,19.5,42.2,22.8L42.2,22.8z\"/> </g> </svg>", "mono": true, "stroked": false}, "nissan": {"kind": "svg", "markup": "<svg viewBox=\"0 0 70 58\" fill=\"none\" xmlns=\"http://www.w3.org/2000/svg\" preserveAspectRatio=\"xMidYMid meet\" focusable=\"false\"> <path d=\"M9.99902 37.5322L10.0303 37.6201C13.6631 48.1408 23.6998 55.2111 35.0059 55.2129H35.0088C46.314 55.2128 56.3507 48.1446 59.9854 37.625L60.0156 37.5381H60.1094C60.7839 37.5385 67.0437 37.5391 67.8389 37.5391H67.9688V38.4844L67.8535 38.498C67.6584 38.5199 64.6925 38.8625 64.6602 38.8662C62.6203 39.1013 62.1845 39.992 61.6328 41.1191L61.4971 41.3936C56.7182 51.4802 46.3202 57.9999 35.0098 58H35.0049C23.6919 57.9987 13.2941 51.477 8.51562 41.3848L8.38184 41.1143C7.8308 39.9863 7.39589 39.0954 5.35547 38.8594C5.35547 38.8594 2.36884 38.5152 2.16309 38.4912L2.04785 38.4775V37.5322H9.99902ZM8.32715 30.9766V24.9629H10.1299V33.0322H7.85254L1.80371 26.9785V33.0322H0V24.9629H2.32129L8.32715 30.9766ZM15.9199 33.0322H14.1172V24.9629H15.9199V33.0322ZM57.502 33.0322H55.3164L54.4121 31.5908H48.4785L47.5742 33.0322H45.3867L50.4746 24.9629H52.417L57.502 33.0322ZM68.1973 30.9766V24.9629H70V33.0322H67.7227L61.6729 26.9785V33.0322H59.8701V24.9629H62.1904L68.1973 30.9766ZM29.1543 26.6357H22.2793C22.0172 26.6357 21.8964 26.6375 21.7803 26.6719C21.3919 26.7868 21.2539 27.117 21.2539 27.3652C21.2539 27.6355 21.3892 27.9604 21.7676 28.0615C21.8586 28.0852 22.0814 28.1025 22.2969 28.1025H27.04V28.2461L27.0566 28.1025C27.1615 28.1008 27.3775 28.1021 27.6416 28.127C28.9893 28.2576 29.6942 29.4385 29.6943 30.5371C29.6943 31.6201 29.0172 32.846 27.5303 32.9775C27.4348 32.9854 27.0152 32.9883 26.9551 32.9883H19.668V31.3438H26.8438C26.9331 31.3437 27.1589 31.3362 27.2109 31.3271C27.6694 31.2475 27.875 30.8783 27.875 30.5488C27.8749 30.2099 27.689 29.8223 27.1689 29.751C27.1253 29.7452 26.9197 29.7402 26.832 29.7402H22.1914C22.0394 29.7398 21.6871 29.7429 21.4414 29.708C20.0645 29.5103 19.4377 28.3571 19.4375 27.3691C19.4375 26.1611 20.2737 25.2035 21.4707 25.042C21.6571 25.0171 21.8728 25.0059 22.1689 25.0059H29.1543V26.6357ZM42.7305 26.6357H35.8555C35.5935 26.6357 35.4727 26.6375 35.3574 26.6719C34.9678 26.7868 34.8301 27.117 34.8301 27.3652C34.8301 27.6355 34.965 27.9604 35.3438 28.0615C35.4351 28.0852 35.6578 28.1025 35.873 28.1025H40.6162V28.2461L40.6328 28.1025C40.7384 28.1008 40.954 28.1021 41.2178 28.127C42.5649 28.2576 43.2704 29.4385 43.2705 30.5371C43.2705 31.6202 42.593 32.8459 41.1064 32.9775C41.0104 32.9854 40.5906 32.9883 40.5303 32.9883H33.2441V31.3438H40.4199C40.5087 31.3437 40.734 31.3361 40.7871 31.3271C41.2452 31.2472 41.4512 30.8783 41.4512 30.5488C41.451 30.2099 41.2654 29.8223 40.7451 29.751C40.7021 29.7452 40.4958 29.7402 40.4082 29.7402H35.7676C35.618 29.7402 35.2634 29.743 35.0176 29.708C33.6406 29.5103 33.0139 28.3571 33.0137 27.3691C33.0137 26.1611 33.8492 25.2038 35.0459 25.042C35.2327 25.0171 35.4481 25.0059 35.7441 25.0059H42.7305V26.6357ZM49.4082 30.0654H53.4805L51.4463 26.8232L49.4082 30.0654ZM35.0088 0C46.321 3.42941e-05 56.7193 6.52008 61.499 16.6104L61.6338 16.8838C62.1866 18.0122 62.6227 18.902 64.6611 19.1377C64.6805 19.1399 67.6502 19.4829 67.8535 19.5059L67.9688 19.5186V20.4648H60.0176L59.9873 20.377C56.3531 9.85638 46.3149 2.78812 35.0088 2.78809C23.7026 2.78809 13.6645 9.85639 10.0303 20.377L10 20.4648H2.04883V19.5186L2.16406 19.5059C2.36673 19.4828 5.35645 19.1377 5.35645 19.1377C7.39618 18.902 7.83213 18.011 8.38379 16.8838L8.51855 16.6104C13.2971 6.5206 23.6954 0 35.0088 0Z\" fill=\"white\"/> </svg>", "mono": true, "stroked": false}, "suzuki": {"kind": "img", "file": "suzuki.png"}, "toyota": {"kind": "svg", "markup": "<svg version=\"1.1\" id=\"レイヤー_1\" xmlns=\"http://www.w3.org/2000/svg\" xmlns:xlink=\"http://www.w3.org/1999/xlink\" x=\"0px\" y=\"0px\" viewBox=\"0 0 160 108\" xml:space=\"preserve\" preserveAspectRatio=\"xMidYMid meet\" focusable=\"false\"> <g> <path d=\"M114.4,9.4C104.8,6.3,92.9,4.5,80,4.5c-12.9,0-24.8,1.8-34.4,4.9c-25.5,8.2-43,25.2-43,44.8c0,27.6,34.6,50.1,77.4,50.1 c42.7,0,77.4-22.4,77.4-50.1C157.4,34.6,139.9,17.6,114.4,9.4z M80,82.8c-6.4,0-11.6-12.5-11.9-28.3C71.9,54.9,75.9,55,80,55 c4.1,0,8.1-0.2,11.9-0.5C91.6,70.3,86.4,82.8,80,82.8z M68.9,42.2c1.7-11.1,6-18.9,11.1-18.9c5,0,9.3,7.8,11.1,18.9 c-3.5,0.3-7.3,0.5-11.1,0.5C76.2,42.7,72.5,42.5,68.9,42.2z M97.9,41.3C95.3,24,88.3,11.5,80,11.5c-8.3,0-15.3,12.4-17.9,29.8 c-15.7-2.5-26.7-8-26.7-14.5c0-8.8,20-15.9,44.6-15.9s44.6,7.1,44.6,15.9C124.6,33.3,113.6,38.9,97.9,41.3z M13.9,52.4 c0-8.5,3.3-16.4,9-23.3c-0.1,0.5-0.1,1-0.1,1.4c0,10.7,16,19.7,38.3,23.1c0,0.8,0,1.6,0,2.4c0,19.8,5.5,36.6,13.1,42.4 C40.4,96.4,13.9,76.6,13.9,52.4z M85.8,98.5c7.6-5.8,13.1-22.6,13.1-42.4c0-0.8,0-1.6,0-2.4c22.3-3.3,38.3-12.4,38.3-23.1 c0-0.5,0-1-0.1-1.4c5.7,6.8,9,14.8,9,23.3C146.1,76.6,119.6,96.4,85.8,98.5z\"/> </g> </svg>", "mono": true, "stroked": false}};
let TINT = true;                                       // true=品牌色 / false=原色（浅色底衬托）
try{ const v = localStorage.getItem('logo-tint'); if(v!==null) TINT = v === '1'; }catch(e){}

function applyLogo(el){
  const f = LOGO_FILES[(el.dataset.b||'').toLowerCase()];
  if(!f) return;                                       // 无车标文件 → 保留内置绘制图标
  el.classList.add('real');
  if(f.kind === 'svg'){
    el.innerHTML = `<span class="pic${f.mono?' mono':''}${f.stroked?' stroked':''}">${f.markup}</span>`
      + (el.dataset.fb||'');
  }else{
    el.innerHTML = `<img class="pic" src="logos/${f.file}" alt="${el.dataset.b}">` + (el.dataset.fb||'');
  }
}
function refreshLogos(){
  document.querySelectorAll('.logo[data-b]').forEach(applyLogo);
  document.body.classList.toggle('orig', !TINT);
}
function upgradeLogos(root){
  (root||document).querySelectorAll('.logo[data-b]').forEach(el=>{
    if(el.dataset.done) return;
    el.dataset.done = '1';
    el.dataset.fb = el.innerHTML;                      // 记住内置图标，供原色模式兜底
    applyLogo(el);
  });
  (root||document).querySelectorAll('.logo').forEach(el=>el.classList.toggle('real',
    !!LOGO_FILES[(el.dataset.b||'').toLowerCase()]));
}
const $ = s => document.querySelector(s);
const fmt = n => (n||0).toLocaleString('en-US');
const hm  = m => Math.floor(m/60) + 'h' + String(m%60).padStart(2,'0') + 'm';

/* ---------- 汇总 ---------- */
const T = R.reduce((a,r)=>({n:a.n+1,km:a.km+r.km,yen:a.yen+r.yen,min:a.min+r.minutes}),{n:0,km:0,yen:0,min:0});
const dates = R.map(r=>r.start.slice(0,10)).sort();
$('#sub').innerHTML = `${dates[0]} → ${dates[dates.length-1]} · 共 <b>${T.n}</b> 次行程 · `
  + `<b>${new Set(R.map(r=>r.base)).size}</b> 个车系 · 总支出 <b>¥${fmt(T.yen)}</b>`;

/* 品牌图例 */
(function(){
  const bs = [...new Set(R.map(r=>r.brand).filter(Boolean))].sort();
  const el = document.createElement('div');
  el.className = 'brands';
  el.innerHTML = bs.map(b=>`<span class="blogo" style="--bc:${BRAND_COLOR[b]}">
    ${logo(b)}<b>${b}</b><i>${R.filter(r=>r.brand===b).length}次</i></span>`).join('');
  document.querySelector('header').appendChild(el);
  upgradeLogos(el);
})();

const KPI = [
  ['总行程', T.n, '次', `平均 ¥${fmt(Math.round(T.yen/T.n))} / 次`, '#22d3ee'],
  ['总行驶距离', T.km, 'km', `平均 ${(T.km/T.n).toFixed(1)} km / 次`, '#a855f7'],
  ['总请求金额', T.yen, '円', `约 ¥${fmt(Math.round(T.yen/ (T.min/60)))} / 小时`, '#ff3d81'],
  ['总利用时间', Math.round(T.min/60), '小时', `${hm(T.min)} 累计`, '#facc15'],
];
$('#kpis').innerHTML = KPI.map(([l,v,u,e,c])=>`
  <div class="kpi" style="--ac:${c}">
    <div class="lb">${l}</div>
    <div class="vl"><span class="num" data-to="${v}">0</span><small>${u}</small></div>
    <div class="ex">${e}</div>
  </div>`).join('');

/* ---------- 数字滚动 ---------- */
const io = new IntersectionObserver(es=>es.forEach(e=>{
  if(!e.isIntersecting) return;
  const el = e.target;
  io.unobserve(el);
  if(el.classList.contains('num')){
    const to = +el.dataset.to, t0 = performance.now(), d = 1400;
    (function step(t){
      const p = Math.min((t-t0)/d,1), e2 = 1-Math.pow(1-p,3);
      el.textContent = Math.round(to*e2).toLocaleString('en-US');
      if(p<1) requestAnimationFrame(step);
    })(t0);
  }else{
    el.classList.add('in');
    el.querySelectorAll('.fill,.cfill').forEach((f,i)=>setTimeout(()=>f.style.width=f.dataset.w,(i*40)+120));
    el.querySelectorAll('.mbar').forEach((b,i)=>setTimeout(()=>b.style.height=b.dataset.h,i*55));
  }
}),{threshold:.18});
document.querySelectorAll('.panel').forEach(p=>io.observe(p));
document.querySelectorAll('.num').forEach(n=>io.observe(n));

/* ---------- 分组 ---------- */
function groupBy(mode){
  const m = new Map();
  R.forEach(r=>{
    const k = r[mode];
    if(!m.has(k)) m.set(k,{name:k,brand:r.brand,variants:new Set(),stations:new Set(),n:0,km:0,yen:0,minutes:0,first:r.start,last:r.start});
    const g = m.get(k);
    g.variants.add(r.car); g.stations.add(r.station);
    g.n++; g.km+=r.km; g.yen+=r.yen; g.minutes+=r.minutes;
    if(r.start<g.first) g.first=r.start;
    if(r.start>g.last)  g.last=r.start;
  });
  return [...m.values()].sort((a,b)=>b.yen-a.yen);
}

let MODE='base', METRIC='km';
function renderCards(){
  const g = groupBy(MODE);
  const maxKm = Math.max(...g.map(x=>x.km)), maxYen = Math.max(...g.map(x=>x.yen));
  $('#grid').innerHTML = g.map((x,i)=>{
    const c = PALETTE[i%PALETTE.length];
    const vs = [...x.variants].filter(v=>v!==x.name);
    return `<div class="card" style="--cc:${c}">
      <div class="rk">${String(i+1).padStart(2,'0')}</div>
      <div class="hd">${logo(x.brand)}
        <div class="nm">${x.name}<span class="en">${(x.brand?x.brand+' · ':'')+(MODEL_EN[x.name]||x.name)}</span></div>
      </div>
      <div class="chips">
        <span class="chip b">${x.n} 次</span>
        ${vs.map(v=>`<span class="chip">${v}</span>`).join('')}
        <span class="chip">${x.stations.size} 个站点</span>
      </div>
      <div class="stats">
        <div class="stat"><div class="v">${hm(x.minutes)}</div><div class="k">总时长</div></div>
        <div class="stat"><div class="v">${fmt(x.km)}</div><div class="k">距离 km</div></div>
        <div class="stat"><div class="v">¥${fmt(x.yen)}</div><div class="k">金额 円</div></div>
      </div>
      <div class="bars">
        <div class="bar"><div class="t"><span>走行距離</span><b>${fmt(x.km)} km</b></div>
          <div class="track"><div class="fill" data-w="${(x.km/maxKm*100).toFixed(1)}%" style="background:linear-gradient(90deg,${c},${c}55)"></div></div></div>
        <div class="bar"><div class="t"><span>請求金額</span><b>¥${fmt(x.yen)}</b></div>
          <div class="track"><div class="fill" data-w="${(x.yen/maxYen*100).toFixed(1)}%" style="background:linear-gradient(90deg,${c}aa,${c})"></div></div></div>
      </div>
      <div class="foot">
        <span>均次 <b>¥${fmt(Math.round(x.yen/x.n))}</b></span>
        <span>均次 <b>${(x.km/x.n).toFixed(1)} km</b></span>
        <span><b>¥${fmt(Math.round(x.yen/(x.minutes/60)))}</b>/時</span>
      </div>
    </div>`;
  }).join('');
  upgradeLogos($('#grid'));
  $('#grid').closest('.panel').classList.add('in');
  requestAnimationFrame(()=>$('#grid').querySelectorAll('.fill').forEach((f,i)=>setTimeout(()=>f.style.width=f.dataset.w,i*45)));
}

/* ---------- 对比图 ---------- */
const META = {km:['走行距離','km','#22d3ee'],yen:['請求金額','円','#ff3d81'],
  minutes:['利用時間','分','#facc15'],count:['利用回数','回','#a855f7']};
function renderChart(){
  const g = groupBy(MODE);
  const [label,unit,c] = META[METRIC];
  const arr = g.map(x=>({name:x.name,brand:x.brand,v:METRIC==='count'?x.n:x[METRIC]}))
               .sort((a,b)=>b.v-a.v);
  const max = Math.max(...arr.map(x=>x.v));
  $('#chart').innerHTML = arr.map((x,i)=>{
    const col = PALETTE[i%PALETTE.length];
    const show = METRIC==='minutes' ? hm(x.v) : fmt(x.v);
    return `<div class="crow">
      <div class="cn" title="${x.name}">${logo(x.brand,true)}<span>${x.name}</span></div>
      <div class="ctrack"><div class="cfill" data-w="${(x.v/max*100).toFixed(1)}%"
        style="background:linear-gradient(90deg,${col},${col}66)">${(x.v/max*100)>18?show:''}</div></div>
      <div class="cv"><b>${show}</b> ${unit}</div>
    </div>`;
  }).join('');
  upgradeLogos($('#chart'));
  requestAnimationFrame(()=>$('#chart').querySelectorAll('.cfill').forEach((f,i)=>setTimeout(()=>f.style.width=f.dataset.w,i*50)));
}
$('#metric').addEventListener('click',e=>{
  const b = e.target.closest('button'); if(!b) return;
  [...e.currentTarget.children].forEach(x=>x.classList.toggle('on',x===b));
  METRIC = b.dataset.k; renderChart();
});
$('#seg').addEventListener('click',e=>{
  const b = e.target.closest('button'); if(!b) return;
  [...e.currentTarget.children].forEach(x=>x.classList.toggle('on',x===b));
  MODE = b.dataset.m; renderCards(); renderChart();
});
$('#tint').addEventListener('click',e=>{
  const b = e.target.closest('button'); if(!b) return;
  [...e.currentTarget.children].forEach(x=>x.classList.toggle('on',x===b));
  TINT = b.dataset.t === '1';
  try{ localStorage.setItem('logo-tint', TINT ? '1' : '0'); }catch(err){}
  refreshLogos();
});

/* ---------- 月度 ---------- */
(function(){
  const m = new Map();
  R.forEach(r=>{const k=r.start.slice(0,7);
    if(!m.has(k)) m.set(k,{n:0,km:0,yen:0});
    const o=m.get(k); o.n++; o.km+=r.km; o.yen+=r.yen;});
  const ks=[...m.keys()].sort(), max=Math.max(...ks.map(k=>m.get(k).yen));
  $('#months').innerHTML = ks.map(k=>{
    const o=m.get(k), h=(o.yen/max*100);
    return `<div class="mcol">
      <div class="mbar" data-h="${Math.max(h,3)}%" style="height:0">
        <span>${o.n}次 · ${o.km}km · ¥${fmt(o.yen)}</span></div>
      <div class="mlb">${k.slice(5)}月</div></div>`;
  }).join('');
})();

/* ---------- 明细 ---------- */
let SORT='start', DESC=true;
function renderTable(){
  const q = $('#q').value.trim().toLowerCase();
  let rows = R.filter(r=>!q || (r.car+r.station+r.no+r.base).toLowerCase().includes(q));
  rows.sort((a,b)=>{
    const x=a[SORT], y=b[SORT];
    return (typeof x==='number' ? x-y : String(x).localeCompare(String(y))) * (DESC?-1:1);
  });
  $('#cnt').textContent = `${rows.length} / ${R.length} 条`;
  $('#tb').innerHTML = rows.map(r=>`
    <tr>
      <td class="mut">${r.start}</td>
      <td class="car"><span class="cw">${logo(r.brand,true)}${r.car}</span></td>
      <td>${r.station}</td>
      <td class="n">${hm(r.minutes)}</td>
      <td class="n">${r.km} km</td>
      <td class="n">¥${fmt(r.yen)}</td>
    </tr>`).join('') || `<tr><td colspan="6" style="text-align:center;color:#8b93ad;padding:30px">无匹配结果</td></tr>`;
  upgradeLogos($('#tb'));
}
$('#q').addEventListener('input',renderTable);
$('#sortseg').addEventListener('click',e=>{
  const b=e.target.closest('button'); if(!b) return;
  [...e.currentTarget.children].forEach(x=>x.classList.toggle('on',x===b));
  SORT=b.dataset.s; DESC=true; renderTable();
});
document.querySelectorAll('th[data-c]').forEach(th=>th.addEventListener('click',()=>{
  const c=th.dataset.c; DESC = (SORT===c) ? !DESC : true; SORT=c; renderTable();
}));

renderCards(); renderChart(); renderTable();
