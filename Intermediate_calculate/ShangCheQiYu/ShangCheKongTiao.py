from Intermediate_calculate.ShangCheINTER import ShangCheINTER
from Intermediate_calculate.ZQiShengINTER import ZQiShengINTER
from Intermediate_calculate.BianFuINTER import BianFuINTER
from Intermediate_calculate.ShenSuoINTER import ShenSuoINTER

import pandas as pd
import numpy as np
from utils.const import Const
from MechanicalFormulas import MechanicalFormulas


class ShangCheKongTiao:

    def __init__(self):
        # ---------------------------- 通过数据库一次性统计出的结果 --------------------------------- #

        # ---------------------------- 根据中间变量进一步计算得出的结果 ------------------------------ #
        self.D0 = 0.0
        self.D1 = 0.0
        self.D2 = 0.0
        self.D6 = 0.0

        self.G3 = 0.0
        self.G4 = 0.0
        self.G8 = 0.0
        self.G9 = 0.0

        self.index = ['上车空调及散热', '散热器', '空调']
        self.out = pd.DataFrame(index=self.index,
                                columns=Const.table_columns)

    def intermediate_compute(self,
                             days: int,
                             sShangCheINTER: ShangCheINTER
                             ):
        # 获取参数
        self.D0 = sShangCheINTER.D0
        self.D1 = sShangCheINTER.D1
        self.D2 = sShangCheINTER.D2
        self.D6 = sShangCheINTER.D6
        self.G3 = sShangCheINTER.G3
        self.G4 = sShangCheINTER.G4
        self.G8 = sShangCheINTER.G8
        self.G9 = sShangCheINTER.G9

        # 载荷次数时间存疑（空缺）

    # 载荷谱输出
    def output_loadspectrum(self, vehicle_id='XCT25L5'):
        # 相同部分
        self.out['车辆型号'] = vehicle_id
        self.out['年工作月数'] = self.D0
        self.out['年工作天数'] = self.D1
        self.out['工作年限'] = self.D6
        for component in ['总循环次数', "载荷谱系数", "使用等级", "载荷状态", "工作级别", "5%以内载荷次数",
                          "5-50%载荷次数", "50-95%载荷次数", "95%以上载荷次数", "5%以内载荷时间",
                          "5-50%载荷时间", "50-95%载荷时间", "95%以上载荷时间"]:
            self.out[component] = np.nan

        # 不同部分
        # 天工作小时数
        for component in ['上车空调及散热', '散热器']:
            self.out['天工作小时数'][component] = self.G3
        self.out['天工作小时数']['空调'] = self.G4

        # 天循环次数
        self.out['天循环次数']['空调'] = np.nan

        # 年工作小时数
        for component in ['上车空调及散热', '散热器']:
            self.out['年工作小时数'][component] = self.G8
        self.out['年工作小时数']['空调'] = self.G9

        # 年循环次数
        self.out['年循环次数']['空调'] = np.nan

        # 总工作时间
        for component in ['上车空调及散热', '散热器']:
            self.out['总工作时间'][component] = self.G8 * self.D6
        self.out['总工作时间']['空调'] = self.G8 * self.D6


if __name__ == '__main__':
    ShangCheKongTiao = ShangCheKongTiao()
    print(ShangCheKongTiao.out)
