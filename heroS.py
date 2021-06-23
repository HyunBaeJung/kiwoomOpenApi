from pykiwoom.kiwoom import *


class heroS:

    #객체생성과 동시에 로그인
    def __init__(self):
        print("로그인 시작")
        self.kiwoom = Kiwoom()
        self.kiwoom.CommConnect(block=True)
        print("블록킹 로그인 완료")

        #사용자 정보
        self.account_num = self.kiwoom.GetLoginInfo("ACCOUNT_CNT")        # 전체 계좌수
        self.accounts = self.kiwoom.GetLoginInfo("ACCNO")                 # 전체 계좌 리스트
        self.user_id = self.kiwoom.GetLoginInfo("USER_ID")                # 사용자 ID
        self.user_name = self.kiwoom.GetLoginInfo("USER_NAME")            # 사용자명
        self.keyboard = self.kiwoom.GetLoginInfo("KEY_BSECGB")            # 키보드보안 해지여부
        self.firewall = self.kiwoom.GetLoginInfo("FIREW_SECGB")           # 방화벽 설정 여부

        #종목코드
        self.kospi  = self.kiwoom.GetCodeListByMarket('0')                # 코스피
        self.kosdaq = self.kiwoom.GetCodeListByMarket('10')               # 코스닥
        self.etf    = self.kiwoom.GetCodeListByMarket('8')                # ETF

    #연결상태 확인하기
    def connectionCheck(self):
        state = self.kiwoom.GetConnectState()
        if state == 0:
            print("미연결")
        elif state == 1:
            print("연결완료")


    #사용자정보 불러오기.
    def getBasicInfo(self):
        print("전체 계좌수 : "+self.account_num)
        print("전체 계좌 리스트 : "+str(self.accounts))
        print("사용자 ID : "+self.user_id)
        print("사용자명 : "+self.user_name)
        print("키보드보안 해지여부 : "+self.keyboard)
        print("방화벽 설정 여부 : "+self.firewall)






    # 종목정보 관련 함수 ---------------------------------------------------------------------------------------------


    # 종목이름 불러오기
    def getStockName(self,stockNo):
        name = self.kiwoom.GetMasterCodeName(stockNo)
        print(name)
        return name

    # 상장 주식수 불러오기
    def getStockAmount(self,stockNo):
        stock_cnt = self.kiwoom.GetMasterListedStockCnt(stockNo)
        print("상장주식수: ", stock_cnt)
        return stock_cnt

    # 종목 감리구분
    # 구분 : '정상', '투자주의', '투자경고', '투자위험', '투자주의환기종목'
    def getStockConstruction(self,stockNo):
        StockState = self.kiwoom.GetMasterConstruction(stockNo)
        print(StockState)
        return StockState

    # 종목 종합상태
    def getStockState(self,stockNo):
        StockState = self.kiwoom.GetMasterStockState(stockNo)
        print(StockState)
        return StockState

    # 테마분류
    def getTheme(self,num):
        group = self.kiwoom.GetThemeGroupList(num)
        print(group)
        return group

    def getThemeDetail(self,code):
        tickers = self.kiwoom.GetThemeGroupCode(code)
        print(tickers)
        return tickers

    #단일조건종목 불러오기
    def getSetUpStock(self,col,row):
        # 조건식을 PC로 다운로드
        print("1")
        self.kiwoom.GetConditionLoad()
        # 전체 조건식 리스트 얻기
        print("2")
        conditions = self.kiwoom.GetConditionNameList()

        # 0번 조건식에 해당하는 종목 리스트 출력
        print("3")
        condition_index = conditions[col][row]
        print(condition_index)
        print("4")
        condition_name = conditions[0][1]
        print(condition_name)
        print("5")
        codes = self.kiwoom.SendCondition("0101", condition_name, condition_index, 2)
        print(codes)

        return [codes,condition_name,condition_index]

    def OnReceiveTrCondition(sScrNo, strCodeList,  strConditionName,  nIndex,  nNext):
        print("되나?")
        print(sScrNo, strCodeList,  strConditionName,  nIndex,  nNext)


        
        
        

    # 주문 관련 함수 ---------------------------------------------------------------------------------------------
    """
    ** 예시

    # 주식계좌
    accounts = kiwoom.GetLoginInfo("ACCNO")
    stock_account = accounts[0]

    # 삼성전자, 10주, 시장가주문 매수
    kiwoom.SendOrder("시장가매수", "0101", stock_account, 1, "005930", 10, 0, "03", "")

    # 삼성전자, 10주, 시장가주문 매도
    kiwoom.SendOrder("시장가매도", "0101", stock_account, 2, "005930", 10, 0, "03", "")

    SendOrder(  sRQName,
                sScreenNO,
                sAccNo,
                nOrderType,
                sCode,
                nQty,
                nPrice,
                sHogaGb,
                sOrgOrderNo )
    """
    
    # sRQName	사용자가 임의로 지정할 수 있는 이름입니다. (예: "삼성전자주문")
    # sScreenNO	화면번호로 "0"을 제외한 4자리의 문자열을 사용합니다. (예: "1000")
    # sAccNo	계좌번호입니다. (예: "8140977311")
    # nOrderType	주문유형입니다. (1: 매수, 2: 매도, 3: 매수취소, 4: 매도취소, 5: 매수정정, 6: 매도 정정)
    # sCode	매매할 주식의 종목코드입니다.
    # nQty	주문수량입니다.
    # nPrice	주문단가입니다.
    # sHogaGb	'00': 지정가, '03': 시장가
    # sOrgOrderNo	원주문번호로 주문 정정시 사용합니다.