from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
import json
import sqlite3

def login(request):
    conn=sqlite3.connect("supermarket.db")
    cursor=conn.cursor()
    if request.method=="GET":
        # conn.execute("DROP TABLE Employees;") 
        conn.execute("CREATE TABLE IF NOT EXISTS SuperMartAdmin(ADMIN_ID INTEGER PRIMARY KEY AUTOINCREMENT,ADMIN_NAME VARCHAR(40) UNIQUE NOT NULL,PASSWORD VARCHAR(40));")
        # conn.execute("INSERT INTO SuperMartAdmin(ADMIN_NAME,PASSWORD) VALUES('admin','1212');")
        # conn.commit()
        conn.execute("CREATE TABLE IF NOT EXISTS Customers(CUSTOMER_ID INTEGER PRIMARY KEY AUTOINCREMENT,CUSTOMER_NAME VARCHAR(40) UNIQUE NOT NULL);")
        conn.execute("CREATE TABLE IF NOT EXISTS Employees(EMPLOYEE_ID INTEGER PRIMARY KEY AUTOINCREMENT,EMPLOYEE_NAME VARCHAR(40) UNIQUE NOT NULL,PASSWORD VARCHAR(40));")
        conn.execute("CREATE TABLE IF NOT EXISTS Vendors(VENDOR_ID INTEGER PRIMARY KEY AUTOINCREMENT,VENDOR_NAME VARCHAR(40) UNIQUE NOT NULL);")
        conn.execute("CREATE TABLE IF NOT EXISTS Products(PRODUCT_ID INTEGER PRIMARY KEY AUTOINCREMENT,PRODUCT_NAME VARCHAR(40) UNIQUE NOT NULL,QUANTITY INT DEFAULT 0, COST_PRICE INT NOT NULL, SELLING_PRICE INT NOT NULL, MINIMUM_QUANTITY INT NOT NULL);")
        
        conn.execute("CREATE TABLE IF NOT EXISTS Purchases(PURCHASE_ID INTEGER PRIMARY KEY AUTOINCREMENT,EMPLOYEE_ID INT NOT NULL, VENDOR_ID INT NOT NULL, TOTAL INT DEFAULT 0, TAX INT DEFAULT 5, GRAND_TOTAL INT DEFAULT 0, PURCHASE_DATE DATETIME DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (EMPLOYEE_ID) REFERENCES Employees(EMPLOYEE_ID), FOREIGN KEY (VENDOR_ID) REFERENCES Vendors(VENDOR_ID));")
        
        conn.execute("CREATE TABLE IF NOT EXISTS PurchaseDetails(PURCHASE_DETAILS_ID INTEGER PRIMARY KEY AUTOINCREMENT,PURCHASE_ID INT NOT NULL,PRODUCT_ID INT NOT NULL, QUANTITY INT NOT NULL, PRICE INT NOT NULL,FOREIGN KEY (PURCHASE_ID) REFERENCES Purchases(PURCHASE_ID), FOREIGN KEY (PRODUCT_ID) REFERENCES Products(PRODUCT_ID));")
        
        conn.execute("CREATE TABLE IF NOT EXISTS Sales(SALE_ID INTEGER PRIMARY KEY AUTOINCREMENT,EMPLOYEE_ID INT NOT NULL, CUSTOMER_ID INT NOT NULL, TOTAL INT DEFAULT 0, TAX INT DEFAULT 5, GRAND_TOTAL INT DEFAULT 0, SALE_DATE DATETIME DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (EMPLOYEE_ID) REFERENCES Employees(EMPLOYEE_ID), FOREIGN KEY (CUSTOMER_ID) REFERENCES Customers(VENDOR_ID));")
        
        conn.execute("CREATE TABLE IF NOT EXISTS SaleDetails(SALE_DETAILS_ID INTEGER PRIMARY KEY AUTOINCREMENT,SALE_ID INT NOT NULL,PRODUCT_ID INT NOT NULL, QUANTITY INT NOT NULL, PRICE INT NOT NULL,FOREIGN KEY (SALE_ID) REFERENCES Sales(SALE_ID), FOREIGN KEY (PRODUCT_ID) REFERENCES Products(PRODUCT_ID));")
        return render(request,"login.html")

    elif request.method=="POST":
        username=request.POST.get("username")
        password=request.POST.get("password")
        role=request.POST.get("role")
        if role=="Employee":
            cursor.execute("SELECT * FROM Employees WHERE EMPLOYEE_NAME=? AND PASSWORD=?",(username,password))
            emp_id=conn.execute("SELECT EMPLOYEE_ID FROM Employees WHERE EMPLOYEE_NAME=?",[(username)]).fetchone()[0]
            isValidEmployee= cursor.fetchone() is not None
            if isValidEmployee:
                request.session["user"]=username
                request.session["role"]=role
                request.session["id"]=emp_id
                return render(request,"employeeHome.html")
            else:
                resp={"status":"Invalid Credentials"}
                return JsonResponse(resp)
        elif role=="Admin":
            cursor.execute("SELECT * FROM SuperMartAdmin WHERE ADMIN_NAME=? AND PASSWORD=?",(username,password))
            adm_id=conn.execute("SELECT ADMIN_ID FROM SuperMartAdmin WHERE ADMIN_NAME=?",[(username)]).fetchone()[0]
            isValidAdmin = cursor.fetchone() is not None
            if isValidAdmin:
                request.session["user"]=username
                request.session["role"]=role
                request.session["id"]=adm_id
                return render(request,"home.html")
            else:
                resp={"status":"Invalid Credentials"}
                return JsonResponse(resp)

