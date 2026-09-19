class Account:
    """Pure Domain Entity Representing an account in GDB """
    def __init__(self,account_number:str,name:str,age:int,balance:float,account_type:str,status:str="Active")->None:
        self.account_number=account_number
        self.name=name
        self.age=age
        self.balance=balance
        self.account_type=account_type
        self.status=status


    def deposit(self,amount:float)->bool:
        if amount>0:
            self.amount+=amount
            return True
        return False

    
    def withdraw(self,amount:float)->bool:
        if amount>0 and amount<=self.balance:
            self.balance-=amount
            return True
        return False

    
    def display_acount_info(self)->None:
        print(f"Account Number: {self.account_number}")
        print(f"Name: {self._name}")
        print(f"Age: {self._age}")
        print(f"Balance: Rs {self._balance}")
        print(f"Account Type: {self._account_type}")
        print(f"Status: {self._status}")

    @property
    def account_number(self)->str:
        return self.account_number

    @property
    def name(self)->str:
        return self.name

    @name.setter
    def name(self,name:str)->None:
        self.name=name

    @property
    def age(self)->int:
        return self.age

    @age.setter
    def age(self,age:int)->None:
        self.age=age

    
    @property
    def balance(self)->float:
        return self.balance

    @property
    def account_type(self)->str:
        return self.account_type

    @property
    def status(self)->str:
        return self.status

    @status.setter
    def status(self,status:str)->None:
        self.status=status




    