from data_loader.OracleManager import OracleManager
from data_structure.ZhengJiZHP import ZhengJiZHP


class QiShengINTER:

    days = None

    def __int__(self):
        # ----------------- 通过数据库一次性统计出的结果 --------------------- #
        self.Q_max = 0.0  # 最大负载率
        self.qs_weight_max = 0.0  # 最大起升重

        # ---------------- 根据中间变量进一步计算得出的结果 -------------------- #
        self.days = 0
        self.D0 = 0.0
        self.D1 = 0.0
        self.D2 = 0.0
        self.D3 = 0.0
        self.D4 = 0.0
        self.D5 = 0.0
        self.D6 = 0.0
        self.D7 = 0.0
        self.D8 = 0.0
        self.D9 = 0.0
        self.D10 = 0.0
        self.D11 = 0.0
        self.D12 = 0.0
        self.D13 = 0.0
        self.D14 = 0.0
        self.D15 = 0.0
        self.D16 = 0.0
        self.D17 = 0.0
        self.D18 = 0.0
        self.D19 = 0.0
        self.M = 0.0
        self.N = 0.0

        # ----------------- 直接输出的载荷谱 (DataFrame) -------------------- #
        self.out = None

    def intermediate_compute(self,
                             days: int,
                             ZhengJiZHP: ZhengJiZHP
                             ):
        """
        该函数主要用于分 Batch 计算载荷谱的结果
        :param days: 要计算载荷谱的总工作时间
        :param ZhengJiZHP: 整机载荷谱
        """
        # 起重机循环次数 (次 / 天)
        self.D3 += sum(ZhengJiZHP.c1 + ZhengJiZHP.c2 + ZhengJiZHP.c3 + ZhengJiZHP.c4 + ZhengJiZHP.c5
                       + ZhengJiZHP.c6 + ZhengJiZHP.c7 + ZhengJiZHP.c8 + ZhengJiZHP.c9 + ZhengJiZHP.c10
                       + ZhengJiZHP.c11 + ZhengJiZHP.c12) / days * 1.3
        # 起重机待机时间 (小时 / 天)
        self.N += sum(ZhengJiZHP.dj_time) / days * 1.3
        # 起重机作业时间 (小时 / 天)
        self.M += sum(ZhengJiZHP.zy_time) / days * 1.3
        # 起重机工作时间 (小时 / 天)
        self.D2 += self.M + self.N
        # 年工作小时数
        self.D4 += self.D2 * self.D1
        # 起重机工作天数 (天 / 年)
        self.D1 += sum(ZhengJiZHP.zy_time) / days * 365
        # 起重机工作月数 (月 / 年)
        self.D0 += self.D1 / 30 / 2 + 6
        # 年循环次数
        self.D5 += self.D3 * self.D1
        # 总工作时间
        self.D7 += self.D6 * self.D4
        # 总循环次数
        self.D8 += self.D6 * self.D5


    def intermediate_count(self,
                           oracleManager: OracleManager,
                           VMI_NAME: str = 'XCT25L5'
                           ):
        """
        该函数主要通过数据库筛选出载荷谱的最大值等不需要分 Batch 计算的部分
        :param oracleManager:
        :param VMI_NAME:
        """
        # step 1: Oracle 连接初始化
        if oracleManager.isConnect is False:
            oracleManager.connect()

        # step 2: 从数据库中查询最大值
        curs = oracleManager.db.cursor()
        # 暂定表名为 INTERMEDIATE_XCT25_JIGOU
        system_name = 'JIGOU'
        table_name = '_'.join(['INTER', VMI_NAME, system_name])

        # 根据载荷谱系数确定载荷状态级别
        # 根据载荷状态级别和起重机使用等级判断起重机的工作级别

        # 工作年限确定 (分工况太麻烦，不分工况了)
        max_weight = self.qs_weight_max
        if max_weight < 80:
            self.D6 = 10
        elif max_weight < 200:
            self.D6 = 12
        elif max_weight < 500:
            self.D6 = 15
        else:
            self.D6 = 20


