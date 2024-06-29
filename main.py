from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QMainWindow,QApplication
from PyQt5.QtWidgets import QWidget
from PyQt5 import QtCore, QtGui, QtWidgets
from Ui_untitled import Ui_mainWindow
import sys
import cv2
import numpy as np
import copy
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
  return [pos_list[x_ind],pos_list[y_ind]],[x_ind,y_ind]

class Board (QtWidgets.QLabel):#监听点击事件
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
    self.Show_label.on_click.connect(self.on_click)#绑定信号
   
  def check(self,inds):#检查胜利条件
    ori=self.board[inds[0]][inds[1]]
    x_pos,y_pos=inds[0],inds[1]
    board=self.board
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
      if((not finish[0]) and x_pos+i<15 and y_pos-i>0 and board[x_pos+i][y_pos-i]==ori):
        yx+=1
      else:
        finish[0]=True
      if((not finish[1]) and x_pos-i>0 and y_pos+i<15 and board[x_pos-i][y_pos+i]==ori):
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
      if((not finish[1]) and x_pos-i>0 and y_pos-i>0 and board[x_pos-i][y_pos-i]==ori):
        xy+=1
      else:
        finish[1]=True
      if(finish[0] and finish[1]):
        break
      i+=1
      
    return x>=5 or y>=5 or xy>=5 or yx>=5
  def win(self):#胜利
    self.log.append('白色胜利'if self.turn else '黑色胜利')
    self.log.append('点击“开始游戏”重置棋盘')
    self.state=False
  def on_click(self,pos):#点击时触发
    if(self.state==False):
      self.log.append('游戏未开始，请点击“开始游戏”')
      return
    pos,inds=locate(pos)
    if(self.board[inds[0]][inds[1]]!=0):
      self.log.append('你不能把棋子放在那里')
      return
    cv2.circle(self.img_board,(pos[0],pos[1]),25,(255,255,255)if self.turn else (0,0,0),-1)
    cv2.circle(self.img_board,(pos[0],pos[1]),25,(0,0,0),3)
    self.board[inds[0]][inds[1]]=1 if self.turn else -1
    self.show_img()#更新棋盘图片
    is_win=self.check(inds)
    if(is_win):
      self.win()
      return
    self.turn=not self.turn#转换出棋方
    self.log.append('轮到白色出棋了'if self.turn else '轮到黑色出棋了')
  def show_img(self):
    showImage=QtGui.QImage(self.img_board.data, self.img_board.shape[1], self.img_board.shape[0],QtGui.QImage.Format_RGB888)
    self.Show_label.setPixmap(QtGui.QPixmap.fromImage(showImage))
  def start(self):
    global base_board
    self.img_board=base_board.copy()#重置棋盘
    self.board=[[0 for i in range(15)] for i in range(15)]#重置棋盘数据
    self.log.clear()
    self.log.append('游戏开始')
    self.state=True
    self.turn=False
    self.show_img()
if __name__ == '__main__':
  
  app = QApplication(sys.argv)
  window_mian = MainWindow()
  window_mian.show()
  sys.exit(app.exec_())