def home(request):
    return render(request,"home.html")

def employeeHome(request):
    return render(request,"employeeHome.html")

def customers(request):
    if request.session["role"]=="Admin":
        conn=sqlite3.connect("supermarket.db")
        cursor=conn.cursor()
        if request.method=="GET":
            tableData= conn.execute("SELECT * FROM Customers;").fetchall()
            data=json.dumps(tableData)
            return render(request,"customer.html",context={"data":data})
            
        elif request.method=="POST":
            operation=request.POST.get("operation")
            if operation=="ADD":
                name=request.POST.get("c_name")
                try:
                    # cursor.execute("INSERT INTO Customers(CUSTOMER_NAME) VALUES('"+name+"')") 
                    conn.execute("INSERT INTO Customers(CUSTOMER_NAME) VALUES(?)",([name]))
                except Exception as e:
                    conn.rollback()
                    return HttpResponse(e)
                else:
                    conn.commit()
                    c_id=cursor.execute("SELECT CUSTOMER_ID FROM Customers WHERE CUSTOMER_NAME='"+name+"';").fetchone()[0]
                    resp={"id":c_id,"status":"success"}
                    return JsonResponse(resp)
                
            elif operation=="DELETE":
                id=request.POST.get("delete_id")
                try:
                    conn.execute("DELETE FROM Customers WHERE CUSTOMER_ID="+id)
                except Exception as e:
                    conn.rollback()
                    return JsonResponse(e)
                else:
                    conn.commit()
                    resp={"status":"success"}
                    return JsonResponse(resp)
            
            elif operation=="EDIT":
                new_name=request.POST.get("new_name")
                edit_id=request.POST.get("edit_id")
                try:
                    conn.execute("UPDATE Customers SET CUSTOMER_NAME='"+new_name+"' WHERE CUSTOMER_ID="+edit_id)
                except Exception as e:
                    conn.rollback()
                    return JsonResponse(e)
                else:
                    conn.commit()
                    resp={"status":"success"}
                    return JsonResponse(resp)
    else:
        return redirect("login")
            
