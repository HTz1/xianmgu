from Intermediate_calculate.ShangCheINTER import ShangCheINTER
from Intermediate_calculate.ZQiShengINTER import ZQiShengINTER
from Intermediate_calculate.BianFuINTER import BianFuINTER
from Intermediate_calculate.ShenSuoINTER import ShenSuoINTER

import pandas as pd
import numpy as np
from utils.const import Const
from MechanicalFormulas import MechanicalFormulas


class ShangCheJiZhong:

    def __init__(self):
        # ---------------------------- 通过数据库一次性统计出的结果 --------------------------------- #

        # ---------------------------- 根据中间变量进一步计算得出的结果 ------------------------------ #
        self.D0 = 0.0
        self.D1 = 0.0
        self.D2 = 0.0
        self.D4 = 0.0
        self.D6 = 0.0

        self.index = ['上车集中润滑系统', '润滑泵', '分配器']
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
        self.D4 = sShangCheINTER.D4
        self.D6 = sShangCheINTER.D6

        # 载荷次数时间存疑（空缺）

    # 载荷谱输出
    def output_loadspectrum(self, vehicle_id='XCT25L5'):
        # 相同部分
        self.out['车辆型号'] = vehicle_id
        self.out['年工作月数'] = self.D0
        self.out['年工作天数'] = self.D1
        self.out['工作年限'] = self.D6
        self.out['天工作小时数'] = 0.08 * self.D2
        self.out['年工作小时数'] = 0.08 * self.D4
        self.out['总工作时间'] = 0.08 * self.D4 * self.D6

        for component in ['天循环次数', '总循环次数', "载荷谱系数", "使用等级", "载荷状态", "工作级别", "5%以内载荷次数",
                          "5-50%载荷次数", "50-95%载荷次数", "95%以上载荷次数", "5%以内载荷时间",
                          "5-50%载荷时间", "50-95%载荷时间", "95%以上载荷时间"]:
            self.out[component] = np.nan


if __name__ == '__main__':
    ShangCheJiZhong = ShangCheJiZhong()
    print(ShangCheJiZhong.out)
