import itasca
import math
import numpy as np

itasca.command("""
set echo off
call AE_postprocess2D.dat
set echo on
""")

def AE_draw_ball(r_min,r_max):
#绘制事件的效果图
    itasca.fish.set('r_min',r_min)
    itasca.fish.set('r_max',r_max)
    itasca.fish.call_function('AE_draw_ball')
    print('Finsh draw_ball')
    
def cal_ratio_R():
#计算事件矩张量R值
    hit_num = itasca.fish.get('hit_num')
    if hit_num > 0:
        for num_h in range(1,hit_num+1):
            itasca.fish.set('num_h',num_h)
            itasca.fish.call_function('copy_data')
            m1 = itasca.fish.get('m_xx')
            m2 = itasca.fish.get('m_xy')
            m3 = itasca.fish.get('m_yx')
            m4 = itasca.fish.get('m_yy')
            m = [[m1, m2],[m3,m4]]
            lis = np.array(m)
            instead=np.linalg.eig(lis)
            m_1 = instead[0][0]
            m_2 = instead[0][1]
            m_3 = 0                         #2D模拟，m_3为0
            
            if m_1 == 0 and m_2 == 0 and m_3 == 0:
                print('The eigenvalue is equal to zero. Pass!')
            elif np.isnan(m_1) or np.isnan(m_2) or np.isnan(m_3):
                print('The eigenvalue is equal to nan. Pass!')
            else:
                M_0_new = math.sqrt((math.pow(m_1,2) + math.pow(m_2,2) + math.pow(m_3,2))/2)
                M_0 = itasca.fish.get('M_0')
                M_w = itasca.fish.get('M_w')
                if M_0 <= M_0_new:
                    M_0 = M_0_new
                    M_w = 2*math.log10(M_0)/3 - 6
                    tr_M = m_1 + m_2 #+ m_3
                    sum_m = abs(m_1-tr_M/2) + abs(m_2-tr_M/2) #+ abs(m_3-tr_M/3)
                    value_R = tr_M*100/(abs(tr_M)+sum_m)
                    if isinstance(m_1,complex) or isinstance(m_2,complex):
                        print('The m_1 or m_2 is complex. Pass!')
                        itasca.fish.set('m_1',0)
                        itasca.fish.set('m_2',0)
                    else:
                        itasca.fish.set('m_1',m_1)
                        itasca.fish.set('m_2',m_2)
                    itasca.fish.set('M_0',M_0)
                    itasca.fish.set('M_w',M_w)
                    if isinstance(value_R,complex):
                        print('The value_R is complex. Pass!')
                        itasca.fish.set('value_R',200)
                    else:
                        itasca.fish.set('value_R',value_R)
                    itasca.fish.call_function('assign_data')
        
def draw_ratio_R(end_time,r_R):
#绘事件矩张量R值形状图
    itasca.fish.call_function('draw_R_main')
    hit_num = itasca.fish.get('hit_num')
    itasca.fish.set('r_R',r_R)
    for num_h in range(1,hit_num+1):
        itasca.fish.set('num_h',num_h)
        itasca.fish.call_function('copy_data')
        hit_begin = itasca.fish.get('hit_begin')
        if end_time == 0 or hit_begin <= end_time:      #设置截止时间s，0绘制全部结果
            itasca.fish.call_function('draw_ratio_R')
    
    print('Finsh draw_ratio_R') 

def draw_tensor():
#绘制事件矩张量图
	hit_num = itasca.fish.get('hit_num')
	itasca.fish.call_function('delete_vector')
	for num_t in range(1,hit_num+1):
		itasca.fish.set('num_t',num_t)
		itasca.fish.call_function('copy_data')
		#t_now = itasca.fish.get('t_now')
		#AE_long = itasca.fish.get('AE_long')
		#if t_now > AE_long:
		m1 = itasca.fish.get('m_xx')
		m2 = itasca.fish.get('m_xy')
		m3 = itasca.fish.get('m_yx')
		m4 = itasca.fish.get('m_yy')
		m = [[m1, m2],[m3,m4]]
		lis = np.array(m)
		instead=np.linalg.eig(lis)
		eig1=instead[0][0]
		eig1x=instead[1][0][0]
		eig1y=instead[1][0][1]
		eig2=instead[0][1]
		eig2x=instead[1][1][0]
		eig2y=instead[1][1][1]
		
		itasca.fish.set('eig1',eig1)
		itasca.fish.set('eig1x',eig1x)
		itasca.fish.set('eig1y',eig1y)
		itasca.fish.set('eig2',eig2)
		itasca.fish.set('eig2x',eig2x)
		itasca.fish.set('eig2y',eig2y)
		itasca.fish.call_function('make_vector')
	
	print('Draw tensor finished!')

def main():
    print("Postprocess begain!")
    itasca.fish.call_function('energy_magnitude')		#计算事件能级
    AE_draw_ball(0.3e-3,1.2e-3)							#绘制事件的效果图。输入事件球半径范围，默认0.3~1.2mmm
    cal_ratio_R()                                       #计算事件矩张量R值
    draw_ratio_R(0,0.5e-3)										#绘事件矩张量R值形状图。输入截止时间，默认为0，绘制全部结果;输入R标记半径，默认为0.5mm
    #draw_tensor()										#绘制事件矩张量图
    print("Postprocess finished!")


if __name__ == '__main__':
    hit_num = itasca.fish.get('hit_num')
    if hit_num > 0:
        main()
    else:
        itasca.set_callback("cal_ratio_R", 52)