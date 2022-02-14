from data_loader.OracleManager import OracleManager
from data_structure.ZHP import ZHP
from data_structure.ZhengJiZHP import ZhengJiZHP
from data_structure.QiShengZHP import QiShengZHP
from Intermediate_calculate.ZhengJiINTER import QiShengINTER
from Intermediate_calculate.PeiZhongINTER import PeiZhongINTER
from Intermediate_calculate.ShangCheINTER import ShangCheINTER
from Intermediate_calculate.ZQiShengINTER import ZQiShengINTER
from Intermediate_calculate.BianFuINTER import BianFuINTER
from Intermediate_calculate.ShenSuoINTER import ShenSuoINTER

import pandas as pd
import numpy as np
from utils.const import Const
from MechanicalFormulas import MechanicalFormulas


class ShangCheDongLi:

    def __init__(self):
        # ---------------------------- 通过数据库一次性统计出的结果 --------------------------------- #
        self.qsb_zj_max = 0.0  # 泵工作扭矩最大值

        # ---------------------------- 根据中间变量进一步计算得出的结果 ------------------------------ #
        self.D0 = 0.0
        self.D1 = 0.0
        self.D2 = 0.0
        self.D3 = 0.0
        self.D4 = 0.0
        self.D5 = 0.0
        self.D6 = 0.0
        self.Z1 = 0.0
        self.Z2 = 0.0
        self.F = 0.0
        self.F1 = 0.0
        self.F2 = 0.0

        self.index = ['上车动力系统', '发动机', '散热器', '空滤器', '消声器', '启动马达', '电油门',
                      '分动箱']
        self.out = pd.DataFrame(index=self.index,
                                columns=Const.table_columns)

    def intermediate_compute(self,
                             days: int,
                             sShangCheINTER: ShangCheINTER,
                             zZQiShengINTER: ZQiShengINTER,
                             bBianFuINTER: BianFuINTER,
                             sShenSuoINTER: ShenSuoINTER
                             ):
        # 获取参数
        self.D0 = sShangCheINTER.D0
        self.D1 = sShangCheINTER.D1
        self.D2 = sShangCheINTER.D2
        self.D3 = sShangCheINTER.D3
        self.D4 = sShangCheINTER.D4
        self.D5 = sShangCheINTER.D5
        self.D6 = sShangCheINTER.D6
        self.qsb_zj_max = sShangCheINTER.qsb_zj_max

        self.Z1 = sShangCheINTER.Z1
        self.Z2 = sShangCheINTER.Z2

        self.F = zZQiShengINTER.F

        self.F1 = bBianFuINTER.F1
        self.F2 = sShenSuoINTER.F2

        # 载荷次数时间存疑（空缺）

    # 载荷谱输出
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
        # 相同部分
        self.out['车辆型号'] = vehicle_id
        self.out['年工作月数'] = self.D0
        self.out['年工作天数'] = self.D1
        self.out['天工作小时数'] = self.D2
        self.out['年工作小时数'] = self.D4
        self.out['工作年限'] = self.D6
        self.out['总工作时间'] = self.D4 * self.D6
        self.out['天循环次数'] = np.nan
        self.out['年循环次数'] = np.nan
        self.out['总循环次数'] = np.nan
        # 不同部分
        # 天循环次数(电油门)
        self.out['天循环次数']['电油门'] = 1.2 * self.F + self.F1 + self.F2
        self.out['年循环次数']['电油门'] = self.D4 * (1.2 * self.F + self.F1 + self.F2)
        self.out['总循环次数']['电油门'] = self.D6 * self.D4 * (1.2 * self.F + self.F1 + self.F2)


if __name__ == '__main__':
    ShangCheDongLi = ShangCheDongLi()
    print(ShangCheDongLi.out)
