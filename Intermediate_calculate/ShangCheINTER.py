from data_loader.OracleManager import OracleManager
from data_structure.ZHP import ZHP
from data_structure.ZhengJiZHP import ZhengJiZHP
from data_structure.QiShengZHP import QiShengZHP
from Intermediate_calculate.ZhengJiINTER import QiShengINTER
from Intermediate_calculate.PeiZhongINTER import PeiZhongINTER
import pandas as pd
import numpy as np
from utils.const import Const
from MechanicalFormulas import MechanicalFormulas


class ShangCheINTER:

    def __init__(self):
        # ---------------------------- 通过数据库一次性统计出的结果 --------------------------------- #
        self.qsb_zj_max = 0.0  # 泵工作扭矩最大值
        self.zt_fl_max = 0.0  # 支腿反力（F1&F2）

        # ---------------------------- 根据中间变量进一步计算得出的结果 ------------------------------ #
        self.days = 0
        self.D0 = 0.0
        self.D1 = 0.0
        self.D2 = 0.0
        self.D3 = 0.0
        self.D4 = 0.0
        self.D5 = 0.0
        self.D6 = 0.0
        self.Z1 = 0.0
        self.Z2 = 0.0

        self.G0 = 0.0
        self.G1 = 0.0
        self.G2 = 0.0
        self.G3 = 0.0
        self.G4 = 0.0
        self.G5 = 0.0
        self.G6 = 0.0
        self.G7 = 0.0
        self.G8 = 0.0
        self.G9 = 0.0

        self.Ct = 0.0  # 主起升总工作循环次数

        # ----------------- 直接输出的载荷谱 (DataFrame) -------------------- #
        # 创建Dataframe用以表示最终的载荷谱表
        self.index = ['上车动力系统', '发动机', '散热器', '空滤器', '消声器', '启动马达', '电油门',
                      '分动箱', '上车公共系统', '力限器', '显示器', '水平仪', 'GPS模块',
                      '中心回转体', '上车空调及散热', '散热器', '空调', '上车集中润滑系统', '润滑泵',
                      '分配器', '操纵室及外观', '雨刮电机', '门锁', '玻璃伸降器', '雨刮', '支腿系统', '垂直油缸',
                      '水平油缸', '双向液压阀', '双向液压阀', '测长传感器', '压力传感器']
        self.out = pd.DataFrame(index=self.index,
                                columns=Const.table_columns)

    def intermediate_count(self,
                           oracleManager: OracleManager,
                           VMI_NAME: str = 'XCT25L5'
                           ):
        """
        该函数主要通过数据库筛选出载荷谱的最大值等不需要分 Batch 计算的部分
        :param oracleManager:
        :param VMI_NAME:
        """
        # ---------------------------- step 1: Oracle 连接初始化 ---------------------------- #
        if oracleManager.isConnect is False:
            oracleManager.connect()

        # ---------------------------- step 2: 从数据库中查询最大值 ---------------------------- #
        curs = oracleManager.db.cursor()
        # 暂定表名为 INTERMEDIATE_XCT25_JIGOU
        system_name = 'JIGOU'
        table_name = '_'.join(['INTER', VMI_NAME, system_name])
        curs.execute('SELECT MAX(qsb_zj) FROM ' + table_name)
        self.qsb_zj_max = curs.fetchone()[0]
        ##不知参数如何提取？？？？？？？？？？？？？？？？？？？？？？？
        curs.execute('SELECT MAX(qzl_q_max) FROM ' + table_name)
        self.zt_fl_max = curs.fetchone()[0]

    def intermediate_compute(self,
                             days: int,
                             pZhp: ZHP,
                             qQiShengINTER: QiShengINTER,
                             pPeiZhongINTER: PeiZhongINTER
                             ):

        self.D0 = qQiShengINTER.D0
        self.D1 = qQiShengINTER.D1
        self.D2 = qQiShengINTER.D2
        self.D3 = qQiShengINTER.D3
        self.D4 = qQiShengINTER.D4
        self.D5 = qQiShengINTER.D5
        self.D6 = qQiShengINTER.D6

        self.Z1 = pPeiZhongINTER.Z1
        self.Z2 = pPeiZhongINTER.Z2

        self.G0 = self.D2
        self.G1 = 0.143 * self.D2
        self.G2 = 0.0143 * self.D2
        self.G3 = 0.34 * self.D2
        self.G4 = 0.45 * self.D2
        self.G5 = self.D1 * self.D2
        self.G6 = 0.143 * self.D1 * self.D2
        self.G7 = 0.0143 * self.D1 * self.D2
        self.G8 = 0.34 * self.D1 * self.D2
        self.G9 = 0.45 * self.D1 * self.D2

        # 载荷谱系数确定 => 问张工
        # 主起升总循环次数
        self.Ct += sum(pZhp.QiShengZHP.qs_cs)

        # 载荷次数/时间计算参数未知？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？？
        # 默认所有载荷次数和时间的初始值为0
        for index in self.index:
            if "%" in index: self.out[index] = 0.0
        for row in Const.MAX_ROWS:
            for component in ['上车动力系统', '发动机', '散热器', '空滤器', '消声器', '启动马达',
                              '分动箱', '中心回转体']:
                if pZhp.JiGouZHP.qsb_zj[row] < 0.05 * self.qsb_zj_max:
                    self.out['5%以内载荷次数'][component] = pZhp.QiShengZHP.qs_cs[row]
                    self.out['5%以内载荷时间'][component] += pZhp.QiShengZHP.qs_time[row] + pZhp.QiShengZHP.ql_time[row]
                elif 0.05 * self.qsb_zj_max <= pZhp.JiGouZHP.jyds_ll[row] < 0.5 * self.qsb_zj_max:
                    self.out['5-50%载荷次数'][component] += pZhp.QiShengZHP.qs_cs[row]
                    self.out['5-50%载荷时间'][component] += pZhp.QiShengZHP.qs_time[row] + pZhp.QiShengZHP.ql_time[row]
                elif 0.5 * self.qsb_zj_max <= pZhp.JiGouZHP.jyds_ll[row] < 0.95 * self.qsb_zj_max:
                    self.out['50-90%载荷次数'][component] += pZhp.QiShengZHP.qs_cs[row]
                    self.out['50-95%载荷时间'][component] += pZhp.QiShengZHP.qs_time[row] + pZhp.QiShengZHP.ql_time[row]
                else:
                    self.out['95%以上载荷次数'][component] += pZhp.QiShengZHP.qs_cs[row]
                    self.out['95%以上载荷时间'][component] += pZhp.QiShengZHP.qs_time[row] + pZhp.QiShengZHP.ql_time[row]

    def output_loadspectrum(self, vehicle_id='XCT25L5'):
        # -------------------------------- 确定剩余需要确定的变量 ---------------------------------- #
        # 使用等级确定 (每个部件都相同)
        self.out['使用等级'] = MechanicalFormulas.compute_shiyong_dengji(self.Ct)
        for component in self.index:
            # 载荷谱状态确定 (需要确定载荷谱系数)
            self.out['载荷状态'][component] = MechanicalFormulas.compute_zaihe_zhuangtai(
                self.out['载荷谱系数'][component])
            # 工作级别确定
            self.out['工作级别'][component] = MechanicalFormulas.compute_gongzuo_jibie(self.out['载荷状态'][component],
                                                                                   self.out['使用等级'][component])
