from data_structure.DiPanZHP import DiPanZHP


class DiPanINTER:

    def __init__(self):
        # ----------------- 通过数据库一次性统计出的结果 --------------------- #

        # ---------------- 根据中间变量进一步计算得出的结果 -------------------- #
        self.days = 0
        self.x1 = 0.0
        self.x2 = 0.0
        self.x3 = 0.0
        self.x4 = 0.0
        self.x5 = 0.0
        self.x6 = 0.0
        self.g0 = 0.0
        self.g1 = 0.0
        self.g2 = 0.0
        self.g3 = 0.0
        self.g4 = 0.0
        self.g5 = 0.0
        self.g6 = 0.0
        self.g7 = 0.0
        self.g8 = 0.0
        self.g9 = 0.0
        self.z1 = 0.0
        self.z2 = 0.0
        self.h1 = 0.0
        self.h2 = 0.0

        # ----------------- 直接输出的载荷谱 (DataFrame) -------------------- #
        self.out = None

    def intermediate_compute(self,
                             diPanZhp: DiPanZHP):
        # 行驶时间（小时 / 天）
        self.x3 += sum(diPanZhp.xs_time) / self.days
        # 待机时间（小时 / 天）
        self.x4 += sum(diPanZhp.dj_time) / self.days
        # 天行驶小时数（小时 / 天）
        self.x5 += self.x3 + self.x4
        # 年行驶天数（天 / 年）
        self.x2 += (sum(diPanZhp.jt_time) / 24) / self.days * 365
        # 年行驶月数（月 / 年）
        self.x1 = self.x2 / 30 / 2 + 6
        # 天行驶里程（km / 天）
        self.x6 += (diPanZhp.s5_dist
                    + diPanZhp.s10_dist
                    + diPanZhp.s20_dist
                    + diPanZhp.s30_dist
                    + diPanZhp.s40_dist
                    + diPanZhp.s50_dist
                    + diPanZhp.s60_dist
                    + diPanZhp.s70_dist
                    + diPanZhp.s80_dist
                    + diPanZhp.g80_dist) / self.days
        # 显示器（小时 / 天）
        self.g0 = 0.35 * (self.x3 + self.x4)
        # 驾驶室雨刮电机（小时 / 天）
        self.g1 = 0.1 * (self.x3 + self.x4)
        # 雨刮（小时 / 天）
        self.g2 = 0.0143 * (self.x3 + self.x4)
        # 散热器（小时 / 天）
        self.g3 = 0.3 * (self.x3 + self.x4)
        # 空调（小时 / 天）
        self.g4 = 0.35 * (self.x3 + self.x4)
        # 显示器（小时 / 年）
        self.g5 = self.x2 * self.g0
        # 驾驶室雨刮电机（小时 / 年）
        self.g6 = self.x2 * self.g1
        # 雨刮（小时 / 年）
        self.g7 = self.x2 * self.g2
        # 散热器（小时 / 年）
        self.g8 = self.x2 * self.g3
        # 空调（小时 / 年）
        self.g9 = self.x2 * self.g4

        # 支腿收放次数（次 / 天）
        self.z1 += sum(diPanZhp.zt_sfcs) / self.days * 1.3
        # 支腿收放次数（次 / 年）
        self.z2 = self.z1 * self.x2
        # 换挡次数（次 / 天）
        self.h1 += sum(diPanZhp.hdcs) / self.days * 1.3
        # 换挡次数（次 / 年）
        self.h2 = self.h1 * self.x2

        # 工作年限
        max_weight = 0  # 产品吨位参数有待确定
        if max_weight < 80:
            self.I = 10
        elif max_weight < 200:
            self.I = 12
        elif max_weight < 500:
            self.I = 15
        else:
            self.I = 20