def employees(request):
    if request.session["role"]=="Admin":
        conn=sqlite3.connect("supermarket.db")
        cursor=conn.cursor()
        if request.method=="GET":
            tableData= conn.execute("SELECT * FROM Employees;").fetchall()
            data=json.dumps(tableData)
            return render(request,"employee.html",context={"data":data})
            
        elif request.method=="POST":
            operation=request.POST.get("operation")
            if operation=="ADD":
                name=request.POST.get("e_name")
                password=request.POST.get("password")
                try:
                    conn.execute("INSERT INTO Employees(EMPLOYEE_NAME,PASSWORD) VALUES(?,?);",(name,password)) 
                except Exception as e:
                    conn.rollback()
                    return HttpResponse(e)
                else:
                    conn.commit()
                    e_id=cursor.execute("SELECT EMPLOYEE_ID FROM Employees WHERE EMPLOYEE_NAME='"+name+"';").fetchone()[0]
                    resp={"id":e_id,"status":"success"}
                    return JsonResponse(resp)
                
            elif operation=="DELETE":
                id=request.POST.get("delete_id")
                try:
                    conn.execute("DELETE FROM Employees WHERE EMPLOYEE_ID="+id)
                except Exception as e:
                    conn.rollback()
                    return JsonResponse(e)
                else:
                    conn.commit()
                    resp={"status":"success"}
                    return JsonResponse(resp)
            
            elif operation=="EDIT":
                new_name=request.POST.get("new_name")
                edit_id=request.POST.get("edit_id")
                try:
                    conn.execute("UPDATE Employees SET EMPLOYEE_NAME='"+new_name+"' WHERE EMPLOYEE_ID="+edit_id)
                except Exception as e:
                    conn.rollback()
                    return JsonResponse(e)
                else:
                    conn.commit()
                    resp={"status":"success"}
                    return JsonResponse(resp)
    else:
        return redirect("login")

def vendors(request):
    if request.session["role"]=="Admin":
        conn=sqlite3.connect("supermarket.db")
        cursor=conn.cursor()
        if request.method=="GET":
            tableData= conn.execute("SELECT * FROM Vendors;").fetchall()
            data=json.dumps(tableData)
            return render(request,"vendor.html",context={"data":data})
            
        elif request.method=="POST":
            name=request.POST.get("c_name")
            operation=request.POST.get("operation")
            if operation=="ADD":
                try:
                    conn.execute("INSERT INTO Vendors(VENDOR_NAME) VALUES('"+name+"')") 
                except Exception as e:
                    conn.rollback()
                    return HttpResponse(e)
                else:
                    conn.commit()
                    c_id=cursor.execute("SELECT VENDOR_ID FROM Vendors WHERE VENDOR_NAME='"+name+"';").fetchone()[0]
                    resp={"id":c_id,"status":"success"}
                    return JsonResponse(resp)
                
            elif operation=="DELETE":
                id=request.POST.get("delete_id")
                try:
                    conn.execute("DELETE FROM Vendors WHERE VENDOR_ID="+id)
                except Exception as e:
                    conn.rollback()
                    return JsonResponse(e)
                else:
                    conn.commit()
                    resp={"status":"success"}
                    return JsonResponse(resp)
            
            elif operation=="EDIT":
                new_name=request.POST.get("new_name")
                edit_id=request.POST.get("edit_id")
                try:
                    conn.execute("UPDATE Vendors SET VENDOR_NAME='"+new_name+"' WHERE VENDOR_ID="+edit_id)
                except Exception as e:
                    conn.rollback()
                    return JsonResponse(e)
                else:
                    conn.commit()
                    resp={"status":"success"}
                    return JsonResponse(resp)
    else:
        return redirect("login")
            
