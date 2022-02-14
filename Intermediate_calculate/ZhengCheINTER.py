from data_loader.OracleManager import OracleManager
from data_structure.ZHP import ZHP
from Intermediate_calculate.ZhengJiINTER import QiShengINTER
from Intermediate_calculate.ZQiShengINTER import ZQiShengINTER
from Intermediate_calculate.FQiShengINTER import FQiShengINTER
from data_structure.JiGouZHP import JiGouZHP
import pandas as pd
import numpy as np
from utils.const import Const
from MechanicalFormulas import MechanicalFormulas
from data_structure.CalculatingParam import CalculatingParam

class ZhengCheINTER:

    def __init__(self):
        # 通过数据库导出的结果
        self.F1_max = 0.0  # （前）拉板拉力最大值F1
        self.hzzc_zj_max = 0.0  # 支承力矩比最大值
        self.zhtsjd_heli_max = 0.0  # 后铰点总支力(合力)
        self.ZT_FL_max = 0.0  # 支反力最大值（f1&f2）
        self.qzl_q_max = 0.0  # 载荷率最大值

        # 塔臂长度
        Ef_bjlongth=0.0
        # 起升总工作循环次数
        self.Ct = 0.0
        self.fCt = 0.0
        self.tCt = 0.0
        # 主起升部分
        self.days = 0
        self.A = 0.0
        self.B = 0.0
        self.C = 0.0
        self.D = 0.0
        self.E = 0.0
        self.F = 0.0
        self.G = 0.0
        self.H = 0.0
        self.I = 0.0
        self.K = 0.0
        # 副主起升部分
        self.fA = 0.0
        self.fB = 0.0
        self.fC = 0.0
        self.fD = 0.0
        self.fE = 0.0
        self.fF = 0.0
        self.fG = 0.0
        self.fH = 0.0
        # 塔起升部分
        self.tA = 0.0
        self.tB = 0.0
        self.tC = 0.0
        self.tD = 0.0
        self.tE = 0.0
        self.tF = 0.0
        self.tG = 0.0
        self.tH = 0.0

        # 输出载荷谱
        self.index = ['整体结构', '主起重臂', '固定副臂', '变幅副臂', '超起装置', '转台', '车架', '支腿']
        self.out = pd.DataFrame(index=self.index
                                , columns=Const.table_columns)

    def intermediate_count(self
                           , oracleManager: OracleManager
                           , VMI_NAME: str = 'XCT25L5'
                           , ):
        # ---------------------------- step 1: Oracle 连接初始化 ---------------------------- #
        if oracleManager.isConnect is False:
            oracleManager.connect()

        # ---------------------------- step 2: 从数据库中查询最大值 ---------------------------- #
        curs = oracleManager.db.cursor()
        # 暂定表名为 INTERMEDIATE_XCT25_JIGOU
        system_name = 'JIGOU'
        table_name = '_'.join(['INTER', VMI_NAME, system_name])
        curs.execute('SELECT MAX(F1_) FROM ' + table_name)
        self.F1_max = curs.fetchone()[0]
        curs.execute('SELECT MAX(hzzc_zj) FROM ' + table_name)
        self.hzzc_zj_max = curs.fetchone()[0]
        curs.execute('SELECT MAX() FROM ' + table_name)
        self._max = curs.fetchone()[0]  # 合力不确定如何查询???????????????????
        curs.execute('SELECT MAX(qzl_q_max) FROM ' + table_name)
        self.qzl_q_max = curs.fetchone()[0]

        # 工作年限确定（超起工况占比K暂定）
        max_weight = MechanicalFormulas.compute_weight(VMI_NAME)
        if max_weight < 80:
            self.I = 10
            self.K = 0.0
        elif max_weight < 200:
            self.I = 12
            self.K = 0.0
        elif max_weight < 300:
            self.I = 15
            self.K = 0.0
        elif max_weight < 500:
            self.I = 15
            self.K = 0.4
        elif max_weight < 650:  # (500~650)未给出K的范围???????????????
            self.I = 20
            self.K = 0.6
        else:
            self.I = 20
            self.K = 0.8

    def intermediate_compute(self,
                             days: int,
                             ZhengJiINTER: QiShengINTER,
                             zZQiShengINTER: ZQiShengINTER,
                             fFQiShengINTER: FQiShengINTER,
                             jJiGouZHP: JiGouZHP,
                             pZhp: ZHP
                             ):

        # 主起升起时间 (小时 / 天)
        self.D += zZQiShengINTER.D
        # 主起升落时间 (小时 / 天)
        self.E += zZQiShengINTER.E
        # 主起升循环次数 (次 / 天)
        self.F += zZQiShengINTER.F
        # 主起升起冲击次数 (次 / 天)
        self.G += zZQiShengINTER.G
        # 主起升落冲击次数 (次 / 天)
        self.H += zZQiShengINTER.H
        # 主起升工作时间 (小时 / 天)
        self.C += zZQiShengINTER.C
        # 主起升工作天数 (天 / 年)
        self.B += zZQiShengINTER.B
        # 主起升工作月数 (月 / 年)
        self.A += zZQiShengINTER.A

        # 副起升起时间 (小时 / 天)
        self.fD += fFQiShengINTER.D_
        # 副起升落时间 (小时 / 天)
        self.fE += fFQiShengINTER.E_
        # 副起升循环次数 (次 / 天)
        self.fF += fFQiShengINTER.F_
        # 副起升起冲击次数 (次 / 天)
        self.fG += fFQiShengINTER.G_
        # 副起升落冲击次数 (次 / 天)
        self.fH += fFQiShengINTER.H_
        # 副起升工作时间 (小时 / 天)
        self.fC += fFQiShengINTER.C_
        # 副起升工作天数 (天 / 年)
        self.fB += fFQiShengINTER.B_
        # 副起升工作月数 (月 / 年)
        self.fA += fFQiShengINTER.A_

        # 塔卷起升起时间 (小时 / 天)
        self.tD += sum(pZhp.QiShengZHP.tqs_time) / days * 1.3
        # 塔卷起升落时间 (小时 / 天)
        self.tE += sum(pZhp.QiShengZHP.tql_time) / days * 1.3
        # 塔卷起升循环次数 (次 / 天)
        self.tF += sum(pZhp.QiShengZHP.tqs_cs) / days * 1.3
        # 塔卷起升起冲击次数 (次 / 天)
        self.tG += sum(pZhp.QiShengZHP.tqs_qcs) / days * 1.3
        # 塔卷起升落冲击次数 (次 / 天)
        self.tH += sum(pZhp.QiShengZHP.tqs_lcs) / days * 1.3
        # 塔卷起升工作时间 (小时 / 天)
        self.tC += self.tD + self.tE
        # 塔卷起升工作天数 (天 / 年)
        self.tB += (sum(pZhp.QiShengZHP.tqs_time) / 24) / (days / 365)
        # 塔卷起升工作月数 (月 / 年)
        self.tA += self.tB / 30 / 2 + 6

        # 载荷谱系数确定 => 问张工
        # 起升总循环次数
        self.Ct = zZQiShengINTER.Ct
        self.tCt += sum(pZhp.QiShengZHP.tqs_cs)

        # 工况参数未知无法区分？？？？？？？？？？？？？？？？
        # 载荷次数/时间计算
        # 默认所有载荷次数和时间的初始值为0
        for index in self.index:
            if "%" in index: self.out[index] = 0.00
        for row in Const.MAX_ROWS:
            # 固定副臂，变幅副臂（载荷次数时间存疑)？？？？？？？？？？？？？？？？？？？？？？？？
            for component in ['固定副臂', '变幅副臂']:
                if pZhp.QiShengZHP.qzl_q[row] < 0.05 * self.qzl_q_max:
                    self.out['5%以内载荷次数'][component] += pZhp.QiShengZHP.fqs_cs[row]
                    self.out['5%以内载荷时间'][component] += pZhp.QiShengZHP.fqs_time[row] + pZhp.QiShengZHP.fql_time[row]
                elif 0.05 * self.qzl_q_max <= pZhp.QiShengZHP.qzl_q[row] < 0.5 * self.qzl_q_max:
                    self.out['5-50%载荷次数'][component] += pZhp.QiShengZHP.fqs_cs[row]
                    self.out['5-50%载荷时间'][component] += pZhp.QiShengZHP.fqs_time[row] + pZhp.QiShengZHP.fql_time[row]
                elif 0.5 * self.qzl_q_max <= pZhp.QiShengZHP.qzl_q[row] < 0.95 * self.qzl_q_max:
                    self.out['50-90%载荷次数'][component] += pZhp.QiShengZHP.fqs_cs[row]
                    self.out['50-95%载荷时间'][component] += pZhp.QiShengZHP.fqs_time[row] + pZhp.QiShengZHP.fql_time[row]
                else:
                    self.out['95%以上载荷次数'][component] += pZhp.QiShengZHP.fqs_cs[row]
                    self.out['95%以上载荷时间'][component] += pZhp.QiShengZHP.fqs_time[row] + pZhp.QiShengZHP.fql_time[row]
            # 主起重臂
            if pZhp.QiShengZHP.qzl_q[row] < 0.05 * self.qzl_q_max:
                self.out['5%以内载荷次数']['主起重臂'] += pZhp.QiShengZHP.fqs_cs[row]
                self.out['5%以内载荷时间']['主起重臂'] += pZhp.QiShengZHP.fqs_time[row] + pZhp.QiShengZHP.fql_time[row]
            elif 0.05 * self.qzl_q_max <= pZhp.QiShengZHP.qzl_q[row] < 0.5 * self.qzl_q_max:
                self.out['5-50%载荷次数']['主起重臂'] += pZhp.QiShengZHP.fqs_cs[row]
                self.out['5-50%载荷时间']['主起重臂'] += pZhp.QiShengZHP.fqs_time[row] + pZhp.QiShengZHP.fql_time[row]
            elif 0.5 * self.qzl_q_max <= pZhp.QiShengZHP.qzl_q[row] < 0.95 * self.qzl_q_max:
                self.out['50-90%载荷次数']['主起重臂'] += pZhp.QiShengZHP.fqs_cs[row]
                self.out['50-95%载荷时间']['主起重臂'] += pZhp.QiShengZHP.fqs_time[row] + pZhp.QiShengZHP.fql_time[row]
            else:
                self.out['95%以上载荷次数']['主起重臂'] += pZhp.QiShengZHP.fqs_cs[row]
                self.out['95%以上载荷时间']['主起重臂'] += pZhp.QiShengZHP.fqs_time[row] + pZhp.QiShengZHP.fql_time[row]
            # 超前装置参数未知？？？？？？？？？？？？？？？？？？

            # 整体结构
            self.out['年工作月数']['整体结构'] = ZhengJiINTER.D0
            self.out['年工作天数']['整体结构'] = ZhengJiINTER.D1
            self.out['天工作小时数']['整体结构'] = ZhengJiINTER.D2
            self.out['天循环次数']['整体结构'] = ZhengJiINTER.D3
            self.out['年工作小时数']['整体结构'] = ZhengJiINTER.D4
            self.out['年循环次数']['整体结构'] = ZhengJiINTER.D5
            self.out['工作年限']['整体结构'] = ZhengJiINTER.D6
            self.out['总工作时间']['整体结构'] = ZhengJiINTER.D7
            self.out['总循环次数']['整体结构'] = ZhengJiINTER.D8

            self.out['5%以内载荷次数']['整体结构'] = ZhengJiINTER.D13
            self.out['5-50%载荷次数']['整体结构'] = ZhengJiINTER.D14
            self.out['50-95%载荷次数']['整体结构'] = ZhengJiINTER.D15
            self.out['95%以上载荷次数']['整体结构'] = ZhengJiINTER.D16
            self.out['5%以内载荷时间']['整体结构'] = ZhengJiINTER.D17
            self.out['5-50%载荷时间']['整体结构'] = ZhengJiINTER.D14
            self.out['50-95%载荷时间']['整体结构'] = ZhengJiINTER.D15
            self.out['95%以上载荷时间']['整体结构'] = ZhengJiINTER.D16
            # 变幅副臂拉板?????????????????????(载荷次数时间存疑)
            if jJiGouZHP.F1_[row] < 0.05 * self.F1_max:
                self.out['5%以内载荷次数']['变幅副臂拉板'] += pZhp.QiShengZHP.fqs_cs[row]
                self.out['5%以内载荷时间']['变幅副臂拉板'] += pZhp.QiShengZHP.fqs_time[row] + pZhp.QiShengZHP.fql_time[row]
            elif 0.05 * self.F1_max <= jJiGouZHP.F1_[row] < 0.5 * self.F1_max:
                self.out['5-50%载荷次数']['变幅副臂拉板'] += pZhp.QiShengZHP.fqs_cs[row]
                self.out['5-50%载荷时间']['变幅副臂拉板'] += pZhp.QiShengZHP.fqs_time[row] + pZhp.QiShengZHP.fql_time[row]
            elif 0.5 * self.F1_max <= jJiGouZHP.F1_[row] < 0.95 * self.F1_max:
                self.out['50-90%载荷次数']['变幅副臂拉板'] += pZhp.QiShengZHP.fqs_cs[row]
                self.out['50-95%载荷时间']['变幅副臂拉板'] += pZhp.QiShengZHP.fqs_time[row] + pZhp.QiShengZHP.fql_time[row]
            else:
                self.out['95%以上载荷次数']['变幅副臂拉板'] += pZhp.QiShengZHP.fqs_cs[row]
                self.out['95%以上载荷时间']['变幅副臂拉板'] += pZhp.QiShengZHP.fqs_time[row] + pZhp.QiShengZHP.fql_time[row]
            ##转台条件参数未知？？？？？？？？？？？？

            ##转台、车架、支腿载荷次数未知???????????????????????????

            for component in ['转台', '车架', '支腿']:
                self.out['5%以内载荷时间'][component] = ZhengJiINTER.D17
                self.out['5-50%载荷时间'][component] = ZhengJiINTER.D14
                self.out['50-95%载荷时间'][component] = ZhengJiINTER.D15
                self.out['95%以上载荷时间'][component] = ZhengJiINTER.D16

            # 年工作月数
            for component in ['转台', '车架', '支腿']:
                self.out['年工作月数'][component] = ZhengJiINTER.D0

    # 总工作循环次数唯一？？？？？
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
        self.out['工作年限'] = self.I

        # 不同部分
        # 年工作月数
        self.out['年工作月数']['主起重臂'] = self.A
        self.out['年工作月数']['固定副臂'] = self.fA
        for component in ['变幅副臂', '变幅副臂拉板']:
            self.out['年工作月数'][component] = self.tA
        self.out['年工作月数']['超起装置'] = self.K * (self.A + self.fA + self.tA)

        # 年工作天数
        self.out['年工作天数']['主起重臂'] = self.B
        self.out['年工作天数']['固定副臂'] = self.fB
        for component in ['变幅副臂', '变幅副臂拉板']:
            self.out['年工作天数'][component] = self.tB
        self.out['年工作天数']['超起装置'] = self.K * (self.B + self.tB)
        for component in ['转台', '车架', '支腿']:
            self.out['年工作天数'][component] = self.B + self.fB

        # 天工作小时数
        self.out['天工作小时数']['主起重臂'] = self.C
        self.out['天工作小时数']['固定副臂'] = self.fC
        for component in ['变幅副臂', '变幅副臂拉板']:
            self.out['天工作小时数'][component] = self.tC
        self.out['天工作小时数']['超起装置'] = self.K * (self.C + self.fC)
        for component in ['转台', '车架', '支腿']:
            self.out['天工作小时数'][component] = self.C + self.fC

        # 天循环次数
        self.out['天循环次数']['主起重臂'] = self.F
        self.out['天循环次数']['固定副臂'] = self.fF
        for component in ['变幅副臂', '变幅副臂拉板']:
            self.out['天循环次数'][component] = self.tF
        self.out['天循环次数']['超起装置'] = self.K * (self.F + self.fF + self.tF)
        for component in ['转台', '车架', '支腿']:
            self.out['天循环次数'][component] = self.F + self.fF + self.tF

        # 年工作小时数
        self.out['年工作小时数']['主起重臂'] = self.B * self.C
        self.out['年工作小时数']['固定副臂'] = self.fB * self.fC
        for component in ['变幅副臂', '变幅副臂拉板']:
            self.out['年工作小时数'][component] = self.tB * self.tC
        self.out['年工作小时数']['超起装置'] = self.K * (self.B * self.C + self.fB * self.fC)
        for component in ['转台', '车架', '支腿']:
            self.out['年工作小时数'][component] = self.B * self.C + self.fB * self.fC

        # 年循环次数
        self.out['年循环次数']['主起重臂'] = self.B * self.F
        self.out['年循环次数']['固定副臂'] = self.fB * self.fF
        for component in ['变幅副臂', '变幅副臂拉板']:
            self.out['年循环次数'][component] = self.tB * self.tF
        self.out['年循环次数']['超起装置'] = self.K * (self.B * self.F + self.fB * self.fF + self.tB * self.tF)
        for component in ['转台', '车架', '支腿']:
            self.out['年循环次数'][component] = self.B * self.F + self.fB * self.fF + self.tB * self.tF


if __name__ == '__main__':
    zhengcheINTER = ZhengCheINTER()
    print(zhengcheINTER.out)
