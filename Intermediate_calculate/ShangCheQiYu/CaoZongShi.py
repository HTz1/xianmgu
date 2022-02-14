from Intermediate_calculate.ShangCheINTER import ShangCheINTER
from Intermediate_calculate.ZQiShengINTER import ZQiShengINTER
from Intermediate_calculate.BianFuINTER import BianFuINTER
from Intermediate_calculate.ShenSuoINTER import ShenSuoINTER

import pandas as pd
import numpy as np
from utils.const import Const
from MechanicalFormulas import MechanicalFormulas


class CaoZongShi:

    def __init__(self):
        # ---------------------------- 通过数据库一次性统计出的结果 --------------------------------- #

        # ---------------------------- 根据中间变量进一步计算得出的结果 ------------------------------ #
        self.D0 = 0.0
        self.D1 = 0.0
        self.D2 = 0.0
        self.D3 = 0.0
        self.D4 = 0.0
        self.D5 = 0.0
        self.D6 = 0.0
        self.Z2 = 0.0

        self.A2 = 0.0
        self.B2 = 0.0
        self.C2 = 0.0
        self.F2 = 0.0
        self.I2 = 0.0

        self.G2 = 0.0
        self.G6 = 0.0
        self.G7 = 0.0

        self.index = ['操纵室及外观', '雨刮电机', '门锁', '玻璃伸降器', '雨刮', ]
        self.out = pd.DataFrame(index=self.index,
                                columns=Const.table_columns)

    def intermediate_compute(self,
                             days: int,
                             sShangCheINTER: ShangCheINTER,
                             sShenSuoINTER: ShenSuoINTER,
                             ):
        # 获取参数
        self.D0 = sShangCheINTER.D0
        self.D1 = sShangCheINTER.D1
        self.D2 = sShangCheINTER.D2
        self.D3 = sShangCheINTER.D3
        self.D4 = sShangCheINTER.D4
        self.D5 = sShangCheINTER.D5
        self.D6 = sShangCheINTER.D6
        self.G2 = sShangCheINTER.G2
        self.G6 = sShangCheINTER.G6
        self.G7 = sShangCheINTER.G7

        self.A2 = sShenSuoINTER.A2
        self.B2 = sShenSuoINTER.B2
        self.C2 = sShenSuoINTER.C2
        self.F2 = sShenSuoINTER.F2
        self.I2 = sShenSuoINTER.I2

        # 载荷次数时间存疑（空缺）

    # 载荷谱输出
    def output_loadspectrum(self, vehicle_id='XCT25L5'):
        # 相同部分
        self.out['车辆型号'] = vehicle_id
        for component in ["载荷谱系数", "使用等级", "载荷状态", "工作级别", "5%以内载荷次数",
                          "5-50%载荷次数", "50-95%载荷次数", "95%以上载荷次数", "5%以内载荷时间",
                          "5-50%载荷时间", "50-95%载荷时间", "95%以上载荷时间"]:
            self.out[component] = np.nan

        # 不同部分
        # 年工作月数
        for component in ['操纵室及外观', '雨刮电机', '雨刮']:
            self.out['年工作月数'][component] = self.D0
        for component in ['门锁', '玻璃伸降器']:
            self.out['年工作月数'][component] = self.A2

        # 年工作天数
        for component in ['操纵室及外观', '雨刮电机', '雨刮']:
            self.out['年工作天数'][component] = self.D1
        for component in ['门锁', '玻璃伸降器']:
            self.out['年工作天数'][component] = self.B2

        # 天工作小时数
        for component in ['门锁', '玻璃伸降器']:
            self.out['天工作小时数'][component] = self.C2
        for component in ['雨刮电机', '雨刮']:
            self.out['天工作小时数'][component] = self.G2
        self.out['天工作小时数']['操纵室及外观'] = self.D2

        # 天循环次数
        for component in ['雨刮电机', '雨刮']:
            self.out['天循环次数'][component] = np.nan
        self.out['天循环次数']['操纵室及外观'] = self.D3
        self.out['天循环次数']['门锁'] = 5 * self.F2
        self.out['天循环次数']['玻璃伸降器'] = 2 * self.F2

        # 年工作小时数
        for component in ['门锁', '玻璃伸降器']:
            self.out['年工作小时数'][component] = self.B2 * self.C2
        self.out['年工作小时数']['操纵室及外观'] = self.D4
        self.out['年工作小时数']['雨刮电机'] = self.G6
        self.out['年工作小时数']['雨刮'] = self.G7

        # 年循环次数
        for component in ['雨刮电机', '雨刮']:
            self.out['年循环次数'][component] = np.nan
        self.out['年循环次数']['操纵室及外观'] = self.D5
        self.out['年循环次数']['门锁'] = 5 * self.F2 * self.B2
        self.out['年循环次数']['玻璃伸降器'] = 2 * self.F2 * self.B2

        # 工作年限
        for component in ['操纵室及外观', '雨刮电机', '雨刮']:
            self.out['工作年限'][component] = self.D6
        for component in ['门锁', '玻璃伸降器']:
            self.out['工作年限'][component] = self.I2

        # 总工作时间
        for component in ['门锁', '玻璃伸降器']:
            self.out['总工作时间'][component] = self.B2 * self.C2 * self.I2
        self.out['总工作时间']['操纵室及外观'] = self.D4 * self.D6
        self.out['总工作时间']['雨刮电机'] = self.G6 * self.D6
        self.out['总工作时间']['雨刮'] = self.G7 * self.D6

        # 总循环次数
        for component in ['雨刮电机', '雨刮']:
            self.out['总循环次数'][component] = np.nan
        self.out['总循环次数']['操纵室及外观'] = self.D6 * self.Z2
        self.out['总循环次数']['门锁'] = 5 * self.F2 * self.B2 * self.I2
        self.out['总循环次数']['玻璃伸降器'] = 2 * self.F2 * self.B2 * self.I2


if __name__ == '__main__':
    CaoZongShi = CaoZongShi()
    print(CaoZongShi.out)