def products(request):
    if request.session["role"]=="Admin":
        conn=sqlite3.connect("supermarket.db")
        cursor=conn.cursor()
        if request.method=="GET":
            tableData= conn.execute("SELECT * FROM Products;").fetchall()
            data=json.dumps(tableData)
            return render(request,"products.html",context={"data":data})
        elif request.method=="POST":
            operation=request.POST.get("operation")
            if operation=="ADD":
                name=request.POST.get("p_name")
                cp=request.POST.get("cp")
                sp=request.POST.get("sp")
                mq=request.POST.get("mq")
                try:
                    conn.execute("INSERT INTO Products(PRODUCT_NAME,COST_PRICE,SELLING_PRICE,MINIMUM_QUANTITY) VALUES(?,?,?,?)",(name,cp,sp,mq)) 
                except Exception as e:
                    conn.rollback()
                    return HttpResponse(e)
                else:
                    conn.commit()
                    p_id=cursor.execute("SELECT PRODUCT_ID FROM Products WHERE PRODUCT_NAME='"+name+"';").fetchone()[0]
                    resp={"id":p_id,"status":"success"}
                    return JsonResponse(resp)
                
            elif operation=="DELETE":
                id=request.POST.get("delete_id")
                try:
                    conn.execute("DELETE FROM Products WHERE PRODUCT_ID="+id)
                except Exception as e:
                    conn.rollback()
                    return JsonResponse(e)
                else:
                    conn.commit()
                    resp={"status":"success"}
                    return JsonResponse(resp)
    else:
        return redirect("login")


def purchase(request):
    if request.session["role"]=="Admin" or request.session["role"]=="Employee":
        conn=sqlite3.connect("supermarket.db")
        cursor=conn.cursor()
        if request.method=="GET":
            ProductData= conn.execute("SELECT PRODUCT_NAME, COST_PRICE,PRODUCT_ID FROM Products;").fetchall()
            vendorData= conn.execute("SELECT * FROM Vendors;").fetchall()
            data={"products":ProductData,"vendors":vendorData,"employee_id":request.session["user"]}
            data=json.dumps(data)
            return render(request,"purchase.html",context={"data":data,"user":request.session["role"]})
        elif request.method=="POST":
            operation=request.POST.get("operation")
            if operation=="ChooseVendor":
                vendorID=request.POST.get("vendorID")
                try:
                    id=request.session["id"]
                    conn.execute("INSERT INTO Purchases(EMPLOYEE_ID,VENDOR_ID) VALUES(?,?)",(id,vendorID))
                except Exception as e:
                    conn.rollback()
                    return HttpResponse(e)
                else:
                    conn.commit()
                    bill_id=cursor.execute("SELECT PURCHASE_ID FROM Purchases ORDER BY PURCHASE_ID DESC LIMIT 1;").fetchone()[0]
                    resp={"id":bill_id,"status":"success"}
                    return JsonResponse(resp)
            elif operation=="purchase":
                data=json.loads(request.POST.get("purchase_data"))
                purchase_id=request.POST.get("purchase_id")
                try:
                    for d in data:
                        cursor.execute("INSERT INTO PurchaseDetails(PURCHASE_ID,PRODUCT_ID,QUANTITY,PRICE) VALUES(?,?,?,(SELECT COST_PRICE FROM Products WHERE PRODUCT_ID=?)*?);",(purchase_id,d,data.get(d),d,data.get(d)))
                        cursor.execute("UPDATE Products SET QUANTITY=QUANTITY+? WHERE PRODUCT_ID=?",(data.get(d),d))
                        cursor.execute("UPDATE Purchases SET TOTAL=TOTAL+(SELECT COST_PRICE FROM Products WHERE PRODUCT_ID=?)*?",(d,data.get(d)))
                        
                    tax=cursor.execute("SELECT TAX FROM Purchases WHERE PURCHASE_ID=?",[(purchase_id)]).fetchone()[0]/100
                    total=cursor.execute("SELECT TOTAL FROM Purchases WHERE PURCHASE_ID=?",[(purchase_id)]).fetchone()[0]
                    cursor.execute("UPDATE Purchases SET GRAND_TOTAL=GRAND_TOTAL+? WHERE PURCHASE_ID=?",(total+(total*tax),purchase_id))
                except Exception as e:
                    conn.rollback()
                    return HttpResponse(e)
                else:
                    conn.commit()
                    print("else")
                    grand_total=cursor.execute("SELECT GRAND_TOTAL FROM Purchases WHERE PURCHASE_ID=?",[(purchase_id)]).fetchone()[0]
                    resp={"status":"success","total":total,"tax":tax,"grand_total":grand_total}
                    return JsonResponse(resp)
    else:
        return redirect("login")
        
