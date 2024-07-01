from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QMainWindow,QApplication,QLabel
from Ui_untitled import Ui_mainWindow
import sys
import cv2
import numpy as np
import random
pos_list=[20+i*90 for i in range(15)]
def locate(pos):#从随意位置的点击坐标转化到最近线交点坐标
  global pos_list
  x_ind,y_ind,m_x,m_y=0,0,999,999
  for i,j in enumerate(pos_list):
    tmp_x=abs(pos[0]-j)
    tmp_y=abs(pos[1]-j)
    if(tmp_x<m_x):
      x_ind=i
      m_x=tmp_x
    if(tmp_y<m_y):
      y_ind=i
      m_y=tmp_y
  return [x_ind,y_ind]
def check(board,inds):#检查胜利条件
  ori=board[inds[0]][inds[1]]
  x_pos,y_pos=inds[0],inds[1]
  x,y,xy,yx,i=1,1,1,1,1
  finish=[False,False]
  i=1
  while(True):
    if((not finish[0]) and x_pos+i<15 and board[x_pos+i][y_pos]==ori):
      x+=1
    else:
      finish[0]=True
    if((not finish[1]) and x_pos-i>0 and board[x_pos-i][y_pos]==ori):
      x+=1
    else:
      finish[1]=True
    if(finish[0] and finish[1]):
      break
    i+=1
  finish=[False,False]
  i=1
  while(True):
    if((not finish[0]) and y_pos+i<15 and board[x_pos][y_pos+i]==ori):
      y+=1
    else:
      finish[0]=True
    if((not finish[1]) and y_pos-i>0 and board[x_pos][y_pos-i]==ori):
      y+=1
    else:
      finish[1]=True
    if(finish[0] and finish[1]):
      break
    i+=1
  finish=[False,False]
  i=1
  while(True):
    if((not finish[0]) and x_pos+i<15 and y_pos-i>=0 and board[x_pos+i][y_pos-i]==ori):
      yx+=1
    else:
      finish[0]=True
    if((not finish[1]) and x_pos-i>=0 and y_pos+i<15 and board[x_pos-i][y_pos+i]==ori):
      yx+=1
    else:
      finish[1]=True
    if(finish[0] and finish[1]):
      break
    i+=1
  finish=[False,False]
  i=1
  while(True):
    if((not finish[0]) and x_pos+i<15 and y_pos+i<15 and board[x_pos+i][y_pos+i]==ori):
      xy+=1
    else:
      finish[0]=True
    if((not finish[1]) and x_pos-i>=0 and y_pos-i>=0 and board[x_pos-i][y_pos-i]==ori):
      xy+=1
    else:
      finish[1]=True
    if(finish[0] and finish[1]):
      break
    i+=1
    
  return x>=5 or y>=5 or xy>=5 or yx>=5,ori
