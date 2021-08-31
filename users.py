import random
import string
import time
import xml.etree.ElementTree as xml

from timeloop import Timeloop
import datetime
from config import db

tl = Timeloop()


def load_users(iter = 0):
    try:
        print("Load new users!")
        root_node = xml.parse('Partners.xml').getroot()
        letters = string.ascii_lowercase + "0123456789" + string.ascii_uppercase
        f = open('users.txt','w')
        list_user = {}
        for post in db.users.find():
            list_user[post['code']] = f"{post['login']} {post['pas']}"
        for tag in root_node.findall("Partner"):
            rand_login = ''.join(random.choice(letters) for i in range(6))
            rand_pas= ''.join(random.choice(letters) for i in range(6))
            if tag.attrib['Code'] not in list_user:
                f.write(f"{tag.attrib['Name']} login:{rand_login} pas:{rand_pas} \n")
                db.users.insert_one({'name': tag.attrib['Name'],
                                     "login":rand_login,
                                     "pas":rand_pas,
                                     "code":tag.attrib['Code'],
                                     "shopping cart":[]})
            else:
                logpas = list_user[tag.attrib['Code']].split(' ')
                f.write(f"{tag.attrib['Name']} login:{logpas[0]} pas:{logpas[1]} \n")
        f.close()
    except:

        if iter<3:
            return load_users(iter+1)
        else:
            return [], -1
    return



@tl.job(interval=datetime.timedelta(hours=10))
def load_user():
    load_users()

tl.start(block=True)
