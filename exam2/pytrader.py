from os import path
import sys
from xml.etree.ElementTree import TreeBuilder
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic
from Kiwoom import *

form_class = uic.loadUiType("C:\\Users\\gusqo\\Documents\\GitHub\\kiwoomOpenApi\\exam2\\pytrader.ui")[0]


class MyWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.kiwoom = Kiwoom()
        self.kiwoom.comm_connect()

        self.timer = QTimer(self)
        self.timer.start(500)
        self.timer.timeout.connect(self.timeout)

        accouns_num = int(self.kiwoom.get_login_info("ACCOUNT_CNT"))
        accounts = self.kiwoom.get_login_info("ACCNO")

        accounts_list = accounts.split(';')[0:accouns_num]
        self.comboBox.addItems(accounts_list)

        self.lineEdit.textChanged.connect(self.code_changed)
        self.pushButton.clicked.connect(self.send_order)
        self.pushButton_TEST.clicked.connect(self.test_button)
        
        ## 조건검색식 관련 추가
        self.load_condition_list()
        self.checkBox_cond.setChecked(True)
        self.pushButton_cond.clicked.connect(self.start_cond)
        self.pushButton_cond_2.clicked.connect(self.start_cond_2)

    def code_changed(self):
        code = self.lineEdit.text()
        name = self.kiwoom.get_master_code_name(code)
        self.lineEdit_2.setText(name)

    def send_order(self):
        order_type_lookup = {'신규매수': 1, '신규매도': 2, '매수취소': 3, '매도취소': 4}
        hoga_lookup = {'지정가': "00", '시장가': "03"}

        account = self.comboBox.currentText()
        order_type = self.comboBox_2.currentText()
        code = self.lineEdit.text()
        hoga = self.comboBox_3.currentText()
        num = self.spinBox.value()
        price = self.spinBox_2.value()

        print(account)
        print(order_type)
        print(code)
        print(hoga)
        print(num)
        print(price)


        self.kiwoom.send_order("send_order_req", "0101", account, order_type_lookup[order_type], code, num, price, hoga_lookup[hoga], "")
    
    def send_auto_order(self,account,order_type,code,hoga,num,price):

        order_type_lookup = {'신규매수': 1, '신규매도': 2, '매수취소': 3, '매도취소': 4}
        hoga_lookup = {'지정가': "00", '시장가': "03"}

        if account == "default":
            account = self.comboBox.currentText()

        print(account)
        print(order_type)
        print(code)
        print(hoga)
        print(num)
        print(price)

        self.kiwoom.send_order("send_order_req", "0101", account, order_type, code, num, price, hoga, "")

    def timeout(self):
        current_time = QTime.currentTime()
        text_time = current_time.toString("hh:mm:ss")
        time_msg = "현재시간: " + text_time

        state = self.kiwoom.get_connect_state()
        if state == 1:
            state_msg = "서버 연결 중"
        else:
            state_msg = "서버 미 연결 중"

        self.statusbar.showMessage(state_msg + " | " + time_msg)

        if self.kiwoom.msg:
            # 텔레그램
            if self.checkBox_cond.isChecked():
                self.kiwoom.bot.sendMessage(chat_id=self.kiwoom.chat_id, text=self.kiwoom.msg)
            self.textEdit_cond.append(self.kiwoom.msg)
            self.textEdit_cond.append(self.kiwoom.msg)
            self.kiwoom.msg = ""
        #종목편입 자동주문
        if self.kiwoom.order:
            order_detail = self.kiwoom.order.split(",")

            """
            실시간 종목 조건검색 요청시 발생되는 이벤트

            :param code: string - 종목코드
            :param event: string - 이벤트종류("I": 종목편입, "D": 종목이탈)
            :param conditionName: string - 조건식 이름
            :param conditionIndex: string - 조건식 인덱스(여기서만 인덱스가 string 타입으로 전달됨)
            """
            code = order_detail[0]
            name = self.kiwoom.get_master_code_name(code)
            event = order_detail[1]
            conditionName = order_detail[2]
            conditionIndex = order_detail[3]

            print(order_detail)

            if conditionName == "DAQ_BUY":
                print("Buy_Order")
                if event == "I":
                    print("DAQ_BUY_종목편입") 
                    if self.checkOwnStock(name):
                        print("횡보중 재진입_BUY")
                    else:
                        print("풀.매.수")
                        stockCurrentPrice = self.searchCurrentPrice(code)
                        stocksNum = self.sharesPerPercentage(1,code)
                        self.send_auto_order(account="default",order_type=1,code=code,hoga="00",num=stocksNum,price=stockCurrentPrice)

                if event == "N":
                    print("DAQ_BUY_시작") 
                    if self.checkOwnStock(name):
                        print("재시작 보유중")
                    else:
                        print("풀.매.수")
                        stockCurrentPrice = self.searchCurrentPrice(code)
                        stocksNum = self.sharesPerPercentage(1,code)
                        self.send_auto_order(account="default",order_type=1,code=code,hoga="00",num=stocksNum,price=stockCurrentPrice)

            if conditionName == "DAQ_SELL":
                print("Sell_Order")
                if event == "I":
                    print("DAQ_SELL_종목편입") 
                    if self.checkOwnStock(name):
                        print("풀.매.도")
                        stockCurrentPrice = self.searchCurrentPrice(code)
                        stocksNum = self.selectOwnStockPercent(100,name)
                        self.send_auto_order(account="default",order_type=2,code=code,hoga="00",num=stocksNum,price=stockCurrentPrice)
                    else:
                        print("횡보중 재진입_SELL")
            
            self.kiwoom.order = ""

                
            
    ## 조건검색식 관련 추가
    def load_condition_list(self):
        print("pytrader.py [load_condition_list]")
        """ condiComboBox에 condition List를 설정한다. """

        cond_list = []
        try:
            # 조건식 실행
            self.kiwoom.getConditionLoad()
            # getConditionLoad 가 정상 실행되면 kiwoom.condition에 조건식 목록이 들어간다.
            dic = self.kiwoom.condition
            
            for key in dic.keys():
                cond_list.append("{};{}".format(key, dic[key]))
            
            # 콤보박스에 조건식 목록 추가
            self.comboBox_cond.addItems(cond_list)
            self.comboBox_cond_2.addItems(cond_list)

        except Exception as e:
            print(e)

    def start_cond(self):
        conditionIndex = self.comboBox_cond.currentText().split(';')[0]
        conditionName = self.comboBox_cond.currentText().split(';')[1]

        if self.pushButton_cond.text() == "적용":

            try: 
                self.kiwoom.sendCondition("0",conditionName,int(conditionIndex),1)
                self.pushButton_cond.setText("해제")
                self.comboBox_cond.setEnabled(False)
                self.checkBox_cond.setEnabled(False)
                print("{} activated".format(conditionName))

            except Exception as e:
                print(e)

        else:
            self.kiwoom.sendConditionStop("0",conditionName,conditionIndex)
            self.pushButton_cond.setText("적용")
            self.comboBox_cond.setEnabled(True)
            self.checkBox_cond.setEnabled(True)

    def start_cond_2(self):
        conditionIndex = self.comboBox_cond_2.currentText().split(';')[0]
        conditionName = self.comboBox_cond_2.currentText().split(';')[1]

        if self.pushButton_cond_2.text() == "적용":

            try: 
                self.kiwoom.sendCondition("1",conditionName,int(conditionIndex),1)
                self.pushButton_cond_2.setText("해제")
                self.comboBox_cond_2.setEnabled(False)
                self.checkBox_cond_2.setEnabled(False)
                print("{} activated".format(conditionName))

            except Exception as e:
                print(e)

        else:
            self.kiwoom.sendConditionStop("1",conditionName,conditionIndex)
            self.pushButton_cond_2.setText("적용")
            self.comboBox_cond_2.setEnabled(True)
            self.checkBox_cond_2.setEnabled(True)

    # 주문가능금액 조회
    # In : X
    # Out : 계좌 현재 주문가능 금액
    def balace_check(self):

        account_number = self.kiwoom.get_login_info("ACCNO")
        account_number = account_number.split(';')[0]
        
        self.kiwoom.set_input_value("계좌번호", account_number)
        self.kiwoom.comm_rq_data("opw00001_req", "opw00001", 0, "2000")


        print(self.kiwoom.d2_deposit)

        return int(self.kiwoom.d2_deposit.replace(",",""))

    # 계좌별 보유종목 전체조회
    # In : X
    # Out : 계좌 보유종목 전체
    def selectOwnStock(self):

        self.kiwoom.reset_opw00018_output()
        account_number = self.kiwoom.get_login_info("ACCNO")
        account_number = account_number.split(';')[0]

        self.kiwoom.set_input_value("계좌번호", account_number)
        self.kiwoom.comm_rq_data("opw00018_req", "opw00018", 0, "2000")


        for i in range(1, 6):
            item = QTableWidgetItem(self.kiwoom.opw00018_output['single'][i - 1])
            print( str(i)+"번째 : "+str(item) )



        # Item list
        item_count = len(self.kiwoom.opw00018_output['multi'])

        for j in range(item_count):
            row = self.kiwoom.opw00018_output['multi'][j]
            for i in range(len(row)):
                print(row[i])
    
    # 동일종목 보유여부 확인
    # In : 종목이름
    # Out : 있을경우 True / 없을경우 False
    def checkOwnStock(self,target):
        print("checkOwnStock")

        self.kiwoom.reset_opw00018_output()
        account_number = self.kiwoom.get_login_info("ACCNO")
        account_number = account_number.split(';')[0]

        self.kiwoom.set_input_value("계좌번호", account_number)
        self.kiwoom.comm_rq_data("opw00018_req", "opw00018", 0, "2000")

        # Item list
        item_count = len(self.kiwoom.opw00018_output['multi'])
        check_list = []

        for j in range(item_count):
            row = self.kiwoom.opw00018_output['multi'][j]
            check_list.append(row[0])
        
        if target in check_list:
            return True
        else:
            return False
    
    # 동일종목 보유갯수 %기준 조회
    # In : 종목이름, %
    # Out : 보유주식 갯수 %
    def selectOwnStockPercent(self,percent,name):
        print("selectOwnStockPercent")

        self.kiwoom.reset_opw00018_output()
        account_number = self.kiwoom.get_login_info("ACCNO")
        account_number = account_number.split(';')[0]

        self.kiwoom.set_input_value("계좌번호", account_number)
        self.kiwoom.comm_rq_data("opw00018_req", "opw00018", 0, "2000")

        # Item list
        item_count = len(self.kiwoom.opw00018_output['multi'])
        check_list = []

        for j in range(item_count):
            row = self.kiwoom.opw00018_output['multi'][j]
            check_list.append([row[0],row[1]])

        target=0

        for list in check_list:
            if name in list:
                target = int(list[1])
                break
        
        if target != 0:
            target = target//(percent/100)
        else:
            target = -1
        
        return int(target)

    # 현재가조회
    # In : 종목코드
    # Out : 현재가
    def searchCurrentPrice(self,code):
        self.kiwoom.set_input_value("종목코드", code)
        self.kiwoom.comm_rq_data("opt10001_req", "opt10001", 0, "2001")
        
        return int(self.kiwoom.stock_current_price.replace(",","").replace("-",""))

    # 현재잔고기준 주문주식수 계산
    # In : 원하는% , 종목코드
    # Out : 주문수량
    def sharesPerPercentage(self,percent,code):
        
        accountAvailable = self.balace_check()
        searchCurrentPrice = self.searchCurrentPrice(code)

        #부호제거
        if int(searchCurrentPrice) < 0:
            searchCurrentPrice = -1*int(searchCurrentPrice)
        else :
            searchCurrentPrice = int(searchCurrentPrice) 

        # 목표주식수 = ( 잔고 * % ) / 현재가
        stocksNum = int( (accountAvailable*(percent/100)) // searchCurrentPrice )
        
        print("주문주식수 : " + str(stocksNum))
        
        return stocksNum
    
    def test_button(self):
        print("test--------")
        stocksNum = self.sharesPerPercentage(10,"229200")
        print(stocksNum)

        self.selectOwnStock()
        print(self.selectOwnStockPercent(100,"위지윅스튜디오"))
        print(self.selectOwnStockPercent(100,"와자작스튜디오"))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()