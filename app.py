import retail_banking.databases
from retail_banking.databases import database,customerdb,transactiondb,executive
from retail_banking import app,routes

if __name__=="__main__":    
    app.run(host='0.0.0.0')

