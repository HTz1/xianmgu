from Intermediate_calculate.ShangCheINTER import ShangCheINTER

import pandas as pd
import numpy as np
from utils.const import Const
from MechanicalFormulas import MechanicalFormulas


class ShangCheGongGong:

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
        self.Z2 = 0.0
        self.G0= 0.0
        self.G5= 0.0

        self.index = ['上车公共系统', '力限器', '显示器', '水平仪', 'GPS模块',
                      '中心回转体']
        self.out = pd.DataFrame(index=self.index,
                                columns=Const.table_columns)

    def intermediate_compute(self,
                             days: int,
                             sShangcheINTER: ShangCheINTER,
                             ):
        # 获取参数
        self.D0 = sShangcheINTER.D0
        self.D1 = sShangcheINTER.D1
        self.D2 = sShangcheINTER.D2
        self.D3 = sShangcheINTER.D3
        self.D4 = sShangcheINTER.D4
        self.D5 = sShangcheINTER.D5
        self.D6 = sShangcheINTER.D6
        self.qsb_zj_max = sShangcheINTER.qsb_zj_max
        self.G0=sShangcheINTER.G0
        self.G5=sShangcheINTER.G5

        self.Z2 = sShangcheINTER.Z2

        # 载荷次数时间存疑（空缺）

    # 载荷谱输出
    def output_loadspectrum(self, vehicle_id='XCT25L5'):

        # 相同部分
        self.out['车辆型号'] = vehicle_id
        self.out['年工作月数'] = self.D0
        self.out['年工作天数'] = self.D1
        self.out['工作年限'] = self.D6
        self.out['天循环次数'] = np.nan
        self.out['年循环次数'] = np.nan
        self.out['总循环次数'] = np.nan

        # 不同部分
        # 天工作小时数
        for component in ['上车公共系统', 'GPS模块', '中心回转体']:
            self.out['天工作小时数'][component] = self.D2
        self.out['天工作小时数']['力限器'] = 1.2 * self.D2
        for component in ['显示器', '水平仪']:
            self.out['天工作小时数'][component] = self.G0

        #天循环次数
        self.out['天循环次数']['上车公共系统'] = self.D3
        self.out['天循环次数']['中心回转体'] = 1.1*self.D3

        #年工作小时数
        for component in ['上车公共系统', 'GPS模块', '中心回转体']:
            self.out['天工作小时数'][component] = self.D4
        self.out['年工作小时数']['力限器'] = 1.2*self.D4
        self.out['年工作小时数']['显示器'] = self.G5
        self.out['年工作小时数']['水平仪'] = self.G5

        #年循环次数
        self.out['年循环次数']['上车公共系统'] = self.D5
        self.out['年循环次数']['中心回转体'] = 1.1*self.D5

        #总工作时间
        for component in ['上车公共系统', 'GPS模块', '中心回转体']:
            self.out['天工作小时数'][component] = self.D4*self.D6
        self.out['总工作时间']['力限器'] = 1.2*self.D4*self.D6
        self.out['总工作时间']['显示器'] = self.G5*self.D6
        self.out['总工作时间']['水平仪'] = self.G5*self.D6

        #总循环次数
        self.out['总循环次数']['上车公共系统'] = self.Z2*self.D6
        self.out['总循环次数']['中心回转体'] = 1.1*self.D4*self.D6




if __name__ == '__main__':
    ShangCheGongGong = ShangCheGongGong()
    print(ShangCheGongGong.out)