class ai():
  range_x=[15,-1]#搜索范围
  range_y=[15,-1]#搜索范围
  def get_score(self,board,x,y):#评分
    s_x,s_y,s_xy,s_yx=0,0,0,0
    #水平方向
    cnt_l,cnt_r=0,0
    f_l,f_r=True,True
    for i in range(1,5):
      if(x+i>=15):
        f_r=False#越界
      if(x-i<0):
        f_l=False
      if(f_r and board[x+i][y]==board[x+1][y]):
        cnt_r+=board[x+i][y]
      else:
        f_r=False#连续子结束
      if(f_l and board[x-i][y]==board[x-1][y]):
        cnt_l+=board[x-i][y]
      else:
        f_l=False#连续子结束
    if(cnt_l*cnt_r>=0):
      s_x=abs(cnt_r+cnt_l)#两侧同色连续，不论颜色，优先级取数量和
    else:
      s_x=max(abs(cnt_l),abs(cnt_r))#异色连续，优先级与最多的数量有关
      # 垂直方向
    cnt_u,cnt_d=0,0
    f_u,f_d=True,True
    for i in range(1,5):
      if(y+i>=15):
        f_d=False  # 越界
      if(y-i<0):
        f_u=False  # 越界
      if(f_d and board[x][y+i]==board[x][y+1]):
        cnt_d+=board[x][y+i]
      else:
        f_d=False  # 连续子结束
      if(f_u and board[x][y-i]==board[x][y-1]):
        cnt_u+=board[x][y-i]
      else:
        f_u=False  # 连续子结束
    if(cnt_u*cnt_d>=0):
      s_y=abs(cnt_u+cnt_d)  # 两侧同色连续，不论颜色，优先级取数量和
    else:
      s_y=max(abs(cnt_u),abs(cnt_d))  # 异色连续，优先级与最多的数量有关
    # 主对角线方向（\）
    cnt_ul,cnt_dr=0,0
    f_ul,f_dr=True,True
    for i in range(1,5):
      if(x+i>=15 or y+i>=15):
        f_dr=False  # 越界
      if(x-i<0 or y-i<0):
        f_ul=False  # 越界
      if(f_dr and board[x+i][y+i]==board[x+1][y+1]):
        cnt_dr+=board[x+i][y+i]
      else:
        f_dr=False  # 连续子结束
      if(f_ul and board[x-i][y-i]==board[x-1][y-1]):
        cnt_ul+=board[x-i][y-i]
      else:
        f_ul=False  # 连续子结束
    if(cnt_ul*cnt_dr>=0):
      s_xy=abs(cnt_ul+cnt_dr)  # 两侧同色连续，不论颜色，优先级取数量和
    else:
      s_xy=max(abs(cnt_ul),abs(cnt_dr))  # 异色连续，优先级与最多的数量有关
    # 副对角线方向
    cnt_ur,cnt_dl=0,0
    f_ur,f_dl=True,True
    for i in range(1,5):
      if(x+i>=15 or y-i<0):
        f_ur=False  # 越界
      if(x-i<0 or y+i>=15):
        f_dl=False  # 越界
      if(f_ur and board[x+i][y-i]==board[x+1][y-1]):
        cnt_ur+=board[x+i][y-i]
      else:
        f_ur=False  # 连续子结束
      if(f_dl and board[x-i][y+i]==board[x-1][y+1]):
        cnt_dl+=board[x-i][y+i]
      else:
        f_dl=False  # 连续子结束
    if(cnt_ur*cnt_dl>=0):
      s_yx=abs(cnt_ur+cnt_dl)  # 两侧同色连续，不论颜色，优先级取数量和
    else:
      s_yx=max(abs(cnt_ur),abs(cnt_dl))  # 异色连续，优先级与最多的数量有关  
    return max(s_x,s_y,s_xy,s_yx)
  def move(self,board):#走搜索范围内评分最高的
    max_score=0
    move_list=[]
    for x in range(self.range_x[0],self.range_x[1]+1):
      for y in range(self.range_y[0],self.range_y[1]+1):
        if(board[x][y]==0):
          score=self.get_score(board,x,y)
          if(score>max_score):#选最高的
            max_score=score
            move_list=[[x,y]]
          if(score==max_score):#增加一点随机，多个最高都记录一下
            move_list.append([x,y])
    if(len(move_list)==1):
      return move_list[0]
    else:
      ind=random.randint(0,len(move_list)-1)
      return move_list[ind]
class Board (QLabel):#监听点击事件
  on_click=QtCore.pyqtSignal(list)
  def __init__(self, parent=None):
    super (Board, self).__init__ (parent)
  def mousePressEvent(self, e):
    if(e.buttons()==QtCore.Qt.LeftButton):
      self.on_click.emit([e.x(),e.y()])

base_board=np.full((1300, 1300, 3),255, dtype = np.uint8)#绘制棋盘
for i in range(15):
  cv2.line(base_board,(20,i*90+20),(1300-20,i*90+20),(0,0,0),2)
  cv2.line(base_board,(i*90+20,20),(i*90+20,1300-20),(0,0,0),2)
cv2.circle(base_board,(int(1300/2),int(1300/2)),10,(0,0,0),-1)
cv2.circle(base_board,(int(1300/2),int(1300/2)),10,(0,0,0),-1)
cv2.circle(base_board,(int(1300/2)-360,int(1300/2)-360),10,(0,0,0),-1)
cv2.circle(base_board,(int(1300/2)+360,int(1300/2)-360),10,(0,0,0),-1)
cv2.circle(base_board,(int(1300/2)-360,int(1300/2)+360),10,(0,0,0),-1)
cv2.circle(base_board,(int(1300/2)+360,int(1300/2)+360),10,(0,0,0),-1)

