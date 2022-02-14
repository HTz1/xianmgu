from Intermediate_calculate.DiPanParamINTER import DiPanParamINTER
from Intermediate_calculate.ZQiShengINTER import ZQiShengINTER
from Intermediate_calculate.BianFuINTER import BianFuINTER
from Intermediate_calculate.ShenSuoINTER import ShenSuoINTER
import pandas as pd
import numpy as np
from utils.const import Const
from MechanicalFormulas import MechanicalFormulas


class DongLiINTER:

    def __init__(self):
        # ---------------------------- 通过数据库一次性统计出的结果 --------------------------------- #

        # ---------------------------- 根据中间变量进一步计算得出的结果 ------------------------------ #
        self.X1 = 0.0
        self.X2 = 0.0
        self.X3 = 0.0
        self.X4 = 0.0
        self.X6 = 0.0
        self.N = 0.0
        self.G_0 = 0.0
        self.G_3 = 0.0
        self.G_4 = 0.0

        self.index = ['动力系统', '发动机', '散热器', '空滤器', '消声器', '启动马达']
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
        self.G_0 = dDiPanParamINTER.G_0
        self.G_3 = dDiPanParamINTER.G_3
        self.G_4 = dDiPanParamINTER.G_4
        self.N = dDiPanParamINTER.N

    # 载荷谱输出
    def output_loadspectrum(self, vehicle_id='XCT25L5'):
        # 相同部分
        self.out['车辆型号'] = vehicle_id
        self.out['年行驶月数'] = self.X1
        self.out['年行驶天数'] = self.X2
        self.out['天行驶小时数'] = self.X3 + self.X4  # 散热器不同
        self.out['天行驶里程KM'] = self.X6
        self.out['年工作小时数'] = self.X2 * (self.X3 + self.X4)  # 散热器不同
        self.out['年行驶里程KM'] = self.X2 * self.X6
        self.out['总工作时间'] = self.N * self.X2 * (self.X3 + self.X4)  # 散热器不同
        self.out['总行驶里程'] = self.N * self.X2 * self.X6
        self.out['工作年限'] = self.N
        # 不同部分
        self.out['天行驶小时数']['散热器'] = self.G_3
        self.out['年工作小时数']['散热器'] = self.X2 * (self.G_3 + self.X4)
        self.out['总工作时间']['散热器'] = self.N * self.X2 * (self.G_3 + self.X4)
        for component in ['散热器', '空滤器', '消声器', '启动马达']:
            self.out['载荷谱系数'][component] = np.nan
            self.out['20%扭矩时间'][component] = np.nan
            self.out['20-50%扭矩时间'][component] = np.nan
            self.out['50-80%扭矩时间'][component] = np.nan
            self.out['80%以上扭矩时间'][component] = np.nan

    #里程数查询未知


if __name__ == '__main__':
    DongLiINTER = DongLiINTER()
    print(DongLiINTER.out)