def sales(request):
    if request.session["role"]=="Admin" or request.session["role"]=="Employee":
        conn=sqlite3.connect("supermarket.db")
        cursor=conn.cursor()
        if request.method=="GET":
            ProductData= conn.execute("SELECT PRODUCT_NAME, COST_PRICE,PRODUCT_ID,QUANTITY FROM Products;").fetchall()
            customerData= conn.execute("SELECT * FROM Customers;").fetchall()
            data={"products":ProductData,"customers":customerData,"employee_id":request.session["user"]}
            data=json.dumps(data)
            return render(request,"sales.html",context={"data":data,"user":request.session["role"]})
        elif request.method=="POST":
            operation=request.POST.get("operation")
            if operation=="Choosecustomer":
                customerID=request.POST.get("customerID")
                try:
                    conn.execute("INSERT INTO Sales(EMPLOYEE_ID,CUSTOMER_ID) VALUES(?,?)",(1,customerID))
                except Exception as e:
                    conn.rollback()
                    return HttpResponse(e)
                else:
                    conn.commit()
                    bill_id=cursor.execute("SELECT SALE_ID FROM Sales ORDER BY SALE_ID DESC LIMIT 1;").fetchone()[0]
                    resp={"id":bill_id,"status":"success"}
                    return JsonResponse(resp)
            elif operation=="sales":
                data=json.loads(request.POST.get("sale_data"))
                sale_id=request.POST.get("sale_id")
                try:
                    for d in data:
                        cursor.execute("INSERT INTO SaleDetails(SALE_ID,PRODUCT_ID,QUANTITY,PRICE) VALUES(?,?,?,(SELECT COST_PRICE FROM Products WHERE PRODUCT_ID=?)*?);",(sale_id,d,data.get(d),d,data.get(d)))
                        cursor.execute("UPDATE Products SET QUANTITY=QUANTITY-? WHERE PRODUCT_ID=?",(data.get(d),d))
                        cursor.execute("UPDATE Sales SET TOTAL=TOTAL+(SELECT COST_PRICE FROM Products WHERE PRODUCT_ID=?)*?",(d,data.get(d)))
                    tax=cursor.execute("SELECT TAX FROM Sales WHERE SALE_ID=?",[(sale_id)]).fetchone()[0]/100
                    total=cursor.execute("SELECT TOTAL FROM Sales WHERE SALE_ID=?",[(sale_id)]).fetchone()[0]
                    cursor.execute("UPDATE Sales SET GRAND_TOTAL=GRAND_TOTAL+? WHERE SALE_ID=?",(total+(total*tax),sale_id))
                except Exception as e:
                    conn.rollback()
                    return HttpResponse(e)
                else:
                    conn.commit()
                    grand_total=cursor.execute("SELECT GRAND_TOTAL FROM Sales WHERE SALE_ID=?",[(sale_id)]).fetchone()[0]
                    resp={"status":"success","total":total,"tax":tax,"grand_total":grand_total}
                    return JsonResponse(resp)
    else:
        return redirect("login")
            
