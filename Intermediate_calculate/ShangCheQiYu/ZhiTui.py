from Intermediate_calculate.ShangCheINTER import ShangCheINTER
from Intermediate_calculate.ZQiShengINTER import ZQiShengINTER
from Intermediate_calculate.BianFuINTER import BianFuINTER
from Intermediate_calculate.ShenSuoINTER import ShenSuoINTER

import pandas as pd
import numpy as np
from utils.const import Const
from MechanicalFormulas import MechanicalFormulas


class ZhiTui:

    def __init__(self):
        # ---------------------------- 通过数据库一次性统计出的结果 --------------------------------- #
        self.zt_fl_max = 0.0  # 支腿反力（F1&F2）

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

        self.C = 0.0
        self.F = 0.0
        self.F1 = 0.0
        self.F2 = 0.0
        self.C2 = 0.0

        self.index = ['垂直油缸', '水平油缸', '双向液压阀', '测长传感器', '压力传感器']
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

        self.Z1 = sShangCheINTER.Z1
        self.Z2 = sShangCheINTER.Z2

        self.C = zZQiShengINTER.C
        self.F = zZQiShengINTER.F

        self.F2 = sShenSuoINTER.F2

        self.C2 = sShenSuoINTER.C2

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
        self.out['工作年限'] = self.D6
        self.out['总工作时间'] = self.D1 * self.D6 * self.C

        # 不同部分
        # 天工作小时数
        for component in ['支腿系统', '垂直油缸', '双向液压阀', '压力传感器']:
            self.out['天工作小时数'][component] = self.C
        for component in ['水平油缸', '测长传感器']:
            self.out['天工作小时数'][component] = self.C2

        # 天循环次数
        for component in ['支腿系统', '垂直油缸', '压力传感器']:
            self.out['天循环次数'][component] = self.F
        for component in ['水平油缸', '双向液压阀', '测长传感器']:
            self.out['天循环次数'][component] = self.Z1

        # 年工作小时数
        for component in ['支腿系统', '垂直油缸', '双向液压阀', '压力传感器']:
            self.out['年工作小时数'][component] = self.C * self.D1
        for component in ['水平油缸', '测长传感器']:
            self.out['年工作小时数'][component] = self.C2 * self.D1

        # 年循环次数
        for component in ['支腿系统', '垂直油缸', '压力传感器']:
            self.out['年循环次数'][component] = self.F * self.D1
        for component in ['水平油缸', '双向液压阀', '测长传感器']:
            self.out['年循环次数'][component] = self.Z2

        # 总工作时间
        for component in ['支腿系统', '垂直油缸', '双向液压阀', '压力传感器']:
            self.out['总工作时间'][component] = self.C * self.D1 * self.D6
        for component in ['水平油缸', '测长传感器']:
            self.out['总工作时间'][component] = self.C2 * self.D1 * self.D6

        # 总循环次数
        for component in ['支腿系统', '垂直油缸', '压力传感器']:
            self.out['总循环次数'][component] = self.F * self.D1 * self.D6
        for component in ['水平油缸', '双向液压阀', '测长传感器']:
            self.out['总循环次数'][component] = self.Z2 * self.D6

        # 其余（支腿反力未讨论）
        for component2 in ["载荷谱系数", "使用等级", "载荷状态", "工作级别", "5%以内载荷次数",
                           "5-50%载荷次数", "50-95%载荷次数", "95%以上载荷次数", "5%以内载荷时间",
                           "5-50%载荷时间", "50-95%载荷时间", "95%以上载荷时间"]:
            for component1 in ['支腿系统', '水平油缸', '双向液压阀', '测长传感']:
                self.out[component1][component2] = np.nan


if __name__ == '__main__':
    ZhiTui = ZhiTui()
    print(ZhiTui.out)
