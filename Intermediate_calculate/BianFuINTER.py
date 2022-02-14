from data_loader.OracleManager import OracleManager
from data_structure.BianFuZHP import BianFuZHP


class BianFuINTER:

    def __init__(self):
        # ----------------- 通过数据库一次性统计出的结果 --------------------- #
        self.bfg_fl_di_cd2_max = 0.0
        self.bfg_fl_max = 0.0
        self.bfg_q_yl_max = 0.0
        self.bfg_l_yl_max = 0.0

        # ---------------- 根据中间变量进一步计算得出的结果 -------------------- #
        self.days = 0
        self.A1 = 0.0
        self.B1 = 0.0
        self.C1 = 0.0
        self.D1 = 0.0
        self.E1 = 0.0
        self.F1 = 0.0
        self.G1 = 0.0
        self.H1 = 0.0
        self.I = 0.0

        # ----------------- 直接输出的载荷谱 (DataFrame) -------------------- #
        self.out = None

    def intermediate_compute(self,
                             bianFuZhp: BianFuZHP):
        # 变幅起时间（小时 / 天）
        self.D1 += sum(bianFuZhp.q_time) / self.days * 1.3
        # 变幅落时间（小时 / 天）
        self.E += sum(bianFuZhp.l_time) / self.days * 1.3
        # 变幅循环次数（次 / 天）
        self.F += sum(bianFuZhp.xhcs) / self.days * 1.3
        # 变幅起冲击次数（次 / 天）
        self.G += sum(bianFuZhp.q_cjcs) / self.days * 1.3
        # 变幅落冲击次数（次 / 天）
        self.H += sum(bianFuZhp.l_cjcs) / self.days * 1.3
        # 变幅工作时间（小时 / 天）
        self.C = self.D + self.E
        # 变幅工作时间（天 / 年）
        self.B += (sum(bianFuZhp.t_time) / 24) / self.days * 365

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

        # 载荷谱系数

    def intermediate_count(self,
                           oracleManager: OracleManager,
                           VMI_NAME: str='XCT25L5'):

        # step 1: Oracle 连接初始化
        if oracleManager.isConnect is False:
            oracleManager.connect()

        # step 2: 从数据库中查询最大值
        curs = oracleManager.db.cursor()

        system_name = 'JIGOU'
        table_name = '_'.join(['INTER', VMI_NAME, system_name])
        curs.execute('SELECT MAX(bfg_fl_di_cd2) FROM ' + table_name)
        self.bfg_fl_di_cd2_max = curs.fetchone()[0]
        curs.execute('SELECT MAX(bfg_fl) FROM ' + table_name)
        self.bfg_fl_max = curs.fetchone()[0]
        curs.execute('SELECT MAX(bfg_q_yl) FROM ' + table_name)
        self.bfg_q_yl_max = curs.fetchone()[0]
        curs.execute('SELECT MAX(bfg_l_yl) FROM ' + table_name)
        self.bfg_l_yl_max = curs.fetchone()[0]