def purchaseReports(request):
    if request.session["role"]=="Admin":
        conn=sqlite3.connect("supermarket.db")
        operation = ''
        if request.method=="GET":
            operation=request.GET.get("operation")
            if operation=="getProducts":
                id=request.GET.get("id")
                data=conn.execute("SELECT pr.PRODUCT_NAME, pd.QUANTITY FROM PurchaseDetails as pd JOIN Products as pr ON pr.PRODUCT_ID=pd.PRODUCT_ID JOIN Purchases as p ON pd.PURCHASE_ID=p.PURCHASE_ID WHERE pd.PURCHASE_ID=?",[(id)]).fetchall()
                resp={"data":data,"status":"success"}
                return JsonResponse(resp)
            
            else:
                data=conn.execute("SELECT e.EMPLOYEE_NAME, v.VENDOR_NAME, p.PURCHASE_ID,p.TOTAL,p.TAX,p.GRAND_TOTAL, p.PURCHASE_DATE FROM PurchaseDetails as pd JOIN Purchases as p ON pd.PURCHASE_ID=p.PURCHASE_ID JOIN Employees as e ON p.EMPLOYEE_ID=e.EMPLOYEE_ID JOIN Vendors as v ON v.VENDOR_ID=p.VENDOR_ID ;").fetchall()
                jsonData=json.dumps(data)
                return render(request,"purchaseReports.html",context={"data":jsonData})         
    else:                    
        return redirect("login")
        
def salesReports(request):
    if request.session["role"]=="Admin":
        conn=sqlite3.connect("supermarket.db")
        operation = ''
        if request.method=="GET":
            operation=request.GET.get("operation")
            if operation=="getProducts":
                id=request.GET.get("id")
                data=conn.execute("SELECT pr.PRODUCT_NAME, pd.QUANTITY FROM SaleDetails as pd JOIN Products as pr ON pr.PRODUCT_ID=pd.PRODUCT_ID JOIN Sales as p ON pd.SALE_ID=p.SALE_ID WHERE pd.SALE_ID=?",[(id)]).fetchall()
                resp={"data":data,"status":"success"}
                return JsonResponse(resp)
            
            else:
                data=conn.execute("SELECT e.EMPLOYEE_NAME, c.CUSTOMER_NAME, s.SALE_ID,s.TOTAL,s.TAX,s.GRAND_TOTAL, s.SALE_DATE FROM SaleDetails as sd JOIN Sales as s ON sd.SALE_ID=s.SALE_ID JOIN Employees as e ON s.EMPLOYEE_ID=e.EMPLOYEE_ID JOIN Customers as c ON c.CUSTOMER_ID=s.CUSTOMER_ID;").fetchall()
                jsonData=json.dumps(data)
                return render(request,"salesReports.html",context={"data":jsonData})           
    else:
        return redirect("login")
    
def productReports(request):
    if request.session["role"]=="Admin":
        conn=sqlite3.connect("supermarket.db")
        if request.method=="GET":
            operation = request.GET.get("operation")
            if operation=="purchase":
                data = conn.execute("SELECT pr.PRODUCT_ID, pr.PRODUCT_NAME,p.PURCHASE_DATE,pd.QUANTITY FROM PurchaseDetails as pd JOIN Purchases as p ON pd.PURCHASE_ID=p.PURCHASE_ID JOIN Products as pr ON pd.PRODUCT_ID=pr.PRODUCT_ID;").fetchall()
                resp={"data":data,"status":"success"}
                return JsonResponse(resp)
            elif operation=="sale":
                data = conn.execute("SELECT pr.PRODUCT_ID, pr.PRODUCT_NAME,s.SALE_DATE,sd.QUANTITY FROM SaleDetails as sd JOIN Sales as s ON sd.SALE_ID=s.SALE_ID JOIN Products as pr ON sd.PRODUCT_ID=pr.PRODUCT_ID;").fetchall()
                resp={"data":data,"status":"success"}
                return JsonResponse(resp)
        return render(request,"productReports.html")
    else:
        return redirect("login")
    
def productReStock(request):
    if request.session["role"]=="Admin":
        conn=sqlite3.connect("supermarket.db")
        if request.method=="GET":
            tableData= conn.execute("SELECT PRODUCT_ID, PRODUCT_NAME, QUANTITY, COST_PRICE FROM Products WHERE QUANTITY<=MINIMUM_QUANTITY;").fetchall()
            vendorData=conn.execute("SELECT * FROM Vendors;").fetchall()
            data={"productData":tableData,"vendorData":vendorData}
            completeData=json.dumps(data)
            return render(request,"productReStock.html",context={"data":completeData})
    else:
        return redirect("login")