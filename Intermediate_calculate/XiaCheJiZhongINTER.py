from Intermediate_calculate.DiPanParamINTER import DiPanParamINTER
from Intermediate_calculate.ZQiShengINTER import ZQiShengINTER
from Intermediate_calculate.BianFuINTER import BianFuINTER
from Intermediate_calculate.ShenSuoINTER import ShenSuoINTER
import pandas as pd
import numpy as np
from utils.const import Const
from MechanicalFormulas import MechanicalFormulas


class XiaCheJiZhongINTER:

    def __init__(self):
        # ---------------------------- 通过数据库一次性统计出的结果 --------------------------------- #

        # ---------------------------- 根据中间变量进一步计算得出的结果 ------------------------------ #
        self.X1 = 0.0
        self.X2 = 0.0
        self.X3 = 0.0
        self.X4 = 0.0
        self.X6 = 0.0
        self.N = 0.0

        self.index = ['下车集中润滑', '分流阀', '润滑泵', ]
        self.out = pd.DataFrame(index=self.index,
                                columns=Const.table_columns_dipan)

    def intermediate_compute(self,
                             days: int,
                             dDiPanParamINTER: DiPanParamINTER
                             ):
        # 获取参数
        self.X1 = dDiPanParamINTER.X1
        self.X2 = dDiPanParamINTER.X2
        self.X3 = dDiPanParamINTER.X3
        self.X4 = dDiPanParamINTER.X4
        self.X6 = dDiPanParamINTER.X6
        self.N = dDiPanParamINTER.N

    # 载荷谱输出
    def output_loadspectrum(self, vehicle_id='XCT25L5'):
        # 相同部分
        self.out['车辆型号'] = vehicle_id
        self.out['年行驶月数'] = self.X1
        self.out['年行驶天数'] = self.X2
        self.out['天行驶小时数'] = 0.08 * self.X3
        self.out['天行驶里程KM'] = 1.7 * self.X6
        self.out['年工作小时数'] = 0.08 * self.X3 * self.X2
        self.out['年行驶里程KM'] = 1.7 * self.X6 * self.X2
        self.out['工作年限'] = self.N
        self.out['总工作时间'] = 0.08 * self.X3 * self.X2 * self.N
        self.out['总行驶里程'] = 1.7 * self.X6 * self.X2 * self.N

        self.out['载荷谱系数'] = np.nan
        self.out['20%扭矩时间'] = np.nan
        self.out['20-50%扭矩时间'] = np.nan
        self.out['50-80%扭矩时间'] = np.nan
        self.out['80%以上扭矩时间'] = np.nan

        # 不同部分

    # 里程数查询未知


if __name__ == '__main__':
    xiaCheJiZhongINTER = XiaCheJiZhongINTER()
    print(xiaCheJiZhongINTER.out)