class MainWindow(QMainWindow,Ui_mainWindow):
  def __init__(self, parent=None) -> None:
    global base_board
    super(MainWindow,self).__init__(parent)
    self.img_board=base_board.copy()#获取棋盘背景图
    self.turn=False#黑棋先手
    self.board=[[0 for i in range(15)] for i in range(15)]#初始化棋盘数据
    self.setupUi(self,Board)#初始化ui
    self.state=False#游戏设置为未开始状态
    self.use_ai=False#是否使用ai
    self.ai=ai()#加载ai
    self.Show_label.on_click.connect(self.on_click)#绑定信号
  def put(self,inds):
    global pos_list
    pos=[pos_list[inds[0]],pos_list[inds[1]]]
    cv2.circle(self.img_board,(pos[0],pos[1]),25,(255,255,255)if self.turn else (0,0,0),-1)
    cv2.circle(self.img_board,(pos[0],pos[1]),25,(0,0,0),3)
    self.board[inds[0]][inds[1]]=1 if self.turn else -1
    self.show_img()#更新棋盘图片
    is_win,ori=check(self.board,inds)
    if(is_win):
      self.win(ori)
  def win(self,ori):#胜利
    self.log.append('白色胜利'if ori==1 else '黑色胜利')
    self.log.append('点击“开始游戏”重置棋盘')
    self.state=False
    self.use_ai=False
  def on_click(self,pos):#点击时触发
    if(self.state==False):
      self.log.append('游戏未开始，请点击“开始游戏”')
      return
    inds=locate(pos)
    if(self.board[inds[0]][inds[1]]!=0):
      self.log.append('你不能把棋子放在那里')
      return
    self.log.append('玩家{}落子({},{})'.format('白色'if self.turn else '黑色',inds[1]+1,inds[0]+1))
    self.put(inds)#落子
    self.next_turn(inds)

  def next_turn(self,inds):
    self.turn=not self.turn#转换出棋方
    self.log.append('轮到白色出棋了'if self.turn else '轮到黑色出棋了')
    if(self.use_ai):#无论如何更新搜索范围
      self.ai.range_x=[min(self.ai.range_x[0],(inds[0]-2)if inds[0]>=2 else 0),max(self.ai.range_x[1],(inds[0]+2)if inds[0]<=12 else 14)]#更新搜索范围，只搜索已有棋子最外围2格区域
      self.ai.range_y=[min(self.ai.range_y[0],(inds[1]-2)if inds[1]>=2 else 0),max(self.ai.range_y[1],(inds[1]+2)if inds[1]<=12 else 14)]#但要小心别越界
      if(self.turn):#ai的回合落子
        move=self.ai.move(self.board)
        self.log.append(f'电脑落子({move[1]+1},{move[0]+1})')
        self.put(move)
        self.next_turn(move)
      pass  
  def show_img(self):
    showImage=QtGui.QImage(self.img_board.data, self.img_board.shape[1], self.img_board.shape[0],QtGui.QImage.Format_RGB888)
    self.Show_label.setPixmap(QtGui.QPixmap.fromImage(showImage))
  def start(self):#标准初始化
    global base_board
    self.img_board=base_board.copy()#重置棋盘
    self.board=[[0 for i in range(15)] for i in range(15)]#重置棋盘数据
    self.log.clear()
    self.log.append('游戏开始')
    self.log.append('黑棋先手，点击棋盘放置棋子')
    self.state=True
    self.turn=False
    self.show_img()
  def pvp_start(self):#不带ai
    self.use_ai=False
    self.start()
  def ai_start(self):#带ai
    self.use_ai=True
    self.ai.range_x=[15,-1]
    self.ai.range_y=[15,-1]
    self.start()
if __name__ == '__main__':
  
  app = QApplication(sys.argv)
  window_mian = MainWindow()
  window_mian.show()
  sys.exit(app.exec_())
