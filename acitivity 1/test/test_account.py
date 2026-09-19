from domain.account import Account

def main():
    print("Testing Activity 1")
    acc=Account("AC101","Akash",20,5000.0,"Savings","Active")

    acc.display_acount_info()

    print("====================================================")
    withdraw_amt=float(input("Enter the withdrawal amount"))
    if (acc.withdraw(withdraw_amt)):
        print(f"The amount can be withdrawn and the current balance is {acc.balance}")
    else:
        print(f"the amount provided is invalid and ur current balance is {acc.balance}")

    if(acc.deposit(2000)):
        print(f"Amount deposited successfully and ur current balanec is {acc.balance}")


if __name__=="__main__":
    main()

    

    