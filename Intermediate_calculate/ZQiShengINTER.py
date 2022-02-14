from data_loader.OracleManager import OracleManager
from data_structure.ZHP import ZHP
from data_structure.ZhengJiZHP import ZhengJiZHP
from data_structure.QiShengZHP import QiShengZHP
import pandas as pd
import numpy as np
from utils.const import Const
from MechanicalFormulas import MechanicalFormulas


class ZQiShengINTER:

    def __init__(self):
        # ---------------------------- 通过数据库一次性统计出的结果 --------------------------------- #
        self.jyds_ll_max = 0.0  # 单绳拉力最大值
        self.qsb_yl_max = 0.0  # (起升) 泵压力值
        self.qsmd_yl_max = 0.0  # 马达压力最大值
        self.qzl_q_max = 0.0  # 载荷率

        # ---------------------------- 根据中间变量进一步计算得出的结果 ------------------------------ #
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
        self.Ct = 0.0  # 主起升总工作循环次数

        # ----------------- 直接输出的载荷谱 (DataFrame) -------------------- #
        # 创建Dataframe用以表示最终的载荷谱表
        self.index = ['主起升机构', '主起升液压泵', '马达', '主减速机', '起升平衡阀单向阀', '起升平衡阀主阀芯', '减速机制动器',
                      '三圈保护器', '高度限位器', '钢丝绳弯曲次数', '吊钩应力循环次数', '起升联多路阀', '制动器控制阀',
                      '制动管路', '压力传感器', '转速传感器', '起升管路', '臂销', '主起升右手柄']
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
        curs.execute('SELECT MAX(jyds_ll) FROM ' + table_name)
        self.jyds_ll_max = curs.fetchone()[0]
        curs.execute('SELECT MAX(qsb_yl) FROM ' + table_name)
        self.qsb_yl_max = curs.fetchone()[0]
        curs.execute('SELECT MAX(qsmd_yl) FROM ' + table_name)
        self.qsmd_yl_max = curs.fetchone()[0]
        system_name = 'QISHENG'
        curs.execute('SELECT MAX(qzl_q_max) FROM ' + table_name)
        self.qzl_q_max = curs.fetchone()[0]

        # 工作年限确定 (分工况太麻烦，不分工况了) => 未确定，问张工
        max_weight = MechanicalFormulas.compute_weight(VMI_NAME)
        if max_weight < 80:
            self.I = 10
        elif max_weight < 200:
            self.I = 12
        elif max_weight < 500:
            self.I = 15
        else:
            self.I = 20

    def intermediate_compute(self,
                             days: int,
                             pZhp: ZHP
                             ):
        """
        该函数主要用于分 Batch 计算载荷谱的结果
        :param pZhp: 载荷谱大类
        :param days: 要计算载荷谱的总工作时间
        """
        # 主起升起时间 (小时 / 天)
        self.D += sum(pZhp.QiShengZHP.qs_time) / days * 1.3
        # 主起升落时间 (小时 / 天)
        self.E += sum(pZhp.QiShengZHP.ql_time) / days * 1.3
        # 主起升循环次数 (次 / 天)
        self.F += sum(pZhp.QiShengZHP.qs_cs) / days * 1.3
        # 主起升起冲击次数 (次 / 天)
        self.G += sum(pZhp.QiShengZHP.qs_qcs) / days * 1.3
        # 主起升落冲击次数 (次 / 天)
        self.H += sum(pZhp.QiShengZHP.qs_lcs) / days * 1.3
        # 主起升工作时间 (小时 / 天)
        self.C += self.D + self.E
        # 主起升工作天数 (天 / 年)
        self.B += (sum(pZhp.QiShengZHP.qs_time) / 24) / (days / 365)
        # 主起升工作月数 (月 / 年)
        self.A += self.B / 30 / 2 + 6

        # 载荷谱系数确定 => 问张工
        # 主起升总循环次数
        self.Ct += sum(pZhp.QiShengZHP.qs_cs)

        # 载荷次数/时间计算
        # 默认所有载荷次数和时间的初始值为0
        for index in self.index:
            if "%" in index: self.out[index] = 0.00
        for row in Const.MAX_ROWS:
            # 主起升机构, 主减速机, 钢丝绳弯曲次数
            for component in ['主起升机构', '主减速机', '钢丝绳弯曲次数']:
                if pZhp.JiGouZHP.jyds_ll[row] < 0.05 * self.jyds_ll_max:
                    self.out['5%以内载荷次数'][component] += pZhp.QiShengZHP.qs_cs[row]
                    self.out['5%以内载荷时间'][component] += pZhp.QiShengZHP.qs_time[row] + pZhp.QiShengZHP.ql_time[row]
                elif 0.05 * self.jyds_ll_max <= pZhp.JiGouZHP.jyds_ll[row] < 0.5 * self.jyds_ll_max:
                    self.out['5-50%载荷次数'][component] += pZhp.QiShengZHP.qs_cs[row]
                    self.out['5-50%载荷时间'][component] += pZhp.QiShengZHP.qs_time[row] + pZhp.QiShengZHP.ql_time[row]
                elif 0.5 * self.jyds_ll_max <= pZhp.JiGouZHP.jyds_ll[row] < 0.95 * self.jyds_ll_max:
                    self.out['50-90%载荷次数'][component] += pZhp.QiShengZHP.qs_cs[row]
                    self.out['50-95%载荷时间'][component] += pZhp.QiShengZHP.qs_time[row] + pZhp.QiShengZHP.ql_time[row]
                else:
                    self.out['95%以上载荷次数'][component] += pZhp.QiShengZHP.qs_cs[row]
                    self.out['95%以上载荷时间'][component] += pZhp.QiShengZHP.qs_time[row] + pZhp.QiShengZHP.ql_time[row]

            # 主起升液压泵, 起升平衡阀单向阀, 起升平衡阀主阀芯, 起升联多路阀, 制动管路, 压力传感器, 起升管路
            for component in ['主起升液压泵', '起升平衡阀单向阀', '起升平衡阀主阀芯', '起升联多路阀', '制动管路', '压力传感器', '起升管路']:
                if pZhp.JiGouZHP.qsb_yl[row] < 0.05 * self.qsb_yl_max:
                    self.out['5%以内载荷次数'][component] += pZhp.QiShengZHP.qs_cs[row]
                    self.out['5%以内载荷时间'][component] += pZhp.QiShengZHP.qs_time[row] + pZhp.QiShengZHP.ql_time[row]
                elif 0.05 * self.qsb_yl_max <= pZhp.JiGouZHP.qsb_yl[row] < 0.5 * self.qsb_yl_max:
                    self.out['5-50%载荷次数'][component] += pZhp.QiShengZHP.qs_cs[row]
                    self.out['5-50%载荷时间'][component] += pZhp.QiShengZHP.qs_time[row] + pZhp.QiShengZHP.ql_time[row]
                elif 0.5 * self.qsb_yl_max <= pZhp.JiGouZHP.qsb_yl[row] < 0.95 * self.qsb_yl_max:
                    self.out['50-90%载荷次数'][component] += pZhp.QiShengZHP.qs_cs[row]
                    self.out['50-95%载荷时间'][component] += pZhp.QiShengZHP.qs_time[row] + pZhp.QiShengZHP.ql_time[row]
                else:
                    self.out['95%以上载荷次数'][component] += pZhp.QiShengZHP.qs_cs[row]
                    self.out['95%以上载荷时间'][component] += pZhp.QiShengZHP.qs_time[row] + pZhp.QiShengZHP.ql_time[row]

            # 马达
            if pZhp.JiGouZHP.qsmd_yl[row] < 0.05 * self.qsmd_yl_max:
                self.out['5%以内载荷次数']['马达'] += pZhp.QiShengZHP.qs_cs[row]
                self.out['5%以内载荷时间']['马达'] += pZhp.QiShengZHP.qs_time[row] + pZhp.QiShengZHP.ql_time[row]
            elif 0.05 * self.qsmd_yl_max <= pZhp.JiGouZHP.qsmd_yl[row] < 0.5 * self.qsmd_yl_max:
                self.out['5-50%载荷次数']['马达'] += pZhp.QiShengZHP.qs_cs[row]
                self.out['5-50%载荷时间']['马达'] += pZhp.QiShengZHP.qs_time[row] + pZhp.QiShengZHP.ql_time[row]
            elif 0.5 * self.qsmd_yl_max <= pZhp.JiGouZHP.qsmd_yl[row] < 0.95 * self.qsmd_yl_max:
                self.out['50-90%载荷次数']['马达'] += pZhp.QiShengZHP.qs_cs[row]
                self.out['50-95%载荷时间']['马达'] += pZhp.QiShengZHP.qs_time[row] + pZhp.QiShengZHP.ql_time[row]
            else:
                self.out['95%以上载荷次数']['马达'] += pZhp.QiShengZHP.qs_cs[row]
                self.out['95%以上载荷时间']['马达'] += pZhp.QiShengZHP.qs_time[row] + pZhp.QiShengZHP.ql_time[row]

            # 吊钩应力循环次数, 臂销
            for component in ['吊钩应力循环次数', '臂销']:
                if pZhp.QiShengZHP.qzl_q[row] < 0.05 * self.qzl_q_max:
                    self.out['5%以内载荷次数'][component] += pZhp.QiShengZHP.qs_cs[row]
                    self.out['5%以内载荷时间'][component] += pZhp.QiShengZHP.qs_time[row] + pZhp.QiShengZHP.ql_time[row]
                elif 0.05 * self.qzl_q_max <= pZhp.QiShengZHP.qzl_q[row] < 0.5 * self.qzl_q_max:
                    self.out['5-50%载荷次数'][component] += pZhp.QiShengZHP.qs_cs[row]
                    self.out['5-50%载荷时间'][component] += pZhp.QiShengZHP.qs_time[row] + pZhp.QiShengZHP.ql_time[row]
                elif 0.5 * self.qzl_q_max <= pZhp.QiShengZHP.qzl_q[row] < 0.95 * self.qzl_q_max:
                    self.out['50-90%载荷次数'][component] += pZhp.QiShengZHP.qs_cs[row]
                    self.out['50-95%载荷时间'][component] += pZhp.QiShengZHP.qs_time[row] + pZhp.QiShengZHP.ql_time[row]
                else:
                    self.out['95%以上载荷次数'][component] += pZhp.QiShengZHP.qs_cs[row]
                    self.out['95%以上载荷时间'][component] += pZhp.QiShengZHP.qs_time[row] + pZhp.QiShengZHP.ql_time[row]

            # 将其他值设为NAN
            for component in ['减速机制动器', '三圈保护器', '高度限位器', '制动器控制阀', '转速传感器', '主起升右手柄']:
                for index in self.index:
                    if "%" in index: self.out[index][component] = np.nan

    # Ct: 起重机总工作循环次数 => 问张工
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

        # ---------------------------- 载荷谱表填写 => 各部件相同部分 ------------------------------ #
        self.out['车辆型号'] = vehicle_id
        self.out['年工作月数'] = self.A
        self.out['年工作天数'] = self.B
        self.out['天工作小时数'] = self.C
        self.out['年工作小时数'] = self.B * self.C
        self.out['工作年限'] = self.I
        self.out['总工作时间'] = self.I * self.B * self.C

        # ---------------------------- 载荷谱表填写 => 各部件不相同部分 ------------------------------ #
        # 天循环次数
        self.out['天循环次数'] = self.F * 2
        for component in ['主减速机', '转速传感器']:
            self.out['天循环次数'][component] = np.nan
        for component in ['主起升机构', '吊钩应力循环次数', '臂销', '主起升右手柄']:
            self.out['天循环次数'][component] = self.F
        self.out['天循环次数']['起升平衡阀单向阀'] = self.G * 2
        self.out['天循环次数']['起升平衡阀主阀芯'] = self.H * 2
        self.out['天循环次数']['三圈保护器'] = self.F * 0.1
        self.out['天循环次数']['高度限位器'] = self.F * 0.2
        self.out['年循环次数']['钢丝绳弯曲次数'] = self.F * 8

        # 年循环次数
        self.out['年循环次数'] = self.F * self.B * 2
        for component in ['主减速机', '转速传感器']:
            self.out['年循环次数'][component] = np.nan
        for component in ['主起升机构', '吊钩应力循环次数', '臂销', '主起升右手柄']:
            self.out['年循环次数'][component] = self.F * self.B
        self.out['年循环次数']['起升平衡阀单向阀'] = self.B * self.G
        self.out['年循环次数']['起升平衡阀主阀芯'] = self.B * self.H
        self.out['年循环次数']['三圈保护器'] = self.B * self.F * 0.1
        self.out['年循环次数']['高度限位器'] = self.B * self.F * 0.2
        self.out['年循环次数']['钢丝绳弯曲次数'] = self.B * self.F * 8

        # 总循环次数
        self.out['总循环次数'] = self.I * self.B * self.F * 2
        for component in ['主减速机', '转速传感器']:
            self.out['年循环次数'][component] = np.nan
        for component in ['主起升机构', '吊钩应力循环次数', '臂销', '主起升右手柄']:
            self.out['年循环次数'][component] = self.I * self.B * self.F
        self.out['年循环次数']['起升平衡阀单向阀'] = self.B * self.G * self.I
        self.out['年循环次数']['起升平衡阀主阀芯'] = self.B * self.H * self.I
        self.out['年循环次数']['三圈保护器'] = self.B * self.F * self.I * 0.1
        self.out['年循环次数']['高度限位器'] = self.B * self.F * self.I * 0.2
        self.out['年循环次数']['钢丝绳弯曲次数'] = self.B * self.F * self.I * 8


if __name__ == '__main__':
    qiShengINTER = ZQiShengINTER()
    print(qiShengINTER.out)
