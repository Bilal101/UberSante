import sqlite3
import sqlite3 as mysql
import sys
from sqlite3 import Error
import app.classes.database_container
from app.common_definitions.common_paths import PATH_TO_DATABASE
from app.controllers.nursecontroller import *

class AppointmentController:
    def isAvailable(self, doctor_speciality, appointment_date, start_time, end_time):
        conn = AppointmentController.connect_database()
        doctorsAvailable = AppointmentController.find_a_doctor(conn, doctor_speciality, appointment_date, start_time, end_time)
        availableRoom = AppointmentController.find_room(conn, appointment_date, start_time, end_time)

        # If no doctor is available
        if doctorsAvailable == False:
            raise Exception('No doctor is available!')

        # If no room is available
        elif availableRoom == False or doctorsAvailable == "No room available!":
            raise Exception('No room is available!')

        else:
            return [doctorsAvailable, availableRoom]


    def create_appointment(self,doctor_speciality, patient_id, appointment_date, start_time, end_time, day_of_week,clinic_name_picked):
        conn = AppointmentController.connect_database(self)
        database = db.get_instance()
        queryexecute = database.execute_query("SELECT id FROM room WHERE id = 2")
        print(conn.rowcount)
        database.commit_db()
        if conn.rowcount == -1:
            data = ''
        else:
            data = database.fetchall()
            database.execute_query("INSERT INTO room(id,name)" \
                                   "VALUES (?,?)", (2, "test"))
        print(data)

        #print(data[0]['id'])

        database.commit_db()
        '''print("DOCTOR")
        print(doctor_speciality)'''
        doctor_id = AppointmentController.find_a_doctor(conn, doctor_speciality, appointment_date, start_time, end_time , day_of_week)
        '''print("MOOSe")
        print(doctor_id)'''
        if doctor_id == False:
            message = "No doctor is available!"
            return message
            #raise Exception('No doctor is available!')
        appointment_room = AppointmentController.find_room(conn, appointment_date, start_time, end_time, clinic_name_picked)
        if appointment_room == False or doctor_id == "No room available!":
            #message = "Availability Added"
            message = "No room is available!"
            return message
            #raise Exception('No room is available!')
        appointment_status = "Approved"
        appointment_type = AppointmentController.getappointment_type(start_time, end_time)

        print(type(doctor_id))
        AppointmentController.finalize_appointment(conn, appointment_room, appointment_type, appointment_status, appointment_date, start_time, end_time, patient_id, doctor_id,clinic_name_picked)
        message = "Appointment Added"
        return message


    def getappointment_type(start_time, end_time):
        def get_sec(time_str):
            h, m, s = time_str.split(':')
            return int(h) * 3600 + int(m) * 60 + int(s)
        start = get_sec(start_time)
        end = get_sec(end_time)
        if (end - start) == 1200:
            return "Regular"
        elif (end - start) == 3600:
            return "Annual"
        else:
            return "Special"


    def find_room(conn, appointment_date, start_time, end_time, clinic_name):
        #query = "SELECT appointment_room FROM appointment WHERE appointment_date=? AND ((start_time<=? AND end_time>?) OR (start_time<? AND end_time>=?))"
        query = "SELECT appointment_room FROM appointment WHERE appointment_date=? AND ((start_time==? AND end_time==?) OR  (start_time<=? AND end_time>?) OR (start_time<? AND end_time>=?))"
        query2 = "SELECT room_number FROM room WHERE clinic_name="+"'"+ clinic_name+ "'"
        conn.execute(query, (appointment_date, start_time,end_time,start_time,start_time,end_time,end_time))
        occupied = conn.fetchall()
        print("hello")
        conn.execute(query2, ())
        availableRooms = conn.fetchall()

        result = sorted(set(availableRooms) - set(occupied))

        if result != []:
            return result[0]
        else:
            return False


    def find_a_doctor(conn, doctor_speciality, appointment_date, start_time, end_time , day_of_week):
        query = "SELECT id FROM doctor WHERE speciality=?"
        query2 = "SELECT doctor_id FROM doctoravailability WHERE date_day=? AND start_time<=? AND end_time>=?"
        #query3 = "SELECT start_time, end_time FROM appointment WHERE doctor_id=? AND appointment_date=? AND ((start_time<? AND end_time>?) OR (start_time<? AND end_time>?))"
        query3 = "SELECT id FROM appointment WHERE doctor_id=? AND appointment_date=? AND ((start_time==? AND end_time==?) OR  (start_time<=? AND end_time>?) OR (start_time<? AND end_time>=?))"

        # query = "SELECT id FROM doctor WHERE speciality=""'"+doctor_speciality+"'"""
        #query2 = "SELECT doctor_id FROM doctoravailability WHERE date_day=""'"+appointment_date+"'"""+" AND start_time<=""'"+start_time+"'"""\
                 #+" AND end_time>=""'"+end_time+"'"""
        #query3 = "SELECT start_time, end_time FROM appointment WHERE doctor_id=? AND appointment_date=? AND ((start_time<=? AND end_time>?) OR (start_time<? AND end_time>=?))"
        # conn.execute(query)
        # conn.execute(query)
        '''print("DA DOC")
        print("SELECT id FROM doctor WHERE speciality="+doctor_speciality)
        print(type(doctor_speciality))'''

        conn.execute(query,(doctor_speciality,))
        specialists = conn.fetchall()
        conn.execute(query2,(day_of_week, start_time,end_time))
        availableDoctors = conn.fetchall()

        '''print("DOCCCCCS")
        print(availableDoctors)
        print(specialists)

        print(day_of_week)
        print(start_time)
        print(end_time)'''

        for specialist in specialists:
            '''print("HHHHH")
            print(specialist)'''
            allAppointmentTimes = []
            if specialist in availableDoctors:
                print("HEEEEEERE")
                '''print(specialist)'''
                idtuple = specialist[0]
                id = int(idtuple)
                #print(id)
                conn.execute(query3, (1, appointment_date, start_time,end_time,start_time,start_time,end_time,end_time))
                allAppointmentTimes = conn.fetchall()
                print("HEEELOO")
                print(allAppointmentTimes)
                count = 0
                for i in allAppointmentTimes:
                    count+=1
                    print("yoyoyo")
                    print(count)
                if count < 5:

                #if allAppointmentTimes == []:
                    #specialist = specialist
                    return specialist
                else:
                    message = "No room available!"
                    return message
        '''if allAppointmentTimes == []:
            return specialist   '''
        return False


    def connect_database(self):
        try:
            conn = sqlite3.connect('./app/database/SOEN344_DATABASE.db')
            c = conn.cursor()
            return c
        except Error as e:
            print(e)
            return None
            
    def finalize_appointment(conn, appointment_room, appointment_type, appointment_status, appointment_date, start_time, end_time, patient_id, doctor_id,clinic_name_picked):
        try:
            database = db.get_instance()

            item = (str(appointment_room[0]), appointment_type, appointment_status, appointment_date, str(start_time),
                    str(end_time), str(patient_id), int(doctor_id[0]),str(clinic_name_picked))

            print(item)
 
            print(clinic_name_picked)

            database.execute_query("INSERT INTO appointment(appointment_room, appointment_type, appointment_status," \
                    " appointment_date, start_time, end_time, patient_id, doctor_id,clinic_name)" \
                    "VALUES (?,?,?,?,?,?,?,?,?)",(str(appointment_room[0]), appointment_type, appointment_status, appointment_date, str(start_time),
                    str(end_time), str(patient_id), int(doctor_id[0]),str(clinic_name_picked)))
            database.commit_db()

            #print(query)
            #conn.execute(query,item)
            #result = conn.fetchall()

            #return True

        except Error as e:
            print(e)
            #return False


    def find_appointment(conn, doctor_id, appointment_date):
        conn = AppointmentController.connect_database()
        query = "SELECT * FROM appointment WHERE doctor_id =? AND appointment_date=?"
        conn.execute(query,(doctor_id, appointment_date))
        result = conn.fetchall()
        return result

    def appointmentupdate(self,doctor_speciality, patient_id, appointment_date, start_time, end_time,id,day_of_week,clinic_name):
        conn = AppointmentController.connect_database(self)
        doctor_id = AppointmentController.find_a_doctor(conn, doctor_speciality, appointment_date, start_time, end_time,day_of_week)
        if doctor_id == False:
            raise Exception('No doctor is available!')
        appointment_room = AppointmentController.find_room(conn, appointment_date, start_time, end_time,clinic_name)
        if appointment_room == False or doctor_id == "No room available!":
            raise Exception('No room is available!')
        appointment_status = "Approved"
        appointment_type = AppointmentController.getappointment_type(start_time, end_time)
        AppointmentController.update_appointment(conn, appointment_room, appointment_type, appointment_status, appointment_date, start_time, end_time, patient_id, doctor_id,id )
        return True

    def update_appointment(conn, appointment_room, appointment_type, appointment_status, appointment_date, start_time, end_time, patient_id, doctor_id,id):
        try:
            database = db.get_instance()
            item = (str(appointment_room[0]), appointment_type, appointment_status, appointment_date,
                                       str(start_time),
                                       str(end_time), str(patient_id), int(doctor_id[0]))

            database.execute_query("UPDATE appointment SET appointment_room =?, appointment_type = ?, appointment_status = ?,appointment_date = ?,start_time = ?,end_time= ?,patient_id = ?, doctor_id = ? WHERE id = ?;",
                                 (
                                       str(appointment_room[0]), appointment_type, appointment_status, appointment_date,
                                       str(start_time),
                                       str(end_time), str(patient_id), int(doctor_id[0]),id))

            print(str(appointment_room[0]), appointment_type, appointment_status, appointment_date,
                                       str(start_time),
                                       str(end_time), str(patient_id), int(doctor_id[0]),id)

            database.commit_db()

        except Error as e:
            print(e)
            return False

    def getallappointments(self, patient_id):
        database = db.get_instance()
        query = "SELECT * FROM appointment WHERE patient_id=" + str(patient_id)
        print(query)
        queryexecute = database.execute_query(query)
        data = queryexecute.fetchall()
        return data


    def appointmentdelete(self,doctor_speciality, patient_id, appointment_date, start_time, end_time,id,day_of_week,clinic_name):
        conn = AppointmentController.connect_database(self)
        doctor_id = AppointmentController.find_a_doctor(conn, doctor_speciality, appointment_date, start_time, end_time,day_of_week)
        '''if doctor_id == False:
            raise Exception('No doctor is available!')'''
        appointment_room = AppointmentController.find_room(conn, appointment_date, start_time, end_time,clinic_name)
        '''if appointment_room == False:
            raise Exception('No room is available!')'''
        appointment_status = "Approved"
        appointment_type = AppointmentController.getappointment_type(start_time, end_time)
        AppointmentController.delete_appointment(conn, appointment_room, appointment_type, appointment_status, appointment_date, start_time, end_time, patient_id, doctor_id,id)
        return True

    def delete_appointment(conn, appointment_room, appointment_type, appointment_status, appointment_date, start_time, end_time, patient_id, doctor_id,id):
        try:
            database = db.get_instance()

            database.execute_query("DELETE FROM appointment WHERE id = "+id+";")
            print("HI")
            print(id)


            database.commit_db()
        except Error as e:
            print(e)
            return False

    '''def get_upcoming_appointmnents_patient(self):
        database = db.get_instance()

        return 0'''
    def deleteappointment(self, appointment_id):
        database = db.get_instance()
        print(appointment_id)
        appointment_id = str(appointment_id)
        query = "DELETE FROM appointment WHERE id =" + appointment_id
        database.execute_query(query)
        database.commit_db()
        message = "Availability Deleted"
        return message

    def getallappointmentsfordoctor(self, doctor_id,clinic_name):
        database = db.get_instance()
        query = "SELECT * FROM appointment WHERE doctor_id=" + str(doctor_id) + " AND clinic_name="+"'"+ clinic_name + "'"
        print(query)
        queryexecute = database.execute_query(query)
        data = queryexecute.fetchall()
        return data
