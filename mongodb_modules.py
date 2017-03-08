from pymongo import MongoClient
import json



client = MongoClient('localhost:27017')
db = client.BBH
stu_rec_coll = db.stu_rec_coll
bbh_univ_coll = db.bbh_univ

bbh_univ = ["School","first and last name","student id" ,"email", "ID Number","DOB", "Home Address","SSN","Phone" ,"Semester","Security A"]
# stu_rec_coll = []
def add_to_bbh(data):
    db.bbh_univ.insert((data))

def add_to_stud(data) :
    db.stu_rec_coll.insert((data))  

# def del_from_bbh(ids):  
#     db.bbh_univ

# def del_from_stu(ids) :
#     db.stu_rec_coll    

def query_in_bbh(data):
    
    # print db.bbh_univ.find()
    db.bbh_univ.find(data)
    return db.bbh_univ.find(data)

def query_in_st(data) :
    db.stu_rec_coll.find(data)
    return db.stu_rec_coll.find(data)


def main():

    while(1):
    # chossing option to do CRUD operations
        selection = raw_input('\nSelect 1 to insert, 2 to update, 3 to read, 4 to delete\n')
    
        if selection == '1':
            insert()
        # elif selection == '2':
        #     update()
        # elif selection == '3':
        #     read()
        # elif selection == '4':
        #     delete()
        else:
            print '\n INVALID SELECTION \n'



def insert():
    # try:
        rec = list()
        table = "bbh_univ"
        all_data=list()
        data={}
        collection ={ "1":"bbh_univ", "2":"stu_rec_coll" }
        while True: 
            
            input_rec= raw_input("Enter 1:BBH_univ , 2:Stu_rec ")
            no_of_rec = raw_input("Enter no of records you wish to add : ")
            print str(input_rec) not in collection.keys()
            if str(input_rec) not in collection.keys() :

              print "Please enter a valid selction"
            else :
              # table = collection[int(input_rec)]
              break 
        
        print "asdad"
        for z in xrange(int(no_of_rec)):
            print "For %s record , Please enter only (Y/N) for student records table :\n"%(z+1) 
            for i in xrange(len(bbh_univ)):
              input1= raw_input("Please enter your "+bbh_univ[i]+".\n")
              print bbh_univ[i]
              data[bbh_univ[i]]=input1
            all_data.append((data))
            data = {}  
        
        if str(input_rec) =='1' :
          add_to_bbh(all_data)
        elif str(input_rec) == '2':
          add_to_stud(all_data)

        print "Record(s) Added Succesfully!"      
        

    
    # except Exception, e:
    #     print str(e)            


# def update():
#     try:
#     criteria = raw_input('\nEnter id to update\n')
#     name = raw_input('\nEnter name to update\n')
#     age = raw_input('\nEnter age to update\n')
#     country = raw_input('\nEnter country to update\n')

#     db.Employees.update_one(
#         {"id": criteria},
#         {
#         "$set": {
#             "name":name,
#             "age":age,
#             "country":country
#         }
#         }
#     )
#     print "\nRecords updated successfully\n"    
    
#     except Exception, e:
#     print str(e)

# def delete():
#     try:
#         coll_=raw_input('\nChoose table to delete from , 1:BBH_univ, 2: Stu_rec\n')    
#         id_ = raw_input('\nEnter student ids to delete\n')

#             db.Employees.delete_many({"id":id_})
#         print '\nDeletion successful\n' 
#     except Exception, e:
#      print str(e) 


def query_mongodb(table_no,json_query) :
    # try :
        if table_no == 1 :
            return query_in_bbh(json_query)
       
        elif tabl_no == 2 :
           return query_in_st(json_query) 

        else  :
            return "Invalid table choice."
    # except:
    #          print "query error!"


# main()