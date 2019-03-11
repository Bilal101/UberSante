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
        elif availableRoom == False:
            raise Exception('No room is available!')
        
        else:
            return [doctorsAvailable, availableRoom]
        

    def create_appointment(self,doctor_speciality, patient_id, appointment_date, start_time, end_time):
        conn = AppointmentController.connect_database(self)
        doctor_id = AppointmentController.find_a_doctor(conn, doctor_speciality, appointment_date, start_time, end_time)
        if doctor_id == False:
            raise Exception('No doctor is available!')
        appointment_room = AppointmentController.find_room(conn, appointment_date, start_time, end_time)
        if appointment_room == False:
            raise Exception('No room is available!')
        appointment_status = "Approved"
        appointment_type = AppointmentController.getappointment_type(start_time, end_time)
        AppointmentController.finalize_appointment(conn, appointment_room, appointment_type, appointment_status, appointment_date, start_time, end_time, patient_id, doctor_id)
        return True

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


    def find_room(conn, appointment_date, start_time, end_time):
        query = "SELECT appointment_room FROM appointment WHERE appointment_date=? AND ((start_time<=? AND end_time>?) OR (start_time<? AND end_time>=?))"
        query2 = "SELECT id FROM room"
        conn.execute(query, (appointment_date, start_time, start_time, end_time, end_time))
        occupied = conn.fetchall()
        conn.execute(query2, ())

        availableRooms = conn.fetchall()
        #print("ROOM")
        #print(availableRooms[0][0])
        for room in availableRooms:
            if room in occupied:
                availableRooms.remove(room)
        if availableRooms != []:
            return availableRooms[0]
        else:
            return False


    def find_a_doctor(conn, doctor_speciality, appointment_date, start_time, end_time):
        query = "SELECT id FROM doctor WHERE speciality=?"
        query2 = "SELECT doctor_id FROM doctoravailability WHERE date_day=? AND start_time<=? AND end_time>=?"
        query3 = "SELECT start_time, end_time FROM appointment WHERE doctor_id=? AND appointment_date=? AND ((start_time<=? AND end_time>?) OR (start_time<? AND end_time>=?))"

        # query = "SELECT id FROM doctor WHERE speciality=""'"+doctor_speciality+"'"""
        #query2 = "SELECT doctor_id FROM doctoravailability WHERE date_day=""'"+appointment_date+"'"""+" AND start_time<=""'"+start_time+"'"""\
                 #+" AND end_time>=""'"+end_time+"'"""
        #query3 = "SELECT start_time, end_time FROM appointment WHERE doctor_id=? AND appointment_date=? AND ((start_time<=? AND end_time>?) OR (start_time<? AND end_time>=?))"
        # conn.execute(query)
        # conn.execute(query)

        conn.execute(query,(doctor_speciality,))
        specialists = conn.fetchall()
        conn.execute(query2,(appointment_date, start_time, end_time))
        availableDoctors = conn.fetchall()

        for specialist in specialists:
            if specialist in availableDoctors:
                print(specialist)
                idtuple = specialist[0]
                id = int(idtuple)
                print(id)
                conn.execute(query3, (id, appointment_date, start_time, start_time, end_time, end_time))
                allAppointmentTimes = conn.fetchall()
                if allAppointmentTimes == []:
                    return specialist
        return False


    def connect_database(self):
        try:
            conn = sqlite3.connect('./app/database/SOEN344_DATABASE.db')
            c = conn.cursor()
            return c
        except Error as e:
            print(e)
            return None
            
    def finalize_appointment(conn, appointment_room, appointment_type, appointment_status, appointment_date, start_time, end_time, patient_id, doctor_id):
        try:

            query = "INSERT INTO appointment(appointment_room, appointment_type, appointment_status," \
                    " appointment_date, start_time, end_time, patient_id, doctor_id)" \
                    "VALUES (?,?,?,?,?,?,?,?)"
                    #"("+str(appointment_room)+")

            print(query)
            '''
                appointment_room = int(appointment_room[0])
                doctor_id = int(doctor_id[0])
            '''

            item = (str(appointment_room[0]), appointment_type, appointment_status, appointment_date, str(start_time), str(end_time),str(patient_id),str(doctor_id[0]))
            print(item)
            conn.execute(query,item)
            result = conn.fetchall()
            print(result)
            return True

        except Error as e:
            #print("START")
            #print(item)
            print(e)
            return False

    def find_appointment(conn, doctor_id, appointment_date):
        conn = AppointmentController.connect_database()
        query = "SELECT * FROM appointment WHERE doctor_id =? AND appointment_date=?"
        conn.execute(query,(doctor_id, appointment_date))
        result = conn.fetchall()
        return result